import asyncio
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from .graph import AssumptionNode, Graph, Node, Edge, NODE_IP, NODE_TASK, ProductNode, TaskNode
from .llm import FAST_LLM
from .prompts import templates

class Worker(ABC):
    '''Meta-cognitive Worker'''

    def get_setup_order(self) -> int:
        '''Lower order = earlier in setup'''
        # Very simplistic system, likely will need to be redesigned
        return 0
    
    async def setup(self, graph: Graph):
        '''Runs once when workers are added to nexus'''
        pass

    async def cycle(self, graph: Graph):
        '''
        Do one cycle with this worker; the implementation will vary widely depending on the worker's purpose.
        Each cycle should be finite, though potentially cycles could be executed indefinitely.
        '''
        pass

class Planner(Worker):
    '''Creates subgraph of subtasks necessary to achieve final goal'''

    def get_setup_order(self) -> int:
        return 100
    
    async def setup(self, graph: Graph):
        # Late setup to have knowledge for available actions etc.
        # Create a subgraph of subtasks with dependency relations as edges, connected to the final goal.
        class NodeItem(BaseModel):
            id: str
            content: str
            action_types: list[str]

        class EdgeItem(BaseModel):
            from_id: str
            to_id: str
        
        class Output(BaseModel):
            nodes: list[NodeItem]
            edges: list[EdgeItem]
        
        prompt = templates.Planner(
            goal=graph.goal,
            graph_context=graph.build_context(),
            action_types="\n".join([f"- {node.id}" for node in graph.query_nodes_by_tag("action_definition")])
        ).render()

        #print("Planning prompt:", prompt, sep="\n")

        resp = await graph.llm.with_structured_output(Output).ainvoke(prompt)
        #resp = await graph.llm.with_structured_output(Output, strict=True).ainvoke(prompt)

        added_nodes = []

        # Build subgraph, todo: could create utils for creating subgraph as structured out
        for item in resp.nodes:
            node = TaskNode(item.id, item.content, item.action_types)
            graph.add_node(node)
            added_nodes.append(node)
        for item in resp.edges:
            graph.add_edge_by_ids(item.from_id, "dependency", item.to_id)
        
        # Finally, for any nodes with no generated outgoing edges, we connect them to final_goal
        goal_node = graph.query_node_by_id("final_goal")
        for node in added_nodes:
            if len(node.downstream_nodes()) == 0:
                graph.add_edge(Edge(node, "achieves", goal_node))
        


class IntermediateProductBuilder(Worker):
    async def cycle(self, graph: Graph):
        class Node(BaseModel):
            id: str# = Field("id of dependency node")
            content: str
        
        class Output(BaseModel):
            dependency_ids: list[str]
            result: Node

        prompt = templates.FrontSearch(
            goal=graph.goal,
            graph_context=graph.build_context(),# TODO what types of nodes do we want here? tmp wildcard
            intermediate_products="\n".join([node.content() for node in filter(lambda n: isinstance(n, ProductNode), graph.get_nodes())])
        ).render()

        #print("IP Builder prompt:", prompt, sep="\n")
    
        resp = await graph.llm.with_structured_output(Output).ainvoke(
            prompt
        )
        #print(resp)
        # "ProductNode" feels very silly
        dest_node = ProductNode(resp.result.id, resp.result.content)

        for dep_id in resp.dependency_ids:
            src_node = graph.query_node_by_id(dep_id)
            if src_node is None:
                raise RuntimeError(f"No existing node with ID `{dep_id}`")
            graph.add_edge(Edge(src_node, "needed for", dest_node))

class AssumptionBuilder(Worker):
    def get_setup_order(self) -> int:
        return 50

    async def setup(self, graph: Graph):
        goal_node = graph.query_node_by_id("final_goal")
        context = graph.build_context()

        prompt = templates.Assumptions(
            goal=graph.goal,
            graph_context=context
        ).render()

        #print("Assumption Builder prompt:", prompt, sep="\n")

        class Assumption(BaseModel):
            id: str
            description: str
        
        class Output(BaseModel):
            assumptions: list[Assumption]

        resp = await graph.llm.with_structured_output(Output).ainvoke(
            prompt
        )
        #print(resp)

        for item in resp.assumptions:
            new_node = AssumptionNode(item.id, item.description)
            graph.add_node(new_node)
            graph.add_edge(Edge(new_node, "assumption", goal_node))

import asyncio
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from .graph import Graph, Node, Edge, NODE_IP, NODE_TASK, ProductNode, TaskNode
from .llm import FAST_LLM
from .prompts import templates

class Worker(ABC):
    '''Meta-cognitive Worker'''
    async def setup(self, graph: Graph):
        pass

    async def cycle(self, graph: Graph):
        '''
        Do one cycle with this worker; the implementation will vary widely depending on the worker's purpose.
        Each cycle should be finite, though potentially cycles could be executed indefinitely.
        '''
        pass

class DependencyDecomposer(Worker):
    def __init__(self):
        self.frontier = None
    
    async def cycle(self, graph: Graph):
        class Subtask(BaseModel):
            id: str
            task: str
        
        class Output(BaseModel):
            subtasks: list[Subtask]
        
        if self.frontier is None:
            self.frontier = [graph.goal_node]
        new_frontier = []

        jobs = []
        for node in self.frontier:
            task = node.content()
            print(f"Expanding: {task}")
            job = FAST_LLM.with_structured_output(Output).ainvoke(
                templates.BackSearch(
                    goal=graph.goal,
                    task=task,
                    graph_context=graph.build_context(Node)# TODO what types of nodes do we want here? tmp wildcard
                ).render()
            )
            jobs.append(job)

        responses = await asyncio.gather(*jobs)

        for node, response in zip(self.frontier, responses):
            print(response)
            for subtask in response.subtasks:
                new_node = TaskNode(subtask.id, subtask.task)
                graph.add_node(new_node)
                graph.add_edge(Edge(new_node, "required for", node))
                new_frontier.append(new_node)
        self.frontier = new_frontier

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
            graph_context=graph.build_context(Node),# TODO what types of nodes do we want here? tmp wildcard
            intermediate_products="\n".join([node.content() for node in filter(lambda n: isinstance(n, ProductNode), graph.nodes)])
        ).render()

        print("IP Builder prompt:", prompt, sep="\n")
    
        resp = await FAST_LLM.with_structured_output(Output).ainvoke(
            prompt
        )
        print(resp)
        # "ProductNode" feels very silly
        dest_node = ProductNode(resp.result.id, resp.result.content)

        for dep_id in resp.dependency_ids:
            src_node = graph.query_node_by_id(dep_id)
            if src_node is None:
                raise RuntimeError(f"No existing node with ID `{dep_id}`")
            graph.add_edge(Edge(src_node, "needed for", dest_node))

        # FIXME - query src nodes instead by ID check if exist
        # src_nodes = [ProductNode(dep, NODE_IP) for dep in resp.dependencies]
        # for src_node in src_nodes:
        #     graph.add_edge(Edge(src_node, "needed for", dest_node))


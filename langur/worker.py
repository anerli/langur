from abc import ABC
from .graph import Graph, Edge, TaskNode
from langur.baml_client import b

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
        resp = await b.PlanSubtasks(
            goal=graph.goal,
            graph_context=graph.build_context(),
            action_types="\n".join([f"- {node.id}" for node in graph.query_nodes_by_tag("action_definition")])
        )

        #print(resp)

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

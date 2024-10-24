from .worker import Worker
from langur.graph.node import Node
from langur.graph.edge import Edge
import langur.baml_client as baml

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from langur.graph.graph import Graph


class TaskNode(Node):
    tags: ClassVar[list[str]] = ["task"]

    content: str
    action_types: list[str]

    # tmp, refactor callers
    def __init__(self, id: str, content: str, action_types: list[str]):
        super().__init__(id=id, content=content, action_types=action_types)
        #self._content = content
        #self.action_types = action_types
    
    def content(self):
        return f"{self._content} {self.action_types}"

class Planner(Worker):
    '''Creates subgraph of subtasks necessary to achieve final goal'''

    def get_setup_order(self) -> int:
        return 100
    
    async def setup(self, graph: 'Graph'):
        # Late setup to have knowledge for available actions etc.
        # Create a subgraph of subtasks with dependency relations as edges, connected to the final goal.
        resp = await baml.b.PlanSubtasks(
            goal=graph.goal,
            graph_context=graph.build_context(),
            action_types="\n".join([f"- {node.id}" for node in graph.query_nodes_by_tag("action_definition")]),
            baml_options={"client_registry": graph.cr}
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

from langur.actions import ActionNode
from langur.graph.graph import Graph
from langur.graph.node import Node
from langur.workers.worker import Worker


class ExecutorWorker(Worker):
    def get_frontier(self, graph: Graph) -> set[ActionNode]:
        '''
        Get the "frontier", i.e. unexecuted action nodes with only executed depedencies.
        '''
        action_nodes: set[ActionNode] = graph.query_nodes_by_tag("action")

        # Naive linear impl
        frontier = set()
        for node in action_nodes:
            valid = True
            for upstream_node in node.upstream_nodes():
                if "action" in upstream_node.get_tags() and upstream_node.output is None:
                    # Upstream un-executed action
                    valid = False
                    break
            if valid:
                frontier.add(node)
        
        return frontier

    def execute_node(self, action_node: ActionNode) -> str:
        # Find corresponding definition node
        action_node.upstream_nodes()
        action_node.e

    async def cycle(self, graph: Graph):
        #action_nodes = graph.query_nodes_by_tag("action")
        frontier = self.get_frontier(graph)

        print("Frontier:", frontier)

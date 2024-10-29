from langur.actions import ActionNode, ActionDefinitionNode
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

    def fill_params(self, action_node: ActionNode, action_definition_node: ActionDefinitionNode):
        #TODO
        pass

    def build_context(self, action_node: ActionNode) -> list[str]:
        # Procedure: Get all upstream completed actions, append all outputs together
        upstream: list[ActionNode] = list(filter(lambda node: "action" in node.get_tags(), action_node.upstream_nodes()))
        context = []
        for node in upstream:
            context.append(node.output)
        #TODO

    def execute_node(self, action_node: ActionNode) -> str:
        # Find corresponding definition node
        action_definition_nodes = list(filter(lambda node: "action_definition" in node.get_tags(), action_node.upstream_nodes()))
        if len(action_definition_nodes) != 1:
            raise RuntimeError("Found none or multiple corresponding definitions for action node:", action_node)
        action_definition_node: ActionDefinitionNode = action_definition_nodes[0]

        # If missing params, need to dynamically fill
        self.fill_params(action_node, action_definition_node)

        # Build context
        context = self.build_context(action_node)

        action_definition_node.execute(
            params=action_node.params,
            context=context
        )

    async def cycle(self, graph: Graph):
        #action_nodes = graph.query_nodes_by_tag("action")
        frontier = self.get_frontier(graph)

        print("Frontier:", frontier)

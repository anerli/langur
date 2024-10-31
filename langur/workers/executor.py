import asyncio
from langur.actions import ActionNode
from langur.baml_client.type_builder import TypeBuilder
from langur.graph.graph import CognitionGraph
from langur.graph.node import Node
from langur.workers.worker import STATE_DONE, Worker
import langur.baml_client as baml


class ExecutorWorker(Worker):
    state: str = "WAITING"

    def get_frontier(self) -> set[ActionNode]:
        '''
        Get the "frontier", i.e. unexecuted action nodes with only executed depedencies.
        '''
        action_nodes = self.cg.query_nodes_by_type(ActionNode)

        #print("action nodes:", action_nodes)

        # Naive linear impl
        frontier = set()
        for node in action_nodes:
            valid = True
            if node.output is not None:
                # Already executed
                #print("already executed:", node)
                valid = False
            else:
                for upstream_node in node.upstream_nodes():
                    if "action" in upstream_node.get_tags() and upstream_node.output is None:
                        #print(f"un-executed upstream: {node.id}<-{upstream_node.id}")
                        # Upstream un-executed action
                        valid = False
                        break
            if valid:
                frontier.add(node)
        
        return frontier

    async def fill_params(self, action_node: ActionNode, context: str):
        empty_params = [k for k, v in action_node.inputs.items() if v is None]

        if len(empty_params) == 0:
            return

        tb = TypeBuilder()
        
        # for now all params assumed to be strings
        # TODO: use actual defined param types, and add param descriptions if specified in action def
        for param_name in empty_params:
            tb.FilledParams.add_property(param_name, tb.string())

        params = await baml.b.FillParams(
            context=context,
            action_desc=action_node.purpose,
            # TODO: actually use jinja features instead of this sillyness
            filled_inputs="\n".join([f"{k}={v}" for k, v in action_node.inputs.items() if v is not None]),
            needed_inputs="\n".join([f"{k}" for k, v in action_node.inputs.items() if v is None]),
            baml_options={
                "tb": tb,
                "client_registry": self.cg.get_client_registry()
            }
        )
        # Fill in node's params
        for k, v in params.model_dump().items():
            action_node.inputs[k] = v

    def build_context_rec(self, action_node: ActionNode) -> list[str]:
        # Procedure: Get all upstream completed actions, append all outputs together
        upstream: list[ActionNode] = list(filter(lambda node: "action" in node.get_tags(), action_node.upstream_nodes()))
        context = []
        for node in upstream:
            if node.output is None:
                # Shouldn't happen, but if it somehow did would want to catch it
                raise RuntimeError(f"Encountered incomplete action while building context: {node}")
            context.append(node.output)
        for node in upstream:
            #context.extend()
            context = [*self.build_context_rec(node), *context]
        return context

    def build_context(self, action_node: ActionNode) -> str:
        context = "\n\n".join(self.build_context_rec(action_node))

        # Potentially, extra could be in the rec procedure - if we wanted to grab the extra context for upstream nodes too
        extra = action_node.extra_context(
            conn=self.cg.query_worker_by_id(action_node.connector_id),
            context=context
        )

        if extra is not None:
            context += f"\n\n{extra}"

        return context

    async def execute_node(self, action_node: ActionNode) -> str:
        # Find corresponding definition node
        # action_definition_nodes = list(filter(lambda node: "action_definition" in node.get_tags(), action_node.upstream_nodes()))
        # if len(action_definition_nodes) != 1:
        #     raise RuntimeError("Found none or multiple corresponding definitions for action node:", action_node)
        # action_definition_node: ActionDefinitionNode = action_definition_nodes[0]

        # Build context
        context = self.build_context(action_node)

        # If missing params, need to dynamically fill
        await self.fill_params(action_node, context)

        #print("Context:", context)

        output = await action_node.execute(
            #params=action_node.params,
            conn=self.cg.query_worker_by_id(action_node.connector_id),
            context=context
        )
        action_node.output = output
        return output

    async def execute_frontier(self):
        #action_nodes = graph.query_nodes_by_tag("action")
        frontier = self.get_frontier()

        print("Frontier:", frontier)
        

        await asyncio.gather(*[self.execute_node(node) for node in frontier])

        is_done = len(self.get_frontier()) == 0
        #print("is done?", )
        if is_done:
            self.state = STATE_DONE
    
    async def cycle(self):
        # TODO super hacky, only works with exactly one executor and planner
        #if self.state == "WAITING" and len(self.cg.get_workers_with_state("WAITING")) == 1:
        if self.state == "WAITING" and self.cg.worker_count(worker_type="PlannerWorker", state=STATE_DONE) == self.cg.worker_count(worker_type="PlannerWorker"):
            await self.execute_frontier()

from langur.actions import ActionDefinitionNode, ActionNode
from langur.baml_client.type_builder import TypeBuilder
from langur.graph.graph import CognitionGraph
from langur.workers.worker import STATE_DONE, STATE_SETUP, Worker
import langur.baml_client as baml

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from .task import TaskNode

class PlannerWorker(Worker):
    task_node_id: str

    state: str = "WAITING"
    _event_prefix: ClassVar[str] = "planner"

    async def cycle(self):
        # a bit hacky idk
        # could in theory cause non-deterministic number of cycles this happens async with others?
        # May happen on cycle 1 or 2 dependending on whether other workers execute first - either way it works - but maybe this is a bit odd.
        if self.state == "WAITING" and self.cg.worker_count(state=STATE_SETUP) == 0:
            await self.plan_task()
            self.state = STATE_DONE

    async def plan_task(self):
        graph = self.cg
        action_def_nodes: list[ActionDefinitionNode] = graph.query_nodes_by_tag("action_definition")
    
        tb = TypeBuilder()
        action_input_types = []
        # Dynamically build action input types
        for action_def_node in action_def_nodes:
            action_def_name = action_def_node.id

            builder = tb.add_class(action_def_name)
            builder.add_property("type", tb.literal_string(action_def_name))
            
            params = action_def_node.params

            for param in params:
                # use field type from action def but make optional (any problems if double applied?)
                # TODO: hardcoded to str and no desc - add back when BAML supports dynamic types from JSON
                # property_builder = builder.add_property(param.param_key, param.field_type.optional())
                # if param.description:
                #     property_builder.description(param.description)
                builder.add_property(param, tb.string().optional())
            action_input_types.append(builder.type())

        tb.ActionNode.add_property("action_input", tb.union(action_input_types)).description("Provide inputs if known else null. Do not hallicinate values.")

        task_node: 'TaskNode' = graph.query_node_by_id(self.task_node_id)
        resp = await baml.b.PlanActions(
            goal=task_node.task,
            observables="\n".join([node.content() for node in graph.query_nodes_by_tag("observable")]),
            action_types="\n".join([f"- {node.id}: {node.description}" for node in action_def_nodes]),
            baml_options={
                "tb": tb,
                "client_registry": graph.get_client_registry()
            }
        )
        

        # Build action use nodes
        nodes = []
        for node_data in resp.nodes:
            #nodes.append(ActionUseNode(item.id, item.action_input))
            node = ActionNode(
                id=node_data.id,
                params=node_data.action_input,
                description=node_data.description
            )
            nodes.append(node)
            graph.add_node(
                node
            )
            graph.add_edge_by_ids(
                src_id=node_data.action_input["type"],
                dest_id=node.id,
                relation="defines"
            )
        
        for edge_data in resp.edges:
            graph.add_edge_by_ids(
                src_id=edge_data.from_id,
                dest_id=edge_data.to_id,
                relation="dependency"
            )
        
        # Connect leaves to task
        for node in nodes:
            if len(node.outgoing_edges()) == 0:
                graph.add_edge_by_ids(
                    src_id=node.id,
                    dest_id=self.task_node_id,
                    relation="achieves"
                )

    

        


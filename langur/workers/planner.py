from langur.actions import ActionNode
from langur.baml_client.types import ActionNode as BAMLActionNode
from langur.baml_client.type_builder import TypeBuilder
from langur.graph.graph import CognitionGraph
from langur.workers.worker import STATE_DONE, STATE_SETUP, Worker
import langur.baml_client as baml
from langur.util.registries import action_node_type_registry

from typing import TYPE_CHECKING, ClassVar, Type

from langur.connectors.workspace_connector import Connector

if TYPE_CHECKING:
    from .task import TaskNode

class PlannerWorker(Worker):
    task_node_id: str

    state: str = "WAITING"

    async def cycle(self):
        # a bit hacky idk
        # could in theory cause non-deterministic number of cycles this happens async with others?
        # May happen on cycle 1 or 2 dependending on whether other workers execute first - either way it works - but maybe this is a bit odd.
        if self.state == "WAITING" and self.cg.worker_count(state=STATE_SETUP) == 0:
            await self.plan_task()
            self.state = STATE_DONE

    def derive_connector(self, node_data: BAMLActionNode) -> Connector:
        '''
        Derive the connector that is associated with the given generated action node.
        TODO: Will eventually need a method for differentiating connectors which have the sames types of actions available
        For example:
        READ ./workspace1/foo/bar -> goes to Connector1
        READ ./workspace2/foo/baz -> goes to Connector2

        For now, multiple connectors of the same type are not allowed.
        '''
        connector_workers = self.cg.query_workers(Connector)
        #action_node_types: dict[str, Type[ActionNode]] = {}
        connector = None
        for worker in connector_workers:
            #action_node_types = set()
            for action_node_type in action_node_type_registry.get_action_node_types(worker.__class__.__name__):#worker.action_node_types:
                #action_node_types
                if node_data.action_input["type"] == action_node_type.action_type_name():
                    if connector:
                        # Found anothing matching connector (or more specifically matching action type in another connector), not supported yet
                        raise RuntimeError("Unable to derive connector for action (multiple connectors of the same type are not yet supported!)")
                    connector = worker
                    break
                #action_node_types[action_node_type.action_type_name()] = action_node_type
        return connector

    async def plan_task(self):
        #action_def_nodes: list[ActionDefinitionNode] = self.cg.query_nodes_by_tag("action_definition")
        connector_workers = self.cg.query_workers(Connector)
        action_node_types: dict[str, Type[ActionNode]] = {}
        for worker in connector_workers:
            for action_node_type in action_node_type_registry.get_action_node_types(worker.__class__.__name__):#worker.action_node_types:
                action_node_types[action_node_type.action_type_name()] = action_node_type
            #action_node_types.extend(worker.get_action_node_types())
    
        tb = TypeBuilder()
        action_input_schemas = []
        # Dynamically build action input types
        for action_type_name, action_node_type in action_node_types.items():
            #action_def_name = action_def_node.id
            #action_type_name = action_node_type.action_type_name()

            builder = tb.add_class(action_type_name)
            builder.add_property("type", tb.literal_string(action_type_name))
            
            # TODO: Actually use JSON schema values - for now just assuming strings
            params = action_node_type.input_schema.keys()

            for param in params:
                # use field type from action def but make optional (any problems if double applied?)
                # TODO: hardcoded to str and no desc - add back when BAML supports dynamic types from JSON
                # property_builder = builder.add_property(param.param_key, param.field_type.optional())
                # if param.description:
                #     property_builder.description(param.description)
                builder.add_property(param, tb.string().optional())
            action_input_schemas.append(builder.type())

        tb.ActionNode.add_property("action_input", tb.union(action_input_schemas)).description("Provide inputs if known else null. Do not hallicinate values.")

        task_node: 'TaskNode' = self.cg.query_node_by_id(self.task_node_id)
        resp = await baml.b.PlanActions(
            goal=task_node.task,
            observables="\n".join([node.observe() for node in self.cg.query_nodes_by_tag("observable")]),
            action_types="\n".join([f"- {action_type_name}: {action_node_type.definition}" for action_type_name, action_node_type in action_node_types.items()]),
            baml_options={
                "tb": tb,
                "client_registry": self.cg.get_client_registry()
            }
        )
        

        # Build action use nodes
        nodes = []
        for node_data in resp.nodes:
            print("action_node_types:", action_node_types)
            print("node_data:", node_data)
            action_node_type = action_node_types[node_data.action_input["type"]]
            #nodes.append(ActionUseNode(item.id, item.action_input))

            action_input_without_type = node_data.action_input.copy()
            del action_input_without_type["type"]

            node = action_node_type(
                id=node_data.id,
                inputs=action_input_without_type,
                purpose=node_data.description,
                connector_id=self.derive_connector(node_data).id
            )
            nodes.append(node)
            self.cg.add_node(
                node
            )
            # self.cg.add_edge_by_ids(
            #     src_id=node_data.action_input["type"],
            #     dest_id=node.id,
            #     relation="defines"
            # )
        
        for edge_data in resp.edges:
            self.cg.add_edge_by_ids(
                src_id=edge_data.from_id,
                dest_id=edge_data.to_id,
                relation="dependency"
            )
        
        # Connect leaves to task
        for node in nodes:
            if len(node.outgoing_edges()) == 0:
                self.cg.add_edge_by_ids(
                    src_id=node.id,
                    dest_id=self.task_node_id,
                    relation="achieves"
                )

    

        




# from typing import Any, ClassVar, Type
# from langur.actions import ActionContext, ActionNode
# from langur.connectors.connector_worker import ConnectorWorker
# import langur.baml_client as baml
# from langur.workers.worker import STATE_DONE

# class ThinkNode(ActionNode):#WorkspaceNode,
#     definition: ClassVar[str] = "Do purely cognitive processing."
#     input_schema: ClassVar[dict[str, Any]] = {}

#     async def execute(self, ctx: ActionContext) -> str:
#         # TODO: Use client registry
#         return await baml.b.Think(context=ctx.context, description=self.purpose, baml_options={"client_registry": ctx.cg.get_client_registry()})

# class CognitiveConnector(ConnectorWorker):
#     action_node_types: ClassVar[list[Type[ActionNode]]] = [ThinkNode]
#     state: str = STATE_DONE

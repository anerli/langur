

from typing import ClassVar, Type
from langur.actions import ActionNode
from langur.connectors.connector import ConnectorWorker
import langur.baml_client as baml
from langur.workers.worker import STATE_DONE

class ThinkNode(ActionNode):#WorkspaceNode,
    definition: ClassVar[str] = "Do purely cognitive processing."
    input_schema: ClassVar[list[str]] = []

    async def execute(self, conn: 'CognitiveConnector', context: str) -> str:
        # TODO: Use client registry
        return await baml.b.Think(context=context, description=self.purpose)#, baml_options={"client_registry": self.cg.get_client_registry()})

class CognitiveConnector(ConnectorWorker):
    action_node_types: ClassVar[list[Type[ActionNode]]] = [ThinkNode]
    state: str = STATE_DONE

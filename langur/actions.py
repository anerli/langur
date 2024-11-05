from abc import abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Optional



from langur.graph.graph import CognitionGraph
from langur.graph.node import Node
from baml_py.type_builder import FieldType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langur.connector import Connector

@dataclass
class ActionContext:
    cg: CognitionGraph
    conn: 'Connector'
    ctx: str
    purpose: str

class ActionNode(Node):
    definition: ClassVar[str]
    # TODO: input schema values are currently ignored, assumed to be strings
    #input_schema: ClassVar[dict[str, Any]]#TODO
    # Should maybe just be one FieldType to captured required properly?
    input_schema: ClassVar[dict[str, FieldType]]

    tags: ClassVar[list[str]] = ["action"]

    inputs: dict
    purpose: str

    # ID of corresponding connector worker - to use config from etc.
    connector_id: str

    # If action has been executed, it will have attached output
    # For now at least, this output from execution should always be a string
    output: Optional[str] = None

    @classmethod
    def action_type_name(cls):
        return cls.__name__

    def extra_context(self, ctx: ActionContext) -> str | None:
        '''
        Implement if you want the input filling procedure to include more information before populating.
        '''
        return None

    @abstractmethod
    async def execute(self, ctx: ActionContext) -> str:
        pass

from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from typing import Any, ClassVar, Generic, Optional, Set, TypeVar, Union

from pydantic import Field


from langur.graph.edge import Edge
from langur.graph.graph import CognitionGraph
from langur.graph.node import Node
from baml_py.type_builder import FieldType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langur.connectors.connector import Connector


# class ActionParameter:
#     def __init__(self, param_key: str, field_type: FieldType, description: str | None = None):
#         self.param_key = param_key
#         self.field_type = field_type
#         self.description = description
    
#     def __str__(self):
#         if self.description:
#             return f"{self.param_key}: {self.description}"
#         else:
#             return f"{self.param_key}"

# TODO: Bump required python to 3.12 to use default='ConnectorWorker'
# C = TypeVar('C', bound='ConnectorWorker')

# @dataclass
# class ActionContext(Generic[C]):
#     cg: CognitionGraph
#     conn: C#Union[C, 'ConnectorWorker']#C
#     ctx: str

@dataclass
class ActionContext:
    cg: CognitionGraph
    conn: 'Connector'
    ctx: str

class ActionNode(Node):
    definition: ClassVar[str]
    # TODO: input schema values are currently ignored, assumed to be strings
    input_schema: ClassVar[dict[str, Any]]

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
    
    # def __init__(self, id: str, params: dict):#, thoughts: str):
    #     '''params: empty, partial, or full input dict'''
    #     super().__init__(id=id, params=params)
    #     #self.params = params
    #     #self.thoughts = thoughts
    
    # def content(self):
    #     formatted_inputs = json.dumps(self.params)
    #     return f"Action Use ID: {self.id}\nAction Inputs:\n{formatted_inputs}"





# class ActionDefinitionNode(Node, ABC):
#     '''
#     description: natural language description of exactly what this action does
#     schema: JSON schema defining input for this action
#     '''
#     tags: ClassVar[list[str]] = ["action_definition"]
#     #edges: Set['Edge'] = Field(default_factory=set, exclude=True)

#     # general connector worker
#     #worker: Worker

#     description: str
#     #params: list[ActionParameter] = Field(exclude=True)
#     # TODO: tmp, assume all strings and just have names - until BAML supports dynamic types from JSON schema
#     params: list[str]

#     #context: str
    
    
#     def content(self) -> str:
#         #formatted_schema = json.dumps(self.schema)
#         params = ", ".join(str(p) for p in self.params)
#         return f"Action ID: {self.id}\nAction Description: {self.description}\nAction Parameters: {params}"#\nAction Input Schema:\n{formatted_schema}

#     @abstractmethod
#     async def execute(self, params: dict[str, str], context: str): ...
#     #def execute(self, *args, **kwargs) -> str: ...
    

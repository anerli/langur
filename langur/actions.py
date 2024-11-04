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
    from langur.connector import Connector


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
    
    # def __init__(self, id: str, params: dict):#, thoughts: str):
    #     '''params: empty, partial, or full input dict'''
    #     super().__init__(id=id, params=params)
    #     #self.params = params
    #     #self.thoughts = thoughts
    
    # def content(self):
    #     formatted_inputs = json.dumps(self.params)
    #     return f"Action Use ID: {self.id}\nAction Inputs:\n{formatted_inputs}"


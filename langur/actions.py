from abc import ABC, abstractmethod
import json
from typing import ClassVar, Optional, Set

from pydantic import Field

from langur.graph.edge import Edge
from langur.graph.node import Node
from baml_py.type_builder import FieldType


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


class ActionNode(Node):
    definition: ClassVar[str]
    input_schema: ClassVar[list[str]]

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

    @abstractmethod
    async def execute(self, conn, context: str) -> str:
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
    

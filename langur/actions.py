import json
from typing import ClassVar

from langur.graph.node import Node
from baml_py.type_builder import FieldType


class ActionParameter:
    def __init__(self, param_key: str, field_type: FieldType, description: str | None = None):
        self.param_key = param_key
        self.field_type = field_type
        self.description = description
    
    def __str__(self):
        if self.description:
            return f"{self.param_key}: {self.description}"
        else:
            return f"{self.param_key}"


class ActionUseNode(Node):
    tags: ClassVar[list[str]] = ["action"]

    params: dict
    
    def __init__(self, id: str, params: dict):#, thoughts: str):
        '''params: empty, partial, or full input dict'''
        super().__init__(id=id, params=params)
        #self.params = params
        #self.thoughts = thoughts
    
    def content(self):
        formatted_inputs = json.dumps(self.params)
        return f"Action Use ID: {self.id}\nAction Inputs:\n{formatted_inputs}"

    # def get_visual_attributes(self):
    #     formatted_inputs = json.dumps(self.params)
    #     return {
    #         **super().get_visual_attributes(),
    #         "params": formatted_inputs,
    #         #"thoughts": self.thoughts
    #     }

    def to_json(self) -> dict:
        return {
            **super().to_json(),
            "params": self.params
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'ActionUseNode':
        return ActionUseNode(data["id"], data["params"])

class ActionDefinitionNode(Node):
    tags: ClassVar[list[str]] = ["action_definition"]

    description: str
    # TODO: deal w params, obviously not serializable
    params: list[ActionParameter]
    
    

    def __init__(self, action_id: str, description: str, params: list[ActionParameter]):#schema: dict[str, FieldType]):
        '''
        description: natural language description of exactly what this action does
        schema: JSON schema defining input for this action
        '''
        super().__init__(id=action_id, description=description, params=params)
        self.description = description
        self.params = params
    
    def content(self) -> str:
        #formatted_schema = json.dumps(self.schema)
        params = ", ".join(str(p) for p in self.params)
        return f"Action ID: {self.id}\nAction Description: {self.description}\nAction Parameters: {params}"#\nAction Input Schema:\n{formatted_schema}

    # def get_visual_attributes(self):
    #     #formatted_schema = json.dumps(self.schema)
    #     # Ideally we would show param types as well, but no easy way to get str representation of FieldType
    #     params = ", ".join(str(p) for p in self.params)
    #     return {
    #         **super().get_visual_attributes(),
    #         "description": self.description,
    #         "params": params
    #         #"schema": formatted_schema
    #     }
    
    def to_json(self) -> dict:
        return {
            **super().to_json(),
            "description": self.description,
            "params": self.params
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'ActionUseNode':
        return ActionUseNode(data["id"], data["description"], data["params"])
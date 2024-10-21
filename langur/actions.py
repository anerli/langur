import json

from langur.graph import Node
from baml_py.type_builder import FieldType

class ActionUseNode(Node):
    tags = ["action"]
    
    def __init__(self, id: str, params: dict):#, thoughts: str):
        '''params: empty, partial, or full input dict'''
        super().__init__(id)
        self.params = params
        #self.thoughts = thoughts
    
    def content(self):
        formatted_inputs = json.dumps(self.params)
        return f"Action Use ID: {self.id}\nAction Inputs:\n{formatted_inputs}"

    def get_visual_attributes(self):
        formatted_inputs = json.dumps(self.params)
        return {
            **super().get_visual_attributes(),
            "params": formatted_inputs,
            #"thoughts": self.thoughts
        }

class ActionDefinitionNode(Node):
    tags = ["action_definition"]

    def __init__(self, action_id: str, description: str, schema: dict[str, FieldType]):
        '''
        description: natural language description of exactly what this action does
        schema: JSON schema defining input for this action
        '''
        super().__init__(action_id)
        self.description = description
        self.schema = schema
    
    def content(self) -> str:
        #formatted_schema = json.dumps(self.schema)
        params = ", ".join(self.schema.keys())
        return f"Action ID: {self.id}\nAction Description: {self.description}\nAction Parameters: {params}"#\nAction Input Schema:\n{formatted_schema}

    def get_visual_attributes(self):
        #formatted_schema = json.dumps(self.schema)
        # Ideally we would show param types as well, but no easy way to get str representation of FieldType
        params = ", ".join(self.schema.keys())
        return {
            **super().get_visual_attributes(),
            "description": self.description,
            "params": params
            #"schema": formatted_schema
        }
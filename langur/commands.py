from abc import abstractmethod
from typing import TYPE_CHECKING, List, Set, Type
from langur.util.general import UniqueClassAttribute
from openai import OpenAI

client = OpenAI()

if TYPE_CHECKING:
    from synthcog.world import World
    from .connectors.connector import Connector

DEPENDENT_INPUTS_SUFFIX = "_dependencies"

class Command():
    _connector_types = UniqueClassAttribute(set)

    input_schema: dict
    description: str

    def __init__(self, inputs: dict):
        '''
        inputs should match input_schema
        '''
        # TODO: prob validate input either via jsonschema or using pydantic and make input schema pydantic model
        self.inputs = inputs
    
    @classmethod
    def get_connector_types(cls) -> List[Type['Connector']]:
        return list(cls._connector_types)
    
    @classmethod
    def get_construction_context(cls, partial_inputs: dict, world: 'World') -> str:
        '''
        Should return context helpful for filling in any missing inputs to the command ("constructing" the command)
        in cases where inputs are not immediately filled during the task decomposition.

        Optional. Necessity depends on the command functionality. For example, an overwriting operation should be aware of the previous content.
        '''
        return ""

    # TODO: re-add world/memory maybe to this iface
    @abstractmethod
    def execute(self, world: 'World') -> str | None:
        '''Execute this command and possibly return relevant output'''
        ...

    
    @classmethod
    def get_keyword(cls):
        return cls.__name__

    @classmethod
    def get_schema(cls):
        '''
        Builds the full schema for the inputs for this command
        '''
        keyword = cls.get_keyword()
        return {
            keyword: cls.input_schema
        }

# TODO: figure out how to get context for when command executions themselves call LLMs
class Think(Command):
    #input_schema = {"direction": {"type": "string"}}
    #description = "Do cognitive work given some thought direction"
    input_schema = {"thoughts": {"type": "string"}}
    description = "Do purely cognitive work. Cannot interact with real-world systems on its own."
    

    #def resolve(self,  world: RealWorld, memory: Memory):
    # TODO: re-add world/memory maybe to this iface
    def execute(self, world: 'World'):
        return self.inputs["thoughts"]
        # client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages={"role": "user", "content": }
        # )

class Assume(Command):
    input_schema = {"assumption": {"type": "string"}}
    description = "Make an assumption about the task. Declare assumptions first."

    def execute(self, world: 'World'):
        pass

# class Status(Command):
#     input_schema = {"status": {
#         "type": "string",
#         "enum": ["COMPLETE", "INCOMPLETE"]
#     }}
#     description = "Declare whether the task will be completed or not after the commands are executed. Always include this command. Put this command last. Consider that it is possible that insufficient commands are provided to complete the task, in which case it may be INCOMPLETE."

# class Deadend(Command):
#     input_schema = {}
#     description = "Use this command when the task cannot be completed with the available commands and resources."

class Criticize(Command):
    input_schema = {
        "criticism": {"type": "string"},
        "status": {"type": "string", "enum": ["COMPLETE", "INCOMPLETE"]}
    }
    description = "Always use this command, and put it last. Question and critizise the effectiveness of the program. Note specifically whether the task will actually be complete or not after running the commands."

class Simulate(Command):
    input_schema = {
        "simulation_description": {"type": "string"},
        "status": {"type": "string", "enum": ["COMPLETE", "INCOMPLETE"]}
    }
    description = "Always use this command, and put it last. Mentally simulate the outcome of the program overall, carefully considering what each command is precisely capable of. Declare at the end whether the task will actually be COMPLETE or if it will remain INCOMPLETE after running the commands."

class Subtask(Command):
    input_schema = {"task_description": {"type": "string"}}
    description = "Designate a subtask to be completed."


class CodeRun(Command):
    input_schema = {"file_path": {"type": "string"}}
    description = "Run a code file and observe the output."

BASE_DIALECT = [Think, Subtask] # Assume

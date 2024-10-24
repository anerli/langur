from abc import ABC

import langur.baml_client as baml
from pydantic import BaseModel, Field

from typing import TYPE_CHECKING, ClassVar, Dict, Type

if TYPE_CHECKING:
    from langur.graph.graph import Graph

class Worker(BaseModel, ABC):
    '''Meta-cognitive Worker'''

    _subclasses: ClassVar[Dict[str, Type['Worker']]] = {}
    #_type: str = Field(default_factory=lambda self: self.__class__.__name__, frozen=True)

    # def __init__(self, **kwargs):
    #     # idk man, no workers use anything like this yet but eventually they will be configurable and tryna figure out how the serde works with that
    #     self.settings = kwargs

    def __init_subclass__(cls, **kwargs):
        """Register subclasses automatically when they're defined"""
        super().__init_subclass__(**kwargs)
        Worker._subclasses[cls.__name__] = cls

    def get_setup_order(self) -> int:
        '''Lower order = earlier in setup'''
        # Very simplistic system, likely will need to be redesigned
        return 0
    
    async def setup(self, graph: 'Graph'):
        '''Runs once when workers are added to nexus'''
        pass

    async def cycle(self, graph: 'Graph'):
        '''
        Do one cycle with this worker; the implementation will vary widely depending on the worker's purpose.
        Each cycle should be finite, though potentially cycles could be executed indefinitely.
        '''
        pass
    
    # def get_settings(self) -> dict:
    #     return {}

    # for now, enforce stateless - can impl later
    # def get_state(self) -> dict:
    #     return {}

    # def to_json(self) -> dict:
    #     return {
    #         "worker_type": self.__class__.__name__,
    #         "settings": self.get_settings(),
    #         #"state": self.get_state()
    #     }

    # @classmethod
    # def from_json(cls, data: dict) -> 'Worker':
    #     worker_type = data["worker_type"]
        
    #     if worker_type not in cls._subclasses:
    #         raise KeyError(f"Unknown worker type: {worker_type}")
            
    #     # Get the appropriate subclass
    #     worker_class = cls._subclasses[worker_type]

    #     # Call subclass from_json if implemented
    #     # Actually don't have the subclass implement it?
    #     # if hasattr(worker_class, 'from_json'):
    #     #     return worker_class.from_json(data)

    #     # Default implementation
    #     return worker_class(**data["settings"])

    # Using different terminology from Pydantic serde functions to avoid confusion since these are a bit different

    # model_dump , **kwargs
    def to_json(self) -> dict:
        data = super().model_dump(mode="json")#, **kwargs
        #data["worker_type"] = self.__class__.__name__
        # Insert subclass name so can reconstruct correct class later
        data = {
            "worker_type": self.__class__.__name__,
            **data
        }
        return data

    # model_validate
    @classmethod
    def from_json(cls, data: dict) -> 'Worker':
        worker_type = data["worker_type"]
        worker_class = Worker._subclasses[worker_type]
        
        # Instantiate the appropriate subclass
        data_no_worker_type = data.copy()
        del data_no_worker_type["worker_type"]
        return worker_class.model_validate(data_no_worker_type)
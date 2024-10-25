from abc import ABC

import langur.baml_client as baml
from pydantic import BaseModel, Field

from typing import TYPE_CHECKING, ClassVar, Dict, Type

if TYPE_CHECKING:
    from langur.graph.graph import Graph

# Kind of special states
# default starting state for most workers
STATE_SETUP = "SETUP"
# end state for most workers
STATE_DONE = "DONE"

class Worker(BaseModel, ABC):
    '''
    Meta-cognitive Worker
    
    Be careful when overriding __init__, kwargs must include all custom properties in order to be automatically deserialized properly.
    '''
    
    # Workers are often state machines, this state is serialized and retained
    state: str = STATE_SETUP

    _subclasses: ClassVar[Dict[str, Type['Worker']]] = {}

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
    
    # Using different terminology from Pydantic serde functions to avoid confusion since these are a bit different

    def to_json(self) -> dict:
        data = super().model_dump(mode="json")
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
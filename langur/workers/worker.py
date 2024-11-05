from abc import ABC

from cuid2 import Cuid
from pydantic import BaseModel, ConfigDict, Field

from typing import TYPE_CHECKING, ClassVar, Dict, Type

if TYPE_CHECKING:
    from langur.graph.graph import CognitionGraph

# Kind of special states
# default starting state for most workers
STATE_SETUP = "SETUP"
# end state for most workers
STATE_DONE = "DONE"

CUID = Cuid(length=10)

class Worker(BaseModel, ABC):
    '''
    Meta-cognitive Worker
    
    Be careful when overriding __init__, kwargs must include all custom properties in order to be automatically deserialized properly.
    '''
    
    
    id: str = Field(default_factory=CUID.generate)
    # Workers are often state machines, this state is serialized and retained
    state: str = Field(default=STATE_SETUP)

    _subclasses: ClassVar[Dict[str, Type['Worker']]] = {}

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Bypass pydantic sillyness for the graph ref
    @property
    def cg(self) -> 'CognitionGraph':
        if not hasattr(self, "_cognition_graph") or self._cognition_graph is None:
            raise RuntimeError("Graph reference not set for Worker:", self)
        return self._cognition_graph
        
    @cg.setter
    def cg(self, value):
        self._cognition_graph = value

    def __init_subclass__(cls, **kwargs):
        """Register subclasses automatically when they're defined"""
        #print("__init_subclass__")
        super().__init_subclass__(**kwargs)
        Worker._subclasses[cls.__name__] = cls
    
    def __hash__(self):
        return hash((self.__class__.__name__, id(self)))

    async def cycle(self) -> str | None:
        '''
        Do one cycle with this worker; the implementation will vary widely depending on the worker's purpose.
        Each cycle should be finite, though potentially cycles could be executed indefinitely.

        Optionally returns a string representing a signal, which can be used from high level - this will probably change.
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

    def log(self, *args, **kwargs):
        print(f"[{self.__class__.__name__}::{self.id}] ", end="")
        print(*args, **kwargs)
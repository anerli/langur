from abc import ABC

import langur.baml_client as baml
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from pydantic.fields import FieldInfo
from pydantic.json_schema import JsonSchemaValue

from typing import TYPE_CHECKING, ClassVar, Dict, ForwardRef, Optional, Type, Any

if TYPE_CHECKING:
    from langur.graph.graph import CognitionGraph

# Kind of special states
# default starting state for most workers
STATE_SETUP = "SETUP"
# end state for most workers
STATE_DONE = "DONE"

# GraphRef = ForwardRef('Graph')

class GraphField(FieldInfo):
    def __init__(self):
        super().__init__(default=None)

    def _annotation_ext(self) -> Any:
        return Any
        
    def json_schema(self) -> JsonSchemaValue:
        return {"type": "object"}


class Worker(BaseModel, ABC):
    '''
    Meta-cognitive Worker
    
    Be careful when overriding __init__, kwargs must include all custom properties in order to be automatically deserialized properly.
    '''
    
    # Workers are often state machines, this state is serialized and retained
    # DO NOT SET DIRECTLY, USE set_state
    #state: str = Field(default=STATE_SETUP)

    #_state: str = PrivateAttr(default=STATE_SETUP)  # Private storage
    state: str = Field(default=STATE_SETUP)  # Public field

    # def __init__(self, **data):
    #     super().__init__(**data)
    #     self._state = self.state  # Sync initial value

    # @property
    # def state(self) -> str:
    #     return self._state
        
    # @state.setter
    # def state(self, value: str) -> None:
    #     print('set state:', value)
    #     self._state = value

    # Ref needs to be set after init hence optional
    #graph: Optional['Graph'] = Field(default=None, exclude=True, annotation_extractor=GraphField)

    #_state: str = PrivateAttr(default=STATE_SETUP, alias='state')

    # Should be set by Worker subclasses
    #_event_prefix: ClassVar[str]
    _subclasses: ClassVar[Dict[str, Type['Worker']]] = {}

    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # def __setattr__(self, name, value):
    #     if name == 'state':
    #         self._on_state_change(value)
    #     object.__setattr__(name, value)
    
    # def _on_state_change(self, value):
    #     print('new state:', value)

    # @property
    # def state(self) -> str:
    #     return self._state
        
    # @state.setter
    # def state(self, value: str) -> None:
    #     print('set state:', value)
    #     self._state = value
    
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
        super().__init_subclass__(**kwargs)
        Worker._subclasses[cls.__name__] = cls

    # def emit(self, event: str):
    #     self.cg.emit(f"{self._event_prefix}.{event}")

    #def set_state()

    # def get_setup_order(self) -> int:
    #     '''Lower order = earlier in setup'''
    #     # Very simplistic system, likely will need to be redesigned
    #     return 0
    
    # async def setup(self, graph: 'Graph'):
    #     '''Runs once when workers are added to nexus'''
    #     pass

    async def cycle(self):
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

# from langur.graph.graph import Graph
# Worker.model_rebuild()
# Worker.update_forward_refs(Graph=ForwardRef('Graph'))
# Worker.model_rebuild()

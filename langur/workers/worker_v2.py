from abc import abstractmethod
from typing import ClassVar, Dict, Generic, Type, Self, TypeVar
from cuid2 import Cuid
from pydantic import BaseModel, Field

from langur.graph.graph import CognitionGraph
from langur.graph.node import Node

CUID = Cuid(length=10)


class AutoSerde(BaseModel):
    _subclasses: ClassVar[Dict[str, Type[Self]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._subclasses[cls.__name__] = cls
    
    def to_json(self) -> dict:
        return {
            "type": self.__class__.__name__,
            **super().model_dump(mode="json")
        }

    @classmethod
    def from_json(cls, data: dict) -> Self:
        data = data.copy()
        if data["type"] not in cls._subclasses:
            raise KeyError(f"Unable to deserialize data, unknown class `{data['type']}`")
        typ = cls._subclasses[data["type"]]
        del data["type"]
        return typ(**data)

class CognitiveWorker(BaseModel):
    _subclasses: ClassVar[Dict[str, Type['CognitiveWorker']]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        CognitiveWorker._subclasses[cls.__name__] = cls

    def __init__(self, cg: CognitionGraph, config: TConfig, state: str = "SETUP"):
        self.cg = cg
        self.config = config
        self.state = state
    
    @abstractmethod
    async def cycle(self): ...

    def to_json(self) -> dict:
        data = {
            "config": self.config.model_dump(mode="json"),
            "state": self.state
        }#super().model_dump(mode="json")
        # Insert subclass name so can reconstruct correct class later
        data = {
            "worker_type": self.__class__.__name__,
            **data
        }
        return data

    # model_validate
    @classmethod
    def from_json(cls, data: dict) -> 'CognitiveWorker':
        worker_type = data["worker_type"]
        worker_class = CognitiveWorker._subclasses[worker_type]
        
        # Instantiate the appropriate subclass
        data_no_worker_type = data.copy()
        del data_no_worker_type["worker_type"]
        #return worker_class.model_validate(data_no_worker_type)

        # This means every subtype of worker has to have an init that looks like this..
        return worker_class(
            config = WorkerConfig.from_json(data["config"]),
            state = data["state"]
        )



# Example non-connector impl

class TaskNode(Node):
    tags: ClassVar[list[str]] = ["task"]
    task: str
    
    def content(self):
        return f"{self.task} {self.action_types}"

class TaskWorkerConfig(WorkerConfig):
    task: str
    task_node_id: str

class TaskWorker(CognitiveWorker[TaskWorkerConfig]):
    async def cycle(self):
        #self.config.task
        if self.state == "SETUP":
            task_node = TaskNode(id=self.node_id, task=self.task)
            self.cg.add_node(task_node)
            self.state = "DONE"


# Example connector impl - this is the one I need to be super easy

class Connector(CognitiveWorker):
    def observe(self) -> str | None:
        return None

    def action(self, fn):
        pass

    async def cycle(self):
        # add observable node that calls self.observe somehow
        self.state = "DONE"



class WorkspaceConfig:
    workspace_path: str

class Workspace(Connector[WorkspaceConfig]):
    def __init__(self, workspace_path: str):
        super().__init__()



# Goal: 
Workspace("./workspace")
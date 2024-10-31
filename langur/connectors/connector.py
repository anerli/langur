'''
General connector cognitive worker - binds real-world connectors to the Langur cognitive system.
'''

from typing import ClassVar, Type
from langur.actions import ActionNode
from langur.workers.worker import Worker


class ConnectorWorker(Worker):
    action_node_types: ClassVar[list[Type[ActionNode]]]
    # @abstractmethod
    # def get_action_node_types(self) -> list[ActionNode]: ...
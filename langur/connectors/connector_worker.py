'''
General connector cognitive worker - binds real-world connectors to the Langur cognitive system.
'''

from abc import ABC
from typing import ClassVar, Type
from langur.actions import ActionNode
from langur.workers.worker import STATE_DONE, Worker


class ConnectorWorker(Worker, ABC):
    '''
    Generic Connector. Can subclass to implement own
    '''
    action_node_types: ClassVar[list[Type[ActionNode]]]

    async def cycle(self):
        self.state = STATE_DONE

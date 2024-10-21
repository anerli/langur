from abc import ABC

import langur.baml_client as baml

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langur.graph import Graph

class Worker(ABC):
    '''Meta-cognitive Worker'''

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

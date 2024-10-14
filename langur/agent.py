

import asyncio
from langur.connectors.connector import Connector
from langur.worker import DependencyDecomposer, IntermediateProductBuilder, Worker
from langur.world import World
from langur.graph import Graph

class Langur:
    def __init__(self, goal: str):
        # TODO: eventually make so one agent can do various goals thus re-using brain state pathways etc cleverly
        self.world = World()
        self.goal = goal
        self.graph = Graph(goal)
    
    def use(self, *connectors: Connector):
        for connector in connectors:
            self.world.register_connector(connector)
        return self

    async def act(self, workers: list[Worker], cycles=1):
        #workers: list[Worker] = [DependencyDecomposer(), IntermediateProductBuilder(), IntermediateProductBuilder()]

        # Call setup for each worker
        jobs = []
        for worker in workers:
            jobs.append(worker.setup(self.graph))
        await asyncio.gather(*jobs)

        for _ in range(cycles):
            jobs = []
            for worker in workers:
                jobs.append(worker.cycle(self.graph))
            # naive async implementation, don't need to necessarily block gather here
            await asyncio.gather(*jobs)

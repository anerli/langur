

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
        self.workers = []
    
    def use(self, *connectors: Connector):
        for connector in connectors:
            self.world.register_connector(connector)
        return self

    async def add_workers(self, *workers: Worker):
        workers_by_setup_order = {}
        for worker in workers:
            setup_order = worker.get_setup_order()
            if setup_order not in workers_by_setup_order:
                workers_by_setup_order[setup_order] = []
            workers_by_setup_order[setup_order].append(worker)
        
        for setup_order, worker_group in workers_by_setup_order.items():
            # Call setup for each worker
            jobs = []
            for worker in worker_group:
                jobs.append(worker.setup(self.graph))
            await asyncio.gather(*jobs)

        # Late setup, TODO: proper priority system
        # jobs = []
        # for worker in workers:
        #     jobs.append(worker.late_setup(self.graph))
        # await asyncio.gather(*jobs)

        self.workers.append(workers)

    async def act(self, cycles=1):
        #workers: list[Worker] = [DependencyDecomposer(), IntermediateProductBuilder(), IntermediateProductBuilder()]

        for _ in range(cycles):
            jobs = []
            for worker in self.workers:
                jobs.append(worker.cycle(self.graph))
            # naive async implementation, don't need to necessarily block gather here
            await asyncio.gather(*jobs)

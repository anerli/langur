

import asyncio
import json
import os
import pickle
from typing import Literal
from baml_py import ClientRegistry
from langur.connectors.connector import Connector
from langur.workers.worker import Worker
from langur.world import World
from langur.graph.graph import Graph

class Langur:
    def __init__(self, goal: str, llm: Literal['Default', 'Fast', 'Smart'] = 'Default', graph: Graph = None):
        # TODO jank ctor, should have a clear one (high lvl) and ugly one separate - maybe agent builder or something idk
        # TODO: eventually make so one agent can do various goals thus re-using brain state pathways etc cleverly
        self.cr = ClientRegistry()
        # self.cr.add_llm_client(name='mini', provider='openai', options={
        #     "model": "gpt-4o-mini",
        #     "temperature": 0.0,
        #     "api_key": os.environ.get('OPENAI_API_KEY')
        # })
        # self.cr.add_llm_client(name='sonnet', provider='anthropic', options={
        #     "model": "gpt-4o-mini",
        #     "temperature": 0.0,
        #     "api_key": os.environ.get('OPENAI_API_KEY')
        # })

        # idk jank
        self.llm = llm
        self.cr.set_primary(llm)
        
        self.world = World()
        #self.goal = goal
        self.graph = graph if graph else Graph(goal, self.cr)
        self.workers = []

        
    
    def use(self, *connectors: Connector):
        for connector in connectors:
            self.world.register_connector(connector)
        return self

    async def add_workers(self, *workers: Worker):
        # setup param is maybe hacky
        #if setup:
        workers_by_setup_order = {}
        for worker in workers:
            setup_order = worker.get_setup_order()
            if setup_order not in workers_by_setup_order:
                workers_by_setup_order[setup_order] = []
            workers_by_setup_order[setup_order].append(worker)
        
        ordered_worker_groups = []
        sorted_setup_orders = sorted(workers_by_setup_order.keys())
        for setup_order in sorted_setup_orders:
            ordered_worker_groups.append(workers_by_setup_order[setup_order])
        
        for worker_group in ordered_worker_groups:
            # Call setup for each worker
            jobs = []
            for worker in worker_group:
                jobs.append(worker.setup(self.graph))
            await asyncio.gather(*jobs)

        #self.workers.extend(workers)
    def add_workers_nosetup(self, *workers: Worker):
        # JANK
        self.workers.extend(workers)

    async def act(self, cycles=1):
        #workers: list[Worker] = [DependencyDecomposer(), IntermediateProductBuilder(), IntermediateProductBuilder()]

        for _ in range(cycles):
            jobs = []
            for worker in self.workers:
                jobs.append(worker.cycle(self.graph))
            # naive async implementation, don't need to necessarily block gather here
            await asyncio.gather(*jobs)
    
    def to_json(self) -> dict:
        return {
            "llm": self.llm,
            "workers": [worker.to_json() for worker in self.workers],
            "graph": self.graph.to_json()
        }

    @classmethod
    def from_json(cls, data: dict) -> 'Langur':
        # problem - worker setups should not retrigger
        # return Langur(

        # )
        workers = [Worker.from_json(worker_data) for worker_data in data["workers"]]
        graph = Graph.from_json(data["graph"])
        # jank, goal should be a worker anyway
        goal = graph.query_node_by_id("final_goal").content
        agent = Langur(
            goal=goal,
            llm=data["llm"],
            graph=graph
        )
        #agent.add_workers(workers, setup=False)
        agent.add_workers_nosetup(workers)
        return agent


    def save(self, path: str="./agent.json"):
        with open(path, "w") as f:
            json.dump(self.to_json(), f)
            #pickle.dump(self, f)

    @classmethod
    def load(cls, path: str="./agent.json") -> 'Langur':
        with open(path, "r") as f:
            #agent = pickle.load(f)
            agent = cls.from_json(json.load(f))
        return agent
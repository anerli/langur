

import asyncio
import json
import os
import pickle
from typing import Any, Dict, Literal, Optional
from baml_py import ClientRegistry
from pydantic import BaseModel
from langur.connectors.connector import Connector
from langur.llm import LLMConfig
from langur.workers.worker import STATE_DONE, Worker
#from langur.world import World
from langur.graph.graph import Graph



class Agent:
    '''
    Lower level agent representation.
    Use Langur instead for high level usage.
    '''
    def __init__(self, workers: list[Worker], llm_config: LLMConfig = None, graph: Graph = None):
        # TODO jank ctor, should have a clear one (high lvl) and ugly one separate - maybe agent builder or something idk
        # TODO: eventually make so one agent can do various goals thus re-using brain state pathways etc cleverly
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

        self.llm_config = llm_config if llm_config else LLMConfig(
            provider="anthropic",
            options={
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.0
            }
        )
        
        #self.world = World()
        #self.goal = goal
        self.graph = graph if graph else Graph(workers=workers, llm_config=self.llm_config)
        self.workers = workers

        
    
    def use(self, *connectors: Connector):
        for connector in connectors:
            self.world.register_connector(connector)
        return self

    # async def add_workers(self, *workers: Worker):
    #     # setup param is maybe hacky
    #     #if setup:
    #     workers_by_setup_order = {}
    #     for worker in workers:
    #         setup_order = worker.get_setup_order()
    #         if setup_order not in workers_by_setup_order:
    #             workers_by_setup_order[setup_order] = []
    #         workers_by_setup_order[setup_order].append(worker)
        
    #     ordered_worker_groups = []
    #     sorted_setup_orders = sorted(workers_by_setup_order.keys())
    #     for setup_order in sorted_setup_orders:
    #         ordered_worker_groups.append(workers_by_setup_order[setup_order])
        
    #     for worker_group in ordered_worker_groups:
    #         # Call setup for each worker
    #         jobs = []
    #         for worker in worker_group:
    #             jobs.append(worker.setup(self.graph))
    #         await asyncio.gather(*jobs)

    #     self.workers.extend(workers)
    
    # def add_workers_nosetup(self, *workers: Worker):
    #     # JANK
    #     self.workers.extend(workers)

    async def run_until_done(self):
        
        # could be helpful info to load/save cycle count instead of resetting if we loaded a prev agent, idk
        cycle_count = 0
        while not self.graph.are_workers_done():
            # a lil jank calling the graph thing here
            # would be cool to live update num done workers mid-cycle based on state changes - if workers were to use some hook to update state
            print(f"[Cycle {cycle_count+1}]: {len(self.graph.get_workers_with_state(STATE_DONE))}/{len(self.workers)} workers done")
            await self.cycle()
            cycle_count += 1
        print("Agent done!")

    async def cycle(self):#, cycles=1):
        #workers: list[Worker] = [DependencyDecomposer(), IntermediateProductBuilder(), IntermediateProductBuilder()]
        #for _ in range(cycles):
        jobs = []
        for worker in self.workers:
            jobs.append(worker.cycle(self.graph))
        # naive async implementation, don't need to necessarily block gather here
        await asyncio.gather(*jobs)
    
    def to_json(self) -> dict:
        return {
            "llm": self.llm_config.model_dump(mode="json"),
            "workers": [worker.to_json() for worker in self.workers],
            "graph": self.graph.to_json()
        }

    @classmethod
    def from_json(cls, data: dict) -> 'Agent':
        # problem - worker setups should not retrigger
        # return Langur(

        # )
        workers = [Worker.from_json(worker_data) for worker_data in data["workers"]]
        llm_config = LLMConfig.model_validate(data["llm"])
        graph = Graph.from_json(
            data=data["graph"],
            workers=workers,
            llm_config=llm_config
        )
        agent = Agent(
            workers=workers,
            #goal=goal,
            llm_config=llm_config,#data["llm"],
            graph=graph
        )
        return agent


    def save(self, path: str="./agent.json"):
        with open(path, "w") as f:
            json.dump(self.to_json(), f, indent=2)
            #pickle.dump(self, f)

    @classmethod
    def load(cls, path: str="./agent.json") -> 'Agent':
        with open(path, "r") as f:
            #agent = pickle.load(f)
            agent = cls.from_json(json.load(f))
        return agent
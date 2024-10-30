

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
from langur.graph.graph import CognitionGraph

# TODO: Combine with CognitionGraph

class Agent:
    '''
    Lower level agent representation.
    Use Langur instead for high level usage.
    '''
    def __init__(self, workers: list[Worker], llm_config: LLMConfig = None, cg: CognitionGraph = None):
        self.llm_config = llm_config if llm_config else LLMConfig(
            provider="anthropic",
            options={
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.0
            }
        )
        
        #self.world = World()
        #self.goal = goal
        self.cg = cg if cg else CognitionGraph(workers=workers, llm_config=self.llm_config)
        self.workers = workers
        
    
    def use(self, *connectors: Connector):
        for connector in connectors:
            self.world.register_connector(connector)
        return self


    async def run_until_done(self):
        
        # could be helpful info to load/save cycle count instead of resetting if we loaded a prev agent, idk
        cycle_count = 0
        while not self.cg.are_workers_done():
            # a lil jank calling the graph thing here
            # would be cool to live update num done workers mid-cycle based on state changes - if workers were to use some hook to update state
            print(f"[Cycle {cycle_count+1}]: {self.cg.worker_count(state=STATE_DONE)}/{self.cg.worker_count()} workers done")
            await self.cycle()
            cycle_count += 1
        print("Agent done!")

    async def cycle(self):#, cycles=1):
        #workers: list[Worker] = [DependencyDecomposer(), IntermediateProductBuilder(), IntermediateProductBuilder()]
        #for _ in range(cycles):
        jobs = []
        for worker in self.workers:
            jobs.append(worker.cycle())
        # naive async implementation, don't need to necessarily block gather here
        await asyncio.gather(*jobs)

    def to_json(self) -> dict:
        return {
            "llm": self.llm_config.model_dump(mode="json"),
            "workers": [worker.to_json() for worker in self.workers],
            "graph": self.cg.to_json(),
        }

    @classmethod
    def from_json(cls, data: dict) -> 'Agent':
        workers = [Worker.from_json(worker_data) for worker_data in data["workers"]]
        llm_config = LLMConfig.model_validate(data["llm"])
        graph = CognitionGraph.from_json(
            data=data["graph"],
            workers=workers,
            llm_config=llm_config,
        )
        agent = Agent(
            workers=workers,
            llm_config=llm_config,#data["llm"],
            cg=graph,
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
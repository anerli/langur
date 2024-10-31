'''
High level agent interface.
'''

import asyncio
import json
from typing import Callable
from langur.behavior import AgentBehavior, Task, Plan, Execute
from langur.agent import Agent
from langur.connector import Connector
from langur.connectors.connector_worker import ConnectorWorker
from langur.util.schema import schema_from_function
from langur.workers.worker import Worker




class Langur:
    def __init__(self, instructions: str = None, behavior: AgentBehavior = None, agent: Agent=None):
        '''
        High level agent interface with customizable behavior.
        Provide either instructions OR behavior.

        Args:
            instructions (str): General directions or task for the agent.
            behavior (AgentBehavior): Custom behavior to use instead of default. If provided, instructions are ignored.
            agent (Agent): Wrap a lower level agent representation - generally can ignore this parameter, used internally.
        
        Raises:
            RuntimeError: If no instructions or behavior are provided.
        '''
        if agent:
            self.agent = agent
            return
        
        if instructions is None and behavior is None:# and agent is None:
            raise RuntimeError(
                "One of instructions or behavior are required. "
                "Provide instructions to use default behavior, or provide custom behavior."
            )
        
        # Custom behavior if provided, otherwise default behavior
        behavior = behavior if behavior else AgentBehavior(
            Plan(Task(instructions)),
            Execute()
        )

        #print(behavior)

        # Default connector for one-off lambda peripherals
        #self._default_connector = None

        workers = behavior.compile()
        #print(workers)
        self.agent = Agent(workers=workers)


    # def get_default_connector(self):
    #     if self._default_connector is None:



    def use(self, peripheral: Worker | Connector | Callable):
        # Use provided connector or tool
        # TODO: impl
        # self.agent.use(...)
        if isinstance(peripheral, Worker):
            self.agent.add_worker(peripheral)
        elif isinstance(peripheral, Callable):
            schema = schema_from_function(peripheral)
            # One-off connector
            conn = Connector(connector_name=schema.name)
            conn.action(peripheral)
            self.use(conn)
        elif isinstance(peripheral, Connector):
            worker_type = peripheral.to_worker_type()
            print("adding worker of type:", worker_type)
            self.agent.add_worker(worker_type())
        else:
            raise TypeError("Invalid peripheral:", peripheral)
        

    def run(self, until: str = None):
        # TODO
        asyncio.run(self.agent.run_until_done())
    
    def show(self):
        return self.agent.cg.show()

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.agent.to_json(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'Langur':
        with open(path, "r") as f:
            agent = Agent.from_json(json.load(f))
        return Langur(agent=agent)
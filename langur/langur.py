'''
High level agent interface.
'''

import asyncio
import json
from langur.behavior import AgentBehavior, BaseBehavior, Plan, Task, Execute
from langur.agent import Agent
from langur.connector import Connector
from langur.connector import Connector
from langur.llm import LLMConfig
from langur.workers.worker import Worker

class Langur:
    def __init__(self, instructions: str = None, behavior: AgentBehavior = None, agent: Agent=None, llm_config: LLMConfig = None):
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

        workers = behavior.compile()
        self.agent = Agent(workers=workers, llm_config=llm_config)


    def use(self, *peripherals: Connector | Worker | AgentBehavior | BaseBehavior):
        '''
        Provide a peripheral for the agent to use. You can provide:
        - Connector - a configurable object with multiple actions
        - Behaviors - either composed AgentBehavior or an individual behavior - which will be added to existing behavior.
        - Worker - low-level cognitive worker
        '''
        for peripheral in peripherals:
            if isinstance(peripheral, Worker):
                self.agent.add_worker(peripheral)
            elif isinstance(peripheral, BaseBehavior):
                # Create one-off agent behavior to compile into workers
                agent_behavior = AgentBehavior(
                    peripheral
                )
                self.use(agent_behavior)
            elif isinstance(peripheral, AgentBehavior):
                workers = peripheral.compile()
                for worker in workers:
                    self.agent.add_worker(worker)
            else:
                raise TypeError("Invalid peripheral:", peripheral)
        

    def run(self, until: str = None):
        asyncio.run(self.agent.run(until=until))
    
    def show(self):
        return self.agent.cg.show()

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.agent.to_json(), f, indent=2)
    
    def save_graph_html(self, path: str):
        self.agent.cg.save_graph_html(path=path)
    
    # def generate_viewer(self, path: str):

    @classmethod
    def load(cls, path: str) -> 'Langur':
        with open(path, "r") as f:
            agent = Agent.from_json(json.load(f))
        return Langur(agent=agent)
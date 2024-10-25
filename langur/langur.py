'''
High level agent interface.
'''

import json
from langur.behavior import AgentBehavior
from langur.agent import Agent


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
            Execute(Plan(Task(instructions)))
        )

        workers = behavior.compile()
        self.agent = Agent(workers=workers)



    def use(self, connector):
        # Use provided connector or tool
        # TODO: impl
        # self.agent.use(...)
        pass
        

    def run(self):
        # TODO
        pass

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.agent.to_json(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'Langur':
        with open(path, "r") as f:
            agent = Agent.from_json(json.load(f))
        return Langur(agent=agent)


from pydantic import BaseModel
from langur.connectors.connector import Connector
from langur.world import World
from langur.graph import Graph, Node, Edge
from langur.prompts import templates
from .llm import FAST_LLM

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

    async def act(self):
        #graph = Graph(task)
        #seed = Node(task)
        #graph.add_node(seed)
        #await graph.back_search(seed, iters=2)
        await self.graph.back_search(iters=2)
        await self.graph.front_search(iters=5)

        # class Output(BaseModel):
        #     subtasks: list[str]

        # response = FAST_LLM.with_structured_output(Output).invoke(
        #     templates.BackSearch(
        #         goal=task,
        #         task=task,
        #         graph_context=graph.describe()
        #     ).render()
        # )
        # print(response)

        # for subtask in response.subtasks:
        #     node = Node(subtask)
        #     graph.add_node(node)
        #     graph.add_edge(Edge(node, "required for", seed))

        #return graph

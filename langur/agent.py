

from pydantic import BaseModel
from langur.connectors.connector import Connector
from langur.world import World
from langur.graph import Graph, Node, Edge
from langur.prompts import templates
from .llm import FAST_LLM

class Langur:
    def __init__(self):
        self.world = World()
    
    def use(self, *connectors: Connector):
        for connector in connectors:
            self.world.register_connector(connector)
        return self

    async def act(self, task: str):
        graph = Graph(task)
        seed = Node(task)
        graph.add_node(seed)
        await graph.back_search(seed, iters=2)

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

        return graph

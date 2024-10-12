import asyncio
from abc import ABC, abstractmethod
from pydantic import BaseModel
from .graph import Graph, Node, Edge, NODE_IP, NODE_TASK
from .llm import FAST_LLM
from .prompts import templates

class Worker(ABC):
    '''Meta-cognitive Worker'''
    @abstractmethod
    async def cycle(self, graph: Graph):
        '''
        Do one cycle with this worker; the implementation will vary widely depending on the worker's purpose.
        Each cycle should be finite, though potentially cycles could be executed indefinitely.
        '''
        pass

class DependencyDecomposer(Worker):
    def __init__(self):
        self.frontier = None
    
    async def cycle(self, graph: Graph):
        class Output(BaseModel):
            subtasks: list[str]
        
        if self.frontier is None:
            self.frontier = [graph.goal_node]
        new_frontier = []

        jobs = []
        for node in self.frontier:
            task = node.content
            print(f"Expanding: {task}")
            job = FAST_LLM.with_structured_output(Output).ainvoke(
                templates.BackSearch(
                    goal=graph.goal,
                    task=task,
                    graph_context=graph.describe()
                ).render()
            )
            jobs.append(job)

        responses = await asyncio.gather(*jobs)

        for node, response in zip(self.frontier, responses):
            print(response)
            for subtask in response.subtasks:
                new_node = Node(subtask, NODE_TASK)
                graph.add_node(new_node)
                graph.add_edge(Edge(new_node, "required for", node))
                new_frontier.append(new_node)
        self.frontier = new_frontier

class IntermediateProductBuilder(Worker):
    async def cycle(self, graph: Graph):
        class Output(BaseModel):
            dependencies: list[str]
            result: str
        
        resp = await FAST_LLM.with_structured_output(Output).ainvoke(
            templates.FrontSearch(
                goal=graph.goal,
                graph_context=graph.describe(),
                intermediate_products="\n".join([node.content for node in filter(lambda n: n.node_type == NODE_IP, graph.nodes)])
            ).render()
        )
        print(resp)
        dest_node = Node(resp.result, NODE_IP)
        src_nodes = [Node(dep, NODE_IP) for dep in resp.dependencies]
        for src_node in src_nodes:
            graph.add_edge(Edge(src_node, "needed for", dest_node))

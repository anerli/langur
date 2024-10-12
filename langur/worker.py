import asyncio
from abc import ABC
from pydantic import BaseModel
from .graph import Graph, Node, Edge, NODE_IP, NODE_TASK
from .llm import FAST_LLM
from .prompts import templates

class Worker(ABC):
    '''Meta-cognitive Worker'''
    async def cycle(self, graph: Graph):
        '''
        Do one cycle with this worker; the implementation will vary widely depending on the worker's purpose.
        Each cycle should be finite, though potentially cycles could be executed indefinitely.
        '''
        pass

class DependencyDecomposer(Worker):
    def __init__(self, iters_per_cycle=1):
        self.iters_per_cycle = iters_per_cycle
    
    async def cycle(self, graph: Graph):
        class Output(BaseModel):
            subtasks: list[str]
        
        frontier = [graph.goal_node]
        new_frontier = []

        for _ in range(self.iters_per_cycle):
            jobs = []
            for node in frontier:
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
                #jobs.append((task, job))
            responses = await asyncio.gather(*jobs)
            #responses = await asyncio.gather(*[job[1] for job in jobs])
            for node, response in zip(frontier, responses):
                print(response)
                for subtask in response.subtasks:
                    new_node = Node(subtask, NODE_TASK)
                    graph.add_node(new_node)
                    graph.add_edge(Edge(new_node, "required for", node))
                    new_frontier.append(new_node)
            frontier = new_frontier

class IntermediateProductBuilder(Worker):
    def __init__(self, products_per_cycle=1):
        self.products_per_cycle = products_per_cycle

    async def cycle(self, graph: Graph):
        class Output(BaseModel):
            dependencies: list[str]
            result: str
        for _ in range(self.products_per_cycle):
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

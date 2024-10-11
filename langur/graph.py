# For vis
import asyncio
import networkx as nx
from ipysigma import Sigma
from pydantic import BaseModel
from .llm import FAST_LLM
from .prompts import templates

NODE_TASK = "TASK"
# Intermediate Product
NODE_IP = "INTERMEDIATE_PRODUCT"

class Node:
    '''Knowledge Graph Node'''
    def __init__(self, content: str, node_type: str):
        self.content = content
        self.node_type = node_type
        self.edges = set()
    
    def __hash__(self):
        return hash((self.node_type, self.content))
    
    def add_edge(self, edge: 'Edge'):
        self.edges.add(edge)

class Edge:
    '''Knowledge Graph Edge'''
    def __init__(self, source_node: Node, relation: str, dest_node: Node, bidirectional=False):
        self.source_node = source_node
        self.dest_node = dest_node
        self.relation = relation
        source_node.add_edge(self)
        dest_node.add_edge(self)
    
    def __hash__(self):
        return hash((self.source_node.content, self.relation, self.dest_node.content))

    def __str__(self):
        return f"{self.source_node.content} {self.relation} {self.dest_node.content}"
    
class Graph:
    '''Knowledge Graph / Task Graph'''
    def __init__(self, goal: str):
        self.goal = goal
        self.goal_node = Node(goal, NODE_TASK)
        self.nodes: set[Node] = set()
        self.edges: set[Edge] = set()
    
    def add_node(self, node: Node):
        self.nodes.add(node)

    def add_edge(self, edge: Edge):
        # Add either node if not already in graph
        if edge.source_node not in self.nodes:
            self.nodes.add(edge.source_node)
        if edge.dest_node not in self.nodes:
            self.nodes.add(edge.dest_node)
        self.edges.add(edge)
    
    def to_networkx(self):
        g = nx.DiGraph()
        for node in self.nodes:
            g.add_node(node.content, node_type=node.node_type)
        for edge in self.edges:
            g.add_edge(edge.source_node.content, edge.dest_node.content, label=edge.relation)
        return g
    
    def show(self):
        return Sigma(
            self.to_networkx(),
            edge_size_range=(4, 8),
            node_size_range=(10, 16),
            start_layout=2,
            default_edge_color="#111",
            default_node_color="#00f",
            default_node_label_size=16,
            node_color="node_type"
        )

    async def grow(self, node: Node):
        class Item(BaseModel):
            relation: str
            destination_node: str
        class Output(BaseModel):
            items: list[Item]
        
        resp = await FAST_LLM.with_structured_output(Output).ainvoke(
            templates.NodeGrow(
                source_node_content=node.content,
                existing_nodes="\n".join([node.content for node in self.nodes]),
                existing_relations="\n".join([str(edge) for edge in self.edges])
            ).render()
        )
        print(resp)

        for item in resp.items:
            dest_node = Node(item.destination_node, NODE_TASK)
            if dest_node not in self.nodes:
                self.add_node(dest_node)
            edge = Edge(node, item.relation, dest_node)
            if edge not in self.edges:
                self.add_edge(edge)
    
    async def back_search(self, iters=1):
        class Output(BaseModel):
            subtasks: list[str]
        
        frontier = [self.goal_node]
        new_frontier = []

        for _ in range(iters):
            jobs = []
            for node in frontier:
                task = node.content
                print(f"Expanding: {task}")
                job = FAST_LLM.with_structured_output(Output).ainvoke(
                    templates.BackSearch(
                        goal=self.goal,
                        task=task,
                        graph_context=self.describe()
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
                    self.add_node(new_node)
                    self.add_edge(Edge(new_node, "required for", node))
                    new_frontier.append(new_node)
            frontier = new_frontier

    async def front_search(self, iters=1):
        class Output(BaseModel):
            dependencies: list[str]
            result: str
        for _ in range(iters):
            resp = await FAST_LLM.with_structured_output(Output).ainvoke(
                templates.FrontSearch(
                    goal=self.goal,
                    graph_context=self.describe(),
                    intermediate_products="\n".join([node.content for node in filter(lambda n: n.node_type == NODE_IP, self.nodes)])
                ).render()
            )
            print(resp)
            dest_node = Node(resp.result, NODE_IP)
            src_nodes = [Node(dep, NODE_IP) for dep in resp.dependencies]
            for src_node in src_nodes:
                self.add_edge(Edge(src_node, "needed for", dest_node))

        
    
    def describe(self) -> str:
        # naive
        s = ""
        for edge in self.edges:
            s += f"{edge.source_node.content}->{edge.dest_node.content}\n"
        return s
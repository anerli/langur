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
    
    def describe(self) -> str:
        # naive
        s = ""
        for edge in self.edges:
            s += f"{edge.source_node.content}->{edge.dest_node.content}\n"
        return s
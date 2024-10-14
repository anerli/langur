# For vis
from abc import ABC, abstractmethod
import asyncio
import json
from typing import Callable
import networkx as nx
from ipysigma import Sigma
from pydantic import BaseModel
from .llm import FAST_LLM
from .prompts import templates

NODE_TASK = "TASK"
# Intermediate Product
NODE_IP = "INTERMEDIATE_PRODUCT"


class Node(ABC):
    '''Knowledge Graph Node'''
    def __init__(self, id: str):
        self.id = id
        self.edges = set()
    
    def __hash__(self):
        return hash((self.__class__.__name__, self.id))
    
    def add_edge(self, edge: 'Edge'):
        self.edges.add(edge)
    
    @abstractmethod
    def content(self) -> str:
        pass

    def get_visual_attributes(self) -> dict:
        '''
        Override to return attributes to be visualized in the graph view.
        Doesn't affect cognitive behavior, only for visual debugging.
        '''
        return {
            "content": self.content()
        }

class ObservableNode(Node):
    def __init__(self, id: str, content_getter: Callable[[], str]):
        super().__init__(id)
        self.content_getter = content_getter
    
    def content(self):
        return self.content_getter()

class StaticNode(Node):
    def __init__(self, id: str, content: str):
        super().__init__(id)
        self._content = content
    
    def content(self):
        return self._content

class TaskNode(StaticNode):
    pass

class ProductNode(StaticNode):
    pass

class ActionDefinitionNode(Node):
    def __init__(self, action_id: str, description: str, schema: dict):
        '''
        description: natural language description of exactly what this action does
        schema: JSON schema defining input for this action
        '''
        super().__init__(action_id)
        self.description = description
        self.schema = schema
    
    def content(self) -> str:
        formatted_schema = json.dumps(self.schema)
        return f"Action ID: {self.id}\nAction Description: {self.description}\nAction Input Schema:\n{formatted_schema}"

    def get_visual_attributes(self):
        formatted_schema = json.dumps(self.schema)
        return {
            **super().get_visual_attributes(),
            "description": self.description,
            "schema": formatted_schema
        }

# class DynamicNode(Node):
#     def __init__

class Edge:
    '''Knowledge Graph Edge'''
    def __init__(self, source_node: Node, relation: str, dest_node: Node, bidirectional=False):
        self.source_node = source_node
        self.dest_node = dest_node
        self.relation = relation
        source_node.add_edge(self)
        dest_node.add_edge(self)
    
    def __hash__(self):
        return hash((self.source_node.id, self.relation, self.dest_node.id))

    def __str__(self):
        return f"{self.source_node.id} {self.relation} {self.dest_node.id}"
    
class Graph:
    '''Knowledge Graph / Task Graph'''
    def __init__(self, goal: str):
        self.goal = goal
        self.goal_node = TaskNode("final_goal", goal)
        self.nodes: set[Node] = set()
        self.edges: set[Edge] = set()
        self.add_node(self.goal_node)
    
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
            #node_attributes = {attr: getattr(node, attr) for attr in dir(node) if not attr.startswith('__') and not callable(getattr(node, attr))}
            #print("Hello?")
            #print("Attrs:", node.get_visual_attributes())
            g.add_node(node.id, node_class=node.__class__.__name__, **node.get_visual_attributes())
        for edge in self.edges:
            g.add_edge(edge.source_node.id, edge.dest_node.id, label=edge.relation)
        return g

    def query_node_by_id(self, node_id: str) -> Node | None:
        # TMP impl, make efficient by making nodes a map from ID to node
        for node in self.nodes:
            if node_id == node.id:
                return node
        return None
    
    def show(self):
        return Sigma(
            self.to_networkx(),
            edge_size_range=(4, 8),
            node_size_range=(10, 16),
            start_layout=2,
            default_edge_color="#111",
            default_node_color="#00f",
            default_node_label_size=16,
            node_color="node_class"
        )
    
    def describe(self) -> str:
        # naive
        s = ""
        for edge in self.edges:
            s += f"{edge.source_node.id}->{edge.dest_node.id}\n"
        return s
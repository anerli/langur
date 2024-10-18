# For vis
from abc import ABC, abstractmethod
import asyncio
import copy
import json
from typing import Callable, Type
import networkx as nx
from ipysigma import Sigma
from pydantic import BaseModel
from .llm import FAST_LLM
from .prompts import templates

NODE_TASK = "TASK"
# Intermediate Product
NODE_IP = "INTERMEDIATE_PRODUCT"


class Node():
    tags = []

    '''Knowledge Graph Node'''
    def __init__(self, id: str):
        self.id = id
        self.edges = set()
    
    def __hash__(self):
        return hash(self.id)
        #return hash((self.__class__.__name__, self.id))
    
    # def __eq__(self, other):
    #     if not isinstance(other, Node):
    #         return False
    
    @classmethod
    def get_tags(cls) -> set[str]:
        all_tags = set(cls.tags)
        for base in cls.__bases__:
            if hasattr(base, 'get_tags'):
                all_tags = all_tags.union(base.get_tags())
        return all_tags
    
    def add_edge(self, edge: 'Edge'):
        self.edges.add(edge)
    
    def incoming_edges(self) -> set['Edge']:
        return set(filter(lambda edge: edge.dest_node == self, self.edges))
    
    def upstream_nodes(self) -> set['Node']:
        return set(edge.src_node for edge in self.incoming_edges())

    def outgoing_edges(self) -> set['Edge']:
        return set(filter(lambda edge: edge.src_node == self, self.edges))

    def downstream_nodes(self) -> set['Node']:
        return set(edge.dest_node for edge in self.outgoing_edges())
    
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

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id='{self.id}' tags={self.get_tags()} edges={self.edges}>"

class ObservableNode(Node):
    tags = ["observable"]

    def __init__(self, id: str, content_getter: Callable[[], str]):
        super().__init__(id)
        self.content_getter = content_getter
    
    def content(self):
        return self.content_getter()

class StaticNode(Node):
    tags = ["static"]

    def __init__(self, id: str, content: str):
        super().__init__(id)
        self._content = content
    
    def content(self):
        return self._content

class TaskNode(Node):
    tags = ["task"]
    def __init__(self, id: str, content: str, action_types: list[str]):
        super().__init__(id)
        self._content = content
        self.action_types = action_types
    
    def content(self):
        return f"{self._content} {self.action_types}"

class ActionUseNode(Node):
    tags = ["action"]
    
    def __init__(self, id: str, payload: dict):
        '''payload: empty, partial, or full input dict'''
        super().__init__(id)
        self.payload = payload
    
    def content(self):
        formatted_inputs = json.dumps(self.payload)
        return f"Action Use ID: {self.id}\nAction Inputs:\n{formatted_inputs}"

    def get_visual_attributes(self):
        formatted_inputs = json.dumps(self.payload)
        return {
            **super().get_visual_attributes(),
            "payload": formatted_inputs
        }

class AssumptionNode(StaticNode):
    pass

class ProductNode(StaticNode):
    pass

class ActionDefinitionNode(Node):
    tags = ["action_definition"]

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
    def __init__(self, src_node: Node, relation: str, dest_node: Node, bidirectional=False):
        # note: don't reassign src_node / dest_node directly cus edges wont be tracked correctly, should redesign to make this clearer
        self.src_node = src_node
        self.dest_node = dest_node
        self.relation = relation
        src_node.add_edge(self)
        dest_node.add_edge(self)
    
    def __hash__(self):
        return hash((self.src_node.id, self.relation, self.dest_node.id))

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        # There are cases where multiple nodes have same ID, so check node refs here
        return (self.src_node, self.relation, self.dest_node) == (other.src_node, other.relation, other.dest_node)
        #return hash(self) == hash(other)

    def __str__(self):
        return f"{self.src_node.id} {self.relation} {self.dest_node.id}"

    # def copy(self):
    #     #return copy.deepcopy(self)
    #     return Edge(self.src_node, self.relation, self.dest_node)

    def __repr__(self) -> str:
        #return f"<{self.__class__.__name__} {self.src_node.id} --{self.relation}--> {self.dest_node.id}>"
        return f"Edge('{self.src_node.id}'-[{self.relation}]->'{self.dest_node.id}')"
    
class Graph:
    '''Knowledge Graph / Task Graph'''
    def __init__(self, goal: str):
        self.goal = goal
        self.goal_node = TaskNode("final_goal", goal, [])
        self._node_map: dict[str, Node] = {}
        self.edges: set[Edge] = set()
        self.add_node(self.goal_node)
    
    def get_nodes(self) -> set[Node]:
        return set(self._node_map.values())

    def add_node(self, node: Node):
        if node.id in self._node_map:
            raise RuntimeError("ID collision when adding node:", node)
        self._node_map[node.id] = node
        #self.nodes.add(node)
    
    def has_node(self, node: Node) -> bool:
        return node in self.get_nodes()

    def add_edge(self, edge: Edge):
        # Make sure nodes are in graph
        if not self.has_node(edge.src_node):
            self.add_node(edge.src_node)
            #raise RuntimeError(f"Edge includes node not in graph: {edge.src_node}")
        if not self.has_node(edge.dest_node):
            self.add_node(edge.dest_node)
            #raise RuntimeError(f"Edge includes node not in graph: {edge.dest_node}")
        self.edges.add(edge)
    
    def add_edge_by_ids(self, src_id: str, relation: str, dest_id: str):
        src_node = self.query_node_by_id(src_id)
        dest_node = self.query_node_by_id(dest_id)
        if not src_node:
            raise RuntimeError(f"Invalid edge added, missing node with ID: `{src_id}`")
        if not dest_node:
            raise RuntimeError(f"Invalid edge added, missing node with ID: `{dest_id}`")
        self.edges.add(Edge(src_node, relation, dest_node))

    def to_networkx(self):
        g = nx.DiGraph()
        for node in self.get_nodes():
            #node_attributes = {attr: getattr(node, attr) for attr in dir(node) if not attr.startswith('__') and not callable(getattr(node, attr))}
            #print("Hello?")
            #print("Attrs:", node.get_visual_attributes())
            g.add_node(node.id, node_class=node.__class__.__name__, **node.get_visual_attributes())
        for edge in self.edges:
            g.add_edge(edge.src_node.id, edge.dest_node.id, label=edge.relation)
        return g

    def query_node_by_id(self, node_id: str) -> Node | None:
        try:
            return self._node_map[node_id]
        except KeyError:
            return None
    
    def query_nodes_by_tag(self, *tags: str) -> set[Node]:
        '''Get all nodes with at least one of the provided tags'''
        # could make more efficient with some kind of caching, idk if necessary
        matches = set()
        for node in self.get_nodes():
            for tag in tags:
                if tag in node.get_tags():
                    matches.add(node)
                    break
        return matches

    def remove_edge(self, edge: Edge):
        edge.src_node.edges.remove(edge)
        edge.dest_node.edges.remove(edge)
        self.edges.remove(edge)
    
    def remove_node(self, node: Node):
        edges = node.edges.copy()
        for edge in edges:
            self.remove_edge(edge)
        del self._node_map[node.id]
    
    # NOPE breaks edge hashes and crap
    # def change_node_id(self, node: Node, new_id: str):
    #     del self._node_map[node.id]
    #     node.id = new_id
    #     self._node_map[new_id] = node

    def substitute(self, node_id: str, replacements: list[Node], keep_incoming=True, keep_outgoing=True):
        '''Replace a node by swapping it out for one or more nodes, which will each assume all incoming and outgoing edges of the replaced node'''
        to_replace = self.query_node_by_id(node_id)
        # basically a hack to avoid ID collisions when replacements have same ID
        #self.change_node_id(to_replace, "REPLACING")
        # copy cus deleting as we go
        to_replace_edges_copy = to_replace.edges.copy()
        self.remove_node(to_replace)

        print(self.query_node_by_id("B"))
        #print(to_replace_edges_copy)
        
            #print("Edge:", edge)
        for node in replacements:
            print("Replacement:", node)
            print(self.query_node_by_id("B"))
            self.add_node(node)
            for edge in to_replace_edges_copy:
                
                #new_edge = edge.copy()
                #if node.id == to_replace.id
                
                
                if to_replace == edge.src_node and keep_outgoing:
                    #new_edge.src_node = node
                    new_edge = Edge(node, edge.relation, edge.dest_node)
                    self.add_edge(new_edge)
                if to_replace == edge.dest_node and keep_incoming:
                    #new_edge.dest_node = node
                    new_edge = Edge(edge.src_node, edge.relation, node)
                    self.add_edge(new_edge)
                #print("Adding:", new_edge)
                
            #print("Removing:", edge)
            #self.remove_edge(edge)
        


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
            s += f"{edge.src_node.id}->{edge.dest_node.id}\n"
        return s

    # def query(self, filter_tags: list[str] = None):
    #     if filter_tags is None:
    #         nodes = self.get_nodes()
    #     else:
    #         nodes = self.query_nodes_by_tag(*filter_tags)
    #     return nodes

    def build_context(self, *nodes: Node):
        '''
        filter_tags: Include only nodes with one of the provided tags
        '''
        nodes = nodes if nodes else self.get_nodes()

        # TODO: Re-add filtering system
        context = ""
        # todo: decide order somehow
        for node in nodes:
            context += f"Node ID: {node.id}\n"
            context += f"Node Edges:\n"
            for edge in node.edges:
                if node == edge.src_node:
                    context += f"{node.id}->{edge.dest_node.id}\n"
                else:
                    context += f"{node.id}<-{edge.src_node.id}\n"
            context += f"Node Content:\n{node.content()}"
            context += "\n\n"
        return context
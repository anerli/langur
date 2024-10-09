# For vis
import networkx as nx
from ipysigma import Sigma
import matplotlib as mpl
import matplotlib.pyplot as plt

class Node:
    '''Knowledge Graph Node'''
    def __init__(self, content: str):
        self.content = content
        self.edges = set()
    
    def __hash__(self):
        return hash(self.content)
    
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
    
class KG:
    '''Knowledge Graph'''
    def __init__(self):
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
            g.add_node(node.content)
        for edge in self.edges:
            g.add_edge(edge.source_node.content, edge.dest_node.content, label=edge.relation)
        return g
    
    def show(self):
        return Sigma(self.to_networkx(), edge_size_range=(6, 12), node_size_range=(10, 16), start_layout=2)#, default_node_size=10, default_edge_size=6)


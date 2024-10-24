from typing import Callable
from baml_py import ClientRegistry
import networkx as nx
from ipysigma import Sigma
from langur.workers.subtask_planner import TaskNode
from .node import Node
from .edge import Edge

class NodeCollisionError(RuntimeError):
    pass

    
class Graph:
    '''Knowledge Graph / Task Graph'''
    def __init__(self, goal: StopIteration, cr: ClientRegistry):
        self.goal = goal
        self.goal_node = TaskNode("final_goal", goal, [])
        self._node_map: dict[str, Node] = {}
        self.edges: set[Edge] = set()
        self.add_node(self.goal_node)
        self.cr = cr

        
    
    def get_nodes(self) -> set[Node]:
        return set(self._node_map.values())

    def add_node(self, node: Node):
        if node.id in self._node_map:
            raise NodeCollisionError("Node ID collision when adding node:", node)
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
            g.add_node(node.id, node_class=node.__class__.__name__, **node.to_json())
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

    def substitute(self, node_id: str, replacements: list[Node], keep_incoming=True, keep_outgoing=True):#, ignore_dupe_ids=False):
        '''Replace a node by swapping it out for one or more nodes, which will each assume all incoming and outgoing edges of the replaced node'''
        to_replace = self.query_node_by_id(node_id)
        # copy cus deleting as we go
        to_replace_edges_copy = to_replace.edges.copy()
        self.remove_node(to_replace)

        for node in replacements:
            self.add_node(node)
            for edge in to_replace_edges_copy:
                if to_replace == edge.src_node and keep_outgoing:
                    #new_edge.src_node = node
                    new_edge = Edge(node, edge.relation, edge.dest_node)
                    self.add_edge(new_edge)
                if to_replace == edge.dest_node and keep_incoming:
                    #new_edge.dest_node = node
                    new_edge = Edge(edge.src_node, edge.relation, node)
                    self.add_edge(new_edge)

    def show(self):
        return Sigma(
            self.to_networkx(),
            edge_size_range=(3, 5),
            node_size_range=(10, 16),
            start_layout=2,
            default_edge_color="#000000aa",
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

    def to_json(self) -> dict:
        return {
            
        }

    @classmethod
    def from_json(cls, data: dict) -> 'Graph':
        return Graph("foo", ClientRegistry())
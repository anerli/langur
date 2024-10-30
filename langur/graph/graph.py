import json
from typing import Callable, ClassVar, Set, Type, TypeVar
from baml_py import ClientRegistry
import networkx as nx
from ipysigma import Sigma

from langur.llm import LLMConfig
from langur.util.type_index import TypeIndex
from langur.workers.worker import STATE_DONE
from .node import Node
from .edge import Edge

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langur.workers.worker import Worker

class NodeCollisionError(RuntimeError):
    pass

N = TypeVar('N', bound='Node')#, Node)

class CognitionGraph:
    def __init__(self, workers: list['Worker'], llm_config: LLMConfig):#cr: ClientRegistry):
        self._node_map: dict[str, Node] = {}
        self.edges: set[Edge] = set()
        
        # sus? graph is clearly more than a graph at this point
        self.workers = workers

        # Give graph ref to workers
        for worker in workers:
            worker.cg = self

        #self.cr = cr
        print("llm_config", llm_config)
        self.llm_config = llm_config

        self._type_index: TypeIndex[Node] = TypeIndex()
    
    def get_client_registry(self) -> ClientRegistry:
        return self.llm_config.to_registry()

    def get_workers_with_state(self, state: str) -> list['Worker']:
        # could make more efficient by having workers callback on state change and keeping a map from state to workers
        return list(filter(lambda worker: worker.state == state, self.workers))

    def are_workers_done(self):
        return len(self.get_workers_with_state(STATE_DONE)) == len(self.workers)

    def get_nodes(self) -> set[Node]:
        return set(self._node_map.values())

    def get_edges(self) -> set[Edge]:
        return self.edges

    def add_node(self, node: Node):
        if node.id in self._node_map:
            raise NodeCollisionError("Node ID collision when adding node:", node)
        self._node_map[node.id] = node
        self._type_index.add(node)
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
            # Convert any nested json in node properties to string so can be seen properly instead of [object Object]
            data = node.to_json()
            for key in data.keys():
                if isinstance(data[key], dict):
                    data[key] = json.dumps(data[key])
            g.add_node(node.id, node_class=node.__class__.__name__, **data)
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
    
    # Not sure if I prefer this approach or tags
    # It is probably preferable to return subclasses as well..
    # def query_nodes_by_type(self, node_type: Type[N]) -> set[N]:
    #     # NOTE: Matches by class name, does NOT match subclasses
    #     matches = set()
    #     for node in self.get_nodes():
    #         if node.__class__.__name__ == node_type.__name__:
    #             matches.add(node)
    #     return matches

    def query_nodes_by_type(self, node_type: Type[N]) -> Set[N]:
        """Query nodes by type, including subclass instances"""
        return self._type_index.get_by_type(node_type)

    def remove_edge(self, edge: Edge):
        edge.src_node.edges.remove(edge)
        edge.dest_node.edges.remove(edge)
        self.edges.remove(edge)
    
    def remove_node(self, node: Node):
        edges = node.edges.copy()
        for edge in edges:
            self.remove_edge(edge)
        del self._node_map[node.id]
        self._type_index.remove(node)

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
            "nodes": [node.to_json() for node in self.get_nodes()],
            "edges": [edge.to_json() for edge in self.get_edges()]
        }

    @classmethod
    def from_json(cls, data: dict, workers: list['Worker'], llm_config: LLMConfig) -> 'CognitionGraph':
        # Passing in the actual data with graph stuff as well as workers and llm_config from agent
        nodes = [Node.from_json(node_data) for node_data in data["nodes"]]
        node_map = {node.id: node for node in nodes}

        edges = []
        for edge_data in data["edges"]:
            edge = Edge(
                src_node=node_map[edge_data["src_node_id"]],
                relation=edge_data["relation"],
                dest_node=node_map[edge_data["dest_node_id"]]
            )
            edges.append(edge)

        graph = CognitionGraph(workers=workers, llm_config=llm_config)

        for node in nodes:
            graph.add_node(node)
        for edge in edges:
            graph.add_edge(edge)
        
        return graph
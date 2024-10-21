from abc import abstractmethod
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .edge import Edge

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
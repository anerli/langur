from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, ClassVar, Dict, Set, Type
from pydantic import BaseModel, ConfigDict, Field

#if TYPE_CHECKING:
# Fully import in order for pydantic models to be built
from .edge import Edge

class Node(BaseModel):
    id: str
    edges: Set['Edge'] = Field(default_factory=set, exclude=True)

    tags: ClassVar[list[str]] = []
    _subclasses: ClassVar[Dict[str, Type['Node']]] = {}

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    # def __init__(self, **data):
    #     super().__init__(**data)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Node._subclasses[cls.__name__] = cls
    
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
    
    # @abstractmethod
    # def content(self) -> str:
    #     pass

    # def get_visual_attributes(self) -> dict:
    #     '''
    #     Override to return attributes to be visualized in the graph view.
    #     Doesn't affect cognitive behavior, only for visual debugging.
    #     '''
    #     return {
    #         "content": self.content()
    #     }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id='{self.id}' tags={self.get_tags()} edges={self.edges}>"

    # Any Node implementation should implment to_json and from_json?

    # def to_json(self) -> dict:
    #     return {
    #         "node_type": self.__class__.__name__,
    #         "id": self.id,
    #     }

    def to_json(self) -> dict:
        data = super().model_dump(mode="json")
        # Insert subclass name so can reconstruct correct class later
        data = {
            "node_type": self.__class__.__name__,
            **data
        }
        return data

    @classmethod
    def from_json(cls, data: dict) -> 'Node':
        node_type = data["node_type"]
        if node_type not in cls._subclasses:
            raise KeyError(f"Unknown node type: {node_type}")
        worker_class = Node._subclasses[node_type]
        # Instantiate the appropriate subclass
        data_no_node_type = data.copy()
        del data_no_node_type["node_type"]
        return worker_class.model_validate(data_no_node_type)
    
# class ObservableNode(Node):
#     tags = ["observable"]

#     def __init__(self, id: str, content_getter: Callable[[], str]):
#         super().__init__(id)
#         self.content_getter = content_getter
    
#     def content(self):
#         return self.content_getter()

# class StaticNode(Node):
#     tags = ["static"]

#     def __init__(self, id: str, content: str):
#         super().__init__(id)
#         self._content = content
    
#     def content(self):
#         return self._content
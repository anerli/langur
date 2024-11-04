from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .node import Node

class Edge():
    '''Graph Edge'''

    def __init__(self, src_node: 'Node', relation: str, dest_node: 'Node'):
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

    def __repr__(self) -> str:
        #return f"<{self.__class__.__name__} {self.src_node.id} --{self.relation}--> {self.dest_node.id}>"
        return f"Edge('{self.src_node.id}'-[{self.relation}]->'{self.dest_node.id}')"

    def to_json(self) -> dict:
        return {
            #**super().model_dump(mode="json"),
            "relation": self.relation,
            "src_node_id": self.src_node.id,
            "dest_node_id": self.dest_node.id
        }
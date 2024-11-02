from typing import TYPE_CHECKING, Dict, List, Set, Type
from collections import defaultdict

if TYPE_CHECKING:
    from langur.connector import Connector
    from langur.actions import ActionNode

class ActionNodeRegistry:
    '''
    For each Connector, keep track of corresponding ActionNode types dynamically generated at runtime.
    This way cognitive workers can be aware of what action types are available by looking at loaded Connectors.
    '''
    def __init__(self):
        self._connector_actions: Dict[str, Dict[str, Type['ActionNode']]] = defaultdict(dict)
    
    def register(self, connector_class_name: str, action_cls: Type['ActionNode']):
        self._connector_actions[connector_class_name][action_cls.__name__] = action_cls
    
    def get_action_node_types(self, connector_class_name: str) -> Set[Type['ActionNode']]:
        return set(self._connector_actions[connector_class_name].values())

action_node_type_registry = ActionNodeRegistry()

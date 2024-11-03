from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Set, Type
from collections import defaultdict

if TYPE_CHECKING:
    from langur.connector import Connector
    from langur.actions import ActionNode

@dataclass
class ActionNodeRegistryEntry:
    name: str
    action_node_type: Type['ActionNode']
    tags: Set[str] = None

@dataclass
class ActionNodeRegistryFilter:
    '''
    names: Filter to only include actions with these names
    tags: Filter to only include actions with at least one of these tags.
    '''
    names: Set[str] = None
    tags: Set[str] = None

class ActionNodeRegistry:
    '''
    For each Connector, keep track of corresponding ActionNode types dynamically generated at runtime.
    This way cognitive workers can be aware of what action types are available by looking at loaded Connectors.
    '''
    def __init__(self):
        self._connector_actions: Dict[str, Dict[str, Type['ActionNode']]] = defaultdict(dict)
    
    def register(self, connector_class_name: str, action_cls: Type['ActionNode'], tags: List[str] = None):
        name = action_cls.__name__
        self._connector_actions[connector_class_name][name] = ActionNodeRegistryEntry(
            name=name,
            action_node_type=action_cls,
            tags=set(tags) if tags else set()
        )
    
    def get_action_node_types(self, connector_class_name: str, action_filter: ActionNodeRegistryFilter=None) -> Set[Type['ActionNode']]:
        entries = list(self._connector_actions[connector_class_name].values())
        #print(entries)
        if action_filter:
            if action_filter.names is not None:
                entries = list(filter(lambda a: a.name in action_filter.names, entries))
            if action_filter.tags is not None:
                entries = list(filter(lambda a: any(tag in action_filter.tags for tag in a.tags), entries))
        # Return just the action node types after filtering done
        #print("entries:", entries)
        return set(a.action_node_type for a in entries)

action_node_type_registry = ActionNodeRegistry()

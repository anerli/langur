from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Set, Type
from collections import defaultdict

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from langur.connector import Connector
    from langur.actions import ActionNode

@dataclass
class ActionNodeRegistryEntry:
    name: str
    action_node_type: Type['ActionNode']
    tags: Set[str] = None


class ActionNodeRegistryFilter(BaseModel):
    '''
    names: Filter to only include actions with these names
    tags: Filter to only include actions with at least one of these tags.
    '''
    # Enabled names override disabled tags
    enabled_names: Set[str] = Field(default_factory=set)
    disabled_names: Set[str] = Field(default_factory=set)
    disabled_tags: Set[str] = Field(default_factory=set)

    def enable_actions(self, names: List[str] = None, tags: List[str] = None):
        if names is not None:
            self.enabled_names = self.enabled_names.union(names)
            self.disabled_names = self.disabled_names.difference(names)
        if tags is not None:
            self.disabled_tags = self.disabled_tags.difference(tags)

    def disable_actions(self, names: List[str] = None, tags: List[str] = None):
        if names is not None:
            self.enabled_names = self.enabled_names.difference(names)
            self.disabled_names = self.disabled_names.union(names)
        if tags is not None:
            self.disabled_tags = self.disabled_tags.union(tags)


def should_include_action(action: ActionNodeRegistryEntry, action_filter: ActionNodeRegistryFilter) -> bool:
    # No filter means include everything
    if action_filter is None:
        return True
        
    # Check enabled names first (highest priority)
    if action_filter.enabled_names is not None and action.name in action_filter.enabled_names:
        return True
        
    # Check disabled names (second priority)
    if action_filter.disabled_names is not None and action.name in action_filter.disabled_names:
        return False
        
    # Check disabled tags (lowest priority)
    # Only check if the action wasn't explicitly enabled by name
    if action_filter.disabled_tags is not None and action.tags:
        if any(tag in action_filter.disabled_tags for tag in action.tags):
            return False
            
    # If we get here, include the action if:
    # - No filtering specified
    # - Name was not disabled
    # - No disabled tags matched
    return True

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
        # entries = list(self._connector_actions[connector_class_name].values())
        # #print(entries)
        # if action_filter:
        #     if action_filter.names is not None:
        #         entries = list(filter(lambda a: a.name in action_filter.names, entries))
        #     if action_filter.tags is not None:
        #         entries = list(filter(lambda a: any(tag in action_filter.tags for tag in a.tags), entries))
        # # Return just the action node types after filtering done
        # #print("entries:", entries)
        # return set(a.action_node_type for a in entries)
        entries = list(self._connector_actions[connector_class_name].values())
        filtered_entries = list(
            filter(lambda entry: should_include_action(entry, action_filter), entries)
        )
        return set(entry.action_node_type for entry in filtered_entries)

action_node_type_registry = ActionNodeRegistry()

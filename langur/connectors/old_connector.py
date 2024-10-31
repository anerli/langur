from abc import abstractmethod
from typing import List, Type, TYPE_CHECKING

from langur.util.general import UniqueClassAttribute

if TYPE_CHECKING:
    from ..commands import Command

def connected(*connector_classes):
    def decorator(command_class: Type['Command']):
        #print(f"connecting: {command_class} with {connector_classes}")
        command_class._connector_types = list(connector_classes)
        for connector_class in connector_classes:
            if not issubclass(connector_class, Connector):
                raise TypeError(f"{connector_class.__name__} is not a subclass of Connector")
            connector_class._command_types.add(command_class)
        return command_class
    return decorator


class Connector:
    _command_types = UniqueClassAttribute(set)

    @classmethod
    def get_command_types(cls) -> List[Type['Connector']]:
        return list(cls._command_types)
    
    @abstractmethod
    def overview(self) -> str:
        pass
    
    def __str__(self):
        return f"{self.__class__.__name__} Overview:\n{self.overview()}"

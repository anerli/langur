from typing import TypeVar, Type, Set, Dict, Generic, Iterable, Optional
from collections import defaultdict

T = TypeVar('T')

class TypeKey:
    """
    Stable identifier for types that survives class redefinitions in Jupyter.
    Uses module name and qualname for comparison instead of type identity.
    """
    def __init__(self, typ: Type):
        # Get fully qualified name
        self.module = typ.__module__
        self.qualname = typ.__qualname__
        
    def __eq__(self, other: 'TypeKey') -> bool:
        if not isinstance(other, TypeKey):
            return False
        return (self.module == other.module and 
                self.qualname == other.qualname)
    
    def __hash__(self) -> int:
        return hash((self.module, self.qualname))
    
    def __repr__(self) -> str:
        return f"TypeKey({self.module}.{self.qualname})"

class TypeIndex(Generic[T]):
    """
    Type indexing system that's resilient to class redefinitions in Jupyter notebooks.
    """
    def __init__(self):
        self._type_index: Dict[TypeKey, Set[T]] = defaultdict(set)
        self._dirty = True
        self._objects: Set[T] = set()
        
    def _get_type_keys(self, obj: T) -> Set[TypeKey]:
        """Get TypeKeys for all types in an object's MRO"""
        return {TypeKey(base) for base in type(obj).__mro__[:-1]}  # Exclude 'object'
    
    def _get_type_key(self, typ: Type) -> TypeKey:
        """Convert a type to its TypeKey"""
        return TypeKey(typ)

    def add(self, obj: T) -> None:
        """Add an object to the index"""
        self._objects.add(obj)
        self._dirty = True

    def remove(self, obj: T) -> None:
        """Remove an object from the index"""
        self._objects.discard(obj)
        self._dirty = True

    def clear(self) -> None:
        """Clear the entire index"""
        self._objects.clear()
        self._type_index.clear()
        self._dirty = True

    def _ensure_index(self) -> None:
        """Rebuild type index if dirty"""
        if self._dirty:
            self._type_index.clear()
            for obj in self._objects:
                # Index object under each of its type keys
                for type_key in self._get_type_keys(obj):
                    self._type_index[type_key].add(obj)
            self._dirty = False

    def get_by_type(self, type_: Type[T]) -> Set[T]:
        """Get all objects of the specified type (including subclasses)"""
        self._ensure_index()
        return self._type_index[self._get_type_key(type_)]

    def get_by_types_union(self, *types: Type[T]) -> Set[T]:
        """Get objects matching ANY of the given types"""
        self._ensure_index()
        result = set()
        for t in types:
            result.update(self._type_index[self._get_type_key(t)])
        return result

    def get_by_types_intersection(self, *types: Type[T]) -> Set[T]:
        """Get objects matching ALL of the given types"""
        if not types:
            return set()
        self._ensure_index()
        result = self._type_index[self._get_type_key(types[0])].copy()
        for t in types[1:]:
            result.intersection_update(self._type_index[self._get_type_key(t)])
        return result

    def get_all(self) -> Set[T]:
        """Get all indexed objects"""
        return self._objects.copy()
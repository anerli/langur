from typing import Any, Callable, Dict, Type

from pydantic import BaseModel


def create_dynamic_model(
    model_name: str,
    fields_dict: Dict[str, tuple[Type, Any]],
    methods_dict: Dict[str, Callable] = None,
    base_class: Type[BaseModel] = BaseModel
) -> Type[BaseModel]:
    annotations = {}
    defaults = {}
    
    for field_name, (field_type, default_value) in fields_dict.items():
        annotations[field_name] = field_type
        if default_value is not None:
            defaults[field_name] = default_value

    namespace = {
        '__annotations__': annotations,
        **defaults
    }
    
    if methods_dict:
        namespace.update(methods_dict)
    
    dynamic_model = type(
        model_name,
        (base_class,),
        namespace
    )
    
    return dynamic_model


from dataclasses import dataclass
import inspect
from typing import Annotated, Any, Callable, Dict, Optional, get_args, get_origin
import typing

from pydantic import Field, PydanticSchemaGenerationError, TypeAdapter
from pydantic.fields import FieldInfo


# Based on ControlFlow's from_function implementation https://github.com/PrefectHQ/ControlFlow/blob/main/src/controlflow/tools/tools.py
@dataclass
class SchemaResult:
    name: str
    description: str
    json_schema: dict
    fields_dict: Dict[str, tuple[Any, FieldInfo]]

def schema_from_function(fn: Callable) -> SchemaResult:
    """
    Convert a function's signature to a Pydantic schema with Fields preserving descriptions.
    
    Args:
        fn: The function to analyze
        
    Returns:
        SchemaResult containing name, description, JSON schema and fields dictionary
    """
    name = fn.__name__
    description = fn.__doc__ or ""
    signature = inspect.signature(fn)
    
    try:
        json_schema = TypeAdapter(fn).json_schema()
    except PydanticSchemaGenerationError:
        raise ValueError(
            f'Could not generate a schema for tool "{name}". '
            "Tool functions must have type hints that are compatible with Pydantic."
        )
    
    # Create fields_dict with Field objects
    fields_dict = {}
    for param_name, param in signature.parameters.items():
        field_kwargs = {}
        
        # Handle default values
        if param.default is inspect.Parameter.empty:
            field_kwargs["default"] = ...
        else:
            # If it's already a Field, preserve its properties
            if isinstance(param.default, FieldInfo):
                field_kwargs.update({
                    "default": param.default.default,
                    "description": param.default.description,
                    "title": param.default.title,
                    "alias": param.default.alias,
                })
            else:
                field_kwargs["default"] = param.default
        
        # Handle type annotations and descriptions
        annotation_type = param.annotation
        param_description = None
        
        # Handle Annotated type hints
        if get_origin(param.annotation) is Annotated:
            args = get_args(param.annotation)
            annotation_type = args[0]
            # Join all annotation arguments as description
            param_description = " ".join(str(a) for a in args[1:])
        
        # Add description to field kwargs if found
        if param_description:
            field_kwargs["description"] = param_description
        elif param_name in json_schema.get("properties", {}) and "description" in json_schema["properties"][param_name]:
            field_kwargs["description"] = json_schema["properties"][param_name]["description"]
        
        # Create the Field with all gathered information
        fields_dict[param_name] = (annotation_type, Field(**field_kwargs))
    
    # Handle return type description
    if signature.return_annotation is not inspect._empty:
        return_schema = {}
        try:
            return_schema.update(
                TypeAdapter(signature.return_annotation).json_schema()
            )
        except PydanticSchemaGenerationError:
            pass
        
        if get_origin(signature.return_annotation) is Annotated:
            return_schema["description"] = " ".join(
                str(a) for a in get_args(signature.return_annotation)[1:]
            )
        
        if return_schema:
            description += f"\n\nReturn value schema: {return_schema}"
    
    if not description:
        print("WARNING: Actions without descriptions may not perform well, give functions a doc comment description to define them for the agent.")
        description = "(No description provided)"
    
    return SchemaResult(name, description, json_schema, fields_dict)
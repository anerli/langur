
from dataclasses import dataclass
import inspect
from typing import Annotated, Any, Callable, Dict, Optional, get_args, get_origin
import typing

from pydantic import Field, PydanticSchemaGenerationError, TypeAdapter
from pydantic.fields import FieldInfo

from langur.actions import ActionContext


@dataclass
class SchemaResult:
    name: str
    description: str
    json_schema: dict
    fields_dict: Dict[str, tuple[Any, FieldInfo]]
    is_async: bool

def schema_from_function(fn: Callable) -> SchemaResult:
    """
    Convert a function's signature to a Pydantic schema with Fields preserving descriptions.
    
    Any field matching the signature `ctx: ActionContext` is omitted from json_schema.
    Any field with the name `self` is omitted from json_schema and fields_dict.
   
    Args:
        fn: The function to analyze
       
    Returns:
        SchemaResult containing name, description, JSON schema and fields dictionary
    """
    name = fn.__name__
    description = fn.__doc__ or ""
    signature = inspect.signature(fn)
    is_async = inspect.iscoroutinefunction(fn)
    
    # Create a wrapper function without ActionContext parameters for schema generation
    def wrapper_fn(*args, **kwargs):
        return fn(*args, **kwargs)
    
    # Copy signature but exclude self and ActionContext parameters
    new_params = []
    for param_name, param in signature.parameters.items():
        # Skip self parameter
        if param_name == 'self':
            continue
            
        # Skip ActionContext parameters
        if not (get_origin(param.annotation) is Annotated and 
                any(isinstance(arg, type) and issubclass(arg, ActionContext) for arg in get_args(param.annotation)) or
                (isinstance(param.annotation, type) and issubclass(param.annotation, ActionContext))):
            new_params.append(param)
    
    wrapper_fn.__annotations__ = {param.name: param.annotation for param in new_params}
    wrapper_fn.__signature__ = signature.replace(parameters=new_params)
    wrapper_fn.__doc__ = fn.__doc__
    
    try:
        json_schema = TypeAdapter(wrapper_fn).json_schema()
    except PydanticSchemaGenerationError:
        raise ValueError(
            f'Could not generate a schema for tool "{name}". '
            "Tool functions must have type hints that are compatible with Pydantic."
        )
   
    # Create fields_dict with Field objects, including ALL original parameters except self
    fields_dict = {}
    for param_name, param in signature.parameters.items():
        # Skip self parameter for fields_dict too
        if param_name == 'self':
            continue
            
        field_kwargs = {}
       
        # Handle default values
        if param.default is inspect.Parameter.empty:
            field_kwargs["default"] = ...
        else:
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
       
        if get_origin(param.annotation) is Annotated:
            args = get_args(param.annotation)
            annotation_type = args[0]
            param_description = " ".join(str(a) for a in args[1:])
       
        # Add description to field kwargs if found
        if param_description:
            field_kwargs["description"] = param_description
        elif param_name in json_schema.get("properties", {}) and "description" in json_schema["properties"][param_name]:
            field_kwargs["description"] = json_schema["properties"][param_name]["description"]
       
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
   
    return SchemaResult(
        name=name,
        description=description,
        json_schema=json_schema,
        fields_dict=fields_dict,
        is_async=is_async
    )
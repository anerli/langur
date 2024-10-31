from abc import ABC
from typing import Any, Callable, ClassVar, Dict, Type

from pydantic import BaseModel, create_model
from langur.actions import ActionContext, ActionNode
from langur.connectors.connector_worker import ConnectorWorker
from langur.util.schema import schema_from_function
from langur.workers.worker import STATE_DONE

# https://docs.pydantic.dev/latest/concepts/models/#dynamic-model-creation
# def create_dynamic_model(
#     model_name: str,
#     fields_dict: Dict[str, tuple[Type, Any]],
#     methods_dict: Dict[str, Callable] = None,
#     base_class: Type[BaseModel] = BaseModel
# ) -> Type[BaseModel]:
#     """
#     Create a Pydantic model dynamically at runtime with custom methods.
    
#     Args:
#         model_name: Name for the dynamic model
#         fields_dict: Dictionary mapping field names to tuples of (type, default_value)
#         methods_dict: Dictionary mapping method names to function implementations
#         base_class: Optional base class to inherit from (defaults to BaseModel)
    
#     Returns:
#         A new Pydantic model class with custom methods
#     """
#     # Create the model first
#     dynamic_model = create_model(
#         model_name,
#         __base__=base_class,
#         **fields_dict
#     )
    
#     # Add methods to the model if provided
#     if methods_dict:
#         for method_name, method_impl in methods_dict.items():
#             setattr(dynamic_model, method_name, method_impl)
    
#     return dynamic_model
def create_dynamic_model(
    model_name: str,
    fields_dict: Dict[str, tuple[Type, Any]],
    methods_dict: Dict[str, Callable] = None,
    base_class: Type[BaseModel] = BaseModel
) -> Type[BaseModel]:
    """
    Create a Pydantic model dynamically at runtime with custom methods,
    properly overriding any existing methods from the base class.
    
    Args:
        model_name: Name for the dynamic model
        fields_dict: Dictionary mapping field names to tuples of (type, default_value)
        methods_dict: Dictionary mapping method names to function implementations
        base_class: Optional base class to inherit from (defaults to BaseModel)
    
    Returns:
        A new Pydantic model class with custom methods
    """
    # Convert fields_dict to annotations and defaults format
    annotations = {}
    defaults = {}
    
    for field_name, (field_type, default_value) in fields_dict.items():
        annotations[field_name] = field_type
        if default_value is not None:
            defaults[field_name] = default_value

    # Start with the namespace containing field defaults
    namespace = {
        '__annotations__': annotations,
        **defaults
    }
    
    # Add methods if provided
    if methods_dict:
        namespace.update(methods_dict)
    
    # Create the dynamic model
    dynamic_model = type(
        model_name,
        (base_class,),
        namespace
    )
    
    return dynamic_model


class Connector:
    def __init__(self, connector_name: str):
        '''
        High level system for generating ConnectorWorkers and ActionNodes from functions
        by extracting their attributes and dynamically creating corresponding pydantic models.
        '''
        self.connector_name = connector_name
        self.action_node_subtypes = []
    
    def action(self, fn: Callable[[Any], Any]):
        schema = schema_from_function(fn)

        print(schema.json_schema)
        print(schema.fields_dict)

        # TODO: Pass ctx to fn if param ctx: ActionContext found in fn def

        if "ctx" in schema.fields_dict and "ctx" not in schema.json_schema["properties"]:
            # This means the fn specifies ctx: ActionContext
            async def execute(self, ctx: ActionContext):
                return fn(ctx=ctx, **self.inputs)
        else:
            async def execute(self, ctx: ActionContext):
                return fn(**self.inputs)

        action_node_subtype = create_dynamic_model(
            schema.name,
            # TODO: modify action type iface to use full schema
            #parameters["properties"],
            {"definition": (ClassVar[str], schema.description), "input_schema": (ClassVar[dict[str, Any]], schema.json_schema["properties"])},#{**schema.fields_dict, },
            {"execute": execute},#{"say_hi": say_hi},
            ActionNode
        )
        self.action_node_subtypes.append(action_node_subtype)

    def to_worker_type(self) -> Type[ConnectorWorker]:
        return create_dynamic_model(
            self.connector_name,
            {"action_node_types": (ClassVar[list[Type[ActionNode]]], self.action_node_subtypes)},
            {},
            ConnectorWorker
        )
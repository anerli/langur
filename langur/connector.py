'''
General connector cognitive worker - binds real-world connectors to the Langur cognitive system.
'''

from abc import ABC
from typing import Any, Callable, ClassVar, Dict, List, Optional, Type

from pydantic import BaseModel
from langur.actions import ActionContext, ActionNode
from langur.graph.node import Node
from langur.util.schema import schema_from_function
from langur.util.model_builder import create_dynamic_model
from langur.workers.worker import STATE_DONE, STATE_SETUP, Worker
from langur.util.registries import action_node_type_registry


# def action(fn: Callable[[Any], Any]):
#     schema = schema_from_function(fn)

#     print(schema.json_schema)
#     print(schema.fields_dict)

#     if "ctx" in schema.fields_dict and "ctx" not in schema.json_schema["properties"]:
#         # This means the fn specifies ctx: ActionContext
#         async def execute(self, ctx: ActionContext):
#             result = fn(self=ctx.conn, ctx=ctx, **self.inputs)
#             return f"Executed action {schema.name} with inputs {self.inputs}, result:\n{result}"
#     else:
#         async def execute(self, ctx: ActionContext):
#             result = fn(self=ctx.conn, **self.inputs)
#             return f"Executed action {schema.name} with inputs {self.inputs}, result:\n{result}"

#     action_node_subtype = create_dynamic_model(
#         schema.name,
#         # TODO: modify action type iface to use full schema
#         #parameters["properties"],
#         {"definition": (ClassVar[str], schema.description), "input_schema": (ClassVar[dict[str, Any]], schema.json_schema["properties"])},#{**schema.fields_dict, },
#         {"execute": execute},#{"say_hi": say_hi},
#         ActionNode
#     )

#     # Identify class associated with this function
#     # TODO: handle if not part of class
#     connector_class_name = fn.__qualname__.split('.')[0]
#     action_node_type_registry.register(connector_class_name, action_node_subtype)

#     # Not actually doing anything to this function itself, just used it to generate the ActionNode type.
#     return fn

def action(
    fn: Optional[Callable] = None,
    tags: Optional[List[str]] = None,
    extra_context: Optional[Callable[[Any], str]] = None
):
    """
    Decorator that can be used either as @action or @action(kw1=...)
    """
    print("tags:", tags)
    tags = tags if tags else []
    def _register_model(func: Callable[[Any], Any]):
        schema = schema_from_function(func)
        print(schema.json_schema)
        print(schema.fields_dict)
        
        if "ctx" in schema.fields_dict and "ctx" not in schema.json_schema["properties"]:
            async def execute(self, ctx: ActionContext):
                result = func(self=ctx.conn, ctx=ctx, **self.inputs)
                return f"Executed action {schema.name} with inputs {self.inputs}, result:\n{result}"
        else:
            async def execute(self, ctx: ActionContext):
                result = func(self=ctx.conn, **self.inputs)
                return f"Executed action {schema.name} with inputs {self.inputs}, result:\n{result}"
        
        action_node_subtype = create_dynamic_model(
            schema.name,
            {
                "definition": (ClassVar[str], schema.description),
                "input_schema": (ClassVar[dict[str, Any]], schema.json_schema["properties"])
            },
            {"execute": execute},
            ActionNode
        )
        
        connector_class_name = func.__qualname__.split('.')[0]
        action_node_type_registry.register(
            connector_class_name=connector_class_name,
            action_cls=action_node_subtype,
            tags=tags
        )
        
        return func

    # Handle @action case
    if fn is not None:
        _register_model(fn)
        return fn
    # Handle @action(kw1=...) case  
    def decorator(func):
        _register_model(func)
        return func
    return decorator


class ConnectorOverview(Node):
    content: str

    tags: ClassVar[list[str]] = ["observable"]

    def observe(self) -> str:
        return self.content

class Connector(Worker, ABC):
    '''
    Generic Connector. Can subclass to implement own
    '''
    #action_node_types: ClassVar[list[Type[ActionNode]]]

    def overview(self) -> str | None:
        '''
        For connectors that have context that is helpful to have constantly available,
        can return it here. Try to keep this brief as it enters the context of many prompts.
        '''
        return None

    async def cycle(self):
        overview = self.overview()
        has_overview = overview is not None
        connector_overview_node_id = self.__class__.__name__

        if has_overview:
            # Every cycle, update the content of the overview node
            overview_node: ConnectorOverview = self.cg.query_node_by_id(connector_overview_node_id)
            if not overview_node:
                # If not exists, create it
                overview_node = ConnectorOverview(id=connector_overview_node_id, content=overview)
                self.cg.add_node(overview_node)
            overview_node.content = overview
        
        if self.state == STATE_SETUP:
            self.state = STATE_DONE

import random
import string
from typing import Dict, List, Literal, Optional, TypedDict, Union
from langur.baml_client.type_builder import TypeBuilder, FieldType

# Src: https://github.com/BoundaryML/berkeley-gorilla/blob/2db7841748ef3af9d365c206904002261844d9da/berkeley-function-call-leaderboard/model_handler/baml_handler.py

def random_name():
    return "".join(random.choices(string.ascii_lowercase, k=10))

class MapParameters(TypedDict):
    type: Literal["dict"]
    properties: Dict[str, Union["BaseParam", "ArrayParam", "MapParameters"]]
    required: Optional[List[str]]

class BaseParam(TypedDict):
    type: Literal["string", "integer", "boolean", "float"]
    description: str

class ArrayParam(BaseParam):
    type: Literal["array", "tuple"]
    items: Union["BaseParam", "ArrayParam", "MapParameters"]
    description: str

def get_type_base(p: MapParameters | BaseParam | ArrayParam, tb: TypeBuilder) -> FieldType:
    match p['type']:
        case "array":
            return get_type_base(p['items'], tb).list()    
        case "tuple":
            return get_type_base(p['items'], tb).list()     
        case "dict":
            if "properties" not in p:
                return tb.map(tb.string(), tb.string())
            else:
                c = tb.add_class(random_name())
                for name, param in p['properties'].items():
                    prop = c.add_property(name, get_type(param, tb, name in p["required"] if "required" in p else False))
                    if "description" in param:
                        desc = param['description']
                        if 'default' in param and param['default']:
                            desc += f". Default to '{param['default']}'"
                        prop.description(desc)
                return c.type()
        case "string":
            #print("STRING")
            # Possible for this to be an enum, so try that.
            if "enum" in p:
                enm = tb.add_enum(random_name())
                for value in p["enum"]:
                    enm.add_value(value)
                # We make all enums optional to enable smoother parsing
                return enm.type().optional()
            return tb.string()
        case "integer":
            #print("INTEGER")
            return tb.int()
        case "boolean":
            return tb.bool()
        case "double":
            return tb.float()
        case "float":
            return tb.float()
        case "any":
            return tb.string()
        case other:
            # print(f"Unknown type: {other} - {p}")
            return tb.string()
    raise UnsupportedType(p['type'])

def get_type(type: str, tb: TypeBuilder, required: bool):
    base = get_type_base(type, tb)
    if required:
        return base
    else:
        return base.optional()
from abc import ABC
from pydantic import BaseModel
from .jinja import jenv

class Template(BaseModel, ABC):
    def render(self) -> str:
        render_kwargs = dict(self)

        # Derive path from class name
        template_path = f"{self.__class__.__name__}.jinja"

        template = jenv.get_template(template_path)
        return template.render(**render_kwargs)

class Test(Template):
    name: str

class NodeGrow(Template):
    source_node_content: str
    existing_nodes: str
    existing_relations: str

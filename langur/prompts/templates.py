from abc import ABC
from pydantic import BaseModel
from .jinja import jenv

class Template(BaseModel, ABC):
    def render(self) -> str:
        render_kwargs = dict(self)

        # Derive path from class name
        template_path = f"{self.__class__.__name__}.jinja"

        template = jenv.get_template(template_path)
        print("Render kwargs:", render_kwargs)
        rendered_template = template.render(**render_kwargs)
        return rendered_template

class Test(Template):
    name: str

class NodeGrow(Template):
    source_node_content: str
    existing_nodes: str
    existing_relations: str

class BackSearch(Template):
    goal: str
    task: str
    graph_context: str

class FrontSearch(Template):
    goal: str
    graph_context: str
    intermediate_products: str

class Criteria(Template):
    goal: str
    graph_context: str

class Assumptions(Template):
    goal: str
    graph_context: str

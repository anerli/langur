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

class FrontSearch(Template):
    goal: str
    graph_context: str
    intermediate_products: str

class Assumptions(Template):
    goal: str
    graph_context: str

class Planner(Template):
    goal: str
    graph_context: str

class PlanAction(Template):
    goal: str
    graph_context: str
    # todo: actually use jinja features
    action_definition_node_ids: str
    task_node_ids: str

class TaskToActions(Template):
    goal: str
    observables: str
    task: str
    action_definitions: str
    upstream_tasks: str

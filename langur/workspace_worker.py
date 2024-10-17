import os
from fs.base import FS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from fs.walk import Walker
from pydantic import BaseModel

from langur.llm import FAST_LLM, SMART_LLM
from langur.prompts import templates
from .worker import Worker
from .graph import ActionDefinitionNode, ActionUseNode, Graph, Node, ObservableNode


class WorkspaceConnector(Worker):
    '''Manages cognitive relations between the nexus and filesystem actions'''

    def __init__(self, filesystem: FS | str = None):
        if isinstance(filesystem, str):
            if not os.path.exists(filesystem):
                os.mkdir(filesystem)
            filesystem = OSFS(filesystem)
        
        self.fs = filesystem if filesystem else MemoryFS()
    
    def overview(self) -> str:
        s = "The current working directory is `.`, which contains these files/subdirectories:\n"
        walker = Walker()
        file_list = []

        for path, directories, files in walker.walk(self.fs):
            for file_info in files:
                file_path = "." + os.path.join(path, file_info.name)
                unix_style_path = file_path.replace(os.sep, "/")
                file_list.append(unix_style_path)
        s += "\n".join(file_list)
        return s
    
    async def setup(self, graph: Graph):
        # Create nodes for workspace actions and dynamic workspace overview
        graph.add_node(
            ObservableNode("workspace", self.overview)
        )
        graph.add_node(
            ActionDefinitionNode(
                action_id="file_read",
                description="Read a single file's contents.",
                schema={"file_path": {"type": "string"}}
            )
        ),
        graph.add_node(
            ActionDefinitionNode(
                action_id="file_write",
                description="Read and subsequently overwrite a file's contents.",
                schema={"file_path": {"type": "string"}, "new_content": {"type": "string"}}
            )
        )
    
    async def cycle(self, graph: Graph):
        # TODO
        # ActionUse: node representing the use of an action
        # - edge from one ActionDefinition TO this node based on which action type it is
        # - edges FROM this node to tasks which are completed via this specific action occurence
        # - content: input payload, which contains fields that are either empty or pre-populated fields
        #     - pre-populated fields are fields which are not expected to change for this action use based on any runtime outcomes
        #     - empty fields are fields which should be populated at runtime by observing upstream tasks
        # - edges from TaskNodes TO this node where the inputs are dependent on task outcomes


        # Query graph for action definitions
        action_def_nodes: list[ActionDefinitionNode] = graph.query_nodes_by_tag("action_definition")
        # Schemas for each action definition
        action_schemas = [node.schema for node in action_def_nodes]

        action_node_schemas = []
        for input_schema in action_schemas:
            action_node_schemas.append({
                "type": "object",
                "properties": {
                    "node_id": {"type": "string"},
                    "action_definition_node_id": {"type": "string"},
                    "action_input": {
                        "type": "object",
                        "properties": input_schema
                        # no "required" array so inputs optional
                    },
                    "downstream_dependent_task_ids": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "upstream_dependency_task_ids": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                },
                "required": ["node_id", "action_definition_node_id", "action_input", "downstream_dependent_task_ids", "upstream_dependency_task_ids"]
            })

        schema = {
            "title": "action_use_response",
            "description": "Generate ActionUse nodes and edges",
            "type": "object",
            "properties": {
                "action_uses": {
                    "type": "array",
                    "items": {
                        "oneOf": action_node_schemas
                    }
                },
                # "edges": {
                #     "type": "array",
                #     "items": {
                #         "type": "object",
                #         "properties": {
                #             "from_id": {"type": "string"},
                #             "to_id": {"type": "string"}
                #         },
                #         "required": ["from_id", "to_id"]
                #     }
                # }
            },
            "required": ["action_uses"]#, "edges"]
        }

        context = graph.build_context()
        
        prompt = templates.PlanAction(
            goal=graph.goal,
            graph_context=context,
            action_definition_node_ids="\n".join([node.id for node in graph.query_nodes_by_tag("action_definition")]),
            task_node_ids="\n".join([node.id for node in graph.query_nodes_by_tag("task")]),
        ).render()

        print("Action connection prompt:", prompt, sep="\n")

        resp = await FAST_LLM.with_structured_output(schema).ainvoke(prompt)

        print(resp)

        # Build action use nodes
        for item in resp["action_uses"]:
            node_id = item["node_id"]
            node = ActionUseNode(node_id, item["action_input"])
            action_def_id = item["action_definition_node_id"]
            downstream_task_ids = item["downstream_dependent_task_ids"]
            upstream_task_ids = item["upstream_dependency_task_ids"]

            graph.add_node(node)

            graph.add_edge_by_ids(action_def_id, "definition", node_id)
            for task_id in downstream_task_ids:
                graph.add_edge_by_ids(node_id, "helps complete", task_id)
            for task_id in upstream_task_ids:
                graph.add_edge_by_ids(task_id, "required for", node_id)
        
        # for item in resp["edges"]:
        #     # todo: relation could be either input dependency, or action task resolve, ...
        #     # maybe separate edges in structured out
        #     # or maybe should be separate prompts/workers
        #     graph.add_edge_by_ids(item["from_id"], "action", item["to_id"])

        # # Build subgraph, todo: could create utils for creating subgraph as structured out
        # for item in resp.nodes:
        #     graph.add_node(TaskNode(item.id, item.content))
        # for item in resp.edges:
        #     graph.add_edge_by_ids(item.from_id, "dependency", item.to_id)

import asyncio
import json
import os
from fs.base import FS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from fs.walk import Walker
from pydantic import BaseModel

from langur.llm import FAST_LLM, SMART_LLM
from langur.prompts import templates
from .worker import Worker
from .graph import ActionDefinitionNode, ActionUseNode, Graph, Node, ObservableNode, TaskNode


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
        graph.add_node(
            ActionDefinitionNode(
                action_id="think",
                description="Do purely cognitive processing.",
                schema={}
            )
        )
    
    async def task_to_actions(self, graph: Graph, task_node: TaskNode):
        

        # Query graph for action definitions
        action_def_nodes: list[ActionDefinitionNode] = graph.query_nodes_by_tag("action_definition")
        # Schemas for each action definition
        #action_schemas = [node.schema for node in action_def_nodes]

        action_schemas = []
        for node in action_def_nodes:
            modified_param_schemas = {}
            for param, param_schema in node.schema.items():
                modified_param_schemas[param] = param_schema
                # nevermind, maybe it does work without dummy? idk mini doesn't listen to this modified schema anyway
                # modified_param_schemas[param] = {
                #     "oneOf": [
                #         param_schema,
                #         #{"type": "object", "properties": {"dummy": {"type": "string", "description": "Describe how this input should be filled in later."}}}
                #         {"type": "string", "const": "DEPENDS"}
                #     ]
                # }
            action_schemas.append(modified_param_schemas)
            # action_schemas.append({
            #     "oneOf": [
            #         node.schema,

            #     ]
            # })

        action_node_schemas = []
        for input_schema in action_schemas:
            action_node_schemas.append({
                "type": "object",
                "properties": {
                    #"thoughts": {"type": "string", "description": "Think about how to build this node and what inputs to populate now or leave out."},
                    "node_id": {"type": "string", "description": "UNIQUE node ID. DO NOT reuse any IDs you have seen before."},
                    "action_type": {"type": "string"},
                    # "inputs_included": {
                    #     "oneOf": [
                    #         {"type": "string", "constant": "FULL"},
                    #         {"type": "string", "constant": "PARTIAL"},
                    #         {"type": "string", "constant": "NONE"},
                    #     ],
                    #     "description": "Whether all action inputs are being provided or only some if they are to be populated later."
                    # },
                    "action_input": {
                        "type": "object",
                        "properties": input_schema,
                        "description": "Input for the action. For each parameter, include it if known right now, otherwise omit it completely."#, otherwise put \"DEPENDS\"."
                        # no "required" array so inputs optional
                    },
                    "upstream_action_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["node_id", "action_type", "action_input", "upstream_action_ids"]
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
                }
            },
            "required": ["action_uses"]
        }

        #print(json.dumps(schema, indent=4))

        context = graph.build_context(
            *task_node.upstream_nodes(),
            *graph.query_nodes_by_tag("action_definition", "observable")
        )

        # Provide context only about action definitions suggested by Planner
        action_def_nodes = [graph.query_node_by_id(action_id) for action_id in task_node.action_types]
        
        prompt = templates.TaskToActions(
            goal=graph.goal,
            observables="\n".join([node.content() for node in graph.query_nodes_by_tag("observable")]),
            task=f"{task_node.id}: {task_node.content()}",
            action_definitions="\n".join([f"- {node.id}: {node.description}" for node in action_def_nodes]),
            #action_definitions="\n".join([f"- {node.id}: {node.description}" for node in graph.query_nodes_by_tag("action_definition")]),
            #action_definition_node_ids="\n".join([node.id for node in graph.query_nodes_by_tag("action_definition")]),
            # TODO: proper filter mechanism for node sets - make sure these upstream are Task nodes, but in less ugly/re-usable way
            #upstream_tasks="\n".join([f"- {node.id}: {node.content()}" for node in filter(lambda n: "task" in n.get_tags(), task_node.upstream_nodes())]),
            #upstream_actions="\n".join([f"{node.content()}" for node in filter(lambda n: "action" in n.get_tags(), task_node.upstream_nodes())]),
            # Because we start with upstream decomp, these should all be upstream deps
            #upstream_actions="\n".join([f"{node.content()}" for node in graph.query_nodes_by_tag("action")]),
            upstream_actions="\n".join([f"- {node.id}" for node in graph.query_nodes_by_tag("action")]),
        ).render()

        print("Action connection prompt:", prompt, sep="\n")

        resp = await graph.llm.with_structured_output(schema).ainvoke(prompt)
        #resp = await graph.llm.with_structured_output(schema, strict=True).ainvoke(prompt)

        print(resp)

        deduped_action_uses = []
        # Remove any nodes whose ID already exists - LLM likes to re-create upstream action nodes sometimes
        for item in resp["action_uses"]:
            existing = graph.query_node_by_id(item["node_id"])
            if item["node_id"] == task_node.id or existing is None:
                # We allow it to replace task node with action node with same ID
                deduped_action_uses.append(item)
            else:
                if "action" in existing.get_tags():
                    # Common LLM sillyness that we simply ignore since it hasn't seemed to indicate poor performance otherwise
                    print("Generated action node with existing ID ignored:", existing.id)
                else:
                    # This suggests some missing context with respect to other nodes in the graph, or a failure to create sufficiently descriptive or unique IDs.
                    raise RuntimeError("Generated action node with same ID as non-action node:", existing, item)

        # Build action use nodes
        action_use_nodes = []
        for item in deduped_action_uses:
            #item["node_id"] = f'{task_node.id}::{item["node_id"]}'
            node_id = item["node_id"]
            node = ActionUseNode(node_id, item["action_input"])#, item["thoughts"])
            action_use_nodes.append(node)
        
        # Substitute the task node for the action nodes, keeping incoming/outgoing edges
        graph.substitute(task_node.id, action_use_nodes, keep_incoming=False, keep_outgoing=True)

        # for item in deduped_action_uses:
        #     print("?", graph.query_node_by_id(item["node_id"]))

        # Add generated deps
        for item in deduped_action_uses:
            for upstream_id in item["upstream_action_ids"]:
                graph.add_edge_by_ids(upstream_id, "gen dep", item["node_id"])
        
        # for item in deduped_action_uses:
        #     print("?", graph.query_node_by_id(item["node_id"]))

        # Add definition edges once substitution is complete
        for item in deduped_action_uses:
            action_def_id = item["action_type"]
            graph.add_edge_by_ids(action_def_id, "definition", item["node_id"])


    async def cycle(self, graph: Graph):
        #task_nodes = [graph.query_node_by_id("grade_papers")]
        # TODO: should be filtering upstream/downstream to make sure only Task nodes
        task_nodes = set(filter(lambda node: node.id != "final_goal", graph.query_nodes_by_tag("task")))
        frontier = set(filter(lambda node: len(node.upstream_nodes()) == 0, task_nodes))

        while frontier:
            new_frontier = set()
            for task_node in frontier:
                # todo: parallel
                print("Converting to actions:", task_node)
                new_frontier = new_frontier.union(task_node.downstream_nodes())
                await self.task_to_actions(graph, task_node)
            goal_node = graph.query_node_by_id("final_goal")
            if goal_node in new_frontier:
                new_frontier.remove(goal_node)
            frontier = new_frontier
            
        # jobs = []
        # # Possibly some concurrent operations could be iffy on shared graph structure
        # for task_node in task_nodes:
        #     jobs.append(self.task_to_actions(graph, task_node))
        #     #await self.task_to_actions(graph, task_node)

        # for task_node in task_nodes:
        #     jobs.append(self.task_to_actions(graph, task_node))
        #     #await self.task_to_actions(graph, task_node)
        
        # await asyncio.gather(*jobs)


import asyncio
import os
from fs.base import FS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from fs.walk import Walker

from langur.baml_client.type_builder import TypeBuilder
from .worker import Worker
from ..graph import Graph, Node, ObservableNode
from ..actions import ActionDefinitionNode, ActionUseNode
import langur.baml_client as baml

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .subtask_planner import TaskNode

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
        tb = TypeBuilder()
        graph.add_node(
            ObservableNode("workspace", self.overview)
        )
        graph.add_node(
            ActionDefinitionNode(
                action_id="FILE_READ",
                description="Read a single file's contents.",
                schema={"file_path": tb.string()}
            )
        ),
        graph.add_node(
            ActionDefinitionNode(
                action_id="FILE_WRITE",
                description="Read and subsequently overwrite a file's contents.",
                schema={"file_path": tb.string(), "new_content": tb.string()}
            )
        )
        graph.add_node(
            ActionDefinitionNode(
                action_id="THINK",
                description="Do purely cognitive processing.",
                schema={}
            )
        )
    
    async def task_to_actions(self, graph: Graph, task_node: 'TaskNode'):
        # Query graph for action definitions
        action_def_nodes: list[ActionDefinitionNode] = graph.query_nodes_by_tag("action_definition")
    
        tb = TypeBuilder()
        action_input_types = []
        # Dynamically build action input types
        for action_def_node in action_def_nodes:
            action_def_name = action_def_node.id
            
            schema = action_def_node.schema

            builder = tb.add_class(action_def_name)
            for param, field_type in schema.items():
                # use field type from action def but make optional (any problems if double applied?)
                builder.add_property(param, field_type.optional())
            
            #builder.add_property("type")
            #tb.string().
            
            action_input_types.append(builder.type())

            # Alternative approach is add a literal type to input builder with node id - but right now cant add literals with tb?
            tb.ActionType.add_value(action_def_name).description(action_def_node.description)

        tb.Action.add_property("action_input", tb.union(action_input_types)).description("Provide inputs if known else null. Do not hallicinate values.")
        

        resp = await baml.b.TaskToActions(
            goal=graph.goal,
            observables="\n".join([node.content() for node in graph.query_nodes_by_tag("observable")]),
            task=f"{task_node.id}: {task_node.content()}",
            action_definitions="\n".join([f"- {node.id}: {node.description}" for node in action_def_nodes]),
            upstream_actions="\n".join([f"- {node.id}" for node in graph.query_nodes_by_tag("action")]),
            baml_options={
                "tb": tb,
                "client_registry": graph.cr
            }
        )

        print("T2A:", resp)

        deduped_action_uses = []
        # Remove any nodes whose ID already exists - LLM likes to re-create upstream action nodes sometimes
        for item in resp:#resp["action_uses"]:
            existing = graph.query_node_by_id(item.node_id)
            if item.node_id == task_node.id or existing is None:
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
            node_id = item.node_id
            node = ActionUseNode(node_id, item.action_input)#, item["thoughts"])
            action_use_nodes.append(node)
        
        # Substitute the task node for the action nodes, keeping incoming/outgoing edges
        graph.substitute(task_node.id, action_use_nodes, keep_incoming=False, keep_outgoing=True)

        # Add generated deps
        for item in deduped_action_uses:
            for upstream_id in item.upstream_action_ids:
                graph.add_edge_by_ids(upstream_id, "gen dep", item.node_id)

        # Add definition edges once substitution is complete
        for item in deduped_action_uses:
            action_def_id = item.action_type
            graph.add_edge_by_ids(action_def_id, "definition", item.node_id)


    async def cycle(self, graph: Graph):
        #task_nodes = [graph.query_node_by_id("grade_papers")]
        # TODO: should be filtering upstream/downstream to make sure only Task nodes
        task_nodes = set(filter(lambda node: node.id != "final_goal", graph.query_nodes_by_tag("task")))
        frontier = set(filter(lambda node: len(node.upstream_nodes()) == 0, task_nodes))

        while frontier:
            new_frontier = set()
            jobs = []
            for task_node in frontier:
                #print("Converting to actions:", task_node)
                new_frontier = new_frontier.union(task_node.downstream_nodes())
                jobs.append(self.task_to_actions(graph, task_node))
            await asyncio.gather(*jobs)
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


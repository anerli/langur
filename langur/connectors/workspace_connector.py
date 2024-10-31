from abc import abstractmethod
import asyncio
import os
from fs.base import FS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from fs.walk import Walker

from langur.baml_client.type_builder import TypeBuilder
from langur.connectors.connector_worker import ConnectorWorker
from ..workers.worker import STATE_DONE, STATE_SETUP, Worker
from ..graph.graph import CognitionGraph
from ..graph.node import Node
from ..actions import ActionNode

from typing import TYPE_CHECKING, Any, ClassVar, Type


# class WorkspaceOverviewNode(Node):
#     overview: str

#     # leaving this since something queries for it
#     tags = ["observable"]

#     def content(self):
#         return self.overview



class WorkspaceNode(Node):
    # Corresponding connector properties to reference
    # More automatic way to do this that's not insane?
    # Or a way to get the corresponding worker?
    # But having serialized references from nodes to workers seems odd?
    workspace_path: str

    def get_fs(self):
        return OSFS(self.workspace_path)


class WorkspaceOverviewNode(WorkspaceNode):
    id: str = "workspace"
    #overview: str

    # leaving this since something queries for it
    tags = ["observable"]

    def content(self):
        return self.overview()
    
    def overview(self) -> str:
        s = "The current working directory is `.`, which contains these files/subdirectories:\n"
        walker = Walker()
        file_list = []

        for path, directories, files in walker.walk(self.get_fs()):
            for file_info in files:
                file_path = "." + os.path.join(path, file_info.name)
                unix_style_path = file_path.replace(os.sep, "/")
                file_list.append(unix_style_path)
        s += "\n".join(file_list)
        return s

# class FileReadDefinitionNode(WorkspaceNode, ActionDefinitionNode):
#     id: str = "FILE_READ"
#     description: str = "Read a single file's contents."
#     params: list[str] = ["file_path"]

#     # This is NOT the high level API, so it doesn't have to be super pretty - will have an adapter
#     async def execute(self, params, context) -> str:
#         with self.get_fs().open(params["file_path"], "r") as f:
#             content = f.read()
#         return f"I read {params['file_path']}, it contains:\n```\n{content}\n```"

# class FileWriteDefinitionNode(WorkspaceNode, ActionDefinitionNode):
#     id: str = "FILE_WRITE"
#     description: str = "Overwrite a file's contents."
#     #description="Read and subsequently overwrite a file's contents."
#     params: list[str] = ["file_path", "new_content"]

    
    # async def execute(self, params, context) -> str:
    #     with self.get_fs().open(params["file_path"], "w") as f:
    #         f.write(params["new_content"])
    #     #return params["new_content"]
    #     return f"I overwrote {params['file_path']}, it now contains:\n```\n{params['new_content']}\n```"

# class ThinkDefinitionNode(ActionDefinitionNode):
#     id: str = "THINK"
#     description: str = "Do purely cognitive processing."
#     params: list[str] = []

#     async def execute(self, params, context) -> str:
#         # TODO: Not using the graph's client registry here so this uses fallback llm, which means its not properly configurable
#         return await baml.b.Think(context=context, description=self.description)



class FileReadNode(ActionNode):#WorkspaceNode,
    definition: ClassVar[str] = "Read a single file's contents."
    input_schema: ClassVar[dict[str, Any]] = {"file_path": {"type": "string"}}

    async def execute(self, conn: 'WorkspaceConnector', context: str) -> str:
        with conn.get_fs().open(self.inputs["file_path"], "r") as f:
            content = f.read()
        return f"I read {self.inputs['file_path']}, it contains:\n```\n{content}\n```"

class FileWriteNode(ActionNode):#WorkspaceNode,
    definition: ClassVar[str] = "Overwrite a single file's contents."
    input_schema: ClassVar[dict[str, Any]] = {"file_path": {"type": "string"}, "new_content": {"type": "string"}}

    def extra_context(self, conn: 'WorkspaceConnector', context: str):
        # We want the file to be read, since its being overwritten should be aware of previous content
        with conn.get_fs().open(self.inputs["file_path"], "r") as f:
            content = f.read()
        return f"I read {self.inputs['file_path']}, it contains:\n```\n{content}\n```"

    async def execute(self, conn: 'WorkspaceConnector', context: str) -> str:
        with conn.get_fs().open(self.inputs["file_path"], "w") as f:
            f.write(self.inputs["new_content"])
        return f"I overwrote {self.inputs['file_path']}, it now contains:\n```\n{self.inputs['new_content']}\n```"



# class ConnectorWorker(Worker):
#     @abstractmethod
#     def get_action_node_types(self) -> list[ActionNode]: ...

class WorkspaceConnector(ConnectorWorker):
    '''Manages cognitive relations between the nexus and filesystem actions'''
    workspace_path: str

    action_node_types: ClassVar[list[Type[ActionNode]]] = [FileReadNode, FileWriteNode]

    # def __init__(self, filesystem: FS | str = None):
    #     if isinstance(filesystem, str):
    #         if not os.path.exists(filesystem):
    #             os.mkdir(filesystem)
    #         filesystem = OSFS(filesystem)
        
    #     self.fs = filesystem if filesystem else MemoryFS()

    # def __init__(self, workspace_path: str):
    #     super().__init__(workspace_path=workspace_path)

    def get_fs(self):
        return OSFS(self.workspace_path)
    
    # def get_action_node_types(self) -> list[ActionNode]:
    #     return [FileReadNode, FileWriteNode, ThinkNode]
    
    
    async def cycle(self):
        if self.state == STATE_SETUP:
            # Create nodes for workspace actions and dynamic workspace overview
            # graph.add_node(
            #     WorkspaceOverviewNode(id="workspace", overview=self.overview())
            # )
            self.cg.add_node(
                WorkspaceOverviewNode(workspace_path=self.workspace_path)
            )
            #self.cg.add_node(FileReadDefinitionNode(workspace_path=self.workspace_path))
            #self.cg.add_node(FileWriteDefinitionNode(workspace_path=self.workspace_path))
            #self.cg.add_node(ThinkDefinitionNode(workspace_path=self.workspace_path))
            self.state = STATE_DONE

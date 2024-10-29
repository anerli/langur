import asyncio
import os
from fs.base import FS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from fs.walk import Walker

from langur.baml_client.type_builder import TypeBuilder
from .worker import STATE_DONE, STATE_SETUP, Worker
from ..graph.graph import Graph
from ..graph.node import Node
from ..actions import ActionDefinitionNode, ActionParameter, ActionNode
import langur.baml_client as baml

from typing import TYPE_CHECKING


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

class FileReadDefinitionNode(WorkspaceNode, ActionDefinitionNode):
    id: str = "FILE_READ"
    description: str = "Read a single file's contents."
    params: list[str] = ["file_path"]

    # todo: derive params from func signature
    # def execute(self, file_path: str) -> str:
    #     with self.get_fs().open(file_path, "r") as f:
    #         return f.read()

    # This is NOT the high level API, so it doesn't have to be super pretty - will have an adapter
    async def execute(self, params, context) -> str:
        with self.get_fs().open(params["file_path"], "r") as f:
            content = f.read()
        return f"I read {params['file_path']}, it contains:\n```\n{content}\n```"

class FileWriteDefinitionNode(WorkspaceNode, ActionDefinitionNode):
    id: str = "FILE_WRITE"
    description: str = "Overwrite a file's contents."
    #description="Read and subsequently overwrite a file's contents."
    params: list[str] = ["file_path", "new_content"]

    # todo: derive params from func signature
    # def execute(self, file_path: str, new_content: str) -> str:
    #     with self.get_fs().open(file_path, "w") as f:
    #         f.write(new_content)
    #     return new_content

    # def extra_context(self) -> str
    
    async def execute(self, params, context) -> str:
        with self.get_fs().open(params["file_path"], "w") as f:
            f.write(params["new_content"])
        #return params["new_content"]
        return f"I overwrote {params['file_path']}, it now contains:\n```\n{params['new_content']}\n```"

class ThinkDefinitionNode(ActionDefinitionNode):
    id: str = "THINK"
    description: str = "Do purely cognitive processing."
    params: list[str] = []

    # TOdo: uhh how do we get context in here?
    # prev pattern we had like world, memory
    # special context parameter?? or property? idkkkkkk
    async def execute(self, params, context) -> str:
        # TODO: Not using the graph's client registry here so this uses fallback llm, which means its not properly configurable
        return await baml.b.Think(context=context, description=self.description)
        #return ""

class WorkspaceConnector(Worker):
    '''Manages cognitive relations between the nexus and filesystem actions'''
    workspace_path: str

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
    
    
    
    async def cycle(self, graph: Graph):
        if self.state == STATE_SETUP:
            # Create nodes for workspace actions and dynamic workspace overview
            # graph.add_node(
            #     WorkspaceOverviewNode(id="workspace", overview=self.overview())
            # )
            graph.add_node(
                WorkspaceOverviewNode(workspace_path=self.workspace_path)
            )
            # graph.add_node(
            #     ActionDefinitionNode(
            #         id="FILE_READ",
            #         description="Read a single file's contents.",
            #         #schema={"file_path": tb.string()}
            #         #params=[ActionParameter("file_path", tb.string())]
            #         params=["file_path"]
            #     )
            # ),
            # graph.add_node(
            #     ActionDefinitionNode(
            #         id="FILE_WRITE",
            #         description="Read and subsequently overwrite a file's contents.",
            #         #schema={"file_path": tb.string(), "new_content": tb.string()}
            #         params=[
            #             #ActionParameter("file_path", tb.string()),
            #             #ActionParameter("new_content", tb.string(), "Content to replace existing")
            #             "file_path", "new_content"
            #         ]
            #     )
            # )
            # graph.add_node(
            #     ActionDefinitionNode(
            #         id="THINK",
            #         description="Do purely cognitive processing.",
            #         #schema={}
            #         params=[]
            #     )
            # )
            graph.add_node(FileReadDefinitionNode(workspace_path=self.workspace_path))
            graph.add_node(FileWriteDefinitionNode(workspace_path=self.workspace_path))
            graph.add_node(ThinkDefinitionNode(workspace_path=self.workspace_path))
            self.state = STATE_DONE

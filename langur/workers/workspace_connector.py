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


class WorkspaceOverviewNode(Node):
    overview: str

    # leaving this since something queries for it
    tags = ["observable"]

    def content(self):
        return self.overview

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
    
    async def cycle(self, graph: Graph):
        if self.state == STATE_SETUP:
            # Create nodes for workspace actions and dynamic workspace overview
            graph.add_node(
                WorkspaceOverviewNode(id="workspace", overview=self.overview())
            )
            graph.add_node(
                ActionDefinitionNode(
                    id="FILE_READ",
                    description="Read a single file's contents.",
                    #schema={"file_path": tb.string()}
                    #params=[ActionParameter("file_path", tb.string())]
                    params=["file_path"]
                )
            ),
            graph.add_node(
                ActionDefinitionNode(
                    id="FILE_WRITE",
                    description="Read and subsequently overwrite a file's contents.",
                    #schema={"file_path": tb.string(), "new_content": tb.string()}
                    params=[
                        #ActionParameter("file_path", tb.string()),
                        #ActionParameter("new_content", tb.string(), "Content to replace existing")
                        "file_path", "new_content"
                    ]
                )
            )
            graph.add_node(
                ActionDefinitionNode(
                    id="THINK",
                    description="Do purely cognitive processing.",
                    #schema={}
                    params=[]
                )
            )
            self.state = STATE_DONE

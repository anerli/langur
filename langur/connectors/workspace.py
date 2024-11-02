# Hypothetical ideal Workspace implementaiton
import os
from fs.base import FS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from fs.walk import Walker

from langur.actions import ActionContext
from langur.connectors.connector import Connector


# Ideal Workpace Implementation
class Workspace(Connector):
    path: str

    # Inherited available properties: cg

    def get_fs(self):
        return OSFS(self.path)
    
    def overview(self):
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

    @action
    def read_file(self, file_path: str, ctx: ActionContext):
        '''Read a single file's contents'''

    

    @action(extra_context=read_file)


# Usage
workspace = Workspace(path="./workspace")
# Hypothetical ideal Workspace implementaiton
import os
import subprocess
from fs.base import FS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from fs.walk import Walker
from pydantic import Field

from langur.actions import ActionContext
from langur.connector import Connector, action
from langur.util.registries import ActionNodeRegistryFilter

def run_python_script(file_path):
    try:
        result = subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr


class Workspace(Connector):
    '''
    path: Path to workspace directory.
    '''
    path: str

    # By default, include read/write options but not code execution
    action_filter: ActionNodeRegistryFilter = Field(default_factory=lambda: ActionNodeRegistryFilter(
        disabled_tags=["exec"]
    ))

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

    @action(tags=["read"])
    def read_file(self, file_path: str):#, ctx: ActionContext
        '''Read a single file's contents'''
        with self.get_fs().open(file_path, "r") as f:
            content = f.read()
        return f"I read {file_path}, it contains:\n```\n{content}\n```"

    def write_file_extra_context(self, file_path: str = None, new_content: str = None) -> str:
        '''
        Since the write file operation overwrites a file, if it has existing content, it should know about it
        before deciding any new content.
        '''
        if file_path:
            if self.get_fs().exists(file_path):
                return self.read_file(file_path)
            else:
                return f"{file_path} is currently empty."

    @action(tags=["write"], extra_context=write_file_extra_context)
    def write_file(self, file_path: str, new_content: str):
        with self.get_fs().open(file_path, "w") as f:
            f.write(new_content)
        return f"I overwrote {file_path}, it now contains:\n```\n{new_content}\n```"

    @action(tags=["exec"])
    def run_python_file(self, file_path: str):
        base_path = os.path.abspath(self.path)
        script_path = os.path.abspath(os.path.join(self.path, file_path))

        # Ensure the resolved path is within the base directory
        if not script_path.startswith(base_path):
            raise ValueError("Access to files outside workspace directory is not allowed")

        stdout, stderr = run_python_script(script_path)
        return f"I ran the script {file_path}.\nstdout:\n```\n{stdout}\n```\nstderr:\n```\n{stderr}\n```"

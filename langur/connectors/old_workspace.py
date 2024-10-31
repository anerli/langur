import os
import subprocess
from fs.base import FS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from fs.walk import Walker
from synthcog.commands.command import Command
from synthcog.world import World
from .connector_worker import ConnectorWorker, connected



class Workspace(ConnectorWorker):
    def __init__(self, filesystem: FS | str = None):
        if isinstance(filesystem, str):
            # assume string path for OSFS, also make dir if not exists
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
                # Adding "." so that we present it as being like a working directory for the LLM
                file_path = "." + os.path.join(path, file_info.name)
                unix_style_path = file_path.replace(os.sep, "/")
                # Not using path.join cus want unix-style slashes for consistency
                #file_path = "." + "/".join([path, file_info.name])
                file_list.append(unix_style_path)
        s += "\n".join(file_list)
        return s

@connected(Workspace)
class FileRead(Command):
    input_schema = {"file_path": {"type": "string"}}
    description = "Read a single file's contents."

    def execute(self, world: World):
        ws: Workspace = world.query_connector(Workspace)

        file_path = self.inputs["file_path"]

        with ws.fs.open(file_path) as f:
            file_content = f.read()
        
        return f"The file {file_path} contains:\n```\n{file_content}\n```"

@connected(Workspace)
class FileWrite(Command):
    input_schema = {"file_path": {"type": "string"}, "new_content": {"type": "string"}}
    description = "Read and subsequently overwrite a file's contents."

    @classmethod
    def get_construction_context(cls, partial_inputs: dict, world: World) -> str:
        if "file_path" not in partial_inputs:
            # If file_path isn't at least provided, no additional context to add
            return ""
        # PROBLEM: Need file_path parameter in this case
        file_path = partial_inputs["file_path"]
        # Return the content of existing file
        ws: Workspace = world.query_connector(Workspace)
        with ws.fs.open(file_path) as f:
            existing_file_content = f.read()
        return f"Existing file {file_path} contains:\n```\n{existing_file_content}\n```"

    def execute(self, world: World):
        ws: Workspace = world.query_connector(Workspace)
        file_path = self.inputs["file_path"]
        new_content = self.inputs["new_content"]

        with ws.fs.open(file_path, 'w') as f:
            f.write(new_content)
        
        return f"The file {file_path} now contains:\n```\n{new_content}\n```"


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



# # TODO: Make this optional / not included by default when using Workspace connector
# @connected(Workspace)
# class RunPythonCode(Command):
#     input_schema = {"file_path": {"type": "string"}}
#     description = "Run a python file and observe the stdout."

#     def execute(self, world: World):
#         ws: Workspace = world.query_connector(Workspace)
#         file_path = self.inputs["file_path"]

#         stdout, stderr = run_python_script(os.path.join(ws.fs.root_path, file_path))

#         return f"Ran Python file: {file_path}\nSTDOUT:{stdout}\nSTDERR:{stderr}"
        


        
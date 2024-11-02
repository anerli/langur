# import os
# import subprocess
# from typing import Any, ClassVar, Type
# from langur.actions import ActionContext, ActionNode
# from langur.connectors.connector_worker import ConnectorWorker
# from langur.connectors.workspace_connector import WorkspaceOverviewNode
# from langur.workers.worker import STATE_DONE, STATE_SETUP

# def run_python_script(file_path):
#     try:
#         result = subprocess.run(
#             ["python", file_path],
#             capture_output=True,
#             text=True,
#             check=True
#         )
#         return result.stdout, result.stderr
#     except subprocess.CalledProcessError as e:
#         return e.stdout, e.stderr

# class RunCode(ActionNode):
#     definition: ClassVar[str] = "Run a python script and observe the stdout."
#     input_schema: ClassVar[dict[str, Any]] = {"file_path": {"type": "string"}}

#     async def execute(self, ctx: ActionContext) -> str:
#         stdout, stderr = run_python_script(os.path.join(ctx.conn.workspace_path, self.inputs["file_path"]))
#         return f"I ran the script {self.inputs['file_path']}.\nstdout:\n```\n{stdout}\n```\nstderr:\n```\n{stderr}\n```"

# # TODO: Merge with Workspace - provide options to select what actions are available.
# # TODO: Ensure only files withing workspace are targeted
# # FIXME: If no Workspace connector exists with same workspace_path, no WorkspaceOverviewNode exists!
# class CodeRunner(ConnectorWorker):
#     '''Manages cognitive relations between the nexus and filesystem actions'''
#     workspace_path: str

#     action_node_types: ClassVar[list[Type[ActionNode]]] = [RunCode]

#     async def cycle(self):
#         if self.state == STATE_SETUP:
#             # Hack in case there is no Workspace
#             # TODO: Support multiple workspace overview nodes - prompt phrasing needs to change from CWD . approach
#             if not self.cg.query_nodes_by_type(WorkspaceOverviewNode):
#                 self.cg.add_node(
#                     WorkspaceOverviewNode(workspace_path=self.workspace_path)
#                 )
#             self.state = STATE_DONE

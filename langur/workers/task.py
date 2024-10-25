from typing import ClassVar
from langur.graph.graph import Graph
from langur.graph.node import Node
from langur.workers.worker import Worker

class TaskNode(Node):
    tags: ClassVar[list[str]] = ["task"]

    task: str
    #action_types: list[str]
    
    def content(self):
        return f"{self.task} {self.action_types}"

class TaskWorker(Worker):
    task: str
    node_id: str

    def __init__(self, task: str, node_id: str):
        super().__init__(task=task, node_id=node_id)

    async def setup(self, graph: Graph):
        task_node = TaskNode(id=self.node_id, task=self.task)
        graph.add_node(task_node)
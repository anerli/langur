from typing import ClassVar
from langur.graph.node import Node
from langur.workers.worker import STATE_DONE, STATE_SETUP, Worker

class TaskNode(Node):
    tags: ClassVar[list[str]] = ["task"]

    task: str
    #action_types: list[str]
    
    def content(self):
        return f"{self.task} {self.action_types}"

class TaskWorker(Worker):
    task: str
    node_id: str
    # def __init__(self, task: str, node_id: str):
    #     super().__init__(task=task, node_id=node_id)

    async def cycle(self):
        if self.state == STATE_SETUP:
            task_node = TaskNode(id=self.node_id, task=self.task)
            self.cg.add_node(task_node)
            self.state = STATE_DONE
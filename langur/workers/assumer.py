#from langur.connectors.connector_worker import ConnectorWorker
import asyncio
from langur.graph.node import Node
from langur.workers.task import TaskNode, TaskWorker
from langur.workers.worker import STATE_DONE, STATE_SETUP, Worker
import langur.baml_client as baml


class Assumption(Node):
    assumption: str
    # TODO: Inherit from some ObservableNode instead with an abstract observe() -> str or something
    tags = ["observable"]

    def overview(self) -> str:
        return self.assumption

class AssumptionWorker(Worker):
    state: str = "WAITING_FOR_TASKS"

    async def create_assumptions(self, task_node: TaskNode):
        #print("CREATING ASSUMPTION FOR:", task_node)
        result = await baml.b.CreateAssumptions(
            task=task_node.task,
            # TODO: maybe create a util on CG for this common observable context pattern
            observables="\n".join([node.observe() for node in self.cg.query_nodes_by_tag("observable")]),
            baml_options={"client_registry": self.cg.get_client_registry()}
        )
        #print(result)
        for assumption in result:
            self.cg.add_node(
                Assumption(id=assumption.assumption_id, assumption=assumption.assumption)
            )

    async def create_all_assumptions(self):
        task_nodes = self.cg.query_nodes_by_type(TaskNode)
        await asyncio.gather(*[self.create_assumptions(task_node) for task_node in task_nodes])
    
    async def cycle(self):
        if self.state == "WAITING_FOR_TASKS":
            if self.cg.worker_count(worker_type=TaskWorker, state=STATE_DONE) == self.cg.worker_count(worker_type=TaskWorker):
                await self.create_all_assumptions()
                self.state = STATE_DONE

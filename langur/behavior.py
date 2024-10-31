'''
High level wrapper essentially defining the cognitive workers to use for an agent.
'''

from abc import ABC, abstractmethod
from langur.workers.executor import ExecutorWorker
from langur.workers.planner import PlannerWorker
from langur.workers.task import TaskWorker
from langur.workers.worker import Worker

#class BehaviorParam<T>:


class AgentBehavior:
    def __init__(self, *behaviors: 'BaseBehavior'):
        self.behaviors = behaviors
        self.task_counter = 0

    def compile(self) -> list[Worker]:
        # Compile behaviors into usable cognitive workers
        workers = []
        for behavior in self.behaviors:
            workers.extend(behavior.compile(self))
        return workers

# class AgentBehaviorTemplate:
#     def __init__(self, behavior: )

class BaseBehavior(ABC):
    @abstractmethod
    def compile(self) -> list[Worker]: ...

class Task(BaseBehavior):
    def __init__(self, task: str):
        self.task = task
    
    def compile(self, behavior: 'AgentBehavior'):
        behavior.task_counter += 1
        return [TaskWorker(task=self.task, node_id=f"goal_{behavior.task_counter}")]

class Plan(BaseBehavior):
    '''
    Plans out the execution of given tasks.
    '''
    def __init__(self, *tasks: Task):
        self.tasks: list[Task] = tasks
    
    def compile(self, behavior: 'AgentBehavior'):
        task_workers = []
        for task in self.tasks:
            task_workers.extend(task.compile(behavior))
        
        planner_workers = [PlannerWorker(task_node_id=task_worker.node_id) for task_worker in task_workers]
        
        return [
            *task_workers,
            *planner_workers,
        ]


class Execute(BaseBehavior):
    '''
    Executes any established plans.

    TODO: Option to execute specific plans.
    '''
    # def __init__(self, *plans: Plan):
    #     self.plans: list[Plan] = plans
    
    def compile(self, behavior: 'AgentBehavior'):
        return [ExecutorWorker()]
        # nested_workers = []
        # for plan in self.plans:
        #     nested_workers.extend(plan.compile())
        
        # TODO: if we needed to filter for a certain type of worker, this pattern will stop working if we have different nested layers w same type of node
        # - might want to retain the heirarchy in returned workers on compilation instead of flattening completely
        #planner_workers = [PlannerWorker(task_node_id=task_worker.node_id) for task_worker in task_workers]
        #exec_worker = ExecutorWorker(...)
        # TODO: implement once we have executor worker
        #return nested_workers

class Assume(BaseBehavior):
    # TODO: implement once have assumption worker
    pass


# # TODO: allow some templating system here, e.g. default behavior here allows some kwarg "goal" which feeds into the Task's task param
# DEFAULT_AGENT_BEHAVIOR = lambda goal: AgentBehavior(
#     Execute(Plan(Task(goal)))
# )
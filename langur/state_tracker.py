from collections import defaultdict


class StateTracker:
    def __init__(self):
        '''
        State / Events system is a WIP
        '''
        self.clear()

    def clear(self):
        self.worker_states = defaultdict(lambda: defaultdict(int))
        self.worker_counts = defaultdict(int)

    def update(self, worker_type: str, state: str):
        self.worker_states[worker_type][state] += 1
        self.worker_counts[worker_type] += 1
    
    def generate_events(self) -> set[str]:
        # Generates derived events based on cached states - e.g. if all workers of a certain type are done
        events = set()
        for worker_type in self.worker_counts.keys():
            total = self.worker_counts[worker_type]
            for state, count in self.worker_states[worker_type].items():
                if count == total:
                    events.add(
                        f"{worker_type}.all.{state}"
                    )
        return events
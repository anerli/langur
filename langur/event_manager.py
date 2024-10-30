# class Emitter:
#     def __init__(self, emitter_id, emitter_type: str

class EventManager():
    def __init__(self):
        self.emitters = {}

    def register_emitter(self, emitter_id: str, emitter_type: str):
        self.emitters[emitter_id] = {"id": emitter_id, "type": emitter_type}

    def emit(self, emitter_id: str, event: str):
        '''
        emitter_id: ID of actor emitting the event, e.g. Worker ID
        event: 

        Example events look like:
        planner.done
        worker.done
        '''
    
    def collect(self):
        '''
        Collect all events since last collection.
        Includes derived events, for example when all planners have emitted done, planner.all.done
        '''
        pass
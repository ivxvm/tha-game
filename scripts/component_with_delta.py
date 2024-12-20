import bge

class ComponentWithDelta(bge.types.KX_PythonComponent):
    def start(self, args):
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        timestamp = bge.logic.getClockTime()
        delta = timestamp - self.prev_frame_timestamp
        self.update_with_delta(delta)
        self.prev_frame_timestamp = timestamp

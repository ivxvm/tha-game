import bge, bpy, math
from collections import OrderedDict
from mathutils import Vector

class MotionSine(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Direction", [0.0, 0.0, 1.0]),
        ("Duration", 5.0),
        ("Phase", 0.0),
    ])

    def start(self, args):
        self.direction = Vector(args["Direction"])
        self.duration = args["Duration"]
        self.phase = args["Phase"]
        self.paused = False
        self.elapsed = 0.0
        self.initial_position = self.object.worldPosition.copy()
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        if self.paused:
            return
        timestamp = bge.logic.getClockTime()
        delta = timestamp - self.prev_frame_timestamp
        self.elapsed += delta
        progress = self.elapsed / self.duration
        new_position = self.initial_position + self.direction * math.sin(self.phase + progress * 2 * math.pi)
        self.object.blenderObject.location = new_position
        self.object.worldPosition = new_position
        self.prev_frame_timestamp = timestamp

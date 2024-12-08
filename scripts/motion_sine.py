import math
import bge
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
        self.elapsed = 0.0
        self.initial_position = self.object.worldPosition.copy()
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        timestamp = bge.logic.getClockTime()
        delta = timestamp - self.prev_frame_timestamp
        self.elapsed += delta
        progress = self.elapsed / self.duration
        self.object.worldPosition = self.initial_position + self.direction * math.sin(self.phase + progress * 2 * math.pi)
        self.prev_frame_timestamp = timestamp

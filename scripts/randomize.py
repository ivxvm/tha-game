import bge
import random
from collections import OrderedDict
from mathutils import Vector

class RandomizeRotation(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Axes", [1.0, 1.0, 1.0]),
        ("Rotation Speed", 0.1),
        ("Direction Change Speed", 1.0),
    ])

    def start(self, args):
        self.rotation_direction = Vector(args["Axes"])
        self.rotation_speed = args["Rotation Speed"]
        self.direction_change_speed = args["Direction Change Speed"]
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        now = bge.logic.getClockTime()
        delta = now - self.prev_frame_timestamp
        for i in range(0, 3):
            self.rotation_direction[i] += random.uniform(-1, 1) * self.direction_change_speed
        self.rotation_direction.normalize()
        self.object.applyRotation(self.rotation_direction * self.rotation_speed * delta, True)
        self.prev_frame_timestamp = now

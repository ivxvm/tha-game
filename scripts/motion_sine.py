import bge, math, deltatime
from collections import OrderedDict
from mathutils import Vector

class MotionSine(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Direction", [0.0, 0.0, 1.0]),
        ("Duration", 5.0),
        ("Phase", 0.0),
        ("Compound Motion", False),
    ])

    def start(self, args):
        self.direction = Vector(args["Direction"])
        self.duration = args["Duration"]
        self.phase = args["Phase"]
        self.compound_motion = args.get("Compound Motion", False)
        self.paused = False
        self.elapsed = 0.0
        self.initial_position = self.object.worldPosition.copy()
        self.last_computed_position = self.initial_position
        deltatime.init(self)

    def update(self):
        if self.paused:
            return
        delta = deltatime.update(self)
        if self.compound_motion and self.object.worldPosition != self.last_computed_position:
            self.initial_position = self.object.worldPosition.copy()
        self.elapsed += delta
        progress = self.elapsed / self.duration
        new_position = self.initial_position + self.direction * math.sin(self.phase + progress * 2 * math.pi)
        self.object.blenderObject.location = new_position
        self.object.worldPosition = new_position
        self.last_computed_position = new_position

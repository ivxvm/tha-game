import math
import bge
from collections import OrderedDict

class SineMovement(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
        ("Speed", 0.5),
        ("Target", ""),
    ])

    def start(self, args):
        self.speed = args["Speed"]
        self.startPosition = self.object.worldPosition
        self.endPosition = self.object.scene.objects[args["Target"]].worldPosition
        self.midPosition = (self.startPosition + self.endPosition) / 2
        self.direction = self.endPosition - self.startPosition
        self.distance = self.direction.length / 2
        self.direction.normalize()
        self.object.worldPosition = self.midPosition

    def update(self):
        self.object.worldPosition = self.midPosition + self.direction * self.distance * math.sin(self.speed * bge.logic.getClockTime())

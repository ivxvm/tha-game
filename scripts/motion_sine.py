import math
import bge
from collections import OrderedDict

class SineMovement(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Speed", 0.5),
        ("Target", ""),
    ])

    def start(self, args):
        self.speed = args["Speed"]
        startPosition = self.object.worldPosition
        endPosition = self.object.scene.objects[args["Target"]].worldPosition
        self.midPosition = (startPosition + endPosition) / 2
        self.direction = endPosition - startPosition
        self.distance = self.direction.length / 2
        self.direction.normalize()
        self.object.worldPosition = self.midPosition

    def update(self):
        self.object.worldPosition = self.midPosition + self.direction * self.distance * math.sin(self.speed * bge.logic.getClockTime())

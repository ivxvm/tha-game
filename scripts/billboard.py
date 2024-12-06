import bge
from mathutils import Vector
from collections import OrderedDict

AXIS_X = Vector([1.0, 0.0, 0.0])

class Billboard(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Track To", "")
    ])

    def start(self, args):
        self.track_to = self.object.scene.objects[args["Track To"]]

    def update(self):
        self.object.alignAxisToVect(self.track_to.getAxisVect(AXIS_X), 0)
        self.object.alignAxisToVect(self.track_to.worldPosition - self.object.worldPosition)

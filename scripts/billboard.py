import bge, bpy, constants
from collections import OrderedDict

class Billboard(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Track To", bpy.types.Object),
    ])

    def start(self, args):
        self.track_to = self.object.scene.objects[args["Track To"].name]

    def update(self):
        self.object.alignAxisToVect(self.track_to.getAxisVect(constants.AXIS_X), 0)
        self.object.alignAxisToVect(self.track_to.worldPosition - self.object.worldPosition)

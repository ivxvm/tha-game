import bge, bpy
from collections import OrderedDict

class CopyVisibility(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Copy From", bpy.types.Object)
    ])

    def start(self, args):
        self.copy_from = self.object.scene.objects[args["Copy From"].name]

    def update(self):
        if self.copy_from.visible != self.object.visible:
            self.object.visible = self.copy_from.visible

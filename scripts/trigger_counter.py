import bge, bpy
from collections import OrderedDict

class TriggerCounter(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Count To", 1),
        ("Target Object", bpy.types.Object)
    ])

    def start(self, args):
        self.count_to = args["Count To"]
        self.target_object = self.object.scene.objects[args["Target Object"].name]
        self.count = 0

    def update(self):
        pass

    def trigger(self):
        self.count += 1
        if self.count >= self.count_to:
            for component in self.target_object.components:
                try:
                    component.trigger()
                except AttributeError:
                    pass

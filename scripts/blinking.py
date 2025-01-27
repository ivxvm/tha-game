import bge, bpy, deltatime
from collections import OrderedDict

BLINKING_TRANSPARENCY = 0.5

class Blinking(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Target", bpy.types.Object),
        ("Blinking Duration", 4.0),
        ("Blinking Period", 0.25),
    ])

    def start(self, args):
        self.blinking_duration = args["Blinking Duration"]
        self.blinking_period = args["Blinking Period"]
        self.target = self.object.scene.objects[args["Target"].name]
        self.target_material = self.target.blenderObject.data.materials[0]
        self.blinking_remaining = 0.0
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        if self.blinking_remaining > 0:
            time = self.blinking_duration - self.blinking_remaining
            if (time // self.blinking_period) % 2 == 0:
                self.target.blenderObject["transparency"] = BLINKING_TRANSPARENCY
            else:
                self.target.blenderObject["transparency"] = 0.0
            self.blinking_remaining -= delta
        elif self.target_material.blend_method == "BLEND":
            self.target_material.blend_method = "OPAQUE"

    def activate(self):
        self.blinking_remaining = self.blinking_duration
        self.target_material.blend_method = "BLEND"

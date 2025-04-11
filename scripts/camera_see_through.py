import bge, bpy
from collections import OrderedDict

class CameraSeeThrough(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Target", bpy.types.Object),
        ("Camera", bpy.types.Object),
        ("Start Distance", 3.0),
        ("Full Transparency Distance", 0.0),
    ])

    def start(self, args):
        self.camera = self.object.scene.objects[args["Camera"].name]
        self.target = self.object.scene.objects[args["Target"].name]
        self.target_material = self.target.blenderObject.data.materials[0]
        self.start_distance = args["Start Distance"]
        self.full_transparency_distance = args["Full Transparency Distance"]

    def update(self):
        distance = (self.camera.worldPosition - self.target.worldPosition).length
        if distance < self.start_distance:
            self.target_material.blend_method = "BLEND"
            transparency = 1.0 - (distance - self.full_transparency_distance) / (self.start_distance - self.full_transparency_distance)
            self.target.blenderObject["transparency"] = max(0.0, min(1.0, transparency))
        else:
            self.target.blenderObject["transparency"] = 0.0

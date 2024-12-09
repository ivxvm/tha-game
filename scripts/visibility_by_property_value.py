import bge, bpy
from collections import OrderedDict

class VisibilityByPropertyValue(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Target Object", bpy.types.Object),
        ("Component Name", ""),
        ("Property Name", ""),
        ("Property Value", ""),
    ])

    def start(self, args):
        self.target = (self.object.scene
            .objects[args["Target Object"].name]
            .components[args["Component Name"]])
        self.property_name = args["Property Name"]
        self.property_value = args["Property Value"]

    def update(self):
        value = getattr(self.target, self.property_name)
        visible = value == self.property_value
        if visible != self.object.visible:
            self.object.setVisible(visible)

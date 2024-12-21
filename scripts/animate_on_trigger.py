import bge, deltatime
from mathutils import Vector
from collections import OrderedDict

class AnimateOnTrigger(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Property", "prop"),
        ("From", 0.0),
        ("To", 1.0),
        ("Duration", 1.0)
    ])

    def start(self, args):
        self.property = args["Property"]
        self.value_from = args["From"]
        self.value_range = args["To"] - args["From"]
        self.duration = args["Duration"]
        self.is_geonode_input = False
        if "." in self.property:
            self.is_geonode_input = True
            modifier_name, input_name = self.property.split(".")
            self.modifier_name = modifier_name
            self.input_id = self.object.blenderObject.modifiers[modifier_name].node_group.interface.items_tree[input_name].identifier
        self.elapsed = 0
        self.active = False
        self.finished = False
        self.start_position = self.object.worldPosition.copy()
        deltatime.init(self)


    def update(self):
        delta = deltatime.update(self)
        if self.active and not self.finished:
            self.elapsed += delta
            progress = min(1.0, self.elapsed / self.duration)
            new_value = self.value_from + progress * self.value_range
            if self.is_geonode_input:
                self.object.blenderObject.modifiers[self.modifier_name][self.input_id] = new_value
                self.object.blenderObject.data.update()
            elif self.property == "@Z":
                self.object.worldPosition = self.start_position + Vector([0, 0, new_value])
            elif self.property == "@scale":
                self.object.worldScale = Vector([new_value, new_value, new_value])
            else:
                self.object.blenderObject[self.property] = new_value
            self.finished = self.elapsed >= self.duration

    def trigger(self):
        self.active = True

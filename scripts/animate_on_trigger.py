import bge, bpy, deltatime
from mathutils import Vector
from collections import OrderedDict

MODE_LINEAR = "Linear"
MODE_PING_PONG = "Ping-Pong"

class AnimateOnTrigger(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Property", "prop"),
        ("From", 0.0),
        ("To", 1.0),
        ("Duration", 1.0),
        ("Mode", {MODE_LINEAR, MODE_PING_PONG}),
    ])

    def start(self, args):
        self.property = args["Property"]
        self.value_from = args["From"]
        self.value_to = args["To"]
        self.value_range = args["To"] - args["From"]
        self.duration = args["Duration"]
        self.mode = args.get("Mode", MODE_LINEAR)
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
            new_value = 0.0
            if self.mode == MODE_LINEAR:
                new_value = self.value_from + progress * self.value_range
            else:
                if progress <= 0.5:
                    new_value = self.value_from + progress * 2 * self.value_range
                else:
                    new_value = self.value_to - (progress - 0.5) * 2 * self.value_range
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
        self.update()

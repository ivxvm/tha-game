import bge
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
        self.prev_frame_timestamp = 0
        self.start_position = self.object.worldPosition.copy()

    def update(self):
        if self.active and not self.finished:
            timestamp = bge.logic.getClockTime()
            self.elapsed += timestamp - self.prev_frame_timestamp
            print(self.elapsed)
            progress = min(1.0, self.elapsed / self.duration)
            new_value = self.value_from + progress * self.value_range
            if self.is_geonode_input:
                self.object.blenderObject.modifiers[self.modifier_name][self.input_id] = new_value
                self.object.blenderObject.data.update()
            elif self.property == "@Z":
                self.object.worldPosition = self.start_position + Vector([0, 0, new_value])
            else:
                self.object.blenderObject[self.property] = new_value
            self.prev_frame_timestamp = timestamp
            self.finished = self.elapsed >= self.duration

    def trigger(self):
        print("AnimateOnTrigger is active now")
        self.prev_frame_timestamp = bge.logic.getClockTime()
        self.active = True

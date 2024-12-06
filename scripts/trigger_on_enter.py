import bge, bpy
from collections import OrderedDict

MODE_ONESHOT = "A. Oneshot"
MODE_REPEATABLE = "B. Repeatable"

class TriggerOnEnter(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Trigger Target", bpy.types.Object),
        ("Tracked Object", bpy.types.Object),
        ("Mode", {MODE_ONESHOT, MODE_REPEATABLE}),
        ("Range", 2.0),
        ("Repeat Cooldown", 3.0),
        ("Required Item", ""),
        ("Required Item Count", 1),
    ])

    def start(self, args):
        self.trigger_target = self.object.scene.objects[args["Trigger Target"].name]
        self.tracked_object = self.object.scene.objects[args["Tracked Object"].name]
        self.mode = args["Mode"]
        self.range = args["Range"]
        self.repeat_cooldown = args["Repeat Cooldown"]
        self.required_item = args["Required Item"]
        self.required_item_count = args["Required Item Count"]
        self.finished = False
        self.cooldown_elapsed = 0.0
        self.prev_frame_timestamp = 0.0
        if self.required_item:
            self.inventory = self.tracked_object.components["Inventory"]

    def update(self):
        timestamp = bge.logic.getClockTime()
        if self.finished:
            if self.mode == MODE_REPEATABLE:
                delta = timestamp - self.prev_frame_timestamp
                self.cooldown_elapsed += delta
                if self.cooldown_elapsed >= self.repeat_cooldown:
                    self.finished = False
                    self.cooldown_elapsed = 0.0
        else:
            distance = (self.tracked_object.worldPosition - self.object.worldPosition).length
            if distance <= self.range:
                passes_item_check = not self.required_item or self.inventory.items.get(self.required_item, 0) >= self.required_item_count
                if passes_item_check:
                    for component in self.trigger_target.components:
                        try:
                            component.trigger()
                        except AttributeError:
                            pass
                    self.finished = True
                    if self.mode == MODE_ONESHOT:
                        self.object.endObject()
                else:
                    print(self.required_item, "is needed")
        self.prev_frame_timestamp = timestamp

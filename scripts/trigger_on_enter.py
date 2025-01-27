import bge, bpy
from collections import OrderedDict
import deltatime

MODE_ONESHOT = "A. Oneshot"
MODE_REPEATABLE = "B. Repeatable"

class TriggerOnEnter(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("TriggerTarget", bpy.types.Object),
        ("TrackedObject", bpy.types.Object),
        ("Mode", {MODE_ONESHOT, MODE_REPEATABLE}),
        ("DeleteAfterTrigger", True),
        ("Range", 2.0),
        ("RepeatCooldown", 3.0),
        ("RequiredItem", ""),
        ("RequiredItemCount", 1),
    ])

    def start(self, args):
        self.trigger_target = self.object.scene.objects[args["TriggerTarget"].name]
        self.tracked_object = self.object.scene.objects[args["TrackedObject"].name]
        self.mode = args["Mode"]
        self.delete_after_trigger = args.get("DeleteAfterTrigger", True)
        self.range = args["Range"]
        self.repeat_cooldown = args["RepeatCooldown"]
        self.required_item = args["RequiredItem"]
        self.required_item_count = args["RequiredItemCount"]
        self.finished = False
        self.cooldown_elapsed = 0.0
        self.inventory = None
        if self.required_item:
            self.inventory = self.tracked_object.components["Inventory"]
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        if self.finished:
            if self.mode == MODE_REPEATABLE:
                self.cooldown_elapsed += delta
                if self.cooldown_elapsed >= self.repeat_cooldown:
                    self.finished = False
                    self.object.setVisible(True)
                    self.cooldown_elapsed = 0.0
        else:
            is_item_missing = self.object.blenderObject.get("is_item_missing", False)
            distance = (self.tracked_object.worldPosition - self.object.worldPosition).length
            if distance <= self.range:
                item_count = (self.inventory and self.inventory.items.get(self.required_item, 0)) or 0
                passes_item_check = not self.required_item or item_count >= self.required_item_count
                if passes_item_check:
                    if self.inventory:
                        self.inventory.items[self.required_item] = item_count - self.required_item_count
                    for component in self.trigger_target.components:
                        try:
                            component.trigger()
                        except AttributeError:
                            pass
                    self.finished = True
                    self.object.setVisible(False)
                    if self.mode == MODE_ONESHOT and self.delete_after_trigger:
                        self.object.endObject()
                elif not is_item_missing:
                    self.object.blenderObject["is_item_missing"] = True
                    self.object.blenderObject.data.update()
            elif is_item_missing:
                self.object.blenderObject["is_item_missing"] = False
                self.object.blenderObject.data.update()

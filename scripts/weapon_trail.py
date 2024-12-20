import bge, bpy
from collections import OrderedDict

class WeaponTrail(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Owner", bpy.types.Object),
        ("Reinstance Physics Mesh Interval", 0.2),
    ])

    def start(self, args):
        self.owner = self.object.scene.objects[args["Owner"].name]
        self.reinstance_interval = args["Reinstance Physics Mesh Interval"]
        self.cooldown = 0
        self.is_active = False
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        if not self.is_active:
            return
        timestamp = bge.logic.getClockTime()
        delta = timestamp - self.prev_frame_timestamp
        self.cooldown -= delta
        if self.cooldown <= 0:
            try:
                self.object.reinstancePhysicsMesh(evaluated=True)
            except Exception as e:
                print("[weapon_trail] Error during reinstancePhysicsMesh:", e)
            self.cooldown = self.reinstance_interval
        self.prev_frame_timestamp = timestamp

    def activate(self):
        self.object.worldPosition = self.owner.worldPosition
        for modifier in self.object.blenderObject.modifiers:
            modifier.show_in_editmode = True
            modifier.show_viewport = True
            modifier.show_render = True
        self.is_active = True

    def deactivate(self):
        for modifier in self.object.blenderObject.modifiers:
            modifier.show_in_editmode = False
            modifier.show_viewport = False
            modifier.show_render = False
        self.is_active = False

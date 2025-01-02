import bge, bpy
from collections import OrderedDict
import deltatime

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
        self.object.worldPosition = [0, 0, 0]
        deltatime.init(self)

    def update(self):
        if not self.is_active:
            return
        delta = deltatime.update(self)
        self.cooldown -= delta
        if self.cooldown <= 0:
            try:
                depsgraph = bpy.context.evaluated_depsgraph_get()
                vertex_count = len(self.object.blenderObject.evaluated_get(depsgraph).data.vertices)
                if vertex_count > 8:
                    self.object.reinstancePhysicsMesh(evaluated=True)
                else:
                    print("[weapon_trail] weird vertex_count:", vertex_count)
            except Exception as e:
                print("[weapon_trail] Error during reinstancePhysicsMesh:", e)
            self.cooldown = self.reinstance_interval

    def activate(self):
        self.object.worldPosition = self.owner.worldPosition
        for modifier in self.object.blenderObject.modifiers:
            modifier.show_in_editmode = True
            modifier.show_viewport = True
            modifier.show_render = True
        self.is_active = True

    def deactivate(self):
        self.object.worldPosition = [0, 0, 0]
        for modifier in self.object.blenderObject.modifiers:
            modifier.show_in_editmode = False
            modifier.show_viewport = False
            modifier.show_render = False
        self.is_active = False

import bge, bpy
from collections import OrderedDict

class ProxyPhysics(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Target Object", bpy.types.Object),
        ("Stillness Eta", 0.1),
    ])

    def start(self, args):
        self.target_object = self.object.scene.objects[args["Target Object"].name]
        self.stillness_eta = args["Stillness Eta"]
        self.sound = self.object.actuators["Sound"]
        self.is_active = False
        self.object.gravity = [0.0, 0.0, -30.0]
        self.prev_position = self.object.worldPosition.copy()

    def update(self):
        self_pos = self.object.worldPosition
        target_pos = self.target_object.worldPosition
        if self.is_active:
            target_pos.x = self_pos.x
            target_pos.y = self_pos.y
            target_pos.z = self_pos.z
            if (self_pos - self.prev_position).magnitude <= self.stillness_eta:
                self.deactivate()
            self.prev_position = self_pos.copy()
        else:
            self_pos.x = target_pos.x
            self_pos.y = target_pos.y
            self_pos.z = target_pos.z

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def hit(self, direction, knockback, damage):
        if self.on_hit:
            self.on_hit(direction, knockback, damage)
        self.sound.startSound()

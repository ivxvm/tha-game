import bge, bpy
from collections import OrderedDict

STILLNESS_ETA = 0.05
STILLNESS_FRAMES = 3

class ProxyPhysics(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Target Object", bpy.types.Object),
    ])

    def start(self, args):
        self.target_object = self.object.scene.objects[args["Target Object"].name]
        self.sound = self.object.actuators["Sound"]
        self.is_active = False
        self.stillness_counter = 0
        self.object.gravity = [0.0, 0.0, -30.0]
        self.prev_position = self.object.worldPosition.copy()

    def update(self):
        self_pos = self.object.worldPosition
        target_pos = self.target_object.worldPosition
        if self.is_active:
            target_pos.x = self_pos.x
            target_pos.y = self_pos.y
            target_pos.z = self_pos.z
            if (self_pos - self.prev_position).magnitude <= STILLNESS_ETA:
                self.stillness_counter += 1
                if self.stillness_counter >= STILLNESS_FRAMES:
                    self.deactivate()
            self.prev_position = self_pos.copy()
        else:
            self_pos.x = target_pos.x
            self_pos.y = target_pos.y
            self_pos.z = target_pos.z

    def activate(self):
        self.is_active = True
        self.stillness_counter = 0

    def deactivate(self):
        self.is_active = False

    def hit(self, direction, knockback, damage, silent):
        if self.on_hit:
            self.on_hit(direction, knockback, damage)
        if not silent:
            self.sound.startSound()

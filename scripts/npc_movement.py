import bge
from collections import OrderedDict
from mathutils import Vector

AXIS_Z = Vector([0, 0, 1])

class NpcMovement(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Walk Speed", 2.0),
        ("Rotation Speed", 0.1),
        ("Stillness Eta", 0.1),
    ])

    def start(self, args):
        self.walk_speed = args["Walk Speed"]
        self.rotation_speed = args["Rotation Speed"]
        self.stillness_eta = args["Stillness Eta"]
        self.target_position = Vector([0, 0, 0])
        self.is_still = False
        self.is_active = False

    def update(self):
        if self.is_active:
            direction = (self.target_position - self.object.worldPosition).normalized()
            direction.z = 0
            if direction.magnitude > self.stillness_eta:
                self.object.applyMovement(direction * self.walk_speed, False)
                self.object.alignAxisToVect(direction, 1)
                self.object.alignAxisToVect(AXIS_Z)
                self.is_still = False
            else:
                self.is_still = True

    def activate(self):
        self.is_active = True
        self.is_still = False

    def deactivate(self):
        self.is_active = False

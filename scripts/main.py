import bge
from collections import OrderedDict
from mathutils import Vector, Matrix

class PlayerController(bge.types.KX_PythonComponent):
    """My take on platformer-like 3rd person player controller"""

    args = OrderedDict([
        ("Move Speed", 0.1),
    ])

    def start(self, args):
        self.move_speed = args['Move Speed']
        self.character = bge.constraints.getCharacter(self.object)
        self.camera_pivot = self.object.children['Player.CameraPivot']
        self.model = self.object.children['Player.Model']
        self.platform_raycast_vec = Vector([0, 0, -1.5])
        self.platform = None
        self.prev_platform_position = Vector([0, 0, 0])

    def update(self):
        keyboard = bge.logic.keyboard.events

        speed_x = 0
        speed_y = 0

        if keyboard[bge.events.AKEY]:
            speed_x -= 1
        if keyboard[bge.events.DKEY]:
            speed_x += 1

        if keyboard[bge.events.WKEY]:
            speed_y += 1
        if keyboard[bge.events.SKEY]:
            speed_y -= 1

        speed_vec = Vector([speed_x, speed_y, 0])
        speed_vec.normalize()
        speed_vec *= self.move_speed

        move_vec = self.camera_pivot.worldOrientation @ speed_vec
        move_vec[2] = 0
        self.object.applyMovement(move_vec, False)

        if speed_x != 0 or speed_y != 0:
            move_vec.normalize()
            self.model.worldOrientation = move_vec.to_track_quat('Y','Z').to_euler()

        if keyboard[bge.events.SPACEKEY]:
           if self.platform:
               self.character.jump()

        if self.character.onGround:
            if not self.platform:
                position = self.object.worldPosition
                hit_target, _, _ = self.object.rayCast(position + self.platform_raycast_vec, mask=0x1)
                if hit_target:
                    self.platform = hit_target
                    self.prev_platform_position = Vector(self.platform.worldPosition)
                    print("self.platform =", self.platform)
        else:
            if self.platform:
                self.platform = None
                print("self.platform =", self.platform)

        if self.platform:
            current_platform_position = Vector(self.platform.worldPosition)
            deltas = current_platform_position - self.prev_platform_position
            self.object.applyMovement(deltas, False)
            self.prev_platform_position = current_platform_position

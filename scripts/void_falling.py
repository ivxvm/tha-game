import bge, bpy
from collections import OrderedDict

BLINKING_TRANSPARENCY = 0.5

class VoidFalling(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Player", bpy.types.Object),
        ("Camera", bpy.types.Object),
        ("Secondary Camera", bpy.types.Object),
        ("Min Z", -100.0),
        ("Min Camera Z", -10.0),
    ])

    def start(self, args):
        self.player = self.object.scene.objects[args["Player"].name]
        self.player_controller = self.player.components["PlayerController"]
        self.camera = self.object.scene.objects[args["Camera"].name]
        self.secondary_camera = self.object.scene.objects[args["Secondary Camera"].name]
        self.min_z = args["Min Z"]
        self.min_camera_z = args["Min Camera Z"]
        self.is_fall_sound_triggered = False
        self.fall_sound = self.object.actuators["FallSound"]

    def update(self):
        if self.camera.worldPosition.z < self.min_camera_z and self.object.worldPosition.z < self.min_camera_z:
            self.secondary_camera.blenderObject.location = self.camera.worldPosition
            self.secondary_camera.blenderObject.location.z = self.min_camera_z
            self.switch_camera(self.secondary_camera)
            if not self.is_fall_sound_triggered:
                self.fall_sound.startSound()
                self.is_fall_sound_triggered = True
        if self.object.worldPosition.z < self.min_z:
            self.player_controller.hp -= 1
            if self.player_controller.hp > 0:
                self.player_controller.respawn_at_last_bound_anchor()
                self.switch_camera(self.camera)
                self.is_fall_sound_triggered = False

    def switch_camera(self, camera):
        if self.object.scene.active_camera != camera:
            self.object.scene.active_camera = camera

import bge, bpy, deltatime
from collections import OrderedDict

BLINKING_TRANSPARENCY = 0.5

class VoidFalling(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Player", bpy.types.Object),
        ("Player Model",bpy.types.Object),
        ("Camera", bpy.types.Object),
        ("Secondary Camera", bpy.types.Object),
        ("Min Z", -100.0),
        ("Min Camera Z", -10.0),
        ("Blinking After Respawn Duration", 2.0),
        ("Blinking After Respawn Period", 0.25),
    ])

    def start(self, args):
        self.player = self.object.scene.objects[args["Player"].name]
        self.player_model = self.object.scene.objects[args["Player Model"].name]
        self.player_model_material = self.player_model.blenderObject.data.materials[0]
        self.player_controller = self.player.components["PlayerController"]
        self.camera = self.object.scene.objects[args["Camera"].name]
        self.secondary_camera = self.object.scene.objects[args["Secondary Camera"].name]
        self.min_z = args["Min Z"]
        self.min_camera_z = args["Min Camera Z"]
        self.blinking_after_respawn_duration = args["Blinking After Respawn Duration"]
        self.blinking_after_respawn_period = args["Blinking After Respawn Period"]
        self.blinking_remaining = 0.0
        self.is_fall_sound_triggered = False
        self.fall_sound = self.object.actuators["FallSound"]
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)

        if self.camera.worldPosition.z < self.min_camera_z:
            self.secondary_camera.blenderObject.location = self.camera.worldPosition
            self.secondary_camera.blenderObject.location.z = self.min_camera_z
            self.switch_camera(self.secondary_camera)
            if not self.is_fall_sound_triggered:
                self.fall_sound.startSound()
                self.is_fall_sound_triggered = True

        if self.player.worldPosition.z < self.min_z:
            self.player_controller.hp -= 1
            if self.player_controller.hp > 0:
                self.player_controller.teleport_to_respawn_anchor()
                self.switch_camera(self.camera)
                self.blinking_remaining = self.blinking_after_respawn_duration
                self.player_model_material.blend_method = "BLEND"
                self.is_fall_sound_triggered = False

        if self.blinking_remaining > 0:
            time = self.blinking_after_respawn_duration - self.blinking_remaining
            if (time // self.blinking_after_respawn_period) % 2 == 0:
                self.player_model.blenderObject["transparency"] = BLINKING_TRANSPARENCY
            else:
                self.player_model.blenderObject["transparency"] = 0.0
            self.blinking_remaining -= delta
        elif self.player_model_material.blend_method == "BLEND":
            self.player_model_material.blend_method = "OPAQUE"

    def switch_camera(self, camera):
        if self.object.scene.active_camera != camera:
            self.object.scene.active_camera = camera

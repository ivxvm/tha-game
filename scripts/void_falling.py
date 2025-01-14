import bge, bpy, constants, deltatime
from collections import OrderedDict

BLINKING_TRANSPARENCY = 0.5

class VoidFalling(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Player", bpy.types.Object),
        ("Player Model",bpy.types.Object),
        ("Camera", bpy.types.Object),
        ("Camera Pivot", bpy.types.Object),
        ("Secondary Camera", bpy.types.Object),
        ("Respawn Anchors", bpy.types.Collection),
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
        self.camera_pivot = self.object.scene.objects[args["Camera Pivot"].name]
        self.secondary_camera = self.object.scene.objects[args["Secondary Camera"].name]
        self.respawn_anchors = [self.object.scene.objects[object.name] for object in args["Respawn Anchors"].objects]
        self.min_z = args["Min Z"]
        self.min_camera_z = args["Min Camera Z"]
        self.blinking_after_respawn_duration = args["Blinking After Respawn Duration"]
        self.blinking_after_respawn_period = args["Blinking After Respawn Period"]
        self.blinking_remaining = 0.0
        self.is_fall_sound_triggered = False
        self.fall_sound = self.object.actuators["FallSound"]
        self.respawn_sound = self.object.actuators["RespawnSound"]
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
        else:
            self.switch_camera(self.camera)

        if self.player.worldPosition.z < self.min_z:
            self.player_controller.hp -= 1
            if self.player_controller.hp > 0:
                last_tracked_position = self.player_controller.last_tracked_position
                best_anchor = None
                best_anchor_distance = 999999.0
                for respawn_anchor in self.respawn_anchors:
                    magnitude = (last_tracked_position - respawn_anchor.worldPosition).magnitude
                    if magnitude < best_anchor_distance:
                        best_anchor = respawn_anchor
                        best_anchor_distance = magnitude
                self.player_controller.proxy_physics.deactivate()
                self.player.worldPosition = best_anchor.worldPosition.copy()
                self.camera_pivot.alignAxisToVect(best_anchor.getAxisVect(constants.AXIS_Y), 1)
                self.camera_pivot.alignAxisToVect(constants.AXIS_Z, 2)
                self.respawn_sound.startSound()
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

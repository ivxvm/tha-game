import bge, bpy
from collections import OrderedDict

class VoidFalling(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Player", bpy.types.Object),
        ("Camera", bpy.types.Object),
        ("Secondary Camera", bpy.types.Object),
        ("Respawn Anchors", bpy.types.Collection),
        ("Min Z", -100.0),
        ("Min Camera Z", -10.0),
    ])

    def start(self, args):
        self.player = self.object.scene.objects[args["Player"].name]
        self.player_controller = self.player.components["PlayerController"]
        self.camera = self.object.scene.objects[args["Camera"].name]
        self.secondary_camera = self.object.scene.objects[args["Secondary Camera"].name]
        self.respawn_anchors = [self.object.scene.objects[object.name] for object in args["Respawn Anchors"].objects]
        self.min_z = args["Min Z"]
        self.min_camera_z = args["Min Camera Z"]

    def update(self):
        if self.camera.worldPosition.z < self.min_camera_z:
            self.secondary_camera.blenderObject.location = self.camera.worldPosition
            self.secondary_camera.blenderObject.location.z = self.min_camera_z
            self.switch_camera(self.secondary_camera)
        else:
            self.switch_camera(self.camera)

        if self.player.worldPosition.z < self.min_z:
            last_tracked_position = self.player_controller.last_tracked_position
            self.player_controller.hp -= 1
            best_anchor = None
            best_anchor_distance = 999999.0
            for respawn_anchor in self.respawn_anchors:
                magnitude = (last_tracked_position - respawn_anchor.worldPosition).magnitude
                if magnitude < best_anchor_distance:
                    best_anchor = respawn_anchor
                    best_anchor_distance = magnitude
            self.player.worldPosition = best_anchor.worldPosition.copy()

    def switch_camera(self, camera):
        if self.object.scene.active_camera != camera:
            self.object.scene.active_camera = camera

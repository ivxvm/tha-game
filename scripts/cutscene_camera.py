import bge, bpy, deltatime
from collections import OrderedDict

class CutsceneCamera(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Duration", 3.0),
        ("Player", bpy.types.Object),
    ])

    def start(self, args):
        self.duration = args["Duration"]
        self.player_controller = self.object.scene.objects[args["Player"].name].components["PlayerController"]
        self.is_active = False
        self.elapsed = 0
        self.previous_active_camera = None
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        if self.is_active:
            self.elapsed += delta
            if self.elapsed >= self.duration:
                self.player_controller.is_blocked = False
                self.is_active = False
                self.object.scene.active_camera = self.previous_active_camera

    def trigger(self):
        self.previous_active_camera = self.object.scene.active_camera
        self.object.scene.active_camera = self.object
        self.elapsed = 0
        self.player_controller.is_blocked = True
        self.is_active = True

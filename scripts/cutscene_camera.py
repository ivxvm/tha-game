import bge, bpy, deltatime
from collections import OrderedDict

class CutsceneCamera(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Duration", 3.0),
    ])

    def start(self, args):
        self.duration = args["Duration"]
        self.is_active = False
        self.elapsed = 0
        self.previous_active_camera = None
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        if self.is_active:
            self.elapsed += delta
            if self.elapsed >= self.duration:
                self.is_active = False
                self.object.scene.active_camera = self.previous_active_camera

    def trigger(self):
        self.previous_active_camera = self.object.scene.active_camera
        self.object.scene.active_camera = self.object
        self.elapsed = 0
        self.is_active = True

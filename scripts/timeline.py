import bpy, bge
from collections import OrderedDict

class Timeline(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Timeline Framerate", 60)
    ])

    def start(self, args):
        self.framerate = args["Timeline Framerate"]
        self.scene = bpy.data.scenes["Scene"]
        self.current_frame = 0
        self.max_timeline_frame = 1048574

    def update(self):
        self.current_frame = int(bge.logic.getFrameTime() * self.framerate)
        self.scene.frame_set(self.current_frame % self.max_timeline_frame)

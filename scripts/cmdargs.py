import bge, bpy, sys, argparse
from collections import OrderedDict

class CmdArgs(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("FPS", bpy.types.Object),
    ])

    def start(self, args):
        parser = argparse.ArgumentParser(prog='Nodot')
        parser.add_argument('-launcher', action='store_true')
        parser.add_argument('-fullscreen', action='store_true')
        parser.add_argument('-fps', action='store_true')
        if '-' in sys.argv:
            cmdargs = parser.parse_args(sys.argv[sys.argv.index('-') + 1 :])
        else:
            cmdargs = parser.parse_args([])
        print("[CmdArgs] cmdargs =", cmdargs)
        if cmdargs.launcher:
            self.is_fullscreen = cmdargs.fullscreen
            self.should_show_fps = cmdargs.fps
        else:
            self.is_fullscreen = False
            self.should_show_fps = True
        print("[CmdArgs] is_fullscreen =", self.is_fullscreen)
        print("[CmdArgs] should_show_fps =", self.should_show_fps)
        if self.is_fullscreen:
            bge.render.setFullScreen(True)
        self.object.scene.objects[args["FPS"].name].visible = self.should_show_fps

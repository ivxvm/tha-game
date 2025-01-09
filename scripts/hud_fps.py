import bge
from collections import OrderedDict

class HudFps(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    def start(self, args):
        pass

    def update(self):
        self.object["Text"] = int(bge.logic.getAverageFrameRate())

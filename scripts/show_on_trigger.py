import bge
from collections import OrderedDict

class ShowOnTrigger(bge.types.KX_PythonComponent):
    args = OrderedDict([])

    def start(self, args):
        self.object.visible = False

    def trigger(self):
        self.object.visible = True

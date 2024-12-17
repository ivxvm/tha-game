import bge
from collections import OrderedDict

class EnableModifiersAfterStart(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    def start(self, args):
        self.finished = False

    def update(self):
        if not self.finished:
            for modifier in self.object.blenderObject.modifiers:
                modifier.show_in_editmode = True
                modifier.show_viewport = True
                modifier.show_render = True
                self.finished = True

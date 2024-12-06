import bge
from collections import OrderedDict

class TimeAware(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Property Name", "time")
    ])

    def start(self, args):
        self.prop = args["Property Name"]
        self.object.blenderObject[self.prop] = bge.logic.getClockTime()

    def update(self):
        self.object.blenderObject[self.prop] = bge.logic.getClockTime()
        self.object.blenderObject.data.update()

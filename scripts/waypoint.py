import bge, bpy
from collections import OrderedDict

class WaypointList(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("NextWaypoint", bpy.types.Object),
    ])

    def start(self, args):
        self.next_waypoint = args["NextWaypoint"]

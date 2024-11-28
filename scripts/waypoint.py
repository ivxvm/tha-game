import bge
from collections import OrderedDict

class WaypointList(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("NextWaypoint", ""),
    ])

import bge, bpy, deltatime
from collections import OrderedDict

def distance_xy(vec_a, vec_b):
    offset = vec_a - vec_b
    offset.z = 0
    return offset.magnitude

class Navigator(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Nav Mesh", bpy.types.Object),
        ("Distance Eta", 0.2),
        ("Debounce Interval", 0.1),
    ])

    def start(self, args):
        self.navmesh = self.object.scene.objects[args["Nav Mesh"].name]
        self.distance_eta = args["Distance Eta"]
        self.debounce_interval = args["Debounce Interval"]
        self.debounce_cooldown = 0
        self.target_position = self.object.worldPosition
        self.path = []
        self.current_path_index = 0
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        if self.debounce_cooldown > 0:
            self.debounce_cooldown -= delta

    def is_navigation_finished(self):
        return distance_xy(self.object.worldPosition, self.target_position) <= self.distance_eta

    def is_target_reachable(self):
        return len(self.path) > 0

    def update_target_position(self, value):
        if self.debounce_cooldown > 0:
            return
        if (self.target_position - value).magnitude < self.distance_eta:
            return
        self.target_position = value.copy()
        self.path = self.navmesh.findPath(self.object.worldPosition, self.target_position)
        self.current_path_index = 0
        self.debounce_cooldown = self.debounce_interval

    def get_next_path_position(self):
        path_len = len(self.path)
        while True:
            if path_len <= self.current_path_index:
                return self.object.worldPosition
            current_path_position = self.path[self.current_path_index]
            if distance_xy(self.object.worldPosition, current_path_position) < self.distance_eta:
                self.current_path_index += 1
                continue
            return current_path_position

import bge, bpy, deltatime
from collections import OrderedDict

class RespawnTracker(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Respawn Anchors", bpy.types.Collection),
        ("Default Anchor", bpy.types.Object),
        ("Binding Distance", 16.0),
        ("Debounce Interval", 0.5),
    ])

    def start(self, args):
        self.respawn_anchors = [self.object.scene.objects[object.name] for object in args["Respawn Anchors"].objects]
        self.binding_distance = args["Binding Distance"]
        self.debounce_interval = args["Debounce Interval"]
        self.last_bound_anchor = self.object.scene.objects[args["Default Anchor"].name]
        self.cooldown = 0
        self.on_bind_anchor = self.on_bind_anchor or None
        deltatime.init(self)

    def update(self):
        self.cooldown -= deltatime.update(self)

        if self.cooldown <= 0:
            for respawn_anchor in self.respawn_anchors:
                magnitude = (self.object.worldPosition - respawn_anchor.worldPosition).magnitude
                if magnitude < self.binding_distance:
                    if self.last_bound_anchor != respawn_anchor:
                        self.last_bound_anchor = respawn_anchor
                        if self.on_bind_anchor:
                            self.on_bind_anchor(respawn_anchor)
                    break
            self.cooldown = self.debounce_interval

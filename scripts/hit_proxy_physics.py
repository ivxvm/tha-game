import bge
from collections import OrderedDict
from mathutils import Vector

class HitProxyPhysics(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Knockback", 5.0),
        ("Collision Center Offset", [0.0, 0.0, 0.0]),
    ])

    def start(self, args):
        self.knockback = args["Knockback"]
        self.offset = Vector(args["Collision Center Offset"])
        self.last_hit_object = None
        self.last_hit_object_proxy_physics = None
        self.object.collisionCallbacks.append(self.handle_collision)

    def handle_collision(self, other):
        proxy_physics = None
        if other == self.last_hit_object:
            proxy_physics = self.last_hit_object_proxy_physics
        else:
            proxy_physics = other.components.get("ProxyPhysics")
            self.last_hit_object_proxy_physics = proxy_physics
            self.last_hit_object = other
        if proxy_physics:
            proxy_physics.hit(other.worldPosition - (self.object.worldPosition + self.offset), self.knockback)

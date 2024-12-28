import bge, deltatime
from collections import OrderedDict
from mathutils import Vector

DEFAULT_DEBOUNCE_INTERVAL = 0.5

class HitProxyPhysics(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Knockback", 5.0),
        ("Collision Center Offset", [0.0, 0.0, 0.0]),
        ("Debounce Interval", DEFAULT_DEBOUNCE_INTERVAL),
    ])

    def start(self, args):
        self.knockback = args["Knockback"]
        self.offset = Vector(args["Collision Center Offset"])
        self.debounce_interval = args.get("Debounce Interval", DEFAULT_DEBOUNCE_INTERVAL)
        self.last_hit_object = None
        self.last_hit_object_proxy_physics = None
        self.object.collisionCallbacks.append(self.handle_collision)
        self.elapsed_since_last_hit = 0.0
        deltatime.init(self)

    def handle_collision(self, other):
        proxy_physics = None
        if other == self.last_hit_object:
            proxy_physics = self.last_hit_object_proxy_physics
        else:
            proxy_physics = other.components.get("ProxyPhysics")
            self.last_hit_object_proxy_physics = proxy_physics
            self.last_hit_object = other
        if proxy_physics:
            self.elapsed_since_last_hit += deltatime.update(self)
            if self.elapsed_since_last_hit > self.debounce_interval:
                proxy_physics.hit(other.worldPosition - (self.object.worldPosition + self.offset), self.knockback)
                self.elapsed_since_last_hit = 0.0

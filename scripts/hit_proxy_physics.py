import bge, bpy, deltatime
from collections import OrderedDict
from mathutils import Vector

DEFAULT_DEBOUNCE_INTERVAL = 0.5

KNOCKBACK_PIVOT_SELF = "Self"
KNOCKBACK_PIVOT_OBJECT = "Object"
KNOCKBACK_PIVOT_HIT_POSITION = "Hit Position"

class HitProxyPhysics(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Knockback", 5.0),
        ("Knockback Pivot", {KNOCKBACK_PIVOT_SELF, KNOCKBACK_PIVOT_OBJECT, KNOCKBACK_PIVOT_HIT_POSITION}),
        ("Knockback Pivot Object", bpy.types.Object),
        ("Damage", 0),
        ("Collision Center Offset", [0.0, 0.0, 0.0]),
        ("Debounce Interval", DEFAULT_DEBOUNCE_INTERVAL),
        ("Silent", False),
    ])

    def start(self, args):
        self.knockback = args["Knockback"]
        self.knockback_pivot = args.get("Knockback Pivot", KNOCKBACK_PIVOT_HIT_POSITION)
        pivot_object_arg = args.get("Knockback Pivot Object")
        if pivot_object_arg:
            self.knockback_pivot_object = self.object.scene.objects[pivot_object_arg.name]
        self.damage = args.get("Damage", 0)
        self.offset = Vector(args["Collision Center Offset"])
        self.debounce_interval = args.get("Debounce Interval", DEFAULT_DEBOUNCE_INTERVAL)
        self.silent = args.get("Silent", False)
        self.last_hit_object = None
        self.last_hit_object_proxy_physics = None
        self.object.collisionCallbacks.append(self.handle_collision)
        self.elapsed_since_last_hit = 0.0
        deltatime.init(self)

    def handle_collision(self, other, hit_position):
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
                pivot = None
                if self.knockback_pivot == KNOCKBACK_PIVOT_SELF:
                    pivot = self.object.worldPosition
                elif self.knockback_pivot == KNOCKBACK_PIVOT_OBJECT:
                    pivot = self.knockback_pivot_object.worldPosition
                elif self.knockback_pivot == KNOCKBACK_PIVOT_HIT_POSITION:
                    pivot = hit_position
                proxy_physics.hit(direction=(other.worldPosition - (pivot + self.offset)).normalized(),
                                  knockback=self.knockback,
                                  damage=self.damage,
                                  silent=self.silent)
                self.elapsed_since_last_hit = 0.0

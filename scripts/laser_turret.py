import bge, bpy, deltatime
from collections import OrderedDict

STATE_ACTIVE = "STATE_ACTIVE"
STATE_DELAY = "STATE_DELAY"

class LaserTurret(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Active Time", 1.0),
        ("Delay Time", 1.0),
        ("Predelay", 0.0),
        ("Laser Ray 1", bpy.types.Object),
        ("Laser Ray 2", bpy.types.Object),
    ])

    def start(self, args):
        self.active_time = args["Active Time"]
        self.delay_time = args["Delay Time"]
        self.laser_rays = [self.object.scene.objects[args["Laser Ray 1"].name],
                           self.object.scene.objects[args["Laser Ray 2"].name]]
        self.laser_sound = self.object.actuators["LaserSound"]
        self.state = STATE_DELAY
        self.cooldown = self.delay_time + args["Predelay"]
        self.active_ray_index = 0
        for ray in self.laser_rays:
            ray.suspendPhysics()
            ray.visible = False
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        self.cooldown -= delta
        if self.state == STATE_ACTIVE:
            if self.cooldown <= 0:
                ray = self.laser_rays[self.active_ray_index]
                ray.suspendPhysics()
                ray.visible = False
                self.state = STATE_DELAY
                self.cooldown = self.delay_time
        elif self.state == STATE_DELAY:
            if self.cooldown <= 0:
                self.active_ray_index = (self.active_ray_index + 1) % len(self.laser_rays)
                ray = self.laser_rays[self.active_ray_index]
                ray.restorePhysics()
                ray.visible = True
                self.laser_sound.startSound()
                self.state = STATE_ACTIVE
                self.cooldown = self.active_time

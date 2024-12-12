import bge, bpy
from collections import OrderedDict

POWERUP_MULTI_JUMP = "Multi Jump"
POWERUP_FLAMETHROWER = "Flamethrower"

STATE_ACTIVE = "STATE_ACTIVE"
STATE_COOLDOWN = "STATE_COOLDOWN"

ICON_SCALE_OFFSET = 0.25
ICON_SCALE_MULTIPLIER = 1.0 - ICON_SCALE_OFFSET

class PickupPowerup(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Player", bpy.types.Object),
        ("Powerup Type", {POWERUP_MULTI_JUMP, POWERUP_FLAMETHROWER}),
        ("Parameter", ""),
        ("Range", 3.0),
        ("Cooldown", 5.0),
    ])

    def start(self, args):
        self.player = self.object.scene.objects[args["Player"].name]
        self.powerup = args["Powerup Type"]
        self.parameter = args["Parameter"]
        self.range = args["Range"]
        self.cooldown = args["Cooldown"]
        self.player_controller = self.player.components["PlayerController"]
        self.rotation_component = self.find_component("RotationDiscrete")
        self.wobble_component = self.find_component("MotionSine")
        self.cooldown_elapsed = 0.0
        self.state = STATE_ACTIVE
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        timestamp = bge.logic.getClockTime()
        delta = timestamp - self.prev_frame_timestamp
        if self.state == STATE_ACTIVE:
            distance = (self.object.worldPosition - self.player.worldPosition).magnitude
            if distance <= self.range:
                self.pickup()
                setattr(self.rotation_component, "paused", True)
                setattr(self.wobble_component, "paused", True)
                self.state = STATE_COOLDOWN
                self.cooldown_elapsed = 0.0
        elif self.state == STATE_COOLDOWN:
            self.cooldown_elapsed += delta
            progress = min(1.0, self.cooldown_elapsed / self.cooldown)
            new_scale = ICON_SCALE_OFFSET + progress * ICON_SCALE_MULTIPLIER
            self.wobble_component.object.blenderObject.scale = (new_scale, new_scale, new_scale)
            for child in self.object.children:
                child.blenderObject["desaturate"] = 1.0 - progress
                child.blenderObject.data.update()
            if progress >= 1.0:
                setattr(self.rotation_component, "paused", False)
                setattr(self.wobble_component, "paused", False)
                self.state = STATE_ACTIVE
        self.prev_frame_timestamp = timestamp

    def find_component(self, name):
        for child in self.object.children:
            component = child.components.get(name)
            if component:
                return component

    def pickup(self):
        setattr(self.player_controller, "powerup", self.powerup)
        if self.powerup == POWERUP_MULTI_JUMP:
            setattr(self.player_controller, "multijumps_left", int(self.parameter))

import bge, bpy
from collections import OrderedDict

MODE_COMPUTE_ONLY = "MODE_COMPUTE_ONLY"
MODE_COMPUTE_AND_APPLY = "MODE_COMPUTE_AND_APPLY"

class SoundVolumeByDistance(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Player", bpy.types.Object),
        ("Sound Actuator Name", "Sound"),
        ("Min Rollout Distance", 10.0),
        ("Max Audible Distance", 50.0),
        ("Volume Multiplier", 1.0),
        ("Mode", {MODE_COMPUTE_ONLY, MODE_COMPUTE_AND_APPLY}),
    ])

    def start(self, args):
        self.player = self.object.scene.objects[args["Player"].name]
        self.sound = self.object.actuators.get(args.get("Sound Actuator Name", "Sound"))
        self.min_rollout_distance = args["Min Rollout Distance"]
        self.max_audible_distance = args["Max Audible Distance"]
        self.volume_multiplier = args.get("Volume Multiplier", 1.0)
        self.mode = args.get("Mode", MODE_COMPUTE_ONLY)
        self.volume = 1.0

    def update(self):
        distance_to_player = (self.player.worldPosition - self.object.worldPosition).magnitude
        self.volume = 1.0
        if distance_to_player > self.min_rollout_distance:
            self.volume = max(0.0, self.max_audible_distance - (distance_to_player - self.min_rollout_distance)) / self.max_audible_distance
        self.volume *= self.volume_multiplier
        if self.mode == MODE_COMPUTE_AND_APPLY and self.sound:
            self.sound.volume = self.volume

import bge, bpy
from collections import OrderedDict

STATE_STOPPED = "STATE_STOPPED"
STATE_PLAYING = "STATE_PLAYING"
STATE_FADE_IN = "STATE_FADE_IN"
STATE_FADE_OUT = "STATE_FADE_OUT"
FAKE_SOUND_TIME = 999.0

class SoundLooper(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Player", bpy.types.Object),
        ("Sound Actuator Name", "Sound"),
        ("Fade In", 0.1),
        ("Fade Out", 0.1),
        ("Min Rollout Distance", 5.0),
        ("Max Audible Distance", 20.0),
        ("Auto Start", False),
    ])

    def start(self, args):
        self.player = self.object.scene.objects[args["Player"].name]
        self.sound = self.object.actuators[args["Sound Actuator Name"]]
        self.min_rollout_distance = args["Min Rollout Distance"]
        self.max_audible_distance = args["Max Audible Distance"]
        self.fade_in = args["Fade In"]
        self.fade_out = args["Fade Out"]
        self.state = STATE_STOPPED
        self.fade_timestamp = bge.logic.getClockTime()
        self.sound.startSound()
        self.sound.time = FAKE_SOUND_TIME
        self.sound.volume = 0.0
        if args["Auto Start"]:
            self.state = STATE_FADE_IN
            self.sound.time = 0.0
            self.sound.volume = 1.0

    def update(self):
        distance_to_player = (self.player.worldPosition - self.object.worldPosition).magnitude
        max_volume = 1.0
        if distance_to_player > self.min_rollout_distance:
            max_volume = max(0.0, self.max_audible_distance - (distance_to_player - self.min_rollout_distance)) / self.max_audible_distance
        if self.state == STATE_FADE_IN:
            fade_duration = bge.logic.getClockTime() - self.fade_timestamp
            self.sound.volume = max_volume * min(1.0, fade_duration / self.fade_in)
            if fade_duration > self.fade_in:
                self.state = STATE_PLAYING
        elif self.state == STATE_FADE_OUT:
            fade_duration = bge.logic.getClockTime() - self.fade_timestamp
            self.sound.volume = max_volume * (1.0 - min(1.0, fade_duration / self.fade_out))
            if fade_duration > self.fade_out:
                self.sound.time = FAKE_SOUND_TIME
                self.state = STATE_STOPPED
        elif self.state == STATE_PLAYING:
            self.sound.volume = max_volume
        elif self.state == STATE_STOPPED:
            self.sound.time = FAKE_SOUND_TIME

    def start_sound(self):
        print("start_sound")
        self.sound.time = 0.0
        self.fade_timestamp = bge.logic.getClockTime()
        self.state = STATE_FADE_IN

    def stop_sound(self):
        print("stop_sound")
        self.fade_timestamp = bge.logic.getClockTime()
        self.state = STATE_FADE_OUT

    def terminate_sound(self):
        print("terminate_sound")
        self.sound.stopSound()
        self.state = STATE_STOPPED

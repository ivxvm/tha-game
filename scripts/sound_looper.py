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
        ("Auto Start", False),
    ])

    def start(self, args):
        self.player = self.object.scene.objects[args["Player"].name]
        self.sound = self.object.actuators[args["Sound Actuator Name"]]
        self.volume_controller = self.object.components.get("SoundVolumeByDistance")
        self.fade_in = args["Fade In"]
        self.fade_out = args["Fade Out"]
        self.state = STATE_STOPPED
        self.fade_timestamp = bge.logic.getClockTime()
        self.config_volume = self.sound.volume
        self.sound.volume = 0.0
        self.sound.startSound()
        self.sound.time = FAKE_SOUND_TIME
        if args["Auto Start"]:
            self.state = STATE_FADE_IN
            self.sound.time = 0.0

    def update(self):
        volume = self.get_volume()
        if self.state == STATE_FADE_IN:
            fade_duration = bge.logic.getClockTime() - self.fade_timestamp
            self.sound.volume = volume * min(1.0, fade_duration / self.fade_in)
            if fade_duration > self.fade_in:
                self.state = STATE_PLAYING
        elif self.state == STATE_FADE_OUT:
            fade_duration = bge.logic.getClockTime() - self.fade_timestamp
            self.sound.volume = volume * (1.0 - min(1.0, fade_duration / self.fade_out))
            if fade_duration > self.fade_out:
                self.sound.time = FAKE_SOUND_TIME
                self.state = STATE_STOPPED
        elif self.state == STATE_PLAYING:
            self.sound.volume = volume
        elif self.state == STATE_STOPPED:
            self.sound.time = FAKE_SOUND_TIME

    def get_volume(self):
        if self.volume_controller:
            return self.volume_controller.volume
        else:
            return self.config_volume

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

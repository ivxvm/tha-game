import bge
from collections import OrderedDict

STATE_STOPPED = "STATE_STOPPED"
STATE_PLAYING = "STATE_PLAYING"
STATE_FADE_IN = "STATE_FADE_IN"
STATE_FADE_OUT = "STATE_FADE_OUT"

class SoundPlayer(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Sound Actuator Name", "Sound"),
        ("Fade In", 0.1),
        ("Fade Out", 0.1),
    ])

    def start(self, args):
        self.sound = self.object.actuators[args["Sound Actuator Name"]]
        self.fade_in = args["Fade In"]
        self.fade_out = args["Fade Out"]
        self.state = STATE_STOPPED
        self.fade_timestamp = 0
        self.sound.startSound()
        self.sound.time = 999.0

    def update(self):
        if self.state == STATE_FADE_IN:
            fade_duration = bge.logic.getClockTime() - self.fade_timestamp
            self.sound.volume = min(1.0, fade_duration / self.fade_in)
            if fade_duration > self.fade_in:
                self.state = STATE_PLAYING
        elif self.state == STATE_FADE_OUT:
            fade_duration = bge.logic.getClockTime() - self.fade_timestamp
            self.sound.volume = 1.0 - min(1.0, fade_duration / self.fade_out)
            if fade_duration > self.fade_out:
                self.sound.time = 999.0
                self.state = STATE_STOPPED
        elif self.state == STATE_STOPPED:
            self.sound.time = 999.0

    def start_sound(self):
        print("start_sound")
        self.sound.time = 0.0
        self.fade_timestamp = bge.logic.getClockTime()
        self.state = STATE_FADE_IN

    def stop_sound(self):
        print("stop_sound")
        self.fade_timestamp = bge.logic.getClockTime()
        self.state = STATE_FADE_OUT

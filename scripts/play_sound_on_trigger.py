import bge, deltatime
from collections import OrderedDict

class PlaySoundOnTrigger(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Sound Actuator Name", "Sound"),
    ])

    def start(self, args):
        self.sound = self.object.actuators[args["Sound Actuator Name"]]
        deltatime.init(self)

    def trigger(self):
        self.sound.startSound()

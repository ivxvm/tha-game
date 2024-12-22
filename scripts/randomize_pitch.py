import bge, random
from collections import OrderedDict

class RandomizePitch(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Sound Actuator Name", "Sound"),
        ("Pitches", "0,1,2"),
    ])

    def start(self, args):
        sound = self.object.actuators[args["Sound Actuator Name"]]
        pitches = [float(p) for p in args["Pitches"].split(",")]
        sound.pitch = random.choice(pitches)

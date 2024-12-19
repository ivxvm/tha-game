import bge
from collections import OrderedDict

class AnimationDefinition(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Animation Name", ""),
        ("Start Frame", 0.0),
        ("End Frame", 0.0),
        ("Layer", 0),
        ("Priority", 0),
        ("Blend-in", 0.0),
        ("Play Mode", {"0: Oneshot", "1: Loop", "2: Ping-Pong"}),
        ("Layer Weight", 0.0),
        ("IPO Flags", 0),
        ("Speed", 1.0),
        ("Blend Mode", {"0: Linear", "1: Additive"}),
    ])

    def start(self, args):
        self.name = args["Animation Name"]
        self.start_frame = args["Start Frame"]
        self.end_frame = args["End Frame"]
        self.layer = args["Layer"]
        self.priority = args["Priority"]
        self.blendin = args["Blend-in"]
        self.play_mode = int(args["Play Mode"].split(":")[0])
        self.layer_weight = args["Layer Weight"]
        self.ipo_flags = args["IPO Flags"]
        self.speed = args["Speed"]
        self.blend_mode = int(args["Blend Mode"].split(":")[0])

    def update(self):
        pass

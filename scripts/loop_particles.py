import bge, deltatime
from collections import OrderedDict

class LoopParticles(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Predelay", 0.0),
        ("Duration", 5.0),
        ("Delay", 0.0),
    ])

    def start(self, args):
        self.predelay = args["Predelay"]
        self.duration = args["Duration"]
        self.delay = args["Delay"]
        self.particle_player = self.object.components["ParticlePlayer"]
        self.cooldown = self.predelay
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        self.cooldown -= delta
        if self.cooldown <= 0:
            self.particle_player.play(self.duration * 1.2)
            self.cooldown = self.duration + self.delay

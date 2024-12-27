import bge, bpy, constants, deltatime
from collections import OrderedDict

STATE_PAUSED = "STATE_PAUSED"
STATE_PLAYING = "STATE_PLAYING"

class ParticlePlayer(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("ParticleSystemName", "")
    ])

    def start(self, args):
        self.particle_system = bpy.data.particles[args["ParticleSystemName"]]
        self.particle_system.frame_start = constants.LAST_TIMELINE_FRAME + 1
        self.particle_system.frame_end = constants.LAST_TIMELINE_FRAME + 1
        self.timeline = self.object.scene.objects["Timeline"].components["Timeline"]
        self.is_playing = False
        self.remaining_duration = 0
        self.callback = None
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        if self.is_playing:
            self.remaining_duration -= delta
            if self.remaining_duration <= 0:
                self.is_playing = False
                if self.callback:
                    self.callback()

    def play(self, duration, callback = None):
        self.is_playing = True
        self.remaining_duration = duration
        self.callback = callback
        self.particle_system.frame_start = self.timeline.current_frame
        self.particle_system.frame_end = int(self.timeline.current_frame + duration * bge.logic.getAverageFrameRate())

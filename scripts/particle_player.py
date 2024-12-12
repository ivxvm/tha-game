import bge, bpy
from collections import OrderedDict

STATE_PAUSED = "STATE_PAUSED"
STATE_PLAYING = "STATE_PLAYING"

class ParticlePlayer(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("ParticleSystemName", "")
    ])

    def start(self, args):
        self.particle_system = bpy.data.particles[args["ParticleSystemName"]]
        self.timeline = self.object.scene.objects["Timeline"].components["Timeline"]
        self.state = STATE_PAUSED
        self.remaining_duration = 0
        self.callback = lambda: None
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        timestamp = bge.logic.getClockTime()
        if self.state == STATE_PLAYING:
            delta = timestamp - self.prev_frame_timestamp
            self.remaining_duration -= delta
            if self.remaining_duration <= 0:
                self.state = STATE_PAUSED
                self.callback()
        self.prev_frame_timestamp = timestamp

    def play(self, duration, callback):
        self.state = STATE_PLAYING
        self.remaining_duration = duration
        self.callback = callback
        self.particle_system.frame_start = self.timeline.current_frame
        self.particle_system.frame_end = int(self.timeline.current_frame + duration * bge.logic.getAverageFrameRate())

from re import A
import bge
from collections import OrderedDict
from mathutils import Vector, Matrix

MODE_ONESHOT = "MODE_ONESHOT"
MODE_LOOPER = "MODE_LOOPER"

class SoundOnMovement(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
        ("Stillness Frames", 5),
        ("Mode", {MODE_ONESHOT, MODE_LOOPER}),
    ])

    def start(self, args):
        self.stillness_frames = args["Stillness Frames"]
        self.mode = args.get("Mode", MODE_LOOPER)
        self.sound = self.object.actuators["Sound"]
        self.sound_looper = self.object.components.get("SoundLooper")
        self.current_stillness_frames = self.stillness_frames
        self.prev_position = Vector(self.object.worldPosition)
        self.prev_orientation = self.object.worldOrientation
        self.is_sound_active = False

    def update(self):
        current_position = Vector(self.object.worldPosition)
        current_orientation = self.object.worldOrientation
        movement_deltas = current_position - self.prev_position
        a = current_orientation.to_euler()
        b = self.prev_orientation.to_euler()
        rotation_deltas = Vector((a.x - b.x, a.y - b.y, a.z - b.z))
        is_still = movement_deltas.magnitude == 0 and rotation_deltas.magnitude == 0
        if self.is_sound_active and is_still:
            self.current_stillness_frames += 1
            if self.current_stillness_frames >= self.stillness_frames:
                if self.mode == MODE_LOOPER:
                    self.sound_looper.stop_sound()
                self.is_sound_active = False
        elif not self.is_sound_active and not is_still:
            self.current_stillness_frames -= 1
            if self.current_stillness_frames <= 0:
                if self.mode == MODE_LOOPER:
                    self.sound_looper.start_sound()
                elif self.mode == MODE_ONESHOT:
                    self.sound.startSound()
                self.is_sound_active = True
        self.prev_position = Vector(self.object.worldPosition)
        self.prev_orientation = self.object.worldOrientation.copy()

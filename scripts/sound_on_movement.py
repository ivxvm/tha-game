import bge
from collections import OrderedDict
from mathutils import Vector, Matrix

class SoundOnMovement(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
        ("Stillness Frames", 3),
    ])

    def start(self, args):
        self.sound = self.object.actuators["Sound"]
        self.sound_player = self.object.components["SoundPlayer"]
        self.stillness_frames = args["Stillness Frames"]
        self.current_stillness_frames = self.stillness_frames
        self.prev_position = Vector(self.object.worldPosition)
        self.prev_orientation = self.object.worldOrientation
        self.is_sound_active = False

    def update(self):
        current_position = Vector(self.object.worldPosition)
        current_orientation = self.object.worldOrientation
        movement_deltas = current_position - self.prev_position
        delta_rotation_z = (current_orientation.to_euler().z - self.prev_orientation.to_euler().z)
        is_still = movement_deltas.magnitude == 0 and delta_rotation_z == 0
        if self.is_sound_active and is_still:
            self.current_stillness_frames += 1
            if self.current_stillness_frames >= self.stillness_frames:
                self.sound_player.stop_sound()
                self.is_sound_active = False
        elif not self.is_sound_active and not is_still:
            self.current_stillness_frames -= 1
            if self.current_stillness_frames <= 0:
                self.sound_player.start_sound()
                self.is_sound_active = True
        # print("self.current_stillness_frames", self.current_stillness_frames)
        self.prev_position = Vector(self.object.worldPosition)
        self.prev_orientation = self.object.worldOrientation.copy()

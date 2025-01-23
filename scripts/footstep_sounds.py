import bge, random
from collections import OrderedDict

FOOTSTEPS_VOLUME = 0.75

class FootstepSounds(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Falling Action", ""),
        ("Movement Action", ""),
        ("Step Frame 1", 0),
        ("Step Frame 2", 0),
        ("Sound Actuator 1", ""),
        ("Sound Actuator 2", ""),
    ])

    def start(self, args):
        self.falling_action = args["Falling Action"]
        self.movement_action = args["Movement Action"]
        self.step_frame_1 = args["Step Frame 1"]
        self.step_frame_2 = args["Step Frame 2"]
        self.sound_actuators_1 = [self.object.actuators[name] for name in args["Sound Actuator 1"].split(",")]
        self.sound_actuators_2 = [self.object.actuators[name] for name in args["Sound Actuator 2"].split(",")]

        self.phase = 0
        self.prev_action = None

        for actuator in self.sound_actuators_1:
            actuator.volume = FOOTSTEPS_VOLUME
        for actuator in self.sound_actuators_2:
            actuator.volume = FOOTSTEPS_VOLUME

    def update(self):
        action = self.object.getActionName()

        if action == self.movement_action:
            frame = self.object.getActionFrame()
            if self.phase == 0 and frame >= self.step_frame_1 and frame < self.step_frame_2:
                random.choice(self.sound_actuators_1).startSound()
                self.phase = 1
            elif self.phase == 1 and frame >= self.step_frame_2:
                random.choice(self.sound_actuators_2).startSound()
                self.phase = 0
        else:
            self.phase = 0

        if self.prev_action == self.falling_action and action != self.falling_action:
            random.choice(self.sound_actuators_1).startSound()
            random.choice(self.sound_actuators_2).startSound()

        self.prev_action = action

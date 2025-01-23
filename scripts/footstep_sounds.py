import bge, random
from collections import OrderedDict

FOOTSTEPS_VOLUME = 0.5

class FootstepSounds(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Falling Actions", ""),
        ("Movement Actions", ""),
        ("Sound Actuator 1", ""),
        ("Sound Actuator 2", ""),
    ])

    def start(self, args):
        self.falling_actions = args["Falling Actions"].split(",")
        self.movement_actions = []
        self.step_frames_1 = []
        self.step_frames_2 = []
        self.sound_actuators_1 = [self.object.actuators[name] for name in args["Sound Actuator 1"].split(",")]
        self.sound_actuators_2 = [self.object.actuators[name] for name in args["Sound Actuator 2"].split(",")]

        for [action, frame1, frame2] in [s.split(":") for s in args["Movement Actions"].split(",")]:
            self.movement_actions.append(action)
            self.step_frames_1.append(int(frame1))
            self.step_frames_2.append(int(frame2))

        self.phase = 0
        self.prev_action = None

        for actuator in self.sound_actuators_1:
            actuator.volume = FOOTSTEPS_VOLUME
        for actuator in self.sound_actuators_2:
            actuator.volume = FOOTSTEPS_VOLUME

    def update(self):
        action = self.object.getActionName()

        if action != self.prev_action:
            self.phase = 0

        if action in self.movement_actions:
            frame = self.object.getActionFrame()
            index = self.movement_actions.index(action)
            if self.phase == 0 and frame >= self.step_frames_1[index] and frame < self.step_frames_2[index]:
                random.choice(self.sound_actuators_1).startSound()
                self.phase = 1
            elif self.phase == 1 and frame >= self.step_frames_2[index]:
                random.choice(self.sound_actuators_2).startSound()
                self.phase = 0
        else:
            self.phase = 0

        if self.prev_action in self.falling_actions and not action in self.falling_actions:
            random.choice(self.sound_actuators_1).startSound()
            random.choice(self.sound_actuators_2).startSound()

        self.prev_action = action

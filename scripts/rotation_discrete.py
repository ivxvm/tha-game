import bge, math
from collections import OrderedDict
from mathutils import Matrix

AXIS_X = "X"
AXIS_Y = "Y"
AXIS_Z = "Z"

START_TYPE_ON_LOAD = "OnLoad"
START_TYPE_ON_TRIGGER = "OnTrigger"

MOTION_TYPE_PING_PONG = "PingPong"
MOTION_TYPE_CYCLE = "Cycle"

STATE_INIT = "INIT"
STATE_RUNNING = "RUNNING"
STATE_DELAY = "DELAY"

class RotationDiscrete(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Axis", {AXIS_X, AXIS_Y, AXIS_Z}),
        ("Angle", 90.0),
        ("Duration", 5.0),
        ("StartType", {START_TYPE_ON_LOAD, START_TYPE_ON_TRIGGER}),
        ("MotionType", {MOTION_TYPE_PING_PONG, MOTION_TYPE_CYCLE}),
        ("AutoLoop", False),
        ("Delay", 0.0),
    ])

    def start(self, args):
        self.axis = args["Axis"]
        self.angle = math.radians(args["Angle"])
        self.duration = args["Duration"]
        self.start_type = args["StartType"]
        self.motion_type = args["MotionType"]
        self.auto_loop = args["AutoLoop"]
        self.delay = args["Delay"]
        self.paused = False
        self.state = STATE_RUNNING
        self.is_active = self.start_type == START_TYPE_ON_LOAD
        self.is_moving_backwards = False
        self.rotation_elapsed = 0.0
        self.delay_elapsed = 0.0
        self.initial_orientation = self.object.localOrientation.copy()
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        if self.paused:
            return
        timestamp = bge.logic.getClockTime()
        if self.state == STATE_RUNNING:
            if self.is_active:
                delta = timestamp - self.prev_frame_timestamp
                self.rotation_elapsed += delta
                progress = min(1, self.rotation_elapsed / self.duration)
                if self.is_moving_backwards:
                    progress = 1 - progress
                rotation_matrix = self.initial_orientation.copy()
                rotation_matrix.rotate(Matrix.Rotation(progress * self.angle, 4, self.axis))
                self.object.localOrientation = rotation_matrix
                if self.rotation_elapsed >= self.duration:
                    if self.motion_type == MOTION_TYPE_PING_PONG:
                        self.is_moving_backwards = not self.is_moving_backwards
                    self.initial_orientation = self.object.localOrientation.copy()
                    self.state = STATE_DELAY
                    self.delay_elapsed = 0.0
                    self.is_active = False
        elif self.state == STATE_DELAY:
            delta = timestamp - self.prev_frame_timestamp
            self.delay_elapsed += delta
            if self.delay_elapsed >= self.delay:
                self.is_active = self.auto_loop
                self.state = STATE_RUNNING
                self.rotation_elapsed = 0.0
        self.prev_frame_timestamp = timestamp

    def trigger(self):
        if self.state == STATE_RUNNING:
            self.is_active = True
            return True
        return False

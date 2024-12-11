import bge, bpy
from collections import OrderedDict

STATE_INIT = "INIT"
STATE_RUNNING = "RUNNING"
STATE_DELAY = "DELAY"

START_TYPE_ON_LOAD = "OnLoad"
START_TYPE_ON_TRIGGER = "OnTrigger"

MOTION_TYPE_PING_PONG = "PingPong"
MOTION_TYPE_CYCLE = "Cycle"

class MotionWaypoints(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("TravelTime", 10.0),
        ("StartTimeOffset", 0.0),
        ("PathTracker", bpy.types.Object),
        ("StartType", {START_TYPE_ON_LOAD, START_TYPE_ON_TRIGGER}),
        ("MotionType", {MOTION_TYPE_PING_PONG, MOTION_TYPE_CYCLE}),
        ("AutoLoop", False),
        ("Delay", 0.0),
    ])

    def start(self, args):
        self.total_travel_time = args["TravelTime"]
        self.path_tracker = self.object.scene.objects[args["PathTracker"].name]
        self.auto_loop = args["AutoLoop"]
        self.start_type = args["StartType"]
        self.motion_type = args["MotionType"]
        self.delay = args["Delay"]
        self.state = STATE_RUNNING
        self.is_active = self.start_type == START_TYPE_ON_LOAD
        self.is_moving_backwards = False
        self.motion_elapsed = args["StartTimeOffset"]
        self.delay_elapsed = 0.0
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        timestamp = bge.logic.getClockTime()
        if self.state == STATE_RUNNING:
            if self.is_active:
                delta = timestamp - self.prev_frame_timestamp
                self.motion_elapsed += delta
                progress = min(1, self.motion_elapsed / self.total_travel_time)
                if self.is_moving_backwards:
                    progress = 1 - progress
                self.path_tracker.blenderObject.constraints["Follow Path"].offset_factor = progress
                self.object.worldPosition = self.path_tracker.worldPosition
                if self.motion_elapsed >= self.total_travel_time:
                    if self.motion_type == MOTION_TYPE_PING_PONG:
                        self.is_moving_backwards = not self.is_moving_backwards
                    self.state = STATE_DELAY
                    self.delay_elapsed = 0.0
                    self.is_active = False
        elif self.state == STATE_DELAY:
            delta = timestamp - self.prev_frame_timestamp
            self.delay_elapsed += delta
            if self.delay_elapsed >= self.delay:
                self.is_active = self.auto_loop
                self.state = STATE_RUNNING
                self.motion_elapsed = 0.0
        self.prev_frame_timestamp = timestamp

    def trigger(self):
        if self.state == STATE_RUNNING:
            self.is_active = True
            return True
        return False

# platform initially still, starts moving on player enter, stops at last point before next triger
#   | start type = on trigger, autoloop = false + empty object with trigger on enter parented to platform
# platform initially still, starts moving on player enter, continues moving back and forth
#   | start type = on trigger, autoloop = true + empty object with trigger on enter parented to platform


import bge, bpy, math
from collections import OrderedDict
from mathutils import Vector

STATE_INIT = "INIT"
STATE_RUNNING = "RUNNING"
STATE_DELAY = "DELAY"

START_TYPE_ON_LOAD = "OnLoad"
START_TYPE_ON_TRIGGER = "OnTrigger"

class MotionWaypoints(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("TravelTime", 10.0),
        ("StartWaypoint", bpy.types.Object),
        ("StartType", {START_TYPE_ON_LOAD, START_TYPE_ON_TRIGGER}),
        ("AutoLoop", False),
        ("Delay", 0.0),
    ])

    def init_waypoints(self):
        total_distance = 0
        segment_lengths = []
        self.waypoints = []
        self.displacements = []
        self.travel_times_by_segment = []
        self.is_cycle = False
        waypoint_ids = []
        current_waypoint = self.start_waypoint
        while True:
            self.waypoints.append(current_waypoint)
            waypoint_ids.append(id(current_waypoint))
            waypoint_list_component = current_waypoint.components.get("WaypointList")
            next_waypoint_name = waypoint_list_component and waypoint_list_component.next_waypoint.name
            if next_waypoint_name:
                next_waypoint = self.object.scene.objects[next_waypoint_name]
                displacement = next_waypoint.worldPosition - current_waypoint.worldPosition
                self.displacements.append(displacement)
                segment_length = displacement.length
                segment_lengths.append(segment_length)
                total_distance += segment_length
                current_waypoint = next_waypoint
                if id(current_waypoint) in waypoint_ids:
                    self.is_cycle = True
                    self.waypoints.append(current_waypoint)
                    break
            else:
                break
        self.segments_count = len(self.waypoints) - 1
        for i in range(self.segments_count):
            self.travel_times_by_segment.append((segment_lengths[i] / total_distance) * self.total_travel_time)
        print("self.travel_times_by_segment", self.travel_times_by_segment)

    def compute_splines(self):
        n = len(self.waypoints)
        xs = []
        ys = []
        for i in range(n):
            w = self.waypoints[i]
            p = w.worldPosition
            xs.append(p.x)
            ys.append(p.y)
        coeffs_a = []
        coeffs_h = []
        for i in range(n):
            coeffs_a.append(ys[i])
            if i < n - 1:
                coeffs_h.append(xs[i + 1] - xs[i])
        coeffs_alpha = [0]
        for i in range(1, n - 1):
            coeffs_alpha.append(
                3 * (coeffs_a[i + 1] - coeffs_a[i]) / coeffs_h[i] -
                3 * (coeffs_a[i] - coeffs_a[i - 1]) / coeffs_h[i - 1])
        coeffs_l = [1]
        coeffs_u = [0]
        coeffs_z = [0]
        for i in range(1, n - 1):
            coeffs_l.append(2 * (xs[i + 1] - xs[i - 1]) - coeffs_h[i - 1] * coeffs_u[i - 1])
            coeffs_u.append(coeffs_h[i] / coeffs_l[i])
            coeffs_z.append((coeffs_alpha[i] - coeffs_h[i - 1] * coeffs_z[i - 1]) / coeffs_l[i])
        coeffs_c = [0 for _ in range(n)]
        coeffs_b = [0 for _ in range(n)]
        coeffs_d = [0 for _ in range(n)]
        for j in reversed(range(n - 1)):
            coeffs_c[j] = coeffs_z[j] - coeffs_u[j] * coeffs_c[j + 1]
            if coeffs_h[j] == 0:
                coeffs_b[j] = 0
                coeffs_d[j] = 0
            else:
                coeffs_b[j] = (coeffs_a[j + 1] - coeffs_a[j]) / coeffs_h[j] - coeffs_h[j] * (coeffs_c[j + 1] + 2 * coeffs_c[j]) / 3
                coeffs_d[j] = (coeffs_c[j + 1] - coeffs_c[j]) / (3 * coeffs_h[j])
        self.splines = []
        for i in range(n):
            self.splines.append([coeffs_a[i], coeffs_b[i], coeffs_c[i], coeffs_d[i], xs[i]])
        # print("splines = ", len(self.splines))
        # print(self.splines)

    def is_end_of_path(self):
        if self.is_cycle:
            return False
        if (self.current_segment_index == 0) and (self.direction_sign == -1):
            return True
        if (self.current_segment_index == len(self.waypoints) - 2) and (self.direction_sign == 1):
            return True
        return False

    def proceed_to_next_segment(self):
        # print("\n\n\n")
        # print("proceed_to_next_segment | self.direction_sign", self.direction_sign)
        # print("proceed_to_next_segment | self.direction_sign", self.current_segment_index)
        # print("proceed_to_next_segment | should_flip_direction_sign", should_flip_direction_sign)
        if self.is_end_of_path():
            if not self.auto_loop:
                self.is_active = False
            self.direction_sign *= -1
        else:
            self.current_segment_index = (self.current_segment_index + self.direction_sign) % self.segments_count
        # print("proceed_to_next_segment | new_direction_sign", self.direction_sign)
        # print("\n\n\n")
        self.start_time = bge.logic.getClockTime()
        self.end_time = self.start_time + self.travel_times_by_segment[self.current_segment_index]
        if self.direction_sign == 1:
            self.start_position = self.waypoints[self.current_segment_index].worldPosition
        else:
            self.start_position = self.waypoints[self.current_segment_index + 1].worldPosition

    def start(self, args):
        self.total_travel_time = args["TravelTime"]
        self.start_waypoint = self.object.scene.objects[args["StartWaypoint"].name]
        self.auto_loop = args["AutoLoop"]
        self.start_type = args["StartType"]
        self.delay = args["Delay"]
        # self.is_waiting_for_trigger = args["StartType"] != START_TYPE_ON_LOAD
        # self.player_controller = self.object.scene.objects["Player.Root"].components["PlayerController"]
        self.state = STATE_INIT
        self.is_active = False
        self.current_segment_index = -1
        self.direction_sign = 1
        self.delay_elapsed = 0.0
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        timestamp = bge.logic.getClockTime()
        if self.state == STATE_INIT:
            self.init_waypoints()
            self.compute_splines()
            self.state = STATE_RUNNING
            if self.start_type == START_TYPE_ON_LOAD:
                self.trigger()
        elif self.state == STATE_RUNNING:
            if self.is_active:
                current_time = bge.logic.getClockTime()
                progress = min(1, (current_time - self.start_time) / self.travel_times_by_segment[self.current_segment_index])
                # if self.object.name == "DeathStar":
                    # print("progress", progress, self.travel_times_by_segment[self.current_segment_index])
                displacement = self.displacements[self.current_segment_index] * self.direction_sign
                # self.object.worldPosition = self.start_position + displacement * progress
                new_linear_position = self.start_position + displacement * progress
                lpx = new_linear_position.x
                [a, b, c, d, x] = self.splines[self.current_segment_index]
                spline_y1 = a + b * (lpx - x) + c * math.pow(lpx - x, 2) + d * math.pow(lpx - x, 3)
                [a, b, c, d, x] = self.splines[self.current_segment_index + 1]
                spline_y2 = a + b * (lpx - x) + c * math.pow(lpx - x, 2) + d * math.pow(lpx - x, 3)
                spline_y = spline_y1 * (1 - progress) + spline_y2 * progress
                self.object.worldPosition = Vector([lpx, spline_y, new_linear_position.z])
                if self.object.name == "DeathStar":
                    print("spline_y1/2", spline_y1, spline_y2)
                    print("xy", self.object.worldPosition.x, self.object.worldPosition.y,)

                if current_time >= self.end_time:
                    if self.object.name == "DeathStar":
                        print("OOOOPS")
                    if self.is_end_of_path() and self.delay > 0.0:
                        self.state = STATE_DELAY
                        self.delay_elapsed = 0.0
                    else:
                        self.proceed_to_next_segment()
        elif self.state == STATE_DELAY:
            delta = timestamp - self.prev_frame_timestamp
            self.delay_elapsed += delta
            if self.delay_elapsed >= self.delay:
                self.state = STATE_RUNNING
                self.proceed_to_next_segment()
            # else:
            #     if self.is_waiting_for_trigger and self.player_controller.platform != self.object:
            #         return
            #     self.proceed_to_next_segment()
            #     self.is_active = True
                # self.start_time = bge.logic.getClockTime()
                # self.end_time = self.start_time + self.travel_times_by_segment[self.current_segment_index]
                # self.start_position = self.waypoints[self.current_segment_index].worldPosition
        self.prev_frame_timestamp = timestamp

    def trigger(self):
        self.proceed_to_next_segment()
        self.is_active = True
        self.state = STATE_RUNNING

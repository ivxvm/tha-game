import bge
from collections import OrderedDict

class MotionWaypoints(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("TravelTime", 10),
        ("StartWaypoint", ""),
        ("Looped", False),
        ("StartType", "OnLoad"), # OnLoad | OnPlayerStep
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
            next_waypoint_name = waypoint_list_component and waypoint_list_component.next_waypoint
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

    def proceed_to_next_segment(self):
        should_flip_direction_sign = False
        if not self.is_cycle:
            if (self.current_segment_index == 0) and (self.direction_sign == -1):
                should_flip_direction_sign = True
            if (self.current_segment_index == len(self.waypoints) - 2) and (self.direction_sign == 1):
                should_flip_direction_sign = True
        # print("\n\n\n")
        # print("proceed_to_next_segment | self.direction_sign", self.direction_sign)
        # print("proceed_to_next_segment | self.direction_sign", self.current_segment_index)
        # print("proceed_to_next_segment | should_flip_direction_sign", should_flip_direction_sign)
        if should_flip_direction_sign:
            if not self.is_looped:
                self.state = "FINISHED"
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
        self.start_waypoint = self.object.scene.objects[args["StartWaypoint"]]
        self.is_looped = args["Looped"]
        self.is_waiting_for_trigger = args["StartType"] != "OnLoad"
        self.player_controller = self.object.scene.objects["Player.Root"].components["PlayerController"]
        self.state = "INIT"
        self.is_active = False
        self.current_segment_index = -1
        self.direction_sign = 1

    def update(self):
        if self.state == "INIT":
            self.init_waypoints()
            self.state = "RUNNING"
        elif self.state == "RUNNING":
            if self.is_active:
                current_time = bge.logic.getClockTime()
                progress = (current_time - self.start_time) / self.travel_times_by_segment[self.current_segment_index]
                displacement = self.displacements[self.current_segment_index] * self.direction_sign
                self.object.worldPosition = self.start_position + displacement * progress
                if current_time >= self.end_time:
                    self.proceed_to_next_segment()
            else:
                if self.is_waiting_for_trigger and self.player_controller.platform != self.object:
                    return
                self.proceed_to_next_segment()
                self.is_active = True
                # self.start_time = bge.logic.getClockTime()
                # self.end_time = self.start_time + self.travel_times_by_segment[self.current_segment_index]
                # self.start_position = self.waypoints[self.current_segment_index].worldPosition

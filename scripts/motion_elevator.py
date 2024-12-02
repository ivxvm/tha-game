import bge
from collections import OrderedDict

class Elevator(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("TravelTime", 10),
        ("Target", ""),
    ])

    def start(self, args):
        self.travel_time = args["TravelTime"]
        self.start_position = self.object.worldPosition.copy()
        self.displacement = self.object.scene.objects[args["Target"]].worldPosition.copy() - self.start_position
        self.player_controller = self.object.scene.objects["Player.Root"].components["PlayerController"]
        self.start_time = 0
        self.end_time = 0
        self.is_triggered = False
        self.is_finished = False

    def update(self):
        if self.is_finished:
            return
        if self.is_triggered:
            current_time = bge.logic.getClockTime()
            progress = min(1.0, (current_time - self.start_time) / self.travel_time)
            self.object.worldPosition = self.start_position + self.displacement * progress
            if current_time >= self.end_time:
                self.is_finished = True
                print(self.object, "finished moving")
        else:
            if self.player_controller.platform == self.object:
                self.start_time = bge.logic.getClockTime()
                self.end_time = self.start_time + self.travel_time
                self.is_triggered = True
                print(self.object, "started moving")

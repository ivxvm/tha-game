import bge, bpy, os, deltatime
from math import floor
from collections import OrderedDict

class GameStats(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Level Index", 0),
        ("Total Drawings", 0),
        ("Player", bpy.types.Object),
        ("Gems", bpy.types.Collection),
        ("Gem Item Id", "gem"),
        ("Drawing Item Id", "drawing"),
    ])

    def start(self, args):
        self.level_index = args["Level Index"]
        self.total_drawings = args["Total Drawings"]
        self.player = self.object.scene.objects[args["Player"].name]
        self.inventory = self.player.components["Inventory"]
        self.total_gems = len(args["Gems"].objects)
        self.gem_item_id = args["Gem Item Id"]
        self.drawing_item_id = args["Drawing Item Id"]
        self.playtime = 0
        deltatime.init(self)
        self.old_best_time = 9999
        self.old_best_gems = 0
        self.old_best_drawings = 0
        self.collected_drawings = []
        self.load_old_stats()

    def update(self):
        self.playtime += deltatime.update(self)

    def load_old_stats(self):
        stats_file_path = bge.logic.expandPath("//gamestats.txt")
        if not os.path.exists(stats_file_path):
            open(stats_file_path, 'w').close()
        with open(stats_file_path, 'r') as file:
            lines = file.read().splitlines()
            self.old_stats_lines = lines + ['']*(self.level_index + 1 - len(lines))
            try:
                level_stats = lines[self.level_index]
                [stats_str, collected_drawings_str] = level_stats.split(";")
                [time, gems, _, drawings, _] = stats_str.split(",")
                self.old_best_time = int(time)
                self.old_best_gems = int(gems)
                self.old_best_drawings = int(drawings)
                self.collected_drawings = [int(x) for x in collected_drawings_str.split(",")]
            except:
                pass

    def save_stats(self):
        stats_file_path = bge.logic.expandPath("//gamestats.txt")
        with open(stats_file_path, 'w') as file:
            for i in range(len(self.old_stats_lines)):
                if i == self.level_index:
                    self.current_gems = self.inventory.items.get(self.gem_item_id, 0)
                    if self.current_gems > self.old_best_gems or (self.current_gems == self.old_best_gems and self.playtime < self.old_best_time):
                        file.write(",".join(str(x) for x in [floor(self.playtime), self.current_gems, self.total_gems]))
                    else:
                        file.write(",".join(str(x) for x in [self.old_best_time, self.old_best_gems, self.total_gems]))
                    file.write(",")
                    file.write(",".join(str(x) for x in [len(self.collected_drawings), self.total_drawings]))
                    file.write(";")
                    file.write(",".join(str(x) for x in self.collected_drawings))
                    file.write("\n")
                else:
                    file.write(self.old_stats_lines[i])
                    file.write("\n")

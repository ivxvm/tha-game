import os, bge, bpy, deltatime
from math import floor
from collections import OrderedDict

STATS_FILE_PATH = bge.logic.expandPath("//gamestats.txt")

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
        self.load_old_stats()

    def update(self):
        self.playtime += deltatime.update(self)

    def load_old_stats(self):
        if not os.path.exists(STATS_FILE_PATH):
            open(STATS_FILE_PATH, 'w').close()
        with open(STATS_FILE_PATH, 'r') as file:
            lines = file.read().splitlines()
            self.old_stats_lines = lines + ['']*(self.level_index + 1 - len(lines))
            try:
                level_stats = lines[self.level_index]
                [time, gems, _, drawings, _] = level_stats.split(",")
                self.old_best_time = int(time)
                self.old_best_gems = int(gems)
                self.old_best_drawings = int(drawings)
                print("")
            except:
                pass

    def save_stats(self):
        with open(STATS_FILE_PATH, 'w') as file:
            for i in range(len(self.old_stats_lines)):
                if i == self.level_index:
                    self.current_gems = self.inventory.items.get(self.gem_item_id, 0)
                    best_gems_result = max(self.old_best_gems, self.current_gems)
                    if best_gems_result != self.old_best_gems or self.playtime < self.old_best_time:
                        file.write(",".join(str(x) for x in [floor(self.playtime), self.current_gems, self.total_gems]))
                    else:
                        file.write(",".join(str(x) for x in [self.old_best_time, self.old_best_gems, self.total_gems]))
                    file.write(",")
                    self.current_drawings = self.inventory.items.get(self.drawing_item_id, 0)
                    file.write(",".join(str(x) for x in [self.current_drawings, self.total_drawings]))
                    file.write("\n")
                else:
                    file.write(self.old_stats_lines[i])
                    file.write("\n")

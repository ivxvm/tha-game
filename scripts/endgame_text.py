import bge, bpy
from collections import OrderedDict

class EndgameText(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Time Text", bpy.types.Object),
        ("Gems Text", bpy.types.Object),
        ("Press Enter Text", bpy.types.Object),
        ("Game Stats", bpy.types.Object),
    ])

    def start(self, args):
        self.time_text = self.object.scene.objects[args["Time Text"].name]
        self.gems_text = self.object.scene.objects[args["Gems Text"].name]
        self.press_enter_text = self.object.scene.objects[args["Press Enter Text"].name]
        self.game_stats = self.object.scene.objects[args["Game Stats"].name].components["GameStats"]
        self.set_hierarchy_visible(self.time_text, False)
        self.set_hierarchy_visible(self.gems_text, False)
        self.press_enter_text.visible = False

    def activate(self):
        time_text = "Time: %d" % int(self.game_stats.playtime)
        gems_text = "Gems: %d/%d" % (self.game_stats.current_gems, self.game_stats.total_gems)
        self.set_hierarchy_text(self.time_text, time_text)
        self.set_hierarchy_text(self.gems_text, gems_text)
        self.set_hierarchy_visible(self.time_text, True)
        self.set_hierarchy_visible(self.gems_text, True)
        self.press_enter_text.visible = True

    def set_hierarchy_text(self, object, text):
        object["Text"] = text
        object.children[0]["Text"] = text

    def set_hierarchy_visible(self, object, value):
        object.visible = value
        object.children[0].visible = value

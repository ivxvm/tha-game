import bge, bpy, deltatime
from collections import OrderedDict

class EndgameText(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Time Text", bpy.types.Object),
        ("Gems Text", bpy.types.Object),
        ("Press Enter Text", bpy.types.Object),
        ("Player", bpy.types.Object),
        ("Gems", bpy.types.Collection),
        ("Gem Item Id", "gem"),
    ])

    def start(self, args):
        self.time_text = self.object.scene.objects[args["Time Text"].name]
        self.gems_text = self.object.scene.objects[args["Gems Text"].name]
        self.press_enter_text = self.object.scene.objects[args["Press Enter Text"].name]
        self.player = self.object.scene.objects[args["Player"].name]
        self.gem_item_id = args["Gem Item Id"]
        self.total_gems = len(args["Gems"].objects)
        self.playtime = 0
        self.set_hierarchy_visible(self.time_text, False)
        self.set_hierarchy_visible(self.gems_text, False)
        self.press_enter_text.visible = False
        deltatime.init(self)

    def update(self):
        self.playtime += deltatime.update(self)

    def activate(self):
        inventory = self.player.components["Inventory"]
        gems_amount = inventory.items.get(self.gem_item_id, 0)
        time_text = "Time: %d" % int(self.playtime)
        gems_text = "Gems: %d/%d" % (gems_amount, self.total_gems)
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

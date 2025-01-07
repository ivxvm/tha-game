import bge, bpy
from collections import OrderedDict

ABSENT_HEALTH_HEART_TRANSPARENCY = 0.9

class HudHealth(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Player", bpy.types.Object),
        ("Heart Icon 1", bpy.types.Object),
        ("Heart Icon 2", bpy.types.Object),
        ("Heart Icon 3", bpy.types.Object),
    ])

    def start(self, args):
        self.player_controller = self.object.scene.objects[args["Player"].name].components["PlayerController"]
        self.heart_icon_1 = args["Heart Icon 1"]
        self.heart_icon_2 = args["Heart Icon 2"]
        self.heart_icon_3 = args["Heart Icon 3"]
        self.last_synced_hp = -1

    def update(self):
        if self.last_synced_hp != self.player_controller.hp:
            print("syncing hp", self.player_controller.hp)
            if self.player_controller.hp < 3:
                self.heart_icon_1["transparency"] = ABSENT_HEALTH_HEART_TRANSPARENCY
            if self.player_controller.hp < 2:
                self.heart_icon_2["transparency"] = ABSENT_HEALTH_HEART_TRANSPARENCY
            if self.player_controller.hp < 1:
                self.heart_icon_3["transparency"] = ABSENT_HEALTH_HEART_TRANSPARENCY
            self.heart_icon_1.data.update()
            self.heart_icon_2.data.update()
            self.heart_icon_3.data.update()
            self.last_synced_hp = self.player_controller.hp

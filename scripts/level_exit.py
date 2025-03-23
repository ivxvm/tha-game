import bge, bpy, deltatime
from collections import OrderedDict

class LevelExit(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Range", 2.0),
        ("Binding Speed", 10.0),
        ("Elevation Speed", 0.1),
        ("Rotation Speed", 1.0),
        ("Player Scale", 0.5),
        ("Player", bpy.types.Object),
        ("Game Stats", bpy.types.Object),
        ("Endgame Text", bpy.types.Object),
    ])

    def start(self, args):
        self.range = args["Range"]
        self.binding_speed = args["Binding Speed"]
        self.elevation_speed = args["Elevation Speed"]
        self.rotation_speed = args["Rotation Speed"]
        self.endgame_text = self.object.scene.objects[args["Endgame Text"].name].components["EndgameText"]
        self.game_stats = self.object.scene.objects[args["Game Stats"].name].components["GameStats"]
        self.player_scale = args["Player Scale"]
        self.player = self.object.scene.objects[args["Player"].name]
        self.player_rig = self.player.children["Player.Rig"]
        self.player_controller = self.player.components["PlayerController"]
        self.is_active = False
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        player_vec = self.object.worldPosition - self.player.worldPosition
        if self.is_active:
            dz = self.elevation_speed * delta
            player_vec.z = 0
            self.player.applyMovement(player_vec * self.binding_speed * delta, False)
            self.player.applyMovement([0, 0, dz], False)
            self.object.applyMovement([0, 0, dz], False)
            self.player_rig.applyRotation([0, 0, -self.rotation_speed * delta], False)
            scale = self.player.worldScale.x
            scale = max(self.player_scale, scale * 0.99)
            self.player.worldScale = [scale] * 3
        elif player_vec.magnitude <= self.range:
            self.game_stats.save_stats()
            self.endgame_text.activate()
            self.player_controller.is_blocked = True
            self.player_rig.stopAction()
            self.player.suspendPhysics()
            self.is_active = True

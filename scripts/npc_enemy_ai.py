import bge, bpy
from collections import OrderedDict

PATROLLING_EPSILON = 1.0

STATE_INIT = "STATE_INIT"
STATE_IDLE = "STATE_IDLE"
STATE_PATROLLING = "STATE_PATROLLING"
STATE_STALKING = "STATE_STALKING"
STATE_ATTACKING = "STATE_ATTACKING"

def get_animation_definition(object):
    return bge.logic.getCurrentScene().objects[object.name].components["AnimationDefinition"]

class NpcEnemyAi(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Max Idle Time", 5.0),
        ("Melee Range", 2.0),
        ("Idle Animation", bpy.types.Object),
        ("Walk Animation", bpy.types.Object),
        ("Attack Animation", bpy.types.Object),
        ("Weapon Trail", bpy.types.Object),
        ("Player", bpy.types.Object),
    ])

    def start(self, args):
        self.max_idle_time = args["Max Idle Time"]
        self.melee_range = args["Melee Range"]
        self.idle_animation = get_animation_definition(args["Idle Animation"])
        self.walk_animation = get_animation_definition(args["Walk Animation"])
        self.attack_animation = get_animation_definition(args["Attack Animation"])
        self.rig = self.object.children[0]
        self.animation_player = self.rig.components["AnimationPlayer"]
        self.movement = self.object.components["NpcMovement"]
        self.nav = self.object.components["Navigator"]
        self.weapon_trail = self.object.scene.objects[args["Weapon Trail"].name].components["WeaponTrail"]
        self.player = self.object.scene.objects[args["Player"].name]
        self.state = STATE_INIT
        self.idle_time = 0.0
        self.patrolling_waypoints = []
        self.patrolling_target_waypoint_index = 0
        self.speed = 1.0
        self.prev_frame_timestamp = bge.logic.getClockTime()

    def update(self):
        timestamp = bge.logic.getClockTime()
        delta = timestamp - self.prev_frame_timestamp
        if self.state == STATE_INIT:
            self.transition_idle()
        elif self.state == STATE_IDLE:
            self.process_idle(delta)
            self.stalk_player_if_visible()
        elif self.state == STATE_PATROLLING:
            self.process_patrolling(delta)
            self.stalk_player_if_visible()
        elif self.state == STATE_STALKING:
            self.process_stalking(delta)
        elif self.state == STATE_ATTACKING:
            self.process_attacking(delta)
        self.prev_frame_timestamp = timestamp

    def process_idle(self, delta):
        self.idle_time += delta
        if self.idle_time > self.max_idle_time and len(self.patrolling_waypoints) > 0:
            return self.transition_patrolling()

    def process_patrolling(self, delta):
        next_path_position = self.nav.get_next_path_position()
        if self.nav.is_navigation_finished():
            return self.transition_idle()
        else:
            self.movement.target_position = next_path_position

    def process_stalking(self, delta):
        if self.is_attack_available(self.player):
            self.transition_attacking(self.player)
        else:
            self.nav.update_target_position(self.player.worldPosition)
            self.movement.target_position = self.nav.get_next_path_position()
            if self.movement.is_still:
                self.animation_player.play(self.idle_animation.name)
                self.movement.rotate_towards(self.player)
                if not self.is_target_visible(self.player):
                    self.transition_idle()
            else:
                self.animation_player.play(self.walk_animation.name)

    def process_attacking(self, delta):
        if self.animation_player.is_playing(self.attack_animation.name):
            if not self.weapon_trail.is_active and self.animation_player.get_playback_progress() > 0.25:
                self.weapon_trail.activate()
            return
        if self.is_attack_available(self.player):
            self.animation_player.play(self.attack_animation.name)
        else:
            self.weapon_trail.deactivate()
            self.transition_stalking(self.player)

    def transition_idle(self):
        print("[npc_enemy_ai] transition_idle")
        self.movement.deactivate()
        self.animation_player.play(self.idle_animation.name)
        self.idle_time = 0
        self.state = STATE_IDLE

    def transition_patrolling(self):
        print("[npc_enemy_ai] transition_patrolling")
        self.patrolling_target_waypoint_index = (self.patrolling_target_waypoint_index + 1) % len(self.patrolling_waypoints)
        self.nav.update_target_position(self.patrolling_waypoints[self.patrolling_target_waypoint_index].worldPosition)
        self.movement.activate()
        self.animation_player.play(self.walk_animation.name)
        self.state = STATE_PATROLLING

    def transition_stalking(self, target):
        print("[npc_enemy_ai] transition_stalking")
        self.movement.activate()
        self.animation_player.play(self.walk_animation.name)
        self.state = STATE_STALKING

    def transition_attacking(self, target):
        print("[npc_enemy_ai] transition_attacking")
        self.movement.deactivate()
        self.animation_player.play(self.attack_animation.name)
        self.state = STATE_ATTACKING

    def stalk_player_if_visible(self):
        if self.is_target_visible(self.player):
            self.transition_stalking(self.player)

    def is_target_visible(self, target):
        hit_target, _, _ = self.object.rayCast(target)
        return hit_target == target

    def is_attack_available(self, target):
        if target:
            return (self.object.worldPosition - target.worldPosition).magnitude < self.melee_range
        else:
            return False

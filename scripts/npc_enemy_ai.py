import bge, bpy, deltatime
from collections import OrderedDict

STATE_INIT = "STATE_INIT"
STATE_IDLE = "STATE_IDLE"
STATE_PATROLLING = "STATE_PATROLLING"
STATE_STALKING = "STATE_STALKING"
STATE_ATTACKING = "STATE_ATTACKING"
STATE_BURNING = "STATE_BURNING"
STATE_BURSTING = "STATE_BURSTING"

TARGET_RAYCAST_MASK = 4
PATROLLING_EPSILON = 1.0

class NpcEnemyAi(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Max Idle Time", 5.0),
        ("Min Stalking Time", 1.0),
        ("Stalk Check Debounce Interval", 0.25),
        ("Melee Range", 2.0),
        ("Burning Duration", 1.0),
        ("Burst Duration", 0.25),
        ("Burning Particles Object", bpy.types.Object),
        ("Burst Particles Object", bpy.types.Object),
        ("Npc Model", bpy.types.Object),
        ("Player", bpy.types.Object),
        ("Weapon Rig", bpy.types.Object),
        ("Weapon Model", bpy.types.Object),
        ("Weapon Trail", bpy.types.Object),
        ("Weapon-In-Hand Bone", "Weapon"),
        ("Weapon-On-Back Bone", "WeaponBack"),
        ("Idle Animation", "Idle"),
        ("Walk Animation", "Running"),
        ("Attack Animation", "AttackingWalking"),
        ("Burning Animation", "Burning"),
    ])

    def start(self, args):
        self.max_idle_time = args["Max Idle Time"]
        self.min_stalking_time = args["Min Stalking Time"]
        self.stalk_check_debounce_interval = args["Stalk Check Debounce Interval"]
        self.melee_range = args["Melee Range"]
        self.burning_duration = args["Burning Duration"]
        self.burst_duration = args["Burst Duration"]
        self.idle_animation_name = args["Idle Animation"]
        self.walk_animation_name = args["Walk Animation"]
        self.attack_animation_name = args["Attack Animation"]
        self.burning_animation_name = args["Burning Animation"]
        self.burning_particle_player = self.object.scene.objects[args["Burning Particles Object"].name].components["ParticlePlayer"]
        self.burst_particle_player = self.object.scene.objects[args["Burst Particles Object"].name].components["ParticlePlayer"]
        self.movement = self.object.components["NpcMovement"]
        self.nav = self.object.components["Navigator"]
        self.weapon_rig = self.object.scene.objects[args["Weapon Rig"].name]
        self.weapon_model = self.object.scene.objects[args["Weapon Model"].name]
        self.weapon_trail_model = self.object.scene.objects[args["Weapon Trail"].name]
        self.weapon_trail = self.weapon_trail_model.components["WeaponTrail"]
        self.weapon_in_hand_bone = args["Weapon-In-Hand Bone"]
        self.weapon_on_back_bone = args["Weapon-On-Back Bone"]
        self.npc_model = self.object.scene.objects[args["Npc Model"].name]
        self.player = self.object.scene.objects[args["Player"].name]
        self.player_controller = self.player.components["PlayerController"]
        self.burning_scream_sound = self.object.actuators["BurningScreamSound"]
        self.burning_fire_sound = self.object.actuators["BurningFireSound"]
        self.bursting_sound = self.object.actuators["BurstingSound"]
        self.unsheath_sound = self.object.actuators["SwordUnsheathSound"]
        self.sheath_sound = self.object.actuators["SwordSheathSound"]
        self.sword_whoosh_sounds = [self.object.actuators["SwordWhooshSound1"],
                                    self.object.actuators["SwordWhooshSound2"]]
        self.rig = self.object.children[0]
        self.animation_player = self.rig.components["AnimationPlayer"]
        self.state = STATE_INIT
        self.idle_time = 0.0
        self.patrolling_waypoints = []
        self.patrolling_target_waypoint_index = 0
        self.speed = 1.0
        self.burning_elapsed = 0.0
        self.bursting_elapsed = 0.0
        self.last_stalk_check_timestamp = bge.logic.getClockTime()
        self.stalking_duration = 0
        self.attack_phase = 0
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        if self.state == STATE_INIT:
            self.original_movement_speed = self.movement.movement_speed
            self.transition_idle()
        elif self.state == STATE_IDLE:
            self.process_idle(delta)
            self.stalk_player_if_visible_and_reachable()
        elif self.state == STATE_PATROLLING:
            self.process_patrolling(delta)
            self.stalk_player_if_visible_and_reachable()
        elif self.state == STATE_STALKING:
            self.process_stalking(delta)
        elif self.state == STATE_ATTACKING:
            self.process_attacking(delta)
        elif self.state == STATE_BURNING:
            self.process_burning(delta)
        elif self.state == STATE_BURSTING:
            self.process_bursting(delta)

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
        if self.player_controller.hp <= 0:
            self.transition_idle()
        elif self.is_melee_reachable(self.player):
            self.transition_attacking(self.player)
        else:
            self.nav.update_target_position(self.player.worldPosition)
            self.movement.target_position = self.nav.get_next_path_position()
            if self.movement.is_still:
                self.animation_player.play(self.idle_animation_name)
                self.movement.rotate_towards(self.player.worldPosition)
                if self.stalking_duration > self.min_stalking_time:
                    self.transition_idle()
            else:
                self.animation_player.play(self.walk_animation_name)
        self.stalking_duration += delta

    def process_attacking(self, delta):
        if self.animation_player.is_playing(self.attack_animation_name):
            progress = self.animation_player.get_playback_progress()
            if progress > 0:
                if not self.weapon_trail.is_active:
                    self.weapon_trail.activate()
                if progress > 0.5 and self.attack_phase == 1:
                    self.sword_whoosh_sounds[1].startSound()
                    self.attack_phase = 0
                if progress > 0.75:
                    self.set_speed_modifier(0.5)
                else:
                    self.set_speed_modifier(0.75)
            self.movement.target_position = self.player.worldPosition
        elif self.is_melee_reachable(self.player) and self.player_controller.hp > 0:
            self.animation_player.play(self.attack_animation_name)
            self.sword_whoosh_sounds[0].startSound()
            self.attack_phase = 1
        else:
            self.weapon_trail.deactivate()
            self.set_speed_modifier(1.0)
            self.transition_stalking(self.player)

    def process_burning(self, delta):
        self.burning_elapsed += delta
        if self.burning_elapsed >= self.burning_duration:
            self.transition_bursting()

    def process_bursting(self, delta):
        self.bursting_elapsed += delta
        if self.bursting_elapsed >= self.burst_duration + 1.0:
            parent_collection = self.object.blenderObject.users_collection[0]
            for object in parent_collection.objects:
                gameobject = self.object.scene.objects[object.name]
                gameobject.endObject()

    def transition_idle(self):
        print("[npc_enemy_ai] transition_idle")
        self.movement.deactivate()
        self.set_weapon_bone(self.weapon_on_back_bone)
        self.animation_player.play(self.idle_animation_name)
        self.idle_time = 0
        if self.state == STATE_STALKING:
            self.sheath_sound.startSound()
        self.state = STATE_IDLE

    def transition_patrolling(self):
        print("[npc_enemy_ai] transition_patrolling")
        self.patrolling_target_waypoint_index = (self.patrolling_target_waypoint_index + 1) % len(self.patrolling_waypoints)
        self.nav.update_target_position(self.patrolling_waypoints[self.patrolling_target_waypoint_index].worldPosition)
        self.movement.activate()
        self.animation_player.play(self.walk_animation_name)
        self.state = STATE_PATROLLING

    def transition_stalking(self, target):
        print("[npc_enemy_ai] transition_stalking")
        self.movement.activate()
        self.set_weapon_bone(self.weapon_in_hand_bone)
        self.animation_player.play(self.walk_animation_name)
        if self.state == STATE_IDLE:
            self.unsheath_sound.startSound()
        self.stalking_duration = 0
        self.state = STATE_STALKING

    def transition_attacking(self, target):
        print("[npc_enemy_ai] transition_attacking")
        self.set_speed_modifier(0.75)
        self.animation_player.play(self.attack_animation_name)
        self.sword_whoosh_sounds[0].startSound()
        self.attack_phase = 1
        self.state = STATE_ATTACKING

    def transition_burning(self):
        self.movement.deactivate()
        self.animation_player.play(self.burning_animation_name)
        self.burning_particle_player.play(self.burning_duration)
        self.burning_scream_sound.startSound()
        self.burning_fire_sound.startSound()
        self.state = STATE_BURNING

    def transition_bursting(self):
        self.npc_model.visible = False
        self.weapon_model.visible = False
        self.weapon_trail_model.visible = False
        self.burst_particle_player.play(self.burst_duration)
        self.bursting_sound.startSound()
        self.state = STATE_BURSTING

    def set_weapon_bone(self, name):
        weapon_bone = self.weapon_rig.blenderObject.pose.bones.get("Bone")
        target_bone = self.rig.blenderObject.pose.bones.get(name)
        weapon_bone.constraints["Copy Location"].subtarget = target_bone.name
        weapon_bone.constraints["Copy Rotation"].subtarget = target_bone.name

    def stalk_player_if_visible_and_reachable(self):
        now = bge.logic.getClockTime()
        delta = now - self.last_stalk_check_timestamp
        if delta >= self.stalk_check_debounce_interval:
            if self.is_target_visible(self.player):
                self.movement.rotate_towards(self.player.worldPosition)
                self.nav.update_target_position(self.player.worldPosition)
                is_player_reachable = self.nav.is_target_reachable() or self.is_melee_reachable(self.player)
                if is_player_reachable and self.player_controller.hp > 0:
                    print("[npc_enemy_ai] player reachable")
                    self.transition_stalking(self.player)
                else:
                    print("[npc_enemy_ai] player unreachable")
            self.last_stalk_check_timestamp = now

    def is_target_visible(self, target):
        hit_target, _, _ = self.object.rayCast(target, mask=TARGET_RAYCAST_MASK)
        return hit_target == target

    def is_melee_reachable(self, target):
        return (self.object.worldPosition - target.worldPosition).magnitude < self.melee_range

    def burn(self):
        if self.state != STATE_BURNING and self.state != STATE_BURSTING:
            self.transition_burning()

    def set_speed_modifier(self, speed_modifier):
        self.movement.movement_speed = self.original_movement_speed * speed_modifier

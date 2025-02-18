import bge, bpy, math, constants, utils, deltatime
from collections import OrderedDict
from mathutils import Vector, Matrix

PLATFORM_RAYCAST_MASK = 1 | 2

POWERUP_MULTI_JUMP = "Multi Jump"
POWERUP_FLAMETHROWER = "Flamethrower"

STATE_IDLE = "STATE_IDLE"
STATE_RUNNING = "STATE_RUNNING"
STATE_FALLING = "STATE_FALLING"
STATE_CASTING = "STATE_CASTING"

class PlayerController(bge.types.KX_PythonComponent):
    """My take on platformer-like 3rd person player controller"""

    args = OrderedDict([
        ("Move Speed", 0.1),
        ("Pre Falling Eta", 0.1),
        ("Platform Change Cooldown", 0.1),
        ("Restart Delay", 3.0),
        ("Flamethrower Duration", 2.0),
        ("Flamethrower Raycast Delay", 0.5),
        ("Flamethrower Range", 3.0),
        ("Player Rig", bpy.types.Object),
        ("Proxy Physics", bpy.types.Object),
        ("Game Over Text", bpy.types.Object),
        ("Idle Animation", "Idle"),
        ("Running Animation", "Running"),
        ("Jumping Animation", "Jumping"),
        ("Falling Animation", "Falling"),
        ("Casting Animation", "Casting"),
        ("Dying Animation", "Dying"),
        ("Dead Animation", "Dead"),
    ])

    def start(self, args):
        self.move_speed = args["Move Speed"]
        self.platform_change_cooldown = args["Platform Change Cooldown"]
        self.restart_delay = args["Restart Delay"]
        self.flamethrower_duration = args["Flamethrower Duration"]
        self.flamethrower_raycast_delay = args["Flamethrower Raycast Delay"]
        self.flamethrower_range = args["Flamethrower Range"]
        self.proxy_physics = self.object.scene.objects[args["Proxy Physics"].name].components["ProxyPhysics"]
        self.proxy_physics.on_hit = self.handle_hit_proxy_physics
        self.particle_player = self.object.scene.objects["Player.ParticlePlayer"].components["ParticlePlayer"]
        self.character = bge.constraints.getCharacter(self.object)
        self.camera_pivot = self.object.children["Player.CameraPivot"]
        self.respawn_tracker = self.object.components["RespawnTracker"]
        self.respawn_tracker.on_bind_anchor = self.handle_bind_anchor
        self.blinking = self.object.components["Blinking"]
        self.rig = self.object.scene.objects[args["Player Rig"].name]
        self.animation_player = self.rig.components["AnimationPlayer"]
        self.jump_sound = self.object.actuators["JumpSound"]
        self.flamethrower_sound = self.object.actuators["FlamethrowerSound"]
        self.respawn_sound = self.object.actuators["RespawnSound"]
        self.death_sound = self.object.actuators["DeathSound"]
        self.game_over_text = self.object.scene.objects[args["Game Over Text"].name]
        self.game_over_text.visible = False
        self.idle_animation_name = args["Idle Animation"]
        self.running_animation_name = args["Running Animation"]
        self.jumping_animation_name = args["Jumping Animation"]
        self.falling_animation_name = args["Falling Animation"]
        self.casting_animation_name = args["Casting Animation"]
        self.dying_animation_name = args["Dying Animation"]
        self.dead_animation_name = args["Dead Animation"]
        self.pre_falling_eta = args["Pre Falling Eta"]
        self.pre_falling_delta = 0
        self.state = STATE_IDLE
        self.last_grounded_timestamp = bge.logic.getClockTime()
        self.last_platform_change_timestamp = bge.logic.getClockTime()
        self.prev_platform_position = Vector([0, 0, 0])
        self.prev_platform_orientation = Matrix.Rotation(0, 4, "Z")
        self.platform_raycast_vec = Vector([0, 0, -1.5])
        self.platform = None
        self.hp = 3
        self.powerup = ""
        self.multijumps_left = 0
        self.multijumps_done = 0
        self.anchor_powerup = ""
        self.anchor_multijumps_left = 0
        self.anchor_multijumps_done = 0
        self.is_initialized = False
        self.is_dying = False
        self.is_blocked = False
        self.is_jumping = False
        self.is_casting = False
        self.casting_elapsed = 0.0
        self.animation_player.play(self.idle_animation_name)
        deltatime.init(self)

    def update(self):
        if not self.is_initialized:
            self.is_initialized = True
            is_first_start = bge.logic.globalDict.get("is_first_start", True)
            if is_first_start:
                bge.logic.globalDict["is_first_start"] = False
            self.respawn_at_last_bound_anchor(silent=is_first_start)

        if self.is_blocked:
            return

        delta = deltatime.update(self)

        is_dying = self.update_dying_status()
        if not is_dying:
            self.update_respawn_request()
            self.update_movement(delta)
            self.update_platform()
            self.update_jumping()
            self.update_casting(delta)

    def update_respawn_request(self):
        if bge.logic.keyboard.events[bge.events.RKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            if self.hp > 1:
                self.hp -= 1
                self.respawn_at_last_bound_anchor()
            else:
                self.object.sendMessage("restart")

    def update_dying_status(self):
        now = bge.logic.getClockTime()

        if self.is_dying:
            delta = now - self.death_timestamp
            if delta >= self.restart_delay:
                self.object.sendMessage("restart")
            if not self.rig.isPlayingAction():
                self.animation_player.play(self.dead_animation_name)
            return True
        elif self.hp <= 0:
            self.is_dying = True
            self.death_timestamp = bge.logic.getClockTime()
            self.rig.stopAction()
            self.animation_player.play(self.dying_animation_name)
            utils.trigger_all_components(self.game_over_text)
            self.game_over_text.visible = True
            return True

        return False

    def update_movement(self, delta):
        keyboard = bge.logic.keyboard.events

        speed_x = 0
        speed_y = 0

        if not self.is_casting:
            if keyboard[bge.events.AKEY]:
                speed_x -= 1
            if keyboard[bge.events.DKEY]:
                speed_x += 1
            if keyboard[bge.events.WKEY]:
                speed_y += 1
            if keyboard[bge.events.SKEY]:
                speed_y -= 1

        speed_vec = Vector([speed_x, speed_y, 0])
        speed_vec.normalize()
        speed_vec *= self.move_speed

        move_vec = self.camera_pivot.worldOrientation @ speed_vec * delta
        move_vec[2] = 0
        self.object.applyMovement(move_vec, False)

        is_running = speed_x != 0 or speed_y != 0

        self.set_running(is_running)
        self.set_grounded(self.character.onGround)

        if is_running:
            move_vec.normalize()
            self.rig.worldOrientation = move_vec.to_track_quat("Y","Z").to_euler()

    def update_platform(self):
        now = bge.logic.getClockTime()

        if now - self.last_platform_change_timestamp > self.platform_change_cooldown:
            platform_changed = False
            if self.character.onGround:
                self.character.maxJumps = 1
                self.is_jumping = False
                hit_target = self.raycast_platform()
                if hit_target and self.platform != hit_target:
                    self.platform = hit_target
                    platform_changed = True
                    self.prev_platform_position = Vector(self.platform.worldPosition)
                    self.prev_platform_orientation = self.platform.worldOrientation.copy()
            else:
                if self.platform:
                    self.platform = None
                    platform_changed = True
            if platform_changed:
                self.last_platform_change_timestamp = now
                print("self.platform =", self.platform)

        if self.platform:
            current_platform_position = Vector(self.platform.worldPosition)
            movement_deltas = current_platform_position - self.prev_platform_position
            self.object.applyMovement(movement_deltas, False)
            self.prev_platform_position = current_platform_position

            current_platform_orientation = self.platform.worldOrientation
            delta_rotation_z = (current_platform_orientation.to_euler().z - self.prev_platform_orientation.to_euler().z)
            if delta_rotation_z != 0.0:
                v = self.object.worldPosition - current_platform_position
                v.rotate(Matrix.Rotation(delta_rotation_z, 4, "Z"))
                self.object.worldPosition = current_platform_position + v
                self.object.applyRotation(Vector([0, 0, delta_rotation_z]), False)
                self.prev_platform_orientation = current_platform_orientation.copy()

    def update_jumping(self):
        keyboard = bge.logic.keyboard.events
        is_jump_just_pressed = keyboard[bge.events.SPACEKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED

        if keyboard[bge.events.SPACEKEY]:
            if self.platform or is_jump_just_pressed and self.raycast_platform():
                self.character.jump()
                self.is_jumping = True
                self.jump_sound.pitch = 1.0
                self.jump_sound.startSound()
            elif self.powerup == POWERUP_MULTI_JUMP:
                if is_jump_just_pressed:
                    if self.is_jumping:
                        self.multijumps_left -= 1
                        self.multijumps_done += 1
                    self.character.maxJumps = self.character.jumpCount + 1
                    self.character.jump()
                    self.is_jumping = True
                    self.jump_sound.pitch = 1.0 + self.multijumps_done
                    self.jump_sound.startSound()
                    self.animation_player.play(self.jumping_animation_name)
                    if self.multijumps_left <= 0:
                        self.powerup = ""
                        self.multijumps_done = 0

    def update_casting(self, delta):
        mouse = bge.logic.mouse.events

        if mouse[bge.events.LEFTMOUSE]:
            if self.powerup == POWERUP_FLAMETHROWER and not self.is_casting:
                self.is_casting = True
                self.casting_elapsed = 0.0
                self.set_casting(True)
                self.particle_player.play(self.flamethrower_duration, self.handle_flamethrower_end)
                self.flamethrower_sound.startSound()

        if self.is_casting:
            self.casting_elapsed += delta
            forward = self.camera_pivot.worldOrientation @ constants.AXIS_Y
            forward[2] = 0
            self.rig.worldOrientation = forward.to_track_quat("Y","Z").to_euler()

            if self.powerup == POWERUP_FLAMETHROWER and self.casting_elapsed >= self.flamethrower_raycast_delay:
                forward = self.camera_pivot.worldOrientation @ constants.AXIS_Y
                forward[2] = 0
                raycast_from = self.object.worldPosition + Vector((0, 0, 1))
                raycast_to = raycast_from + forward.normalized() * self.flamethrower_range
                hit_target, _, _ = self.object.rayCast(raycast_to, raycast_from, mask=0b1000)
                if hit_target:
                    hit_target.components["NpcEnemyAi"].burn()

    def raycast_platform(self):
        position = self.object.worldPosition
        hit_target, _, _ = self.object.rayCast(position + self.platform_raycast_vec, mask=PLATFORM_RAYCAST_MASK)
        return hit_target

    def respawn_at_last_bound_anchor(self, silent=False):
        anchor = self.respawn_tracker.last_bound_anchor
        self.proxy_physics.deactivate()
        self.object.worldPosition = anchor.worldPosition.copy()
        for object in [self.camera_pivot, self.rig]:
            object.alignAxisToVect(anchor.getAxisVect(constants.AXIS_Y), 1)
            object.alignAxisToVect(constants.AXIS_Z, 2)
        self.object.scene.active_camera = self.camera_pivot.children[0]
        self.powerup = self.anchor_powerup
        self.multijumps_left = self.anchor_multijumps_left
        self.multijumps_done = self.anchor_multijumps_done
        if not silent:
            self.respawn_sound.startSound()
            self.blinking.activate()

    def handle_flamethrower_end(self):
        self.is_casting = False
        self.set_casting(False)
        self.powerup = ""

    def handle_hit_proxy_physics(self, direction, knockback, damage):
        if not self.proxy_physics.is_active:
            was_already_dead = self.hp <= 0
            self.hp -= damage
            self.proxy_physics.activate()
            self.proxy_physics.object.setLinearVelocity(direction * knockback)
            direction[2] = 0
            if knockback > 0:
                self.rig.worldOrientation = direction.to_track_quat("-Y","Z").to_euler()
            if self.hp <= 0:
                if knockback > 0:
                    self.proxy_physics.object.worldOrientation = direction.to_track_quat("-Y","Z").to_euler()
                    self.proxy_physics.object.applyRotation([math.pi / 2, 0, 0], True)
                if not was_already_dead:
                    self.death_sound.startSound()

    def handle_bind_anchor(self, anchor):
        self.anchor_powerup = self.powerup
        self.anchor_multijumps_left = self.multijumps_left
        self.anchor_multijumps_done = self.multijumps_done
        print("binding respawn anchor:", anchor, anchor.worldPosition)

    def set_running(self, value):
        if self.state == STATE_IDLE:
            if value:
                self.rig.stopAction()
                self.animation_player.play(self.running_animation_name)
                self.state = STATE_RUNNING
                print("self.state", self.state)
        elif self.state == STATE_RUNNING:
            if not value:
                self.rig.stopAction()
                self.animation_player.play(self.idle_animation_name)
                self.animation_player.play(self.idle_animation_name)
                self.state = STATE_IDLE
                print("self.state", self.state)

    def set_grounded(self, value):
        current_grounded_timestamp = bge.logic.getClockTime()
        if self.state == STATE_FALLING:
            if value:
                self.rig.stopAction()
                self.animation_player.play(self.idle_animation_name)
                self.state = STATE_IDLE
                print("self.state", self.state)
        elif self.state != STATE_CASTING:
            if not value:
                self.pre_falling_delta += current_grounded_timestamp - self.last_grounded_timestamp
                if self.is_jumping or self.pre_falling_delta > self.pre_falling_eta:
                    self.rig.stopAction()
                    self.animation_player.play(self.falling_animation_name)
                    self.state = STATE_FALLING
                    self.pre_falling_delta = 0
                    print("self.state", self.state)
            else:
                self.pre_falling_delta = 0
        self.last_grounded_timestamp = current_grounded_timestamp

    def set_casting(self, value):
        if value and self.state != STATE_CASTING:
            self.rig.stopAction()
            self.animation_player.play(self.casting_animation_name)
            self.state = STATE_CASTING
        elif not value and self.state == STATE_CASTING:
            self.rig.stopAction()
            self.animation_player.play(self.idle_animation_name)
            self.state = STATE_IDLE

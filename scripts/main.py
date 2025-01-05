import bge, bpy, constants, deltatime
from collections import OrderedDict
from mathutils import Vector, Matrix

POWERUP_MULTI_JUMP = "Multi Jump"
POWERUP_FLAMETHROWER = "Flamethrower"

class PlayerController(bge.types.KX_PythonComponent):
    """My take on platformer-like 3rd person player controller"""

    args = OrderedDict([
        ("Move Speed", 0.1),
        ("Pre Falling Eta", 0.1),
        ("Platform Change Cooldown", 0.1),
        ("Flamethrower Duration", 2.0),
        ("Flamethrower Raycast Delay", 0.5),
        ("Flamethrower Range", 3.0),
        ("Proxy Physics", bpy.types.Object),
    ])

    def start(self, args):
        self.move_speed = args["Move Speed"]
        self.platform_change_cooldown = args["Platform Change Cooldown"]
        self.flamethrower_duration = args["Flamethrower Duration"]
        self.flamethrower_raycast_delay = args["Flamethrower Raycast Delay"]
        self.flamethrower_range = args["Flamethrower Range"]
        self.proxy_physics = self.object.scene.objects[args["Proxy Physics"].name].components["ProxyPhysics"]
        self.proxy_physics.on_hit = self.handle_hit_proxy_physics
        self.particle_player = self.object.scene.objects["Player.ParticlePlayer"].components["ParticlePlayer"]
        self.character = bge.constraints.getCharacter(self.object)
        self.camera_pivot = self.object.children["Player.CameraPivot"]
        self.model = self.object.children["Player.Model"]
        self.jump_sound = self.object.actuators["JumpSound"]
        self.flamethrower_sound = self.object.actuators["FlamethrowerSound"]
        self.player_animator = PlayerAnimator(
            armature=self.model,
            speed=1.0,
            pre_falling_eta=args["Pre Falling Eta"])
        self.platform_raycast_vec = Vector([0, 0, -1.5])
        self.platform = None
        self.prev_platform_position = Vector([0, 0, 0])
        self.prev_platform_orientation = Matrix.Rotation(0, 4, "Z")
        self.last_platform_change_timestamp = bge.logic.getClockTime()
        self.powerup = ""
        self.multijumps_left = 0
        self.multijumps_done = 0
        self.is_casting = False
        self.casting_elapsed = 0.0
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)

        keyboard = bge.logic.keyboard.events
        mouse = bge.logic.mouse.events

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

        self.player_animator.set_running(is_running)
        self.player_animator.set_grounded(self.character.onGround)

        if is_running:
            move_vec.normalize()
            self.model.worldOrientation = move_vec.to_track_quat("Y","Z").to_euler()
        elif self.is_casting:
            self.casting_elapsed += delta
            forward = self.camera_pivot.worldOrientation @ constants.AXIS_Y
            forward[2] = 0
            self.model.worldOrientation = forward.to_track_quat("Y","Z").to_euler()

        now = bge.logic.getClockTime()

        if now - self.last_platform_change_timestamp > self.platform_change_cooldown:
            platform_changed = False
            if self.character.onGround:
                position = self.object.worldPosition
                hit_target, _, _ = self.object.rayCast(position + self.platform_raycast_vec, mask=0x1)
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

        if keyboard[bge.events.SPACEKEY]:
            if self.platform:
                self.character.jump()
                self.jump_sound.pitch = 1.0
                self.jump_sound.startSound()
            elif self.powerup == POWERUP_MULTI_JUMP:
                if keyboard[bge.events.SPACEKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
                    self.multijumps_left -= 1
                    self.multijumps_done += 1
                    self.character.jump()
                    self.jump_sound.pitch = 1.0 + self.multijumps_done
                    self.jump_sound.startSound()
                    self.player_animator.play_jumping()
                    if self.multijumps_left <= 0:
                        self.powerup = ""
                        self.multijumps_done = 0

        if mouse[bge.events.LEFTMOUSE]:
            if self.powerup == POWERUP_FLAMETHROWER and not self.is_casting:
                self.is_casting = True
                self.casting_elapsed = 0.0
                self.player_animator.set_casting(True)
                self.particle_player.play(self.flamethrower_duration, self.on_flamethrower_end)
                self.flamethrower_sound.startSound()

        if self.powerup == POWERUP_FLAMETHROWER:
            if self.particle_player.is_playing and self.casting_elapsed >= self.flamethrower_raycast_delay:
                forward = self.camera_pivot.worldOrientation @ constants.AXIS_Y
                forward[2] = 0
                raycast_from = self.object.worldPosition + Vector((0, 0, 1))
                raycast_to = raycast_from + forward.normalized() * self.flamethrower_range
                hit_target, _, _ = self.object.rayCast(raycast_to, raycast_from, mask=0b1000)
                if hit_target:
                    hit_target.components["NpcEnemyAi"].burn()

        self.player_animator.update()

    def on_flamethrower_end(self):
        self.is_casting = False
        self.player_animator.set_casting(False)
        self.powerup = ""

    def handle_hit_proxy_physics(self, direction, knockback):
        if not self.proxy_physics.is_active:
            self.proxy_physics.activate()
            self.proxy_physics.object.setLinearVelocity(direction * knockback)

class PlayerAnimator():
    def __init__(self, armature, speed, pre_falling_eta):
        self.armature = armature
        self.speed = speed
        self.pre_falling_eta = pre_falling_eta
        self.state = "IDLE"
        self.play_idle()
        self.last_grounded_timestamp = bge.logic.getClockTime()
        self.pre_falling_delta = 0

    def set_running(self, value):
        if self.state == "IDLE":
            if value:
                self.armature.stopAction()
                self.play_running()
                self.state = "RUNNING"
                print("self.state", self.state)
        elif self.state == "RUNNING":
            if not value:
                self.armature.stopAction()
                self.play_idle()
                self.state = "IDLE"
                print("self.state", self.state)

    def set_grounded(self, value):
        current_grounded_timestamp = bge.logic.getClockTime()
        if self.state == "FALLING":
            if value:
                self.armature.stopAction()
                self.play_idle()
                self.state = "IDLE"
                print("self.state", self.state)
        elif self.state != "JUMPING" and self.state != "CASTING":
            if not value:
                self.pre_falling_delta += current_grounded_timestamp - self.last_grounded_timestamp
                if self.pre_falling_delta > self.pre_falling_eta:
                    self.armature.stopAction()
                    self.play_falling()
                    self.state = "FALLING"
                    self.pre_falling_delta = 0
                    print("self.state", self.state)
            else:
                self.pre_falling_delta = 0
        self.last_grounded_timestamp = current_grounded_timestamp

    def set_casting(self, value):
        if value and self.state != "CASTING":
            self.armature.stopAction()
            self.play_casting()
            self.state = "CASTING"
        elif not value and self.state == "CASTING":
            self.armature.stopAction()
            self.play_idle()
            self.state = "IDLE"

    def update(self):
        pass

    def play_idle(self):
        self.armature.playAction("Idle", 0, 16, 0, 0, 0, 1, 0, 0, self.speed * 0.5)

    def play_running(self):
        self.armature.playAction("Running", 0, 20, 0, 0, 0, 1, 0, 0, self.speed)

    def play_jumping(self):
        self.armature.playAction("Jumping", 4, 8, 0, 0, 0, 0, 0, 0, self.speed * 2)

    def play_falling(self):
        self.armature.playAction("Falling", 0, 32, 0, 0, 0, 1, 0, 0, self.speed)

    def play_casting(self):
        self.armature.playAction("Casting", 0, 16, 0, 0, 0, 1, 0, 0, self.speed)

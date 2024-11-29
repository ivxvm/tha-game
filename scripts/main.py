import bge
from collections import OrderedDict
from mathutils import Vector, Matrix

class PlayerController(bge.types.KX_PythonComponent):
    """My take on platformer-like 3rd person player controller"""

    args = OrderedDict([
        ("Move Speed", 0.1),
        ("Pre Falling Eta", 0.1),
    ])

    def start(self, args):
        self.move_speed = args['Move Speed']
        self.character = bge.constraints.getCharacter(self.object)
        self.camera_pivot = self.object.children['Player.CameraPivot']
        self.model = self.object.children['Player.Model']
        self.player_animator = PlayerAnimator(
            armature=self.model,
            speed=1.0,
            pre_falling_eta=args['Pre Falling Eta'],
            on_jump_animation_end=self.on_jump_animation_end)
        self.platform_raycast_vec = Vector([0, 0, -1.5])
        self.platform = None
        self.prev_platform_position = Vector([0, 0, 0])

    def on_jump_animation_end(self):
        self.character.jump()

    def update(self):
        keyboard = bge.logic.keyboard.events

        speed_x = 0
        speed_y = 0

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

        move_vec = self.camera_pivot.worldOrientation @ speed_vec
        move_vec[2] = 0
        self.object.applyMovement(move_vec, False)

        is_running = speed_x != 0 or speed_y != 0

        self.player_animator.set_running(is_running)
        self.player_animator.set_grounded(self.character.onGround)

        if is_running:
            move_vec.normalize()
            self.model.worldOrientation = move_vec.to_track_quat('Y','Z').to_euler()

        if self.character.onGround:
            if not self.platform:
                position = self.object.worldPosition
                hit_target, _, _ = self.object.rayCast(position + self.platform_raycast_vec, mask=0x1)
                if hit_target:
                    self.platform = hit_target
                    self.prev_platform_position = Vector(self.platform.worldPosition)
                    print("self.platform =", self.platform)
        else:
            if self.platform:
                self.platform = None
                print("self.platform =", self.platform)

        if self.platform:
            current_platform_position = Vector(self.platform.worldPosition)
            deltas = current_platform_position - self.prev_platform_position
            self.object.applyMovement(deltas, False)
            self.prev_platform_position = current_platform_position

        if keyboard[bge.events.SPACEKEY]:
            if self.platform:
                self.player_animator.start_jumping()

        self.player_animator.update()

class PlayerAnimator():
    def __init__(self, armature, speed, pre_falling_eta, on_jump_animation_end):
        self.armature = armature
        self.speed = speed
        self.pre_falling_eta = pre_falling_eta
        self.state = "IDLE"
        self.play_idle()
        self.on_jump_animation_end = on_jump_animation_end
        self.last_grounded_timestamp = bge.logic.getClockTime()
        self.pre_falling_delta = 0

    def set_running(self, value):
        if self.state == "IDLE":
            if value:
                self.armature.stopAction()
                self.play_running()
                self.state = "RUNNING"
        elif self.state == "RUNNING":
            if not value:
                self.armature.stopAction()
                self.play_idle()
                self.state = "IDLE"

    def set_grounded(self, value):
        current_grounded_timestamp = bge.logic.getClockTime()
        if self.state == "FALLING":
            if value:
                self.armature.stopAction()
                self.play_idle()
                self.state = "IDLE"
        elif self.state != "JUMPING":
            if not value:
                self.pre_falling_delta += current_grounded_timestamp - self.last_grounded_timestamp
                if self.pre_falling_delta > self.pre_falling_eta:
                    self.armature.stopAction()
                    self.play_falling()
                    self.state = "FALLING"
                    self.pre_falling_delta = 0
            else:
                self.pre_falling_delta = 0
        self.last_grounded_timestamp = current_grounded_timestamp

    def start_jumping(self):
        print("self.state", self.state)
        if self.state != "JUMPING":
            print("start_jumping")
            self.armature.stopAction()
            self.play_jumping()
            self.state = "JUMPING"

    def update(self):
        if self.state == "JUMPING":
            if not self.armature.isPlayingAction():
                self.on_jump_animation_end()
                self.play_falling()
                self.state = "FALLING"

    def play_idle(self):
        self.armature.playAction('Idle', 0, 16, 0, 0, 0, 1, 0, 0, self.speed * 0.5)

    def play_running(self):
        self.armature.playAction('Running', 0, 20, 0, 0, 0, 1, 0, 0, self.speed)

    def play_jumping(self):
        self.armature.playAction('Jumping', 0, 8, 0, 0, 0, 0, 0, 0, self.speed * 2)

    def play_falling(self):
        self.armature.playAction('Falling', 0, 32, 0, 0, 0, 1, 0, 0, self.speed)

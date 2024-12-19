import bge, bpy
from collections import OrderedDict

class AnimationPlayer(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Animation Definitions", bpy.types.Collection)
    ])

    def start(self, args):
        self.animation_definitions = args["Animation Definitions"]
        self.is_initialized = False
        self.animations = {}
        self.current_animation_name = ""

    def update(self):
        if self.is_initialized:
            return
        for object in self.animation_definitions.objects:
            gameobject = self.object.scene.objects[object.name]
            animdef = gameobject.components.get("AnimationDefinition", None)
            if animdef:
                self.animations[animdef.name] = animdef
        self.is_initialized = True

    def play(self, name):
        is_playing = self.object.isPlayingAction()
        if name == self.current_animation_name and is_playing:
            return
        animdef = self.animations.get(name, None)
        if animdef:
            if is_playing:
                self.object.stopAction()
            self.object.playAction(
                animdef.name,
                animdef.start_frame,
                animdef.end_frame,
                animdef.layer,
                animdef.priority,
                animdef.blendin,
                animdef.play_mode,
                animdef.layer_weight,
                animdef.ipo_flags,
                animdef.speed,
                animdef.blend_mode)
            self.current_animation_name = name

    def is_playing(self, name):
        return self.object.isPlayingAction() and name == self.current_animation_name

    def get_playback_progress(self):
        current_animdef = self.animations.get(self.object.getActionName())
        if current_animdef:
            return self.object.getActionFrame() / current_animdef.end_frame
        else:
            return 0

import bge
from collections import OrderedDict
from animation_definition import AnimationDefinition

class AnimationPlayer(bge.types.KX_PythonComponent):
    args = OrderedDict([])

    def start(self, args):
        self.is_initialized = False
        self.animations = {}
        self.current_animation_name = ""

    def update(self):
        if self.is_initialized:
            return
        for component in self.object.components:
            if isinstance(component, AnimationDefinition):
                self.animations[component.name] = component
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

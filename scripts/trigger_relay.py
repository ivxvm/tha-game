import bge, bpy
from collections import OrderedDict
import deltatime

class TriggerRelay(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Delay1", 0.0),
        ("Target1", bpy.types.Object),
        ("Delay2", 0.0),
        ("Target2", bpy.types.Object),
        ("Delay3", 0.0),
        ("Target3", bpy.types.Object),
        ("Delay4", 0.0),
        ("Target4", bpy.types.Object),
    ])

    def start(self, args):
        self.delays = []
        self.targets = []
        for i in range(1, 5):
            delay = args.get(f"Delay{i}", 0.0)
            target = args.get(f"Target{i}", None)
            self.delays.append(delay)
            self.targets.append(target and self.object.scene.objects[target.name])
        self.current_index = 0
        self.elapsed = 0.0
        self.is_active = False
        deltatime.init(self)

    def update(self):
        delta = deltatime.update(self)
        if self.is_active:
            self.elapsed += delta
            while True:
                current_delay = self.delays[self.current_index]
                current_target = self.targets[self.current_index]
                if self.elapsed >= current_delay:
                    if not current_target:
                        self.is_active = False
                        return
                    for component in current_target.components:
                        try:
                            component.trigger()
                        except AttributeError:
                            pass
                    self.current_index += 1
                    self.elapsed = self.elapsed - current_delay
                else:
                    break
            if self.current_index > len(self.delays):
                self.is_active = False

    def trigger(self):
        if not self.is_active:
            self.current_index = 0
            self.elapsed = 0.0
            self.is_active = True

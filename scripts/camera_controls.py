import bge, bpy
from collections import OrderedDict

# Designed to be placed on camera pivot object
class CameraControls(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Look Sensitivity", 0.002),
        ("Zoom Sensitivity", 1.0),
        ("Min Camera Distance", 3.0),
        ("Max Camera Distance", 20.0),
        ("Camera", bpy.types.Object),
    ])

    def start(self, args):
        self.look_sensitivity = args["Look Sensitivity"]
        self.zoom_sensitivity = args["Zoom Sensitivity"]
        self.min_camera_distance = args["Min Camera Distance"]
        self.max_camera_distance = args["Max Camera Distance"]
        self.camera = self.object.scene.objects[args["Camera"].name]
        self.mouse = self.object.sensors["Mouse"]
        self.camera_distance = self.min_camera_distance

    def update(self):
        mouse_events = bge.logic.mouse.events
        if mouse_events[bge.events.WHEELUPMOUSE]:
            self.camera_distance = max(self.min_camera_distance, self.camera_distance - self.zoom_sensitivity)
        if mouse_events[bge.events.WHEELDOWNMOUSE]:
            self.camera_distance = min(self.max_camera_distance, self.camera_distance + self.zoom_sensitivity)

        direction = (self.camera.worldPosition - self.object.worldPosition).normalized()
        self.camera.worldPosition = self.object.worldPosition + direction * self.camera_distance

        screen_center_x = bge.render.getWindowWidth() // 2
        screen_center_y = bge.render.getWindowHeight() // 2
        dx = screen_center_x - self.mouse.position[0]
        dy = screen_center_y - self.mouse.position[1]
        bge.render.setMousePosition(screen_center_x, screen_center_y)
        self.object.applyRotation([0, 0, dx * self.look_sensitivity], False)
        self.object.applyRotation([dy * self.look_sensitivity, 0, 0], True)

        hit_target, hit_position, _ = self.object.rayCast(self.camera.worldPosition, mask=0x1)
        if hit_target:
            self.camera.worldPosition = hit_position

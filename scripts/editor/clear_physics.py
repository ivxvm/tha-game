import bpy

for obj in bpy.context.selected_objects:
    obj.game.physics_type = "NO_COLLISION"

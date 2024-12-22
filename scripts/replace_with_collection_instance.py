import bpy
for obj in bpy.context.selected_objects:
    bpy.ops.object.collection_instance_add(collection='Level1.Gem', location=obj.location, rotation=obj.rotation_euler)
    bpy.context.active_object.scale = obj.scale
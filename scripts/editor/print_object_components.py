import bpy
import copy

for obj in bpy.context.selected_objects:
    print("\n: Components of [% s]" % obj.name)
    for component in obj.game.components:
        print("  *", component.name)
        for property in component.properties:
            print("    >", property.name, "=", property.value)

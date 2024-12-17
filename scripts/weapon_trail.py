import bge, bpy
from collections import OrderedDict

class WeaponTrail(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Owner", bpy.types.Object),
        ("Player", bpy.types.Object),
        ("Reinstance Physics Mesh Interval", 0.2),
    ])

    def start(self, args):
        self.owner = self.object.scene.objects[args["Owner"].name]
        self.player = self.object.scene.objects[args["Player"].name]
        self.player_controller = self.player.components["PlayerController"]
        self.reinstance_interval = args["Reinstance Physics Mesh Interval"]
        self.cooldown = 0
        self.prev_frame_timestamp = bge.logic.getClockTime()
        self.object.collisionCallbacks.append(self.onCollision)

    def update(self):
        timestamp = bge.logic.getClockTime()
        delta = timestamp - self.prev_frame_timestamp
        self.cooldown -= delta
        if self.cooldown <= 0:
            self.object.reinstancePhysicsMesh(evaluated=True)
            self.cooldown = self.reinstance_interval
        self.prev_frame_timestamp = timestamp

    def onCollision(self, other, point):
        if other == self.player:
            # print("point", point)
            self.player_controller.hit(other.worldPosition - self.owner.worldPosition)
        # pickup = other.components.get("Pickup")
        # if pickup and pickup.active:
            # print(self, "collided with pickup", pickup.item_id)
            # self.items[pickup.item_id] = self.items.get(pickup.item_id, 0) + pickup.item_amount
            # pickup.active = False
            # other.endObject()
            # print(self.items)

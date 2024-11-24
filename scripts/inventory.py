import bge
from collections import OrderedDict

class Inventory(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([])

    def start(self, args):
        self.items = OrderedDict([])
        self.object.collisionCallbacks.append(self.onCollision)

    def onCollision(self, other):
        pickup = other.components.get("Pickup")
        if pickup and pickup.active:
            print(self, "collided with pickup", pickup.item_id)
            self.items[pickup.item_id] = self.items.get(pickup.item_id, 0) + pickup.item_amount
            pickup.active = False
            other.endObject()
            print(self.items)

    def update(self):
        # Put your code executed every logic step here.
        # self.object is the owner object of this component.
        # self.object.scene is the main scene.
        pass

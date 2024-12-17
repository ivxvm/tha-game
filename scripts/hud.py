import bge, bpy
from collections import OrderedDict

class ItemAmountInvalidator(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Target Object", bpy.types.Object),
        ("Target Item Id", "coin"),
    ])

    def start(self, args):
        target_object = self.object.scene.objects[args["Target Object"].name]
        self.item_id = args["Target Item Id"]
        self.inventory = target_object.components["Inventory"]
        self.last_item_amount = 0

    def update(self):
        current_item_amount = self.inventory.items.get(self.item_id, 0)
        if current_item_amount != self.last_item_amount:
            print("updating item amount to", current_item_amount)
            self.last_item_amount = current_item_amount
            self.object["Text"] = str(current_item_amount)

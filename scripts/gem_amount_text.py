import bge, bpy
from collections import OrderedDict

class GemAmountText(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Player", bpy.types.Object),
        ("Gems", bpy.types.Collection),
        ("Gem Item Id", "gem"),
    ])

    def start(self, args):
        target_object = self.object.scene.objects[args["Player"].name]
        self.item_id = args["Gem Item Id"]
        self.inventory = target_object.components["Inventory"]
        self.total = len(args["Gems"].objects)
        self.last_item_amount = -1

    def update(self):
        current_item_amount = self.inventory.items.get(self.item_id, 0)
        if current_item_amount != self.last_item_amount:
            self.last_item_amount = current_item_amount
            self.object["Text"] = "%d/%d" % (current_item_amount, self.total)

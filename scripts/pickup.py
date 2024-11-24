import bge
from collections import OrderedDict

class Pickup(bge.types.KX_PythonComponent):
    
    args = OrderedDict([
        ("Item Id", "coin"),
        ("Item Amount", 1),
        ("Turn Speed", 0.1),
        ("Active", True),
    ])

    def start(self, args):
        self.item_id = args['Item Id']
        self.item_amount = args['Item Amount']
        self.turn_speed = args['Turn Speed']
        self.active = args['Active']

    def update(self):
        if not self.active:
            return
        self.object.applyRotation((0, 0,  self.turn_speed), True)

import bge
from collections import OrderedDict

TRIGGER_ACTION_DEACTIVATE = "Deactivate"
TRIGGER_ACTION_REMOVE = "Remove"
TRIGGER_ACTION_HIDE = "Hide"

class Pickup(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Item Id", "gem"),
        ("Item Amount", 1),
        ("Trigger Action", {TRIGGER_ACTION_DEACTIVATE, TRIGGER_ACTION_REMOVE, TRIGGER_ACTION_HIDE}),
    ])

    def start(self, args):
        self.item_id = args['Item Id']
        self.item_amount = args['Item Amount']
        self.trigger_action = args['Trigger Action']
        self.is_active = True

    # Triggered from Inventory component
    def trigger(self):
        if not self.is_active:
            return
        for component in self.object.components:
            if component != self:
                try:
                    component.trigger()
                except AttributeError:
                    pass
        if self.trigger_action == TRIGGER_ACTION_REMOVE:
            self.object.endObject()
        elif self.trigger_action == TRIGGER_ACTION_HIDE:
            self.object.visible = False
        self.is_active = False

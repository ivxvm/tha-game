import bge
from collections import OrderedDict

TRIGGER_ACTION_DEACTIVATE = "Deactivate"
TRIGGER_ACTION_REMOVE = "Remove"

class Pickup(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Item Id", "gem"),
        ("Item Amount", 1),
        ("Trigger Action", {TRIGGER_ACTION_DEACTIVATE, TRIGGER_ACTION_REMOVE}),
    ])

    def start(self, args):
        self.item_id = args['Item Id']
        self.item_amount = args['Item Amount']
        self.trigger_action = args['Trigger Action']
        self.is_active = True

    def trigger(self):
        if not self.is_active:
            return
        for component in self.object.components:
            if component != self:
                try:
                    component.trigger()
                except AttributeError:
                    pass
        if self.trigger_action == TRIGGER_ACTION_DEACTIVATE:
            self.is_active = False
        elif self.trigger_action == TRIGGER_ACTION_REMOVE:
            self.object.endObject()

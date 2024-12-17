import bge
from collections import OrderedDict

class EnemyController(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    def start(self, args):
        self.speed = 1.0
        self.object.playAction("Attacking", 0, 28, 0, 0, 0, 1, 0, 0, self.speed)

    def update(self):
        pass

import bge, bpy
from collections import OrderedDict

class Drawing(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Drawing ID", 0),
        ("Game Stats", bpy.types.Object),
    ])

    def start(self, args):
        self.drawing_id = args["Drawing ID"]
        self.game_stats = self.object.scene.objects[args["Game Stats"].name].components["GameStats"]
        self.is_checked = False

    def update(self):
        if not self.is_checked:
            if self.drawing_id in self.game_stats.collected_drawings:
                self.object.endObject()
            self.is_checked = True

    def trigger(self):
        print("[Drawing] adding drawing #%d to collected_drawings" % self.drawing_id)
        self.game_stats.collected_drawings.append(self.drawing_id)

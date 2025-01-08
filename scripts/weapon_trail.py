import bge, bpy, bmesh
from collections import OrderedDict
import deltatime

class WeaponTrail(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Owner", bpy.types.Object),
        ("Weapon", bpy.types.Object),
        ("Reinstance Physics Mesh Interval", 0.2),
    ])

    def start(self, args):
        self.owner = self.object.scene.objects[args["Owner"].name]
        self.weapon = args["Weapon"]
        self.reinstance_interval = args["Reinstance Physics Mesh Interval"]
        self.cooldown = 0
        self.is_active = False
        # self.object.worldPosition = [0, 0, 0]
        # self.deactivate()
        self.trail_bm = bmesh.new()
        self.trail_bm.from_mesh(self.object.blenderObject.data)
        self.weapon_bm = bmesh.new()
        self.weapon_bm.from_mesh(self.weapon.data)
        self.weapon_bm.verts.ensure_lookup_table()
        self.last_vertex_row = []
        self.vertex_age = OrderedDict()
        self.face_groups = []
        deltatime.init(self)

    def update(self):
        if not self.is_active:
            return
        delta = deltatime.update(self)
        self.cooldown -= delta
        if self.cooldown <= 0:
            new_vertex_row = []
            for vertex in self.weapon_bm.verts:
                # print("vert.co", vertex.co)
                # print("self.weapon.worldTransform @ vert.co", self.weapon.worldTransform @ vert.co)
                # print("self.weapon.worldTransform.inverted() @ self.weapon.worldTransform @ vert.co", self.weapon.worldTransform.inverted() @ self.weapon.worldTransform @ vert.co)
                co = self.object.worldTransform.inverted() @ self.weapon.matrix_world @ vertex.co
                new_vertex = self.trail_bm.verts.new(co)
                # new_vertex = bmesh.ops.create_vert(self.trail_bm, co=co)['vert'][0]
                # print("new_vertex", new_vertex)
                new_vertex_row.append(new_vertex)
            # self.trail_bm.verts.ensure_lookup_table()
            if len(self.last_vertex_row) > 0:
                new_faces = []
                for i in range(0, len(new_vertex_row) - 1):
                    new_face = bmesh.ops.contextual_create(self.trail_bm,
                                                           geom=[new_vertex_row[i],
                                                                 new_vertex_row[i + 1],
                                                                 self.last_vertex_row[i + 1],
                                                                 self.last_vertex_row[i],
                                                                 ])["faces"][0]
                    new_faces.append(new_face)
                    # print("new_face", new_face)
                    # print("><", i, i + 1)
                self.face_groups.append(new_faces)
                # print("self.face_groups", self.face_groups)
                if len(self.face_groups) > 3:
                    bmesh.ops.delete(self.trail_bm, geom=self.face_groups[0], context="FACES")
                    self.face_groups = self.face_groups[1:]
                self.trail_bm.to_mesh(self.object.blenderObject.data)
            # vertices_to_delete = []
            # for vertex in self.trail_bm.verts:
            #     # print("vertex.index", vertex.index)
            #     # id = vertex.co.magnitude()
            #     new_age = self.vertex_age.get(vertex.index, 0) + 1
            #     if new_age > 16:
            #         vertices_to_delete.append(vertex)
            #         self.vertex_age[vertex.index] = 0
            #     else:
            #         self.vertex_age[vertex.index] = new_age
            # bmesh.ops.delete(self.trail_bm, geom=vertices_to_delete)
            # self.trail_bm.verts.ensure_lookup_table()
            # print("self.vertex_age", self.vertex_age)
            self.last_vertex_row = new_vertex_row
            self.cooldown = self.reinstance_interval
            # bmesh.ops.contextual_create(self.trail_bm, geom=[])
        #     try:
        #         # depsgraph = bpy.context.evaluated_depsgraph_get()
        #         # vertex_count = len(self.object.blenderObject.evaluated_get(depsgraph).data.vertices)
        #         if True: # vertex_count > 8:
        #             self.object.reinstancePhysicsMesh(evaluated=True)
        #         else:
        #             print("[weapon_trail] weird vertex_count:", vertex_count)
        #     except Exception as e:
        #         print("[weapon_trail] Error during reinstancePhysicsMesh:", e)
        #     self.cooldown = self.reinstance_interval

    def activate(self):
        # self.object.worldTransform = self.owner.worldTransform
        # for modifier in self.object.blenderObject.modifiers:
        #     modifier.show_in_editmode = True
        #     modifier.show_viewport = True
        #     modifier.show_render = True
        # self.object.blenderObject.data.update()
        print("[weapon_trail] activating")
        self.last_vertex_row = []
        self.face_groups = []
        self.is_active = True

    def deactivate(self):
        # self.object.worldPosition = [0, 0, 0]
        # for modifier in self.object.blenderObject.modifiers:
        #     modifier.show_in_editmode = False
        #     modifier.show_viewport = False
        #     modifier.show_render = False
        # self.object.blenderObject.data.update()
        print("[weapon_trail] deactivating")
        bmesh.ops.delete(self.trail_bm, geom=self.trail_bm.verts)
        self.trail_bm.to_mesh(self.object.blenderObject.data)
        self.trail_bm.verts.ensure_lookup_table()
        self.is_active = False

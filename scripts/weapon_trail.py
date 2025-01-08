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
        self.trail_bm = bmesh.new()
        self.trail_bm.from_mesh(self.object.blenderObject.data)
        self.weapon_bm = bmesh.new()
        self.weapon_bm.from_mesh(self.weapon.data)
        self.weapon_bm.verts.ensure_lookup_table()
        self.last_vertex_row = []
        self.face_groups = []
        self.existing_vertices = OrderedDict()
        deltatime.init(self)

    def update(self):
        if not self.is_active:
            return

        delta = deltatime.update(self)
        self.cooldown -= delta

        skip_row = False
        new_vertex_row = []

        for vertex in self.weapon_bm.verts:
            co = self.object.worldTransform.inverted() @ self.weapon.matrix_world @ vertex.co
            key = co.copy()
            key.freeze()
            if self.existing_vertices.get(key, False):
                skip_row = True
                break
            else:
                self.existing_vertices[key] = True
            new_vertex = self.trail_bm.verts.new(co)
            new_vertex_row.append(new_vertex)

        if not skip_row:
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
                self.face_groups.append(new_faces)
                if len(self.face_groups) > 3:
                    face_group = self.face_groups[0]
                    bmesh.ops.delete(self.trail_bm, geom=face_group, context="FACES")
                    self.face_groups = self.face_groups[1:]
                    self.existing_vertices = OrderedDict()
                    for face_group in self.face_groups:
                        for face in face_group:
                            for vert in face.verts:
                                key = vert.co.copy()
                                key.freeze()
                                self.existing_vertices[key] = True
                self.trail_bm.to_mesh(self.object.blenderObject.data)
            self.last_vertex_row = new_vertex_row

        if self.cooldown <= 0:
            if len(self.face_groups) > 0:
                self.object.reinstancePhysicsMesh(evaluated=True)
            self.cooldown = self.reinstance_interval

    def activate(self):
        print("[weapon_trail] activating")
        self.object.worldPosition = self.owner.worldPosition
        bmesh.ops.delete(self.trail_bm, geom=self.trail_bm.verts)
        self.trail_bm.to_mesh(self.object.blenderObject.data)
        self.last_vertex_row = []
        self.face_groups = []
        self.is_active = True

    def deactivate(self):
        print("[weapon_trail] deactivating")
        bmesh.ops.delete(self.trail_bm, geom=self.trail_bm.verts)
        self.trail_bm.to_mesh(self.object.blenderObject.data)
        self.trail_bm.verts.ensure_lookup_table()
        self.is_active = False

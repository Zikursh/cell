"""Export a .blend to a web-sized GLB plus a JSON sidecar (key text, object bounds).
Usage: python3 -I export_model.py model.blend outdir [--preview]
Needs Blender as a Python module: pip install bpy"""
import bpy, sys, json, math
from mathutils import Vector
args = [a for a in sys.argv[1:] if not a.startswith('--')]
blend, out = args[-2], args[-1]
bpy.ops.wm.open_mainfile(filepath=blend)
s = bpy.context.scene; vl = bpy.context.view_layer

# 1. Objects hidden with the eye icon are Boolean cutters: keep them out of renders and the export.
hidden = [o for o in bpy.data.objects if o.hide_get() or o.hide_viewport]
for o in hidden: o.hide_render = True

# 2. Key text, exactly as typed in Blender.
key_text = "\n".join(o.data.body for o in bpy.data.objects if o.type == 'FONT' and not o.hide_get())

def to_mesh(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); vl.objects.active = o
    bpy.ops.object.convert(target='MESH')

# 3. Metaballs and text become meshes (glTF has neither).
for o in [o for o in bpy.data.objects if o.type == 'FONT' and not o.hide_get()]: to_mesh(o)
metas = [o for o in bpy.data.objects if o.type == 'META']
if metas:
    base = min(metas, key=lambda o: o.name)      # the family base owns the evaluated surface
    to_mesh(base); base = vl.objects.active       # convert replaces the metaball with a new mesh object
    for o in [o for o in bpy.data.objects if o.type == 'META']: bpy.data.objects.remove(o)
    bpy.ops.object.select_all(action='DESELECT'); base.select_set(True); vl.objects.active = base
    # One mesh per separate blob, named Mball.p0, Mball.p1, ... from largest to smallest.
    before = set(bpy.data.objects)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')
    blobs = sorted([base] + [o for o in bpy.data.objects if o not in before], key=lambda o: -len(o.data.polygons))
    for i, o in enumerate(blobs): o.name = f"Mball.p{i}"

# 4. Thin out very dense meshes so the page stays small.
for o in bpy.data.objects:
    if o.type != 'MESH' or o in hidden or o.modifiers: continue
    n = len(o.data.vertices)
    ratio = 0.03 if n > 100000 or (n > 5000 and max(o.dimensions) < 0.3) else 0.3 if n > 5000 else None
    if ratio:
        m = o.modifiers.new("web", 'DECIMATE'); m.ratio = ratio
        to_mesh(o)

# 5. World-space bounds of every visible object, in glTF axes (x, z, -y).
vl.update()
info = {}
for o in bpy.data.objects:
    if o.type != 'MESH' or o in hidden: continue
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector(map(min, zip(*pts))); hi = Vector(map(max, zip(*pts)))
    c = (lo + hi) / 2; d = hi - lo
    mat = o.material_slots[0].material if o.material_slots else None
    col = None
    if mat and mat.node_tree:
        for n in mat.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED': col = [round(x, 3) for x in n.inputs['Base Color'].default_value[:3]]
    info[o.name] = dict(c=[round(c.x,3), round(c.z,3), round(-c.y,3)], d=[round(d.x,3), round(d.z,3), round(d.y,3)], col=col, tris=sum(len(p.vertices)-2 for p in o.data.polygons))
json.dump(dict(key_text=key_text, objects=info), open(f"{out}/cell.json", "w"), indent=1)

bpy.ops.export_scene.gltf(filepath=f"{out}/cell.glb", export_format='GLB', use_visible=True, export_apply=True,
                          export_yup=True, export_texcoords=False, export_normals=False, export_animations=False, export_cameras=False, export_lights=False)
print("TRIS", sum(v['tris'] for v in info.values()), "OBJECTS", len(info))

if '--preview' in sys.argv:
    s.render.engine = 'CYCLES'; s.cycles.samples = 24
    s.render.resolution_x, s.render.resolution_y = 1400, 900
    sun = bpy.data.lights.new("s", 'SUN'); sun.energy = 3
    so = bpy.data.objects.new("s", sun); s.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(110))
    for n in s.world.node_tree.nodes:
        if n.type == 'BACKGROUND': n.inputs[0].default_value = (0.9,0.9,0.9,1); n.inputs[1].default_value = 0.8
    cam = bpy.data.cameras.new("c"); co = bpy.data.objects.new("c", cam); s.collection.objects.link(co); s.camera = co
    for name, loc, tgt in [("front", (17,-3.6,2.2), (0,-3.6,2.2)), ("cell", (8,2.5,3.5), (0,0,2)), ("back", (-14,-3,4), (0,-3,2))]:
        co.location = loc; co.rotation_euler = (Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
        s.render.filepath = f"{out}/{name}.png"; bpy.ops.render.render(write_still=True)

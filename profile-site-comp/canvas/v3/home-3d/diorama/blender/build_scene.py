"""Build the 1/12 study diorama in Blender (Cycles) with a 48 s day-night loop and a camera sway.

Coordinates below are written like the web version (x right, y up, z toward the viewer) and converted.
Run: blender -b -P build_scene.py -- <out.blend>
"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else os.path.join(HERE, 'study.blend')
TEX = os.path.join(HERE, 'assets/tex'); MOD = os.path.join(HERE, 'assets/models'); IMG = os.path.join(HERE, 'img')
FPS, CYCLE = 24, 48
FRAMES = FPS * CYCLE            # 1152 frames = one seamless loop
STEP = 3                        # key/render every 3rd frame (8 fps), interpolated to 24 fps later
M_PER_BU = 0.3                  # 1 unit = 30 cm in the room's own scale
rnd = random.Random(1212)

def T(x, y, z): return Vector((x, -z, y))

# ---------- reset ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'; prefs.get_devices()
for d in prefs.devices: d.use = d.type == 'METAL'
scene.cycles.device = 'GPU'
scene.render.fps = FPS
scene.frame_start, scene.frame_end, scene.frame_step = 1, FRAMES, STEP
scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast' if False else 'None'
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
root = bpy.data.collections.new('Diorama'); scene.collection.children.link(root)

# ---------- materials ----------
def nodes_of(mat):
    mat.use_nodes = True
    nt = mat.node_tree; bsdf = nt.nodes.get('Principled BSDF'); return nt, bsdf
def img_node(nt, path, non_color=False):
    n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(path, check_existing=True)
    if non_color: n.image.colorspace_settings.name = 'Non-Color'
    return n
_mats = {}
def pbr(name, tex, scale=1.0, tint=None, rough_mul=1.0, nor=1.0, box=True, extra=None):
    key = (name,)
    if key in _mats: return _mats[key]
    mat = bpy.data.materials.new(name); nt, b = nodes_of(mat)
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs['Object' if box else 'UV'], mp.inputs['Vector'])
    def tx(fn, nc):
        n = img_node(nt, os.path.join(TEX, tex, fn), nc)
        if box: n.projection = 'BOX'; n.projection_blend = 0.25
        nt.links.new(mp.outputs['Vector'], n.inputs['Vector']); return n
    d = tx('diff.jpg', False)
    if tint:
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 1.0
        nt.links.new(d.outputs['Color'], mix.inputs['A']); mix.inputs['B'].default_value = (*tint, 1)
        nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
    else: nt.links.new(d.outputs['Color'], b.inputs['Base Color'])
    if os.path.exists(os.path.join(TEX, tex, 'rough.jpg')):
        r = tx('rough.jpg', True); m = nt.nodes.new('ShaderNodeMath'); m.operation = 'MULTIPLY'; m.inputs[1].default_value = rough_mul
        nt.links.new(r.outputs['Color'], m.inputs[0]); nt.links.new(m.outputs[0], b.inputs['Roughness'])
    if os.path.exists(os.path.join(TEX, tex, 'nor.jpg')):
        n = tx('nor.jpg', True); nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = nor
        nt.links.new(n.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    if extra: extra(b)
    _mats[key] = mat; return mat
def solid(name, color, rough=0.5, metal=0.0, coat=0.0, emission=None):
    if name in _mats: return _mats[name]
    mat = bpy.data.materials.new(name); nt, b = nodes_of(mat)
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    if emission: b.inputs['Emission Color'].default_value = (*emission, 1)
    _mats[name] = mat; return mat
def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
def image_mat(name, fn, rough=0.6, metal=0.0, emissive=False, strength=1.0):
    mat = bpy.data.materials.new(name); nt, b = nodes_of(mat)
    tc = nt.nodes.new('ShaderNodeTexCoord'); n = img_node(nt, os.path.join(IMG, fn))
    nt.links.new(tc.outputs['UV'], n.inputs['Vector'])
    nt.links.new(n.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emissive:
        nt.links.new(n.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = strength
    return mat

WOOD_FLOOR = pbr('floor', 'laminate_floor_02', scale=1 / 5.5, nor=0.6)
PLASTER = pbr('plaster', 'beige_wall_001', scale=1 / 6, tint=(1.12, 1.1, 1.08), nor=0.35)
OAK = pbr('oak', 'oak_veneer_01', scale=1 / 4, rough_mul=0.8, nor=0.4)
WALNUT = pbr('walnut', 'american_walnut_veneer', scale=1 / 4, tint=(1.0, 0.72, 0.5), rough_mul=0.9, nor=0.4)
HINOKI = pbr('hinoki', 'hinoki_planks', scale=1 / 4, nor=0.3)
RUG = pbr('rug', 'fabric_pattern_07', scale=1 / 1.6, tint=(0.62, 0.7, 0.8), nor=0.8)
FABRIC = pbr('chairfab', 'fabric_pattern_05', scale=1 / 0.8, tint=(0.28, 0.32, 0.38), nor=0.8)
PLINTH = solid('plinth', srgb('#1d2226'), 0.28, coat=0.6)
IRON = solid('iron', srgb('#24262a'), 0.35, 0.85)
ALU = solid('alu', srgb('#b9bcc0'), 0.3, 1.0)
BLACK_PLASTIC = solid('blackplastic', srgb('#16171a'), 0.45)
WHITE_PAINT = solid('whitepaint', srgb('#e9e5dd'), 0.45)
RUBBER = solid('rubber', srgb('#141414'), 0.8)
CERAMIC = solid('ceramic', srgb('#f1efe9'), 0.18, coat=0.4)
CORK = solid('cork', srgb('#b08a60'), 0.9)
KEYCAP = solid('keycap', srgb('#d9dcdf'), 0.5)
CAP = solid('cutcap', srgb('#cbbfa8'), 0.9)
BRASS = image_mat('brass_plate', 'plate.png', rough=0.28, metal=0.9)

# emissive materials whose strength follows the time of day
def emissive(name, color, base_color=None, rough=0.4):
    mat = bpy.data.materials.new(name); nt, b = nodes_of(mat)
    b.inputs['Base Color'].default_value = (*(base_color or color), 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Emission Color'].default_value = (*color, 1); b.inputs['Emission Strength'].default_value = 0
    return mat
SHADE = emissive('lampshade', srgb('#ffcf8a'), srgb('#efe6d4'), 0.8)
SOFTBOX = emissive('softbox', srgb('#ffffff'), srgb('#f4f4f2'), 0.9)
SCREEN_A = image_mat('screen_editor', 'screen_editor.png', rough=0.15, emissive=True, strength=1.5)
SCREEN_B = image_mat('screen_channel', 'screen_channel.png', rough=0.15, emissive=True, strength=1.5)

# glass that lets shadow rays through (keeps the sun patch clean)
GLASS = bpy.data.materials.new('glass'); nt, b = nodes_of(GLASS)
out = nt.nodes['Material Output']; nt.nodes.remove(b)
lp = nt.nodes.new('ShaderNodeLightPath'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); gl = nt.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.02
fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = 1.5
m1 = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(fr.outputs[0], m1.inputs[0]); nt.links.new(tr.outputs[0], m1.inputs[1]); nt.links.new(gl.outputs[0], m1.inputs[2])
m2 = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(lp.outputs['Is Shadow Ray'], m2.inputs[0]); nt.links.new(m1.outputs[0], m2.inputs[1]); nt.links.new(tr.outputs[0], m2.inputs[2])
nt.links.new(m2.outputs[0], out.inputs['Surface'])

# window view: three images blended by keyed factors
VIEW = bpy.data.materials.new('outside'); nt, b = nodes_of(VIEW)
out = nt.nodes['Material Output']; nt.nodes.remove(b)
tc = nt.nodes.new('ShaderNodeTexCoord')
imgs = []
for m in ('day', 'dusk', 'night'):
    n = img_node(nt, os.path.join(IMG, f'outside_{m}.png')); nt.links.new(tc.outputs['UV'], n.inputs['Vector']); imgs.append(n)
VIEW_F1 = nt.nodes.new('ShaderNodeValue'); VIEW_F2 = nt.nodes.new('ShaderNodeValue'); VIEW_S = nt.nodes.new('ShaderNodeValue')
mixa = nt.nodes.new('ShaderNodeMix'); mixa.data_type = 'RGBA'; nt.links.new(VIEW_F1.outputs[0], mixa.inputs['Factor']); nt.links.new(imgs[0].outputs['Color'], mixa.inputs['A']); nt.links.new(imgs[1].outputs['Color'], mixa.inputs['B'])
mixb = nt.nodes.new('ShaderNodeMix'); mixb.data_type = 'RGBA'; nt.links.new(VIEW_F2.outputs[0], mixb.inputs['Factor']); nt.links.new(mixa.outputs['Result'], mixb.inputs['A']); nt.links.new(imgs[2].outputs['Color'], mixb.inputs['B'])
em = nt.nodes.new('ShaderNodeEmission'); nt.links.new(mixb.outputs['Result'], em.inputs['Color']); nt.links.new(VIEW_S.outputs[0], em.inputs['Strength'])
nt.links.new(em.outputs[0], out.inputs['Surface'])

# ---------- mesh helpers ----------
def link(obj, parent=None):
    root.objects.link(obj)
    if parent: obj.parent = parent
    return obj
def empty(name, loc, ry=0.0, parent=None):
    e = bpy.data.objects.new(name, None); e.location = loc; e.rotation_euler = (0, 0, ry); return link(e, parent)
def box(name, mat, c, s, parent=None, ry=0.0, bevel=0.02, rx=0.0, rz=0.0):
    """c: centre (web coords, relative to parent), s: (w, h, d) in web axes."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[2], v.co.z * s[1]))
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    o = bpy.data.objects.new(name, me); o.location = T(*c) if parent is None or True else T(*c)
    o.rotation_euler = Euler((rx, rz, ry), 'XYZ')
    me.materials.append(mat); link(o, parent)
    if bevel > 0:
        md = o.modifiers.new('bevel', 'BEVEL'); md.width = min(bevel, min(s) * 0.45); md.segments = 3; md.limit_method = 'ANGLE'; md.harden_normals = False
    return o
def cyl(name, mat, c, r, h, parent=None, axis='Y', verts=32, bevel=0.01, r2=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r if r2 is None else r2, depth=h)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = T(*c)
    if axis == 'Y': o.rotation_euler = (0, 0, 0)         # web up = blender Z (cone default axis)
    elif axis == 'Z': o.rotation_euler = (math.pi / 2, 0, 0)
    elif axis == 'X': o.rotation_euler = (0, math.pi / 2, 0)
    me.materials.append(mat); link(o, parent)
    if bevel > 0: md = o.modifiers.new('bevel', 'BEVEL'); md.width = bevel; md.segments = 2; md.limit_method = 'ANGLE'
    return o
def rod(name, mat, a, b, r, parent=None):
    a, b = T(*a), T(*b); d = b - a
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=r, radius2=r, depth=d.length); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = (a + b) / 2
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    me.materials.append(mat); return link(o, parent)
def sphere(name, mat, c, r, parent=None, scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=r); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = T(*c); o.scale = (scale[0], scale[2], scale[1]); me.materials.append(mat); return link(o, parent)
def plane(name, mat, c, w, h, parent=None, facing='Z', ry=0.0, rz_tilt=0.0):
    """Vertical plane facing web +z (default) or a floor plane (facing='Y')."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * h, 0))
    uv = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        for l in f.loops: l[uv].uv = (l.vert.co.x / w + 0.5, l.vert.co.y / h + 0.5)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = T(*c)
    if facing == 'Z': o.rotation_euler = Euler((math.pi / 2, rz_tilt, ry), 'XYZ')
    me.materials.append(mat); return link(o, parent)
def import_gltf(name, loc, ry=0.0, scale=1 / M_PER_BU, parent=None, keep=None):
    before = set(bpy.data.objects)
    path = [os.path.join(MOD, name, f) for f in os.listdir(os.path.join(MOD, name)) if f.endswith('.gltf')][0]
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    if keep:
        drop = [o for o in new if o.type == 'MESH' and not o.name.endswith(keep)]
        for o in drop: bpy.data.objects.remove(o, do_unlink=True)
        new = [o for o in new if o not in drop]
    holder = empty(name, T(*loc), ry, parent)
    for o in new:
        for c in o.users_collection: c.objects.unlink(o)
        root.objects.link(o)
        if o.parent is None: o.parent = holder
    holder.scale = (scale, scale, scale)
    return holder

# ---------- the room ----------
W, D, WH = 16, 12, 7.6
bz, lx = -D / 2 + 0.15, -W / 2 + 0.15
box('floorbase', PLINTH, (0, -0.175, 0), (W, 0.35, D), bevel=0.01)
plane('floor', WOOD_FLOOR, (0, 0.002, 0), W, D, facing='Y')
box('plinth_top', PLINTH, (0, -0.4, 0), (W, 0.1, D), bevel=0.0)
box('hinoki_frame', HINOKI, (0, -0.46, 0), (W + 0.5, 0.22, D + 0.5), bevel=0.03)
box('plinth_body', PLINTH, (0, -1.17, 0), (W + 1.3, 1.2, D + 1.3), bevel=0.04)
box('plinth_column', PLINTH, (0, -21.75, 0), (W - 2, 40, D - 2), bevel=0.0)
plane('plate', BRASS, (0, -1.17, D / 2 + 0.66), 4.8, 0.62)

wall = lambda n, c, s: box(n, PLASTER, c, s, bevel=0.01)
wall('wall_back_l', (-3.8, WH / 2, bz), (8.4, WH, 0.3)); wall('wall_back_r', (6.3, WH / 2, bz), (3.4, WH, 0.3))
wall('wall_under', (2.5, 1.45, bz), (4.2, 2.9, 0.3)); wall('wall_over', (2.5, 6.9, bz), (4.2, 1.4, 0.3))
wall('wall_left', (lx, WH / 2, 0.15), (0.3, WH, D - 0.3))
box('cap_back', CAP, (0, WH + 0.01, bz), (W, 0.02, 0.3), bevel=0); box('cap_left', CAP, (lx, WH + 0.01, 0.15), (0.3, 0.02, D - 0.3), bevel=0)
box('skirting_b', WHITE_PAINT, (0, 0.15, bz + 0.17), (W - 0.3, 0.3, 0.04), bevel=0.01); box('skirting_l', WHITE_PAINT, (lx + 0.17, 0.15, 0.15), (0.04, 0.3, D - 0.3), bevel=0.01)
# window
for n, c, s in [('sill', (2.5, 2.9, bz + 0.12), (4.5, 0.1, 0.55)), ('head', (2.5, 6.2, bz), (4.4, 0.1, 0.34)),
                ('jamb_l', (0.4, 4.55, bz), (0.1, 3.4, 0.34)), ('jamb_r', (4.6, 4.55, bz), (0.1, 3.4, 0.34)), ('mullion', (2.5, 4.55, bz), (0.08, 3.3, 0.2))]:
    box('win_' + n, WHITE_PAINT, c, s, bevel=0.015)
plane('win_glass', GLASS, (2.5, 4.55, bz - 0.02), 4.1, 3.2)
plane('outside', VIEW, (2.5, 4.55, bz - 0.8), 4.6, 3.6)
for n, c, s in [('t', (2.5, 6.35, bz - 0.45), (4.8, 0.1, 0.8)), ('b', (2.5, 2.75, bz - 0.45), (4.8, 0.1, 0.8)), ('l', (0.2, 4.55, bz - 0.45), (0.1, 3.7, 0.8)), ('r', (4.8, 4.55, bz - 0.45), (0.1, 3.7, 0.8))]:
    box('shroud_' + n, PLASTER, c, s, bevel=0)

# rug
box('rug', RUG, (2.0, 0.02, -1.8), (6.4, 0.04, 4.2), bevel=0.02)

# desk
box('desk_top', OAK, (2.5, 2.4, -4.55), (5.6, 0.12, 2.1), bevel=0.03)
for x in (-0.25, 5.25): box('desk_side', WALNUT, (x, 1.17, -4.55), (0.1, 2.34, 1.9), bevel=0.02)
box('desk_drawers', WALNUT, (4.4, 1.4, -4.55), (1.5, 1.6, 1.8), bevel=0.02)
for i, y in enumerate((1.9, 1.2)):
    box(f'drawer_line{i}', WALNUT, (4.4, y + 0.36, -3.64), (1.44, 0.02, 0.02), bevel=0)
    box(f'handle{i}', ALU, (4.4, y, -3.62), (0.42, 0.04, 0.04), bevel=0.01)

# monitors
monitors = empty('monitors', T(0, 0, 0))
for i, (img, x, ry) in enumerate([(SCREEN_A, 1.35, 0.14), (SCREEN_B, 3.7, -0.14)]):
    g = empty(f'monitor{i}', T(x, 3.5, -5.05), ry, monitors)
    box(f'bezel{i}', BLACK_PLASTIC, (0, 0, -0.035), (2.14, 1.28, 0.07), g, bevel=0.025)
    box(f'back{i}', BLACK_PLASTIC, (0, -0.05, -0.1), (1.2, 0.8, 0.08), g, bevel=0.04)
    plane(f'screen{i}', img, (0, 0.02, 0.002), 2.04, 1.15, g)
    box(f'neck{i}', ALU, (0, -0.85, -0.14), (0.12, 0.62, 0.06), g, bevel=0.02)
    box(f'foot{i}', ALU, (0, -1.09, -0.02), (0.62, 0.025, 0.42), g, bevel=0.01)
# keyboard with key caps, mouse, mug, mic, stationery
kb = box('keyboard', ALU, (2.5, 2.475, -3.95), (1.42, 0.03, 0.48), bevel=0.012)
key = box('key', KEYCAP, (2.5 - 0.64, 2.505, -3.95 - 0.18), (0.075, 0.025, 0.075), bevel=0.008)
ar = key.modifiers.new('ax', 'ARRAY'); ar.count = 14; ar.relative_offset_displace = (1.25, 0, 0)
ar2 = key.modifiers.new('ay', 'ARRAY'); ar2.count = 5; ar2.relative_offset_displace = (0, -1.25, 0)
sphere('mouse', solid('mousewhite', srgb('#e4e6e8'), 0.35), (3.6, 2.5, -3.9), 0.12, scale=(0.75, 0.35, 1.1))
cyl('mug', CERAMIC, (4.75, 2.6, -3.95), 0.12, 0.28, verts=40)
bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.02, location=T(4.9, 2.6, -3.95), rotation=(0, 0, 0))
h = bpy.context.active_object; h.name = 'mug_handle'; h.data.materials.append(CERAMIC)
for c in h.users_collection: c.objects.unlink(h)
root.objects.link(h); h.rotation_euler = (math.pi / 2, 0, 0)
cyl('mic_base', IRON, (4.3, 2.49, -4.4), 0.12, 0.05); rod('mic_stem', IRON, (4.3, 2.5, -4.4), (4.3, 2.8, -4.4), 0.02)
m = cyl('mic', solid('micgrey', srgb('#2b2e33'), 0.3, 0.6), (4.3, 2.98, -4.35), 0.09, 0.34); m.rotation_euler = (0.25, 0, 0)
import_gltf('stationery_supplies', (0.35, 2.46, -4.3), 0.3)
import_gltf('standing_picture_frame_01', (5.0, 2.46, -5.1), -0.4)
import_gltf('desk_lamp_arm_01', (0.1, 2.46, -5.0), 0.8)

# chair
g = empty('chair', T(2.4, 0, -2.3), 0.2)
for k in range(5):
    a = k / 5 * math.tau
    leg = box(f'chair_leg{k}', IRON, (math.sin(a) * 0.45, 0.12, math.cos(a) * 0.45), (0.09, 0.07, 0.9), g, ry=a, bevel=0.02)
    sphere(f'caster{k}', RUBBER, (math.sin(a) * 0.86, 0.07, math.cos(a) * 0.86), 0.07, g)
cyl('chair_gas', ALU, (0, 0.85, 0), 0.055, 1.3, g)
box('chair_seat', FABRIC, (0, 1.58, 0), (1.5, 0.24, 1.45), g, bevel=0.1)
box('chair_back', FABRIC, (0, 2.8, 0.78), (1.4, 1.95, 0.2), g, bevel=0.09)
for sx in (-0.8, 0.8):
    box('arm_post', IRON, (sx, 1.87, 0.1), (0.06, 0.5, 0.06), g, bevel=0.01)
    box('arm_pad', BLACK_PLASTIC, (sx, 2.12, 0.05), (0.14, 0.06, 0.8), g, bevel=0.025)

# bookshelf with books
g = empty('shelf', T(-7.15, 0, -1.0))
Hs, Ls = 6.2, 5
for z in (-Ls / 2, Ls / 2): box('shelf_side', WALNUT, (0, Hs / 2, z), (1.0, Hs, 0.1), g, bevel=0.015)
box('shelf_back', WALNUT, (-0.47, Hs / 2, 0), (0.06, Hs, Ls), g, bevel=0)
book_cols = ['#34597a', '#6b2a24', '#2e4a3a', '#8a7a64', '#d8d2c4', '#44506a', '#5a3e30', '#9aa7b1', '#c9b99a', '#1f2a33']
book_mats = [solid('book' + c, srgb(c), rnd.uniform(0.45, 0.75)) for c in book_cols]
for s in range(5):
    y = 0.08 + s * 1.2; box(f'shelf_board{s}', WALNUT, (0, y, 0), (1.0, 0.08, Ls), g, bevel=0.01)
    if s in (4,): continue
    if s == 2:
        import_gltf('book_encyclopedia_set_01', (0.02, y + 0.04, -0.9), math.pi / 2, parent=None).location = T(-7.13, y + 0.04, -1.9)
        zstart = 0.3
    else: zstart = -Ls / 2 + 0.1
    z = zstart
    while z < Ls / 2 - 0.3:
        bw, bh = rnd.uniform(0.11, 0.24), rnd.uniform(0.62, 1.02)
        if rnd.random() < 0.07: z += 0.45; continue
        lean = rnd.uniform(-0.04, 0.04) if rnd.random() < 0.25 else 0
        box('book', rnd.choice(book_mats), (0.05, y + 0.04 + bh / 2, z + bw / 2), (rnd.uniform(0.62, 0.82), bh, bw - 0.012), g, bevel=0.012, rx=lean)
        z += bw
import_gltf('potted_plant_02', (-7.1, 6.24, 0.8), 0.5)
import_gltf('ceramic_vase_03', (-7.1, 6.24, -2.6), 0.0)

# pegboard with speaker badges, note, calendar, clock
g = empty('pegboard', T(-4.0, 4.55, bz + 0.17))
box('cork', CORK, (0, 0, 0), (3.2, 1.7, 0.05), g, bevel=0.01)
lan = ['#2f4a66', '#6b2a24', '#2e4a3a', '#44506a', '#8a6628']
for i, c in enumerate(lan):
    x = -1.3 + i * 0.65
    box(f'lanyard{i}', solid('lan' + c, srgb(c), 0.8), (x, 0.36, 0.04), (0.035, 0.5, 0.008), g, bevel=0)
    p = plane(f'badge{i}', image_mat(f'badge{i}', f'badge_{i}.png', rough=0.25), (x, -0.2, 0.05), 0.44, 0.6, g, rz_tilt=rnd.uniform(-0.08, 0.08))
g = empty('note', T(-1.1, 4.85, bz + 0.17))
plane('note_paper', image_mat('note', 'note.png', rough=0.85), (0, 0, 0.005), 1.4, 1.05, g, rz_tilt=0.05)
box('note_tape', solid('tape', srgb('#cfe3f0'), 0.5), (0, 0.5, 0.012), (0.4, 0.1, 0.005), g, bevel=0)
g = empty('calendar', T(6.4, 4.6, bz + 0.17))
plane('calendar_paper', image_mat('calendar', 'calendar.png', rough=0.8), (0, 0, 0.005), 1.5, 1.88, g)
import_gltf('wall_clock', (6.4, 6.55, bz + 0.18), 0.0)

# plant, floor lamp, tripod camera, softbox
p = import_gltf('pachira_aquatica_01', (6.8, 0, -4.4), 0.7, keep='_b')
for c in p.children: c.location = (0, 0, 0)
cyl('lamp_base', IRON, (-5.8, 0.04, -4.6), 0.35, 0.08)
rod('lamp_pole', IRON, (-5.8, 0.05, -4.6), (-5.8, 4.9, -4.6), 0.03)
cyl('lamp_shade', SHADE, (-5.8, 5.1, -4.6), 0.5, 0.62, r2=0.36, verts=48, bevel=0)
g = empty('tripod', T(2.3, 0, 1.9), math.pi)
for k in range(3):
    a = k / 3 * math.tau; rod(f'tripod_leg{k}', IRON, (math.sin(a) * 0.7, 0, math.cos(a) * 0.7), (0, 3.1, 0), 0.028, g)
box('cam_body', solid('cambody', srgb('#23262b'), 0.4), (0, 3.35, 0), (0.62, 0.44, 0.36), g, bevel=0.05)
cyl('cam_lens', solid('lens', srgb('#15161a'), 0.2, 0.5), (0, 3.35, 0.34), 0.14, 0.32, g, axis='Z')
g = empty('softbox', T(6.0, 0, -1.4), -0.9)
rod('sb_pole', IRON, (0, 0, 0), (0, 4.4, 0), 0.03, g)
for k in range(3):
    a = k / 3 * math.tau; rod(f'sb_leg{k}', IRON, (0, 0.8, 0), (math.sin(a) * 0.6, 0, math.cos(a) * 0.6), 0.024, g)
sb = box('sb_front', SOFTBOX, (0, 4.4, 0.3), (1.1, 0.9, 0.06), g, bevel=0.01, rx=0.3)
box('sb_housing', solid('sbhouse', srgb('#1c1d20'), 0.7), (0, 4.45, 0.12), (1.2, 1.0, 0.3), g, bevel=0.03, rx=0.3)

# ---------- lights ----------
def point(name, c, energy, radius=0.15, color='#ffffff'):
    L = bpy.data.lights.new(name, 'POINT'); L.energy = 0; L.shadow_soft_size = radius; L.color = srgb(color)
    o = bpy.data.objects.new(name, L); o.location = T(*c); link(o); return L
LAMP_FLOOR = point('floorlamp_light', (-5.8, 4.95, -4.6), 0, 0.3, '#ffc98a')
LAMP_DESK = point('desklamp_light', (0.9, 3.9, -4.3), 0, 0.12, '#ffe2c0')
SB_LIGHT = bpy.data.lights.new('softbox_light', 'AREA'); SB_LIGHT.shape = 'RECTANGLE'; SB_LIGHT.size, SB_LIGHT.size_y = 1.0, 0.8; SB_LIGHT.energy = 0
sbo = bpy.data.objects.new('softbox_light', SB_LIGHT); link(sbo); sbo.location = T(6.0, 4.4, -1.4) + Vector((0, 0, 0))
sbo.rotation_euler = Euler((math.radians(90 - 17), 0, -0.9 + math.pi), 'XYZ')
SUN = bpy.data.lights.new('sun', 'SUN'); SUN.angle = math.radians(1.2)
suno = bpy.data.objects.new('sun', SUN); link(suno)

# ---------- world: sky lights the room, the camera sees a dark backdrop ----------
world = bpy.data.worlds.new('world'); scene.world = world; world.use_nodes = True
nt = world.node_tree; nt.nodes.clear()
sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'MULTIPLE_SCATTERING'; sky.sun_disc = False
bg = nt.nodes.new('ShaderNodeBackground'); nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
night = nt.nodes.new('ShaderNodeBackground'); night.inputs['Color'].default_value = (*srgb('#27324c'), 1)
WORLD_MIX = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(bg.outputs[0], WORLD_MIX.inputs[1]); nt.links.new(night.outputs[0], WORLD_MIX.inputs[2])
cam_bg = nt.nodes.new('ShaderNodeBackground'); cam_bg.inputs['Color'].default_value = (*srgb('#0d141b'), 1); cam_bg.inputs['Strength'].default_value = 1
lpw = nt.nodes.new('ShaderNodeLightPath'); fin = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(lpw.outputs['Is Camera Ray'], fin.inputs[0]); nt.links.new(WORLD_MIX.outputs[0], fin.inputs[1]); nt.links.new(cam_bg.outputs[0], fin.inputs[2])
wout = nt.nodes.new('ShaderNodeOutputWorld'); nt.links.new(fin.outputs[0], wout.inputs['Surface'])
SKY_BG, NIGHT_BG = bg, night

# ---------- cameras ----------
TARGET = T(0.6, 1.8, -0.8)   # near the room's centre so the sway keeps it in place
pivot = empty('pivot', TARGET)
def camera(name, dist, shift_x, shift_y, fstop):
    cd = bpy.data.cameras.new(name); cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.lens = 12 / math.tan(math.radians(15))
    cd.shift_x, cd.shift_y = shift_x, shift_y; cd.clip_start = 0.5; cd.clip_end = 900
    cd.dof.use_dof = True; cd.dof.focus_object = focus; cd.dof.aperture_fstop = fstop; cd.dof.aperture_blades = 7
    o = bpy.data.objects.new(name, cd); link(o, pivot)
    d = Vector((14.5, 11.4, 19.8)).normalized() * dist
    o.location = T(d.x, d.y, d.z)
    c = o.constraints.new('TRACK_TO'); c.target = pivot; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    return o
focus = empty('focus', T(2.4, 2.9, -4.0))
CAM_WIDE = camera('cam_wide', 42, -0.27, 0.0, 0.6)
CAM_TALL = camera('cam_tall', 92, 0.0, 0.16, 0.9)
scene.camera = CAM_WIDE

# ---------- the 48 s cycle ----------
def fade(t): return t * t * (3 - 2 * t)
def cycleK(c):
    for a, b, k0, k1 in ((16, 24, 0, 1), (24, 28, 1, 2), (28, 34, 2, 2), (34, 38, 2, 1), (38, 44, 1, 0)):
        if a <= c < b: return k0 + (k1 - k0) * fade((c - a) / (b - a))
    return 0.0
ARC = [T(45, 5, -25), T(24, 42, 18), T(6, 5, 45)]
MOON = T(-12, 40, 22)
def sun_dir(c, k):
    u = ((c - 36 + CYCLE) % CYCLE) / 36
    if u > 1: u = 1 if c < 30 else 0
    R, N, S = ARC
    p = R * (1 - u) ** 2 + N * (2 * u * (1 - u)) + S * u * u
    w = min(1, max(0, k - 1))
    return (p.normalized() * (1 - w) + MOON.normalized() * w).normalized()
def lerp(a, b, t): return a + (b - a) * t
def lerpc(a, b, t): return tuple(lerp(x, y, t) for x, y in zip(a, b))
KEYS = [  # sun colour, sun strength, sky strength, night-mix, exposure, lamps
    dict(sun=srgb('#fff1dc'), sunI=4.2, sky=0.35, nmix=0.0, exp=0.0),
    dict(sun=srgb('#ff8a50'), sunI=3.0, sky=0.25, nmix=0.15, exp=0.35),
    dict(sun=srgb('#9fb4e0'), sunI=0.18, sky=0.0, nmix=1.0, exp=0.9),
]
def key(obj, path, frame, idx=-1):
    obj.keyframe_insert(path, frame=frame, index=idx)
for f in range(1, FRAMES + 2, STEP):
    t = (f - 1) / FPS; c = (6 + t) % CYCLE; k = cycleK(c)
    i = 0 if k < 1 else 1; fr = k - i; A, B = KEYS[i], KEYS[i + 1]
    lit = min(1.0, k)
    d = sun_dir(c, k)
    suno.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); key(suno, 'rotation_euler', f)
    SUN.color = lerpc(A['sun'], B['sun'], fr); SUN.energy = lerp(A['sunI'], B['sunI'], fr)
    SUN.keyframe_insert('color', frame=f); SUN.keyframe_insert('energy', frame=f)
    el = math.asin(max(-1, min(1, d.z))); az = math.atan2(d.y, d.x)
    sky.sun_elevation = max(el, math.radians(-4)); sky.sun_rotation = az % math.tau
    sky.keyframe_insert('sun_elevation', frame=f); sky.keyframe_insert('sun_rotation', frame=f)
    SKY_BG.inputs['Strength'].default_value = lerp(A['sky'], B['sky'], fr); SKY_BG.inputs['Strength'].keyframe_insert('default_value', frame=f)
    NIGHT_BG.inputs['Strength'].default_value = 0.04 * lerp(A['nmix'], B['nmix'], fr); NIGHT_BG.inputs['Strength'].keyframe_insert('default_value', frame=f)
    WORLD_MIX.inputs[0].default_value = lerp(A['nmix'], B['nmix'], fr); WORLD_MIX.inputs[0].keyframe_insert('default_value', frame=f)
    scene.view_settings.exposure = lerp(A['exp'], B['exp'], fr); scene.view_settings.keyframe_insert('exposure', frame=f)
    # window view
    VIEW_F1.outputs[0].default_value = min(1, k * 1.6); VIEW_F1.outputs[0].keyframe_insert('default_value', frame=f)
    VIEW_F2.outputs[0].default_value = max(0, min(1, (k - 1) * 1.4)); VIEW_F2.outputs[0].keyframe_insert('default_value', frame=f)
    VIEW_S.outputs[0].default_value = lerp(1.6, 0.9, min(1, k / 2)); VIEW_S.outputs[0].keyframe_insert('default_value', frame=f)
    # things that light up after dark
    for mat, d0, d1 in ((SHADE, 0.0, 6.0), (SOFTBOX, 0.3, 4.0)):
        b = mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']; b.default_value = lerp(d0, d1, lit); b.keyframe_insert('default_value', frame=f)
    for mat in (SCREEN_A, SCREEN_B):
        b = mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']; b.default_value = lerp(1.3, 2.2, lit); b.keyframe_insert('default_value', frame=f)
    LAMP_FLOOR.energy = 180 * lit; LAMP_FLOOR.keyframe_insert('energy', frame=f)
    LAMP_DESK.energy = 60 * lit; LAMP_DESK.keyframe_insert('energy', frame=f)
    SB_LIGHT.energy = 120 * lit; SB_LIGHT.keyframe_insert('energy', frame=f)
    # camera sway: one full swing per loop so the video repeats seamlessly
    pivot.rotation_euler = (0, 0, 0.36 * math.sin(math.tau * t / CYCLE)); key(pivot, 'rotation_euler', f, 2)

def linearize(idblock):
    ad = getattr(idblock, 'animation_data', None)
    if not ad or not ad.action: return
    for layer in getattr(ad.action, 'layers', []):
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    for fc in getattr(ad.action, 'fcurves', []) or []:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
for idb in [suno, SUN, sky.id_data, world, scene, VIEW, SHADE, SOFTBOX, SCREEN_A, SCREEN_B, LAMP_FLOOR, LAMP_DESK, SB_LIGHT, pivot]:
    try: linearize(idb if not hasattr(idb, 'node_tree') or idb.node_tree is None else idb.node_tree); linearize(idb)
    except Exception as e: print('linearize skip', idb, e)

# ---------- render settings ----------
cy = scene.cycles
cy.samples = 128; cy.adaptive_threshold = 0.015; cy.use_denoising = True
cy.max_bounces = 8; cy.diffuse_bounces = 4; cy.glossy_bounces = 4; cy.transmission_bounces = 4
cy.sample_clamp_indirect = 8
scene.render.use_persistent_data = True
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
# set last: the glTF importer scales by the unit scale. Depth of field then behaves like a real 1/10-ish miniature.
scene.unit_settings.scale_length = 0.03
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('SAVED', OUT)

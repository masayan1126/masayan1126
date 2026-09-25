# 背景透過版の映像で、モニター2台が映像のどこにあるかを書き出す (切り抜き後の座標、0〜1)。
# Run: blender -b study_nopedestal.blend -P track_alpha.py -- <crop.json> <out.json>
import bpy, json, sys
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
crop_path, out_path = sys.argv[sys.argv.index('--') + 1:][:2]
crop = json.load(open(crop_path))            # {"w":1280,"h":1080,"box":[x0,y0,x1,y1]} in render pixels
s = bpy.context.scene; cam = bpy.data.objects['cam_wide']; s.camera = cam
cam.data.lens, cam.data.shift_x, cam.data.shift_y = 50, -0.045, 0.06   # same as render_transparent.sh
s.render.resolution_x, s.render.resolution_y = crop['w'], crop['h']
x0, y0, x1, y1 = crop['box']; cw, ch = x1 - x0, y1 - y0
bezels = [bpy.data.objects['bezel0'], bpy.data.objects['bezel1']]
boxes = []
for f in range(s.frame_start, s.frame_end + 1, s.frame_step):
    s.frame_set(f); xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for b in bezels:
        ob = b.evaluated_get(dg)
        for c in ob.bound_box:
            p = world_to_camera_view(s, cam, ob.matrix_world @ Vector(c))
            xs.append((p.x * crop['w'] - x0) / cw); ys.append(((1 - p.y) * crop['h'] - y0) / ch)
    boxes.append([round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)])
json.dump({'duration': s.frame_end / s.render.fps, 'boxes': boxes}, open(out_path, 'w'))
print('TRACK', len(boxes))

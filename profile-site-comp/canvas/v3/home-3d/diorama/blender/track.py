# Export where the two monitors sit in each camera's frame, so the page can put a click target on them.
import bpy, json, sys
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
s = bpy.context.scene; out = {}
bezels = [bpy.data.objects['bezel0'], bpy.data.objects['bezel1']]
for cam_name in ('cam_wide', 'cam_tall'):
    cam = bpy.data.objects[cam_name]; s.camera = cam
    s.render.resolution_x, s.render.resolution_y = (1600, 900) if cam_name == 'cam_wide' else (720, 1280)
    track = []
    for f in range(s.frame_start, s.frame_end + 1, s.frame_step):
        s.frame_set(f); xs, ys = [], []
        for b in bezels:
            dg = bpy.context.evaluated_depsgraph_get(); ob = b.evaluated_get(dg)
            for c in ob.bound_box:
                p = world_to_camera_view(s, cam, ob.matrix_world @ Vector(c)); xs.append(p.x); ys.append(1 - p.y)
        track.append([round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)])
    out['wide' if cam_name == 'cam_wide' else 'tall'] = track
json.dump({'duration': (s.frame_end) / s.render.fps, 'boxes': out}, open(sys.argv[sys.argv.index('--') + 1], 'w'))
print('TRACK', len(out['wide']))

import bpy, sys, time
args = sys.argv[sys.argv.index('--') + 1:]
cam, res, spp, out = args[0], args[1], int(args[2]), args[3]
frames = [int(x) for x in args[4].split(',')]
s = bpy.context.scene
s.camera = bpy.data.objects[cam]
w, h = map(int, res.split('x')); s.render.resolution_x, s.render.resolution_y = w, h
s.cycles.samples = spp
for f in frames:
    s.frame_set(f); s.render.filepath = f'{out}_{f:04d}.png'
    t = time.time(); bpy.ops.render.render(write_still=True); print('FRAME', f, round(time.time() - t, 1), 's')

import bpy, sys
args = sys.argv[sys.argv.index('--') + 1:]
s = bpy.context.scene; cam, res, spp, out = args[0], args[1], int(args[2]), args[3]
s.camera = bpy.data.objects[cam]
w, h = map(int, res.split('x')); s.render.resolution_x, s.render.resolution_y = w, h
s.cycles.samples = spp; s.render.filepath = out
s.render.use_overwrite = False; s.render.use_placeholder = True

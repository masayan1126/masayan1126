import bpy, sys
args = sys.argv[sys.argv.index('--') + 1:]
s = bpy.context.scene; cam, res, spp, out = args[0], args[1], int(args[2]), args[3]
s.camera = bpy.data.objects[cam]
# Closer framing for the white hero (approved 2026-09-25): the room fills the frame, centred.
if len(args) > 4:
    s.camera.data.lens = float(args[4]); s.camera.data.shift_x = float(args[5]); s.camera.data.shift_y = float(args[6])
w, h = map(int, res.split('x')); s.render.resolution_x, s.render.resolution_y = w, h
s.cycles.samples = spp; s.render.filepath = out
s.render.use_overwrite = False; s.render.use_placeholder = True
# Transparent background so the diorama sits on the white hero (approved 2026-09-25).
s.render.film_transparent = True
s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'

# Remove the display pedestal so the room stands on its own floor slab (approved 2026-09-25).
import bpy
for name in ('plinth_top', 'hinoki_frame', 'plinth_body', 'plinth_column', 'plate'):
    o = bpy.data.objects.get(name)
    if o: o.hide_render = True; o.hide_viewport = True
base = bpy.data.objects['floorbase']
wood = bpy.data.objects['hinoki_frame'].active_material
base.data.materials.clear(); base.data.materials.append(wood)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.replace('study.blend', 'study_nopedestal.blend'))

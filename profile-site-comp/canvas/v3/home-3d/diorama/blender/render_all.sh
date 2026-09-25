#!/bin/zsh
cd "$(dirname "$0")"
blender -b study.blend -P setup_render.py -a -- cam_wide 1600x900 64 //frames/w_#### > frames/w.log 2>&1
blender -b study.blend -P setup_render.py -a -- cam_tall 720x1280 64 //frames/t_#### > frames/t.log 2>&1
echo done > frames/DONE

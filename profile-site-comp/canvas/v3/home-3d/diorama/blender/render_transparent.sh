#!/bin/zsh
# 白基調のヒーロー用: 台座なし・寄りの構図・背景透過で 48 秒ループを描く (2026-09-25)。
# study.blend (build_scene.py の出力) から台座を外した study_nopedestal.blend を作ってから描く。
cd "$(dirname "$0")"
[ -f study_nopedestal.blend ] || blender -b study.blend -P no_pedestal.py
mkdir -p frames_np
blender -b study_nopedestal.blend -P setup_transparent.py -a -- cam_wide 1280x1080 64 //frames_np/w_#### 50 -0.045 0.06 > frames_np/w.log 2>&1
echo done > frames_np/DONE

#!/bin/zsh
# frames_np の透過 PNG (8fps) を、部屋のまわりで切り抜いて 24fps に補間し、透過付きの映像にする。
#   Chrome・Edge・Firefox: WebM (VP9 + alpha) / Safari・iPhone: HEVC + alpha (VideoToolbox)
set -e
cd "$(dirname "$0")"
M=/Users/masayan/git/masayan1126/profile-site-comp/canvas/v3/home-3d/diorama/media
mkdir -p enc_a $M
python3 - <<'PY'
import glob, json
from PIL import Image
frames = sorted(glob.glob('frames_np/w_*.png'))
x0 = y0 = 10**9; x1 = y1 = 0
for f in frames:
    im = Image.open(f); bb = im.getchannel('A').point(lambda a: 255 if a > 6 else 0).getbbox()
    x0, y0, x1, y1 = min(x0, bb[0]), min(y0, bb[1]), max(x1, bb[2]), max(y1, bb[3])
w, h = im.size; pad = 12
box = [max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)]
box[2] -= (box[2] - box[0]) % 2; box[3] -= (box[3] - box[1]) % 2   # even sizes for yuv420
json.dump({'w': w, 'h': h, 'box': box}, open('enc_a/crop.json', 'w')); print('CROP', box, len(frames))
PY
read X0 Y0 X1 Y1 < <(python3 -c "import json;b=json.load(open('enc_a/crop.json'))['box'];print(*b)")
CW=$((X1-X0)); CH=$((Y1-Y0))
rm -rf enc_a/seq; mkdir -p enc_a/seq; i=0
for f in $(ls frames_np/w_*.png | sort); do ln -s ../../$f enc_a/seq/$(printf %04d $i).png; i=$((i+1)); done
ln -s ../../frames_np/w_0001.png enc_a/seq/$(printf %04d $i).png          # wrap so the loop interpolates across the seam
ln -s ../../frames_np/w_0004.png enc_a/seq/$(printf %04d $((i+1))).png
# Interpolate colour and alpha separately (minterpolate ignores alpha), then merge again.
ffmpeg -y -loglevel error -framerate 8 -i enc_a/seq/%04d.png -filter_complex \
 "[0]crop=$CW:$CH:$X0:$Y0,format=rgba,split[c][a];[c]format=rgb24,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1[ci];[a]alphaextract,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1[ai];[ci][ai]alphamerge,trim=end_frame=1152,setpts=PTS-STARTPTS" \
 -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le enc_a/inter.mov
ffmpeg -y -loglevel error -i enc_a/inter.mov -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 33 -row-mt 1 -auto-alt-ref 0 -g 96 -an $M/study-alpha.webm
ffmpeg -y -loglevel error -i enc_a/inter.mov -c:v hevc_videotoolbox -allow_sw 1 -alpha_quality 0.8 -b:v 1200k -maxrate 1600k -tag:v hvc1 -pix_fmt bgra -movflags +faststart -an $M/study-alpha.hevc.mp4
python3 -c "from PIL import Image; import json; b=json.load(open('enc_a/crop.json'))['box']; Image.open('frames_np/w_0001.png').crop(b).save('$M/study-alpha.webp', quality=85, method=6)"
blender -b study_nopedestal.blend -P track_alpha.py -- enc_a/crop.json $M/track-alpha.json | grep TRACK
ls -la $M/study-alpha.* $M/track-alpha.json

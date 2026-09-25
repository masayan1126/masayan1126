#!/bin/zsh
set -e
cd "$(dirname "$0")"
M=/Users/masayan/git/masayan1126/profile-site-comp/canvas/v3/home-3d/diorama/media
mkdir -p enc $M
for k in w t; do
  kind=$([ $k = w ] && echo wide || echo tall)
  rm -rf enc/seq_$k; mkdir -p enc/seq_$k; i=0
  for f in $(ls frames/${k}_*.png | sort); do ln -s ../../$f enc/seq_$k/$(printf %04d $i).png; i=$((i+1)); done
  ln -s ../../frames/${k}_0001.png enc/seq_$k/$(printf %04d $i).png     # wrap frame so the loop interpolates across the seam
  ln -s ../../frames/${k}_0004.png enc/seq_$k/$(printf %04d $((i+1))).png   # one more, or minterpolate stops 2 frames short of 48 s
  ffmpeg -y -loglevel error -framerate 8 -i enc/seq_$k/%04d.png -vf "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,trim=end_frame=1152,setpts=PTS-STARTPTS" -c:v libx264 -crf 10 -preset fast -pix_fmt yuv444p enc/inter_$k.mp4
  ffmpeg -y -loglevel error -i enc/inter_$k.mp4 -c:v libx264 -preset slow -crf 25 -profile:v high -pix_fmt yuv420p -g 96 -movflags +faststart -an $M/study-$kind.h264.mp4
  ffmpeg -y -loglevel error -i enc/inter_$k.mp4 -c:v libsvtav1 -preset 5 -crf 40 -g 240 -pix_fmt yuv420p -movflags +faststart -an $M/study-$kind.av1.mp4
  python3 -c "from PIL import Image; Image.open(\"frames/${k}_0001.png\").convert(\"RGB\").save(\"$M/study-$kind.webp\", quality=82, method=6)"
done
blender -b study.blend -P track.py -- $M/track.json | grep TRACK
ls -la $M

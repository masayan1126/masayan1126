"""Build the full-viewport hero: a Blender-rendered study diorama video, preserving homepage content."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'home-3d'
MEDIA=SOURCE/'diorama/media'
def build(design,output):
    assets=output/'home-assets';assets.mkdir(exist_ok=True)
    def asset(stem,suffix,data):
        if isinstance(data,str):data=data.encode()
        name=f'{stem}.{hashlib.sha256(data).hexdigest()[:12]}.{suffix}'
        (assets/name).write_bytes(data)
        return '/home-assets/'+name
    css=''.join((SOURCE/f).read_text()+'\n' for f in ('immersive/base.css','immersive/studio.css','immersive/refinement.css','diorama/diorama.css'))
    css_url=asset('immersive','css',css)
    bundled=assets/'studio.build.mjs'
    subprocess.run([str(HERE.parent.parent/'node_modules/.bin/esbuild'),str(SOURCE/'diorama/video-hero.js'),'--bundle','--format=esm','--minify','--target=es2020','--outfile='+str(bundled),'--log-level=warning'],check=True)
    script_url=asset('studio','mjs',bundled.read_bytes());bundled.unlink()
    # Transparent diorama for the white hero (approved 2026-09-25): WebM (VP9 alpha) and HEVC alpha for Safari.
    from PIL import Image
    poster=MEDIA/'study-alpha.webp'; w,h=Image.open(poster).size
    sets={'webm':asset('study-alpha','webm',(MEDIA/'study-alpha.webm').read_bytes()),
          'hevc':asset('study-alpha.hevc','mp4',(MEDIA/'study-alpha.hevc.mp4').read_bytes()),
          'poster':asset('study-alpha','webp',poster.read_bytes()),'w':w,'h':h}
    track_url=asset('study-track-alpha','json',(MEDIA/'track-alpha.json').read_bytes())
    hero=(SOURCE/'immersive/hero.html').read_text().replace('%%SETS%%',json.dumps(sets,separators=(',',':'))).replace('%%TRACK%%',track_url)
    body,count=re.subn(r'<section class="v3-hero">.*?</section>',lambda _:hero,design['public_payloads']['home'],count=1,flags=re.S)
    if count!=1:raise ValueError('Expected one original homepage hero')
    preload=f'<link rel="preload" as="image" href="{sets["poster"]}">'
    return {'body':body,'head':f'<link rel="stylesheet" href="{css_url}">{preload}<script type="module" src="{script_url}"></script>'}

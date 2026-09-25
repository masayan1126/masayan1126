# ---- step 5
cd /private/tmp/claude-501/-Users-masayan-git-content-youtube-deep-tech/35fc86b1-8167-4d8e-b2d9-f6ae6d7c8e4e/scratchpad/blend && cat > fetch.py <<'EOF'
import json, os, sys, urllib.request
def get(u): return json.load(urllib.request.urlopen(u))
def dl(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path): urllib.request.urlretrieve(url, path)
TEX = ['laminate_floor_02', 'beige_wall_001', 'oak_veneer_01', 'american_walnut_veneer', 'fabric_pattern_07', 'fabric_pattern_05', 'hinoki_planks']
MODELS = ['modern_arm_chair_01', 'potted_plant_02', 'desk_lamp_arm_01', 'decorative_book_set_01', 'book_encyclopedia_set_01', 'wall_clock', 'standing_picture_frame_01', 'stationery_supplies', 'ceramic_vase_03', 'pachira_aquatica_01']
for t in TEX:
    d = get(f'https://api.polyhaven.com/files/{t}')
    for k, key in [('Diffuse', 'diff'), ('nor_gl', 'nor'), ('Rough', 'rough')]:
        if k in d: dl(d[k]['2k']['jpg']['url'], f'assets/tex/{t}/{key}.jpg')
    print('tex', t)
for m in MODELS:
    d = get(f'https://api.polyhaven.com/files/{m}')['gltf']['1k']['gltf']
    base = f'assets/models/{m}/'
    dl(d['url'], base + os.path.basename(d['url']))
    for rel, inf in d.get('include', {}).items(): dl(inf['url'], base + rel)
    print('model', m)
EOF
python3 fetch.py 2>&1 | tail -20; du -sh assets
# ---- step 6
cd /private/tmp/claude-501/-Users-masayan-git-content-youtube-deep-tech/35fc86b1-8167-4d8e-b2d9-f6ae6d7c8e4e/scratchpad/blend && python3 - <<'EOF'
s=open('fetch.py').read()
s=s.replace("def get(u): return json.load(urllib.request.urlopen(u))","UA={'User-Agent':'miyabiya-studio-diorama/1.0'}\ndef get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA)))")
s=s.replace("    if not os.path.exists(path): urllib.request.urlretrieve(url, path)","    if not os.path.exists(path): open(path,'wb').write(urllib.request.urlopen(urllib.request.Request(url,headers=UA)).read())")
open('fetch.py','w').write(s)
EOF
python3 fetch.py 2>&1 | tail -20; du -sh assets
# ---- step 7
cd /private/tmp/claude-501/-Users-masayan-git-content-youtube-deep-tech/35fc86b1-8167-4d8e-b2d9-f6ae6d7c8e4e/scratchpad/blend && python3 - <<'EOF'
s=open('fetch.py').read()
s=s.replace("""    d = get(f'https://api.polyhaven.com/files/{m}')['gltf']['1k']['gltf']""","""    f = get(f'https://api.polyhaven.com/files/{m}')
    if 'gltf' not in f: print('skip', m, list(f)[:5]); continue
    d = f['gltf']['1k']['gltf']""")
open('fetch.py','w').write(s)
EOF
python3 fetch.py 2>&1 | grep -E "model|skip"; du -sh assets; find assets/models -name "*.gltf"
# ---- step 17
cd /private/tmp/claude-501/-Users-masayan-git-content-youtube-deep-tech/35fc86b1-8167-4d8e-b2d9-f6ae6d7c8e4e/scratchpad/blend && python3 - <<'EOF'
import json, urllib.request
UA={'User-Agent':'miyabiya-studio-diorama/1.0'}
for t in ['fabric_pattern_07','fabric_pattern_05']:
    d=json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.polyhaven.com/files/{t}',headers=UA)))
    k=[x for x in d if x.startswith('col')][0]
    u=d[k]['2k']['jpg']['url']; open(f'assets/tex/{t}/diff.jpg','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers=UA)).read()); print(t,k)
EOF

"""公開ページの YouTube の数値 (登録者数・代表動画の再生数) をビルド時に最新化する。

本文の元データ (Main.dc.html・works-story.html など) には、最後に承認した時点の数値
(SNAPSHOT) がそのまま書かれている。ビルドの最後に apply() で、生成したページ内の
その数値だけを最新の値に置き換える。元データは書き換えない。

取得には、リポジトリの SessionStart フック (.claude/hooks/fetch_subscribers.py) と
同じ OAuth トークンを使う。取得できないとき (オフライン・トークン切れ) は、
前回の取得結果 youtube-stats.json を使ってビルドを続ける。
メンバー数は、Studio で確認した人数と確認日を youtube-audience.json で管理する。
"""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import runpy
import urllib.error
import urllib.parse

HERE = Path(__file__).resolve().parent
CACHE = HERE / 'youtube-stats.json'
HOOK = HERE.parents[2] / '.claude/hooks/fetch_subscribers.py'
JST = timezone(timedelta(hours=9))

# 元データに書かれている、承認済みの時点の数値。
SNAPSHOT = {
    'subs': '3,462',
    'date': '2026年9月22日時点',
    'subs_floor': '3,500<small>人+</small>',
    'videos': {'Kggm_W0w0lw': '15,495', 'BxQ2nutD-_o': '4,706', 'D1gsaCoJelw': '4,446'},
}

# Studio の確認値。API の取得日でメンバーの確認日を更新しない。
AUDIENCE = json.loads((HERE / 'youtube-audience.json').read_text())
MEMBERS = AUDIENCE['members']['count']
_member_date = datetime.fromisoformat(AUDIENCE['members']['as_of'])
MEMBERS_AS_OF = f'{_member_date.year}年{_member_date.month}月{_member_date.day}日時点'


def _fetch():
    hook = runpy.run_path(str(HOOK))
    ids = ','.join(SNAPSHOT['videos'])
    for token_path in hook['TOKEN_CANDIDATES']:
        if not token_path.exists():
            continue
        token_data = json.loads(token_path.read_text())

        def get(token):
            headers = {'Authorization': f'Bearer {token}'}
            channel = hook['http_json']('https://www.googleapis.com/youtube/v3/channels?' + urllib.parse.urlencode(
                {'part': 'statistics', 'id': hook['CHANNEL_ID']}), headers=headers)
            videos = hook['http_json']('https://www.googleapis.com/youtube/v3/videos?' + urllib.parse.urlencode(
                {'part': 'statistics', 'id': ids}), headers=headers)
            return (int(channel['items'][0]['statistics']['subscriberCount']),
                    {v['id']: int(v['statistics']['viewCount']) for v in videos['items']})

        try:
            subs, views = get(token_data.get('token', ''))
        except urllib.error.HTTPError as error:
            if error.code != 401:
                raise
            subs, views = get(hook['refresh_access_token'](token_path, token_data))
        if set(views) != set(SNAPSHOT['videos']):
            raise RuntimeError(f'動画の再生数を取得できませんでした: {sorted(set(SNAPSHOT["videos"]) - set(views))}')
        return {'subs': subs, 'date': datetime.now(JST).strftime('%Y-%m-%d'), 'videos': views}
    raise RuntimeError('OAuth トークンが見つかりません')


def load(fetch=True):
    """最新の数値を返す。fetch=False か取得に失敗したときは前回の取得結果を使う。"""
    if fetch:
        try:
            stats = _fetch()
            CACHE.write_text(json.dumps(stats, ensure_ascii=False, indent=1) + '\n')
            return stats
        except Exception as error:  # noqa: BLE001 — 数値の取得失敗でサイトの公開は止めない
            print(f'警告: YouTube の数値を取得できませんでした。前回の値を使います ({type(error).__name__}: {error})')
    return json.loads(CACHE.read_text())


def apply(html, stats):
    """生成したページ内の承認時点の数値を、stats の値に置き換える。"""
    year, month, day = (int(x) for x in stats['date'].split('-'))
    floor = stats['subs'] // 100 * 100
    member_snapshot = f'メンバー <b>37人</b><small>{SNAPSHOT["date"]}</small>'
    html = html.replace(member_snapshot, f'メンバー <b>{MEMBERS}人</b><small>{MEMBERS_AS_OF}</small>')
    html = html.replace(SNAPSHOT['subs_floor'], f'{floor:,}<small>人+</small>')
    html = html.replace(SNAPSHOT['subs'], f'{stats["subs"]:,}')
    html = html.replace(SNAPSHOT['date'], f'{year}年{month}月{day}日時点')
    html = html.replace('メンバー <b>37人</b>', f'メンバー <b>{MEMBERS}人</b>').replace('メンバー37人', f'メンバー{MEMBERS}人')
    for video_id, old in SNAPSHOT['videos'].items():
        html = html.replace(f'{old}回再生', f'{stats["videos"][video_id]:,}回再生')
    return html


# ---- 最新の本編3本 (トップの「最新の動画」欄、approved 2026-09-25) ----
LATEST_CACHE = HERE / 'latest-videos.json'
THUMBS = HERE / 'latest-thumbs'


def _iso_duration(value):
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', value)
    hours, minutes, seconds = (int(x or 0) for x in match.groups())
    return hours * 3600 + minutes * 60 + seconds


def _fetch_latest(count=3):
    hook = runpy.run_path(str(HOOK))
    for token_path in hook['TOKEN_CANDIDATES']:
        if not token_path.exists():
            continue
        token_data = json.loads(token_path.read_text())
        token = token_data.get('token', '')

        def get(url, params):
            return hook['http_json'](url + '?' + urllib.parse.urlencode(params), headers={'Authorization': f'Bearer {token}'})

        try:
            get('https://www.googleapis.com/youtube/v3/channels', {'part': 'id', 'id': hook['CHANNEL_ID']})
        except urllib.error.HTTPError as error:
            if error.code != 401:
                raise
            token = hook['refresh_access_token'](token_path, token_data)
        uploads = 'UU' + hook['CHANNEL_ID'][2:]
        found, page_token = [], None
        # Shorts make up most uploads, so walk back until three public videos longer than 3 minutes are found.
        for _ in range(20):
            params = {'part': 'contentDetails', 'playlistId': uploads, 'maxResults': 50}
            if page_token:
                params['pageToken'] = page_token
            page = get('https://www.googleapis.com/youtube/v3/playlistItems', params)
            ids = ','.join(item['contentDetails']['videoId'] for item in page['items'])
            videos = get('https://www.googleapis.com/youtube/v3/videos', {'part': 'snippet,contentDetails,status', 'id': ids})
            for video in videos['items']:
                # The uploads playlist can list the same video twice; keep one card per video.
                if video['status']['privacyStatus'] == 'public' and _iso_duration(video['contentDetails']['duration']) > 180 and all(v['id'] != video['id'] for v in found):
                    found.append({'id': video['id'], 'title': video['snippet']['title'], 'published': video['snippet']['publishedAt'][:10]})
            page_token = page.get('nextPageToken')
            if len(found) >= count or not page_token:
                break
        found.sort(key=lambda v: v['published'], reverse=True)
        return found[:count]
    raise RuntimeError('OAuth トークンが見つかりません')


def _save_thumbnail(video_id):
    import io
    import urllib.request
    from PIL import Image
    THUMBS.mkdir(exist_ok=True)
    target = THUMBS / f'{video_id}.webp'
    if target.exists():
        return
    for size in ('maxresdefault', 'hqdefault'):
        try:
            with urllib.request.urlopen(f'https://i.ytimg.com/vi/{video_id}/{size}.jpg', timeout=10) as response:
                image = Image.open(io.BytesIO(response.read())).convert('RGB')
            break
        except urllib.error.HTTPError:
            continue
    width, height = image.size
    crop = round(width * 9 / 16)
    top = (height - crop) // 2
    image.crop((0, top, width, top + crop)).resize((640, 360), Image.LANCZOS).save(target, 'WEBP', quality=80, method=6)


def load_latest(fetch=True):
    """最新の本編3本を返す。取得に失敗したときは前回の結果を使う。"""
    if fetch:
        try:
            videos = _fetch_latest()
            for video in videos:
                _save_thumbnail(video['id'])
            LATEST_CACHE.write_text(json.dumps(videos, ensure_ascii=False, indent=1) + '\n')
            return videos
        except Exception as error:  # noqa: BLE001 — 取得失敗でサイトの公開は止めない
            print(f'警告: 最新の動画を取得できませんでした。前回の値を使います ({type(error).__name__}: {error})')
    return json.loads(LATEST_CACHE.read_text())


def render_latest(videos):
    import html as html_lib
    cards = ''.join(
        f'<a href="https://youtu.be/{v["id"]}"><img src="/latest-thumb-{v["id"]}.webp" width="640" height="360" alt="" loading="lazy">'
        f'<b>{html_lib.escape(v["title"])}</b><small>{int(v["published"][:4])}年{int(v["published"][5:7])}月{int(v["published"][8:10])}日</small></a>'
        for v in videos)
    return ('<section class="latest" id="latest"><div class="wrap"><div class="latest-head"><div><h2>最新の動画</h2>'
            '<p class="lead">YouTubeで公開した新しい本編3本です。</p></div>'
            '<a href="https://www.youtube.com/@masayan-ai-hack">YouTubeチャンネルを見る ↗</a></div>'
            f'<div class="latest-cards">{cards}</div></div></section>')

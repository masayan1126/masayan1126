#!/usr/bin/env python3
"""Build an additive multi-page design without rewriting earlier versions."""
import base64
import html
import json
from pathlib import Path
import re
import runpy
from html.parser import HTMLParser

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'Main.dc.html'
OUT = HERE / 'preview'
OUT.mkdir(exist_ok=True)
src = SOURCE.read_text()
# Keep the existing channel identity accurate while using the requested personal name.
src = src.replace('YouTube「まさやん【AIギルドch】」', 'YouTubeチャンネル').replace('「まさやん【AIギルドch】」', 'YouTubeチャンネル').replace('まさやん', 'Masaya Nishigaki')
src = src.replace('開発・AI導入', 'プロダクト開発・AI導入支援')
css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)

def element(text, ident):
    m = re.search(r'<([a-z][\w-]*)\b[^>]*\bid="'+re.escape(ident)+r'"[^>]*>', text)
    if not m:
        raise ValueError(ident)
    tag, depth = m.group(1), 1
    for n in re.finditer(r'</?'+tag+r'\b[^>]*>', text[m.end():]):
        depth += -1 if n.group().startswith('</') else 1
        if depth == 0:
            return text[m.start():m.end()+n.end()]
    raise ValueError('unclosed '+ident)

files = {'home':'Artboard.dc.html', 'profile':'Artboard2.dc.html', 'works':'Artboard3.dc.html',
         'services':'Artboard4.dc.html', 'media':'Artboard5.dc.html', 'talks':'Artboard6.dc.html',
         'membership':'Artboard7.dc.html', 'contact':'Artboard8.dc.html', 'mobile':'Artboard9.dc.html'}
titles = {'home':'トップ', 'profile':'プロフィール・経歴', 'works':'実績', 'services':'プロダクト開発・AI導入支援',
          'media':'YouTube・PR・コラボ', 'talks':'技術登壇', 'membership':'メンバーシップ',
          'contact':'お問い合わせ', 'mobile':'トップ・スマホ'}
anchors = {'top':'home', 'services':'services', 'pr':'media', 'ratecard':'media', 'works':'works',
           'videos':'media', 'membership':'membership', 'talks':'talks', 'career-history':'profile',
           'career':'profile', 'flow':'contact', 'contact':'contact', 'route':'home'}

def link(key, label, cls=''):
    return f'<a class="{cls}" href="{files[key]}">{label}<span aria-hidden="true"> →</span></a>'

def header(active):
    return '<header class="v3-head"><div class="v3-wrap">'+link('home','<img class="v3-logo-icon" src="avatar.webp" alt="" width="36" height="36"><b>Miyabiya <em>Studio</em></b>','v3-logo')+'<nav aria-label="メインメニュー">'+''.join(link(k,nav_icon(k)+titles[k], 'current' if k==active else '') for k in ('profile','works','media'))+'</nav>'+link('contact','お問い合わせ','v3-contact-link')+'</div></header>'

def nav_icon(key):
    shape = {'profile':'<circle cx="12" cy="7" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/>', 'works':'<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V3h8v4M3 12h18m-9 0v4"/>', 'media':'<rect x="2" y="4" width="20" height="16" rx="4"/><path d="m10 8 6 4-6 4Z"/>'}.get(key)
    return '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+shape+'</svg>' if shape else ''

def footer():
    return '<footer class="v3-footer"><div class="v3-wrap"><div class="v3-footer-top"><div><b>Miyabiya Studio</b><p>Masaya Nishigaki</p></div><div class="v3-social"><a href="https://www.youtube.com/@masayan-ai-hack">YouTube ↗</a><a href="https://x.com/masayan_ai_hack">X ↗</a><a href="https://github.com/masayan1126">GitHub ↗</a></div></div><nav aria-label="ページ一覧">'+''.join(link(k,nav_icon(k)+titles[k]) for k in ('profile','works','services','media','talks','membership','contact'))+'</nav><div class="v3-footer-bottom"><span>© 2026 Masaya Nishigaki</span><div><a href="https://www.instagram.com/miyabiya1126/">Instagram ↗</a><a href="https://zenn.dev/masayan1126">Zenn ↗</a><a href="https://substack.com/@masayan1126">Substack ↗</a></div></div></div></footer>'

custom = '''
.v3{font-family:var(--sans);color:#2A2926;background:#fff;font-size:16px;line-height:1.8;overflow-wrap:anywhere}
.v3 *{box-sizing:border-box}.v3 a{text-underline-offset:5px}.v3 a:focus-visible,.v3 summary:focus-visible{outline:3px solid #4164A5;outline-offset:5px}
.v3-wrap{max-width:1168px;margin:auto;padding:0 24px}.v3-head{position:sticky;top:0;z-index:50;border-bottom:1px solid #DDE2E6;background:white}.v3-head>.v3-wrap{display:flex;align-items:center;gap:32px;min-height:80px}
.v3-logo{font-size:19px;color:#2A2926;text-decoration:none;font-weight:700;white-space:nowrap}.v3-logo em{color:#133F8F;font-style:normal}.v3-logo>span{display:none}.v3-head nav{margin-left:auto;display:flex;gap:28px}.v3-head nav a{display:inline-flex;align-items:center;gap:7px;font-size:14px;color:#3B3936;text-decoration:none;white-space:nowrap}.v3-head nav a>svg{width:18px;height:18px;flex:none;color:#133F8F}.v3-head nav a>span{display:none}.v3-head nav a.current{color:#133F8F;text-decoration:underline}.v3-contact-link{border:1px solid #133F8F;border-radius:10px;padding:8px 14px;text-decoration:none;font-size:13px;font-weight:700}
.v3-hero{padding:88px 0 80px}.v3-hero>.v3-wrap{display:grid;grid-template-columns:1.5fr 1fr;gap:64px;align-items:center}.v3-eyebrow{color:#133F8F;font-size:14px;font-weight:700;margin:0 0 22px}.v3 h1{font-size:54px;line-height:1.4;letter-spacing:-.035em;text-wrap:balance}.v3-intro{margin:24px 0;color:#525452;font-size:17px;max-width:600px}.v3 .v3-photo{margin:0;background:transparent;border-radius:0;overflow:hidden;height:385px}.v3-photo img{width:100%;height:100%;object-fit:cover;object-position:center 24%}.v3-primary{display:inline-flex;align-items:center;gap:32px;text-decoration:none;background:#133F8F;color:white;border-radius:12px;padding:13px 24px;font-size:15px;font-weight:700}.v3-primary:hover{background:#0F3373;color:white}.v3-text-link{font-weight:700;text-decoration:none;border-bottom:1px solid #B1BFDA;padding-bottom:5px;display:inline-flex;gap:18px;font-size:14px}
.v3-activities{border-top:1px solid #DDE2E6;padding:56px 0 64px;background:#F7F7F5}.v3-section-title{font-size:30px;margin-bottom:30px;line-height:1.5}.v3-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.v3-card{background:white;border:1px solid #DDE2E6;border-radius:16px;padding:30px 28px;display:flex;flex-direction:column;align-items:flex-start}.v3-card h3{font-size:22px;margin:14px 0 12px}.v3-card p{color:#525452;margin:0 0 24px;font-size:15px}.v3-card .v3-text-link{margin-top:auto}.v3-symbol{color:#133F8F;width:42px;height:42px;background:#ECEFF6;border-radius:50%;display:grid;place-items:center;font-size:20px;font-weight:700}
.v3-contact{background:#133F8F;color:white;padding:56px 0}.v3-contact .v3-wrap{display:flex;align-items:center;justify-content:space-between;gap:32px}.v3-contact h2{font-size:25px;line-height:1.5}.v3-contact p{margin-top:8px;font-size:14px;color:#ECEFF6}.v3-contact a{background:white;color:#133F8F;white-space:nowrap}.v3-footer{border-top:1px solid #DDE2E6;background:#F7F7F5;padding:48px 0 32px;color:#525452;font-size:13px}.v3-footer a{color:#525452;text-decoration:none}.v3-footer-top,.v3-footer-bottom{display:flex;justify-content:space-between;align-items:center;gap:24px}.v3-footer-top b{font-size:18px;color:#2A2926}.v3-footer-top p{margin-top:5px}.v3-social,.v3-footer-bottom>div{display:flex;gap:24px}.v3-footer nav{display:flex;gap:16px 24px;flex-wrap:wrap;margin:28px 0}.v3-footer nav a{font-size:13px}.v3-footer nav a>span{display:none}.v3-footer-bottom{border-top:1px solid #DDE2E6;padding-top:20px;font-size:12px}
.v3-page-head{padding:56px 0 48px;background:#F7F7F5;border-bottom:1px solid #DDE2E6}.v3-breadcrumb{display:block;font-size:13px;margin-bottom:24px}.v3-page-head h1{font-size:42px}.v3-page-head p{margin-top:16px;max-width:800px;color:#525452}.v3-detail .sec{padding:64px 0}.v3-detail .sec-h{font-size:29px}.v3-detail .sec-lead{margin-bottom:32px}.v3-detail .card{padding:26px 24px}.v3-detail .msg{padding:44px 0}.v3-detail .msg h2{font-size:32px}.v3-detail .wrap{max-width:1168px}.v3-detail .aud{margin-top:30px}.v3-detail .hero-lead{max-width:none}.v3-detail .section-cta{margin-top:22px}.v3-detail .short-route{padding:24px;background:#F6F7FB;border:1px solid #DDE2E6;border-radius:14px;margin:28px 0}.v3-detail .short-route h3{font-size:20px;margin-bottom:10px}.v3-detail .short-route p{margin-bottom:14px}.v3-detail .ratecard{margin-top:26px}.v3-detail details{overflow-wrap:anywhere}.v3-detail .talk{grid-template-columns:90px 1fr auto}.v3-detail .btns>a,.v3-detail .contact-ctas>a{flex:1;text-align:center}.v3-detail .videos{gap:20px}.v3-detail .vcard h3{font-size:16px}
@media(min-width:821px) and (max-width:1050px){.v3-head>.v3-wrap{gap:20px}.v3-head nav{gap:18px}.v3-head nav a{font-size:13px}.v3-head .v3-logo{font-size:17px}.v3-head .v3-contact-link{font-size:12px;padding:7px 10px}}
@media(max-width:820px){.v3-head>.v3-wrap{min-height:68px;gap:12px;justify-content:space-between}.v3-logo{font-size:16px}.v3-head nav{display:none}.v3-contact-link{font-size:12px;padding:8px 10px}.v3-contact-link>span{display:none}.v3-hero{padding:40px 0 56px}.v3-hero>.v3-wrap{grid-template-columns:1fr;gap:26px}.v3 h1{font-size:34px;line-height:1.48}.v3-eyebrow{font-size:12px;margin-bottom:16px}.v3-intro{font-size:15px;margin:20px 0}.v3 .v3-photo{height:225px}.v3-photo img{object-position:center 28%}.v3-primary{font-size:14px;width:100%;justify-content:space-between;padding:12px 20px}.v3-activities{padding:36px 0}.v3-section-title{font-size:25px;margin-bottom:24px}.v3-cards{grid-template-columns:1fr;gap:16px}.v3-card{padding:24px}.v3-card h3{font-size:21px;margin-top:12px}.v3-card p{font-size:14px;margin-bottom:20px}.v3-symbol{width:36px;height:36px;font-size:18px}.v3-contact{padding:48px 0}.v3-contact .v3-wrap{display:block}.v3-contact h2{font-size:23px}.v3-contact p{margin-bottom:22px}.v3-footer-top,.v3-footer-bottom{align-items:flex-start;flex-direction:column;gap:18px}.v3-footer{padding-top:40px}.v3-footer nav{display:grid;grid-template-columns:1fr 1fr;gap:14px}.v3-footer nav a{font-size:12px}.v3-page-head{padding:40px 0}.v3-page-head h1{font-size:30px}.v3-page-head p{font-size:15px}.v3-detail .sec{padding:48px 0}.v3-detail .talk{grid-template-columns:1fr}.v3-detail .btn{width:100%}.v3-detail .videos{grid-template-columns:1fr}.v3-detail .contact-ctas{flex-direction:column}.v3-detail .ratecard table{font-size:13px}}
@media(prefers-reduced-motion:reduce){.v3 *{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
'''

home_hero = '''<section class="v3-hero"><div class="v3-wrap"><div class="v3-hero-copy"><p class="v3-eyebrow">Masaya Nishigaki / Webエンジニア・テックリード</p><h1>AIでクリエイティブと<br>開発を仕組み化・<br class="v3-title-mobile-break">自動化して<br class="v3-title-desktop-break">成果を出す</h1><p class="v3-intro">WebエンジニアのMasaya Nishigakiです。<br>現在はテックリードとしてMCPサーバーやAPI開発に携わり、個人のYouTubeチャンネルで発信しています。</p></div><div class="v3-hero-ctas">'''+link('contact','仕事の相談をする','v3-primary')+link('profile','プロフィール・経歴を見る','v3-primary v3-secondary')+'''</div><div class="v3-hero-media"><figure class="v3-photo"><img src="hero-photo.webp" alt="Masaya Nishigakiのプロフィール写真"></figure></div></div></section>'''
home_contact = '<section class="v3-contact"><div class="v3-wrap"><div><h2>お問い合わせ</h2><p>相談内容に合わせて、連絡先とご依頼の流れをご案内します。</p></div>'+link('contact','お問い合わせ','v3-primary')+'</div></section>'

career = element(src,'career-history')
# Show the latest role first on both pages, preserving each entry's wording.
timeline = re.search(r'<ul class="tl">(.*?)</ul>', career, re.S)
entries = re.findall(r'<li>.*?</li>', timeline.group(1), re.S)
career = career[:timeline.start(1)]+'\n'+ '\n'.join(reversed(entries))+'\n'+career[timeline.end(1):]
# Strengths and recruitment stay on the detail page.
career_display = career.split('<div class="strengths">', 1)[0]+'</div>'
home_career = '<div class="v3-detail">'+career_display+'<div class="v3-career-cta">'+link('profile','経歴の詳細を見る','v3-primary v3-secondary')+'</div></div></div></div>'

works = element(src,'works')
services = element(src,'services')
pr = element(src,'pr')
services = services.replace(pr,'')
pricing_builder = runpy.run_path(str(HERE / 'build_pricing.py'))
pr = pr.replace(element(pr,'ratecard'), pricing_builder['media_summary']())
pr = pr.replace('企業のタイアップは料金表をご覧ください。', '企業のタイアップは、見積もりシミュレーターで料金をお試しください。')
videos = element(src,'videos')
membership = element(src,'membership')
videos = videos.replace(membership,'<div class="short-route"><h3>メンバーシップについて</h3><p>メンバー限定の特典をご案内しています。</p>'+link('membership','メンバーシップの詳細を見る','v3-text-link')+'</div>')
membership = re.sub(r'<p class="sub-h">発信で大切にしていること</p>\s*<ul class="promise">.*?</ul>', '', membership, flags=re.S)
profile = '<section class="sec"><div class="wrap"><p class="hero-lead">'+re.search(r'<p class="hero-lead">(.*?)</p>',src,re.S).group(1)+'</p></div></section>'+career

# Home uses the same information groups and components as the detail pages.
# Detailed evidence, rates and request conditions stay on those pages.
work_titles = [
    'AI駆動開発環境の構築・運用',
    'MCPサーバーの開発とプロジェクト推進',
    'YouTubeチャンネルの運営',
    '技術登壇',
]
for old,new in zip(re.findall(r'<h3>(.*?)</h3>',works,re.S),work_titles):
    works = works.replace('<h3>'+old+'</h3>', '<h3>'+new+'</h3>', 1)
work_descriptions = [
    'AIエージェントを使う開発フローを構築し、大幅な開発工数の削減を実現しています',
    'MCPサーバーを社外クライアントと社内の運用チームに導入し、両者の業務工数を削減しました。',
    '登録者3,350人、メンバー30人以上のYouTubeチャンネルを一人で運営しています。収益化もしています。',
    'ClaudeCodeMeetupOsakaとAI駆動開発勉強会 神戸支部で、AI活用の実践例を発表しました。',
]
works_intro = '実務・個人でのAI活用、YouTube運営、技術登壇の実績をご紹介します。'
home_works = '<section class="sec home-overview"><div class="wrap"><h2 class="sec-h">実績</h2><p class="sec-lead">'+works_intro+'</p><div class="grid3 home-work-grid">'+''.join(
    '<a class="card work home-summary-card" href="'+files['works']+('#talks' if i==3 else '')+'"><p class="lbl">'+('個人' if i>=2 else '本業')+'</p><h3>'+title+'</h3><p>'+desc+'</p><span class="home-detail-cta">詳細を見る →</span></a>'
    for i,(title,desc) in enumerate(zip(work_titles,work_descriptions))
)+'</div></div></section>'
# Reuse the original talk records so dates, titles and event links stay identical.
talks = element(src,'talks')
works_talks = talks.split('<div class="talk-more">',1)[0].replace('class="sec alt"','class="sec"',1)
works += works_talks+'<div class="section-cta">'+link('talks','登壇テーマ・ご依頼について','v3-text-link')+'</div></div></div>'
service_summaries = [
    ('services','プロダクト開発・AI導入支援','Webサービスの開発から、AIの導入・定着まで支援します。','プロダクト開発・AI導入支援の詳細を見る'),
    ('media','YouTubeでの製品PR・コラボ','AIツールや開発者向けサービスを、動画で紹介します。対談や共同企画もご相談ください。','PR・コラボの詳細を見る'),
    ('talks','技術登壇','実務でのAI活用を、勉強会や社内向けの講演でお話しします。','登壇の詳細を見る'),
]
home_services = '<section class="sec alt home-overview"><div class="wrap"><h2 class="sec-h">事業内容</h2><p class="sec-lead">プロダクト開発・AI導入支援、製品PR、技術登壇のご相談をお受けします。</p><div class="grid3">'+''.join(
    '<a class="card work home-summary-card" href="'+files[key]+'"><h3>'+title+'</h3><p>'+desc+'</p><span class="home-detail-cta">'+cta+' →</span></a>'
    for key,title,desc,cta in service_summaries
)+'</div></div></section>'
home = home_hero+'<div class="v3-detail">'+home_services+home_works+'</div>'+home_career+home_contact
custom += '.v3-home .career{display:block;max-width:880px}.v3-hero>.v3-wrap{grid-template-areas:"copy portrait" "actions portrait";column-gap:64px;row-gap:24px}.v3-hero-copy{grid-area:copy}.v3-hero-media{grid-area:portrait}.v3-hero-ctas{grid-area:actions}.v3-hero-copy .v3-intro{margin-bottom:0}@media(max-width:820px){.v3-hero>.v3-wrap{grid-template-areas:"copy" "portrait" "actions";gap:26px}}'
custom += '.v3-hero-ctas{display:flex;flex-wrap:wrap;gap:14px;align-items:center}.v3-hero-ctas .v3-primary{width:auto;justify-content:center;gap:12px;padding:13px 20px;font-size:14px;white-space:nowrap;border:1px solid #133F8F}.v3-hero-ctas .v3-primary>span{flex:none}.v3-secondary{background:white;color:#133F8F}.v3-secondary:hover{background:#F6F7FB;color:#133F8F}.v3-home #career-history{border-top:1px solid #DDE2E6}.v3-logo{display:inline-flex;align-items:center;gap:10px}.v3-logo-icon{display:block;width:36px;height:36px;flex:none;border-radius:50%;object-fit:cover;background:#E8EEF8;border:1px solid #DDE2E6}@media(max-width:820px){.v3-hero-ctas{flex-direction:column;align-items:stretch}.v3-hero-ctas .v3-primary{width:100%}.v3-logo{gap:8px}.v3-logo-icon{width:28px;height:28px}}'
custom += '.home-summary-card{color:#2A2926;text-decoration:none}.home-summary-card:hover{color:#2A2926;border-color:#133F8F;background:#F6F7FB}.home-detail-cta{display:block;margin-top:20px;color:#133F8F;font-size:13px;font-weight:700}.work.home-summary-card .home-detail-cta{margin-top:auto;padding-top:24px}.home-overview .talks{max-width:none}.home-overview .talk .lk{font-size:13px}.home-overview .vcard .vb{display:flex;flex-direction:column;flex:1}.home-overview .vcard .home-detail-cta{margin-top:auto;padding-top:18px}'
custom += '.home-work-grid{grid-template-columns:repeat(2,minmax(0,1fr))}@media(max-width:820px){.home-work-grid{grid-template-columns:1fr}}'
custom += '.v3-career-cta{display:flex;justify-content:flex-start;margin-top:36px;padding-left:28px}.v3-career-cta .v3-primary{border:1px solid #B1BFDA;gap:12px;padding:13px 20px}.v3-contact .v3-primary{border:1px solid white;gap:12px;padding:13px 20px;transition:background-color .18s,color .18s,box-shadow .18s}.v3-contact .v3-primary:hover,.v3-contact .v3-primary:focus-visible{background:#ECEFF6;color:#133F8F;box-shadow:0 0 0 4px rgba(255,255,255,.24)}@media(max-width:820px){.v3-career-cta{margin-top:28px;padding-left:0}.v3-career-cta .v3-primary,.v3-contact .v3-primary{justify-content:center}}'

contents = {'home':home,'mobile':home,'profile':profile,'works':works,'services':services,'media':videos+'<section class="sec"><div class="wrap">'+pr+'</div></section>', 'talks':element(src,'talks'),'membership':'<section class="sec"><div class="wrap">'+membership+'</div></section>', 'contact':element(src,'flow')+element(src,'contact')}
intros = {'profile':'これまでの経歴と、開発の経験をご紹介します。採用・業務委託のご相談もこちらでご案内します。','works':works_intro,'services':'Webサービスの開発から、AIの導入・定着まで支援します。','media':'代表動画と、製品PR・コラボのご案内です。','talks':'過去の登壇と、お話しできるテーマ・形式をご紹介します。','membership':'メンバー限定の特典と、加入方法をご案内します。','contact':'ご依頼の流れと、メール・SNSの連絡先をご案内します。'}

custom += '.v3-photo img{object-fit:contain;object-position:center bottom;padding:8px 12px 0}'
icon_paths = {
    'code':'<path d="m8 7-5 5 5 5m8-10 5 5-5 5m-3-14-2 18"/>',
    'workflow':'<rect x="3" y="3" width="6" height="6" rx="1.5"/><rect x="15" y="15" width="6" height="6" rx="1.5"/><path d="M6 9v9h9M9 6h9v9"/>',
    'play':'<rect x="2.5" y="4.5" width="19" height="15" rx="4"/><path d="m10 8 6 4-6 4Z"/>',
    'presentation':'<path d="M2 3h20M4 3v13h16V3M12 16v5m-4 0 4-5 4 5M7 12l3-3 3 2 4-5"/>',
    'users':'<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3m2-16a3 3 0 0 1 0 6m2 10v-3a6 6 0 0 0-3-5"/>',
    'shield':'<path d="m12 2 8 4v6c0 5-8 10-8 10S4 17 4 12V6Zm-4 10 3 3 5-6"/>',
    'briefcase':'<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V3h8v4M3 12a20 20 0 0 0 18 0m-9 0v4"/>',
    'chat':'<path d="M21 11a8 8 0 0 1-8 8H6l-4 3V11a9 9 0 0 1 19 0Z"/><path d="M7 10h10M7 14h6"/>',
    'screen':'<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 22h8m-4-5v5M6 8h12M6 12h8"/>',
}
card_icons = {
    'プロダクト開発・AI導入支援':'code','YouTubeでの製品PR・コラボ':'play','技術登壇':'presentation',
    'AI駆動開発環境の構築・運用':'code','MCPサーバーの開発とプロジェクト推進':'workflow','YouTubeチャンネルの運営':'play',
    '保守性の高い開発':'shield','AI・MCPによる成果創出':'workflow','採用・業務委託のご相談':'briefcase',
    'AI駆動のWebプロダクト開発':'code','AIエージェントの設計・ハーネス構築':'workflow','AI導入支援・社内勉強会':'users',
    'メンバーシップについて':'users','お話しできるテーマ':'chat','対応できる形式':'screen',
}
for video_title in re.findall(r'<h3>(.*?)</h3>',videos,re.S):
    if video_title.startswith('Claude Code'): card_icons[video_title]='play'
def add_card_icons(content):
    content = re.sub(r'<div class="icochip">.*?</div>', '', content, flags=re.S)
    for title,kind in card_icons.items():
        icon = '<span class="v3-card-icon" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+icon_paths[kind]+'</svg></span>'
        content = content.replace('<h3>'+title+'</h3>', '<h3 class="v3-card-title">'+icon+'<span>'+title+'</span></h3>')
    return content
custom += '.v3-card-title{display:flex;align-items:flex-start;gap:10px}.v3-card-title>span:last-child{min-width:0}.v3-card-icon{display:grid;place-items:center;width:34px;height:34px;flex:0 0 34px;border-radius:9px;background:#ECEFF6;color:#133F8F}.v3-card-icon svg{display:block}.v3-detail .card .v3-card-title{margin-top:0}.v3-detail .vcard .v3-card-icon{width:28px;height:28px;flex-basis:28px}.v3-detail .vcard .v3-card-icon svg{width:18px;height:18px}'
custom += '.v3-footer nav a{display:inline-flex;align-items:center;gap:7px}.v3-footer nav a>svg{flex:none;color:#133F8F}.v3-hero>.v3-wrap{grid-template-columns:minmax(0,1.35fr) minmax(0,.85fr);column-gap:52px}.v3 .v3-photo{height:440px;max-width:420px;margin:0 auto}.v3-photo img{padding:0;object-position:center bottom}.v3-hero h1{font-size:clamp(38px,3.7vw,52px)}.v3-hero-ctas{gap:12px}@media(max-width:820px){.v3-hero{padding:36px 0 48px}.v3-hero>.v3-wrap{grid-template-columns:1fr;max-width:600px;row-gap:22px}.v3-hero-copy{text-align:center}.v3-hero h1{font-size:34px}.v3-eyebrow{font-size:12px;line-height:1.8;max-width:360px;margin:0 auto 20px}.v3-hero-copy .v3-intro{font-size:14px;line-height:1.9;max-width:480px;margin:20px auto 0}.v3 .v3-photo{height:320px;width:100%;max-width:330px}.v3-hero-ctas{width:100%;max-width:420px;margin:0 auto}.v3-hero-ctas .v3-primary{min-height:50px}}'
custom += '.v3-hero h1{font-size:clamp(32px,3.3vw,46px);line-height:1.5}.v3-title-mobile-break{display:none}@media(max-width:820px){.v3-hero h1{font-size:clamp(25px,7vw,30px);line-height:1.6}.v3-title-mobile-break{display:block}.v3-title-desktop-break{display:none}}'
mapping=[]
payloads={}
for key,content in contents.items():
    content = add_card_icons(content)
    # Keep destinations distinct from same-page anchor scrolling.
    for anchor,dest in anchors.items():
        content=content.replace('href="#'+anchor+'"','href="'+files[dest]+'#'+anchor+'"')
    content=content.replace('実績は上のセクションのとおりです。','詳しい成果は実績ページでご紹介しています。')
    if key=='services':
        content += '<div class="v3-wrap section-cta">'+link('contact','ご依頼の流れ・連絡先を見る','v3-primary')+'</div>'
    pre = '' if key in ('home','mobile') else '<section class="v3-page-head"><div class="v3-wrap"><a class="v3-breadcrumb" href="'+files['home']+'">← トップに戻る</a><h1>'+titles[key]+'</h1><p>'+intros[key]+'</p></div></section>'
    payload = '<div class="v3 '+('v3-detail' if pre else 'v3-home')+'"><style>'+css+custom+'</style>'+header(key)+pre+'<main>'+content+'</main>'+footer()+'</div>'
    payloads[key]=payload
    # Standard HTML preview and editable design source share the exact body.
    (OUT/files[key]).write_text('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+titles[key]+' | Miyabiya Studio</title></head><body>'+payload+'</body></html>')
    (HERE/files[key]).write_text('<!doctype html><html lang="ja"><head><meta charset="utf-8"><script src="./support.js"></script></head><body><x-dc>'+payload+'</x-dc></body></html>')
    mapping.append({'key':key,'title':'別案 V3｜'+titles[key],'file':files[key]})

public_payloads = payloads.copy()

# Native radio controls switch full-page prototype views without navigating the
# sandboxed canvas document. Each artboard retains its own initial page.
route_css = '.v3-route{display:none;max-height:100vh;overflow-y:auto}.v3-router:not(:has(.v3-nav-control:checked))>.v3-default{display:block}.v3-nav{position:relative;cursor:pointer}.v3-nav-control{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:pointer}.v3-nav:has(input:focus-visible){outline:3px solid #4164A5;outline-offset:5px}'
route_bodies = {}
for key in ('home','profile','works','services','media','talks','membership','contact'):
    body = re.sub(r'<style>.*?</style>', '', payloads[key], flags=re.S)
    for destination, filename in files.items():
        route = 'home' if destination=='mobile' else destination
        pattern = r'<a([^>]*?)href="'+re.escape(filename)+r'(?:#[^"]*)?"([^>]*)>(.*?)</a>'
        def control(m, route=route):
            attrs=m.group(1)+m.group(2)
            if 'class="' in attrs: attrs=attrs.replace('class="','class="v3-nav ',1)
            else: attrs+=' class="v3-nav"'
            label=re.sub(r'<[^>]*>','',m.group(3)).strip().replace(' →','')
            return '<label'+attrs+'><input class="v3-nav-control" type="radio" name="v3-route" value="'+route+'" aria-label="'+html.escape(label,quote=True)+'">'+m.group(3)+'</label>'
        body = re.sub(pattern, control, body, flags=re.S)
    route_bodies[key] = body
    route_css += '.v3-router:has(.v3-nav-control[value="'+key+'"]:checked)>.v3-route-'+key+'{display:block}'
custom = re.sub(r'(?<=[ .>])a(?=[:.>{\s])', ':is(a,.v3-nav)', custom)
for key in payloads:
    default = 'home' if key=='mobile' else key
    payload = '<div class="v3-router"><style>'+css+custom+route_css+'</style>'+''.join(
        '<div id="page-'+route+'" class="v3-route v3-route-'+route+(' v3-default' if route==default else '')+'">'+body+'</div>'
        for route,body in route_bodies.items())+'</div>'
    payloads[key] = payload
    (OUT/files[key]).write_text('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+titles[key]+' | Miyabiya Studio</title></head><body>'+payload+'</body></html>')
    (HERE/files[key]).write_text('<!doctype html><html lang="ja"><head><meta charset="utf-8"><script src="./support.js"></script></head><body><x-dc>'+payload+'</x-dc></body></html>')

for asset in (HERE.parent/'assets').glob('*.webp'):
    (OUT/asset.name).write_bytes(asset.read_bytes())
portrait = HERE.parent.parent/'site/hero-photo.webp'
if portrait.exists():
    (OUT/'hero-photo.webp').write_bytes(portrait.read_bytes())

class Text(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0; self.parts=[]
    def handle_starttag(self,t,a):
        if t in ('style','script'): self.skip+=1
        elif t in ('h1','h2','h3','h4','p','li','a','label','dt','dd'): self.parts.append('\n')
    def handle_endtag(self,t):
        if t in ('style','script'): self.skip-=1
        elif t in ('h1','h2','h3','h4','p','li','a','label','dt','dd'): self.parts.append('\n')
    def handle_data(self,d):
        if not self.skip:self.parts.append(d)
    def value(self): return re.sub(r'\n[ \t]*\n+', '\n\n',''.join(self.parts)).strip()

copy=[]
for key in ('home','profile','works','services','media','talks','membership','contact'):
    t=Text();t.feed(route_bodies[key]);copy.append('# '+titles[key]+'\n\n'+t.value())
(HERE/'copy.md').write_text('\n\n'.join(copy))
t=Text(); t.feed(route_bodies['home'])
fresh=['# トップページ\n\n'+t.value()]
for key,intro in intros.items():
    fresh.append('# '+titles[key]+'の導入文\n\n'+intro)
(HERE/'copy-new.md').write_text('\n\n'.join(fresh))
(HERE/'pages.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))

# A private helper screen exposes the prepared HTML through normal copy controls.
helper='<html lang="ja"><meta charset="utf-8"><title>カンプ転記</title><style>body{font:16px sans-serif;padding:30px}button{margin:10px;padding:14px}textarea{width:90%;height:180px}</style><h1>カンプ転記</h1>'
for key,payload in payloads.items():
    helper+='<section><h2>'+titles[key]+'</h2><button data-key="'+key+'">'+key+' をコピー</button><textarea id="'+key+'">'+html.escape(payload)+'</textarea></section>'
helper+='<script>document.querySelectorAll("button").forEach(b=>b.onclick=async()=>{await navigator.clipboard.writeText(document.getElementById(b.dataset.key).value);b.textContent=b.dataset.key+" コピー済み"})</script></html>'
(OUT/'transfer.html').write_text(helper)

# Local comparison preserves every existing artboard and adds this version to the right.
source=HERE.parent.parent/'build/site-comp-artifact.html'
if source.exists():
    artifact=source.read_text()
    m=re.search(r'(<script type="application/json" id="appifact-doc">\s*)(.*?)(\s*</script>)',artifact,re.S)
    doc=json.loads(m.group(2)); c=json.loads(doc['content']['files']['canvas.json'])
    right=max(a['x']+a['w'] for a in c['artboards'])+400
    for i,(key,payload) in enumerate(payloads.items()):
        name=files[key]
        if name in doc['content']['files']: raise ValueError('name collision: '+name)
        doc['content']['files'][name]=(HERE/name).read_text()
        c['artboards'].append({'file':name,'x':right+(i%3)*1680,'y':(i//3)*3300,'w':390 if key=='mobile' else 1440,'h':3600 if key=='mobile' else 3000,'title':'別案 V3｜'+titles[key],'print':'flow'})
    doc['content']['files']['canvas.json']=json.dumps(c,ensure_ascii=False)
    new=json.dumps(doc,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    (HERE/'comparison.html').write_text(artifact[:m.start(2)]+new+artifact[m.end(2):])
print('Created',len(payloads),'pages; previous sources preserved.')

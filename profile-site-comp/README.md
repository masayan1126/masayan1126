# Miyabiya Studio のサイト管理

[Miyabiya Studio](https://studio.msyn.me/)と[PR動画制作の見積もり](https://studio.msyn.me/pricing/)を管理します。

現在公開しているサイトは `canvas/v3/` から生成します。ルートの `build_site.py` と `canvas/build.py` は旧版用です。現在のサイト更新には使用しません。

## 編集するファイル

| 変更内容 | ファイル |
|---|---|
| ページ構成・既存の本文 | `canvas/v3/build_v3.py` |
| 共通の文字・余白・配色・メニュー | `canvas/v3/site-design.css`、`canvas/v3/build_site_design.py`、`canvas/v3/site-navigation.js` |
| ヒーローの書斎ジオラマ (Blender で描いた映像) | 映像: `canvas/v3/home-3d/diorama/media/`、再生と配置: `canvas/v3/home-3d/diorama/video-hero.js`、描画スクリプト: `canvas/v3/home-3d/diorama/blender/` |
| 経歴・登壇などの元となる本文 | `canvas/Main.dc.html` |
| 料金・選択項目・基本料金に含む作業 | `canvas/v3/pricing-data.json` |
| 見積もりページの説明文・注意事項 | `canvas/v3/build_pricing.py` |
| 見積もりの計算・問い合わせ本文・共有URL | `canvas/v3/pricing-model.mjs` |
| 見積書PDFのレイアウト・保存処理 | `canvas/v3/pricing-pdf.mjs` |
| 選択操作・表示更新・コピー | `canvas/v3/pricing-ui.mjs` |
| 見積もりページの見た目 | `canvas/v3/pricing.css` |
| 公開ページの生成・メタ情報・配信設定 | `canvas/v3/build_public.py`、`wrangler.toml` |
| YouTubeの登録者数・代表動画の再生数 (ビルド時に自動取得) | `canvas/v3/youtube_stats.py`、前回の取得結果は `canvas/v3/youtube-stats.json` |
| 画像素材 | `canvas/assets/`、`site/` 内の画像 |

料金の根拠は[料金設定の根拠](docs/pricing/price-basis.md)にまとめています。元の料金表は `canvas/v3/pricing-proposal.json` に保存しています。

## 動作確認

Python 3 と Node.js を使用します。初回は `npm ci` で依存パッケージをインストールしてください。このディレクトリで次のコマンドを実行します。

```sh
npm ci
npm run build
npm test
npm run preview
```

プレビューは `http://127.0.0.1:8769/` で確認できます。公開用の生成先は `canvas/v3/site/` です。

トップページは、画面いっぱいの3Dヒーローと、白を基調にした本文で構成します。ヒーローは1/12の書斎ジオラマを Blender (Cycles) で描いた映像で、昼・夕暮れ・夜・朝が48秒で巡り、左右にゆっくり振れます。パソコン用 (1600×900) とスマホ用 (720×1280) の2本を画面の縦横比で切り替え、映像の中のモニターの位置に YouTube へのリンクを重ねます (`media/track.json`)。映像を作り直すときは `home-3d/diorama/blender/` の build_scene.py → render_all.sh → encode.sh の順です。見出しと文言は `canvas/v3/home-3d/immersive/hero.html` です。

全ページのレビューは `python3 canvas/v3/build_review.py` で生成します。`python3 canvas/v3/preview_review.py` でサーバーを起動し、`http://127.0.0.1:8776/review.html` で確認できます。更新後は同じタブを再読み込みしてください。

`python3 canvas/v3/validate_home.py` は、全ページのリンクと見出し、元の本文と料金の維持を検査します。レビュー用HTMLは公開用の生成先に含まれません。

## 公開

Cloudflare の対象アカウントで認証してから実行します。

```sh
npm ci
npm run deploy
```

公開先は既存の Cloudflare Pages プロジェクト `miyabiya-studio` です。GitHub へのpushだけでは公開サイトを更新しません。

## 共有した見積もりを保つ

`canvas/v3/pricing-rates/` は、過去に共有した見積もりの料金表です。各ファイルを編集・削除せず、Gitへ保存してください。料金を変えてビルドすると、新しい料金表が追加されます。既存の共有URLは共有時の金額を保持します。

生成済みのサイト、作業用プレビュー、認証キャッシュはGitに含めません。非公開の原資料と監査記録はローカルに保存し、公開用の料金根拠と分けて管理します。

## 見積書のPDF出力

PDFには、画面で選択した作業・金額・税額と、入力した宛名を記載します。宛名は外部に送信せず、ブラウザ内でPDFを作成します。共有URLから開いた場合は、共有時の料金を使います。PDFの末尾にも、同じ選択内容を開くリンクを付けます。

日本語フォントとPDF用ライブラリは、ダウンロード操作時に読み込みます。フォントの出典とライセンスは `canvas/v3/pdf-assets/` に保存しています。

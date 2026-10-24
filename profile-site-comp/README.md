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
| リンクを共有したときのプレビュー画像 (OGP) | `canvas/v3/build_og.py` で `site/og-profile.png` を生成 |

料金の根拠は[料金設定の根拠](docs/pricing/price-basis.md)にまとめています。元の料金表は `canvas/v3/pricing-proposal.json` に保存しています。

## 実績の数字を書くとき

計算で出した数字 (削減時間・削減率など) には、計算根拠を必ず小さく添えます。トップの数字は `<small class="stat-basis">`、実績カードは `<small class="result-basis">` を使います。

- 例: 月230〜350時間 → `月平均30件 ×（従来8〜12時間 − 改善後20分）＝ 月230〜350時間`
- 数字を変えたら、根拠の式も同時に直します。トップ・実績カード・実績ページ本文・`test-fixtures/approved-works-*.html` の数字をそろえます

## トップページと詳細ページの内容をそろえる

トップページは、詳細ページの内容を全部、または重要な部分だけ抜き出して載せる場所です。**トップページにあって、詳細ページに無い情報は作りません。** トップページだけを直して、詳細ページとずれることを防ぐためです。

| トップページのセクション | 詳細ページ |
|---|---|
| 事業内容 (`#business-gallery`) | `/services/` |
| 実績・成果 (`#works-story`) | `/works/` |
| 最新の動画 (`#latest`) | `/media/` |
| 経歴 (`#career-history`) | `/profile/` |

- 項目の数: トップページに出す項目は、すべて詳細ページにもあります。詳細ページだけにある項目は構いません (例: 事業内容の「AIエージェントの設計・ハーネス構築」)
- 文言: トップページの本文・数字・根拠は、詳細ページにも同じ文言で載せます。詳細ページはそこに説明を足します
- 見せ方: 同じ部品 (事業内容なら「悩み → 対応内容 → 実績 → 相談ボタン」、同じイラスト) を使います。詳細ページは横長にするなど配置は変えてよいですが、別物に見える構成にはしません
- 直し方: トップページを変えるときは、同じ変更を詳細ページにも入れます。できるだけ同じデータから両方を生成します (事業内容は `build_v3.py` の `service_summaries` と `service_details`、実績は `works-story.html`、最新の動画は `youtube_stats.render_latest`)
- 検査: `validate_home.py` が、トップページの各セクションの文言が詳細ページにあるかを確かめます。「詳細を見る」「相談する」などのリンクの文言と、リンク横の一言 (`section-foot`) は比べません。ずれていると検査が止まります
- 新しいセクションをトップページに足すときは、対応する詳細ページを決め、`validate_home.py` の `TOP_TO_DETAIL` に追加します

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

## OGP画像 (リンクのプレビュー画像)

プレビュー画像は、表示先の枠に合わせて中央から切り抜かれます (X・Facebook は 1.91:1、細いカードは 1.5:1 前後、小さいカードは正方形)。そのため、文字は中央の 630×630 に収め、左右の端には背景だけを置きます。文言や配置を変えたら、次のコマンドで作り直します。

```sh
python3 canvas/v3/build_og.py
```

文字が中央の範囲からはみ出すと、生成を止めます。比率ごとの見え方は `output/og-profile-crops.png` で確認できます。Google Chrome が必要です (見つからないときは `CHROME` にパスを指定)。ビルド時は画像の内容から `og-profile.<ハッシュ>.png` を作って `og:image` に指定するため、画像を変えると各サービスのキャッシュも新しい画像に切り替わります。

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


## 本編・ショート・X投稿の見積もり

2026年10月24日から、`mediaSchema: 1` の料金表で7構成を扱います。`pricing-model.mjs` の `quote` と `quotePresentation` を、画面・問い合わせ本文・PDFが共通で使います。本編の既存作業単価と税の扱いは維持します。

- `mediaRates` は新しい料金・条件の設定です。未設定は `null` とし、0円の確定料金と区別します。単独ショート、X製品PR投稿、動画のX告知、本編からの追加ショート（Xなし）を分けます。
- 本編と追加ショートは、検証・撮影を重ねて加算しません。既存の追加ショート・SNSシェアの料金は引き続き参照しますが、本数や未確定条件を確定済みとは表示しません。
- 新URLの `media` は `main`・`short`・`x` だけを受け付けます。追加修正と相談項目も復元します。媒体指定のない旧URLは、共有時の料金版による本編見積もりです。URLから料金を上書きする機能はありません。
- 個別契約の金額や本人確認用の仮条件は、Git対象外の `docs/pricing/private/media-reference.json` に保存します。公開データ・公開ビルド・料金履歴へ混ぜません。
- 非公開条件の検算は `PRICING_PRIVATE_FIXTURE` にそのファイルの絶対パスを指定して `npm test` を実行します。指定がない通常のテストでは、非公開条件の検算だけをスキップします。
- 本人確認用の比較資料は `node canvas/v3/build_pricing_review.mjs` で作り、既存の `build_review.py`・`preview_review.py` に束ねます。この生成処理は公開ビルドから呼びません。公開用の操作画面と、本人向けの参考額を同じレビュータブ内で確認できます。

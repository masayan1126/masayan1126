# 生成元と検証

作業場所は `profile-site-comp/`。リポジトリの親ではなく、`package.json`があるこのディレクトリで実行する。進捗は`TODO.md`を更新する。

## 変更する場所

| 変更 | 正本 |
| --- | --- |
| 検索・共有・保存用メタ情報 | `canvas/v3/site_metadata.py`。最終出力は `prototypes/editorial/build.py` が適用 |
| OGP・favicon・Appleアイコン | `canvas/v3/build_og.py`。採用済みマークとIBM Plex Sans JPから `prototypes/editorial/assets/social/` へ生成。入力・出力ハッシュと文字の安全範囲をmanifestで確認 |
| トップ本文・活動の並び・共通ヘッダーとフッター | `canvas/v3/prototypes/editorial/content.py` |
| 余白・配色・共通の操作表現 | `canvas/v3/prototypes/editorial/compact.css`、`editorial.css` |
| 見積もりページとダイアログの見た目 | `canvas/v3/prototypes/editorial/pricing-local.css` |
| ホバーの色変化を除く生成処理 | `canvas/v3/prototypes/editorial/interactions.py` |
| 表示文言の整合・導線整理 | `canvas/v3/prototypes/editorial/site_copy.py` |
| 文字サイズの尺度 | `canvas/v3/prototypes/typography/scales.mjs` |
| 採用書体の通常配布 | `canvas/v3/prototypes/editorial/assets/fonts/ibm-plex-sans-jp/`。`fetch_site_fonts.py`でGoogle Fontsの通常配布を取得し、400・700とOFL・出典・ハッシュを保つ |
| 全ページで使う色・寸法・余白の共通値 | `canvas/v3/prototypes/editorial/compact.css`の共通CSS変数。各ページ・`pricing-local.css`から参照 |
| トップのスクロール進行表示 | `canvas/v3/prototypes/editorial/reading-progress.mjs`、`compact.css`、`build.py` |
| 共通の線画／SNSアイコン | `canvas/v3/prototypes/editorial/icons/` |
| 拡張機能のアイコン・正式名 | `canvas/v3/prototypes/editorial/assets/extensions/manifest.json`と同フォルダの画像 |
| 人数と確認日 | `canvas/v3/youtube-audience.json`、`canvas/v3/prototypes/editorial/assets/extension-user-counts.json` |
| 料金・共有URL・問い合わせ文・PDF | `canvas/v3/pricing-data.json`、`pricing-model.mjs`、`pricing-pdf.mjs`、`pricing-rates/` |
| 公開用生成 | `canvas/v3/build_public.py`、`canvas/v3/prototypes/editorial/publish.py` |

`canvas/v3/site/`と`output/`は生成先。生成元を直してビルドする。旧版のルート`build_site.py`や`canvas/build.py`を使って現在のサイトを更新しない。

## 変更に合わせて確認する

- 付帯情報の変更では、公開7ページのtitle・description・OGP・Xカード・JSON-LD・正規URL・アイコン・manifestの整合と資産の実体を確認する。通常OGPの白以外の実画素が中央630px内に収まり、正方形でも見切れないことを検査する。X用は別の横長画像とし、横長の安全範囲と左右の余白の釣り合いを検査する。文字の計算値だけで見切れなしと判定しない。2026年10月28日の「正方形が見切れてる」という指摘に基づく。2026年10月28日、本人が横長専用画像の追加を採用したため、`og:image`と`twitter:image`の参照を分ける。通常OGPまで横長用の配置へ置き換えない。通常OGPは文字なしの大きなアバターにし、カード側のタイトル・説明文と画像内の文言を重ねない。小さなサムネイルでも顔が分かる密度を確認する。レビューには公開メタ情報が指す画像を使い、レビューだけ別画像へ置き換えて改善済みとしない。画像の寸法・配置はSNS側で変わるため、レビューの幅112pxなどを実サービスでの保証として扱わない。2026年10月28日の小カードの重複と画像が小さいという指摘に基づく。画像生成の入力を変えた場合は、先に`canvas/v3/build_og.py`で再生成し、manifestの一致を確認する。旧下地のOGPを現在の公開参照へ戻さない。
- サイトのコード変更は`npm run build`を実行する。これは公開用の生成と`validate_home.py`を含む。
- ローカルの採用案は`python3 canvas/v3/prototypes/editorial/build.py`で更新し、`python3 canvas/v3/prototypes/editorial/validate.py`で本文・リンク・資産・料金DOM・フォーム互換性を確認する。
- 関連する既存テストを実行する。共有の計算・フォーム・生成処理を変更した場合は`npm test`も通す。文書・スキルだけの変更では、サイトの再ビルドやデプロイを行わず、リンク・スキル形式・文章・同期を検証する。
- ビルドで取得キャッシュが変わることがある。今回の変更に必要か確認し、無関係な数値更新を混ぜない。
- PCと320px程度のスマホ幅で、余白によるまとまり、左端の整列、折り返し、画像・文字・フォーカスの欠け、横はみ出しを確認する。
- CSSの共通変更は、上書き後の計算済みスタイルを確認する。ホバー色の除去と、選択・フォーカス・エラーの表示を混同しない。
- 文字サイズの共通値を変えたら、全ページ（現在7ページ）のPC・スマホで、文字を表示している要素の計算済み`font-size`を集計する。追加したページも対象に含める。通常表示に加え、補足・注記・フォームの状態表示・見積もりダイアログも24・18・14pxの3種類に収まることを確認する。旧い12pxの指定も検査対象にする。
- 色・寸法・余白の共通値を変えたら、同じ役割の要素をページ横断で比較する。色は役割別の共通色、寸法と余白はpx単位の共通値に一致するかを確認する。PC・スマホの切り替えも共通のブレークポイントを使う。
- 共通変数を宣言しただけで統一済みにしない。後から読み込むCSS、詳細度、インライン指定などで、実際の表示値が上書きされていないことを確認する。
- 見積もりの計算や引き継ぎに触れたら、7通りの媒体の組み合わせ、要相談、別案、共有URL、PDF、問い合わせ文の一致と旧料金版の復元を確認する。

## レビュー・公開・後片付け

- 既存レビューは`http://127.0.0.1:8776/review.html`。同じ趣旨のレビューは同じファイルを更新し、工程をページ内のタブにまとめる。既存タブを再読み込みし、ユーザーが見ているタブを別の作業URLへ置き換えない。
- 採用済みの案を毎回選び直してもらわない。判断が必要な変更だけ、完成した案を見せて質問する。
- Gitでは無関係な未コミット・未追跡ファイルを保護し、対象だけをステージする。並列で編集する場合は担当別のworktreeを使う。読み取りだけのレビュー担当と同時編集を混同しない。
- 現行の統合先ブランチとCloudflareの公開先指定は異なる場合がある。公開前に[README](../../../../README.md)と実際の設定を読み戻し、最新の指示・必須チェックに従う。
- 公開した場合は`https://studio.msyn.me/`の対象ページと参照CSSを再取得し、公開画面も再読み込みする。CloudflareのHTML変換を考慮し、転送や配信の反映途中を完了扱いにしない。
- 使った検証用タブ・作業ブランチ・worktreeを整理する。ユーザーが利用しているサーバー、レビュータブ、保存が必要な資料は残す。
- 報告は変更点・確認結果・確認先を短く示す。未確認の作業を完了と書かない。

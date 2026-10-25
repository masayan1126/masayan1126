# 依頼の判断と相談を支えるデザイン

2026-10-25。対象は Miyabiya Studio 全9ページ。確定した料金・実績と3Dヒーローを保ち、情報の優先順位、操作、読みやすさを整える。以下は設計の根拠であり、問い合わせ増加を保証するものではない。

| 調べた知見 | 今回の適用 |
| --- | --- |
| [NN/g：視覚的な階層](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/) / [近接の原則](https://www.nngroup.com/articles/gestalt-proximity/) | 見出しと説明を近づけ、別の話題は余白で離す。近い灰色を親子に重ねず、面は名前を付けた節だけに指定する。装飾の上線・左線を使わない。 |
| [GOV.UK：ボタン](https://design-system.service.gov.uk/components/button/) | 相談などの主操作、確認・保存などの副操作、本文リンクを区別する。ボタンは部分的な修飾クラスだけで作らず、全インスタンスに共通の寸法・余白・状態を持たせる。 |
| [NN/g：一般的な条件の料金を示す](https://www.nngroup.com/articles/show-prices-for-common-scenarios/) | PRページに本編・ショートの代表価格と条件を載せる。公開の共通計算を実行して生成し、個別契約の金額を混ぜない。 |
| [NN/g：B2Bの信頼](https://www.nngroup.com/articles/b2b-trust-from-b2c/) | サービスに対応する担当実績、実際のPR動画、視聴者データ、登壇記録を判断材料として近くに置く。根拠のある数字と比較条件を保持する。 |
| [NN/g：段階的開示](https://www.nngroup.com/articles/progressive-disclosure/) | PR概要では価格例と主操作を先に置き、修正料などの詳しい条件は見出しから開く。見積もり内の金額・追加料金・要相談の有無は引き続き表示する。 |
| [NN/g：再認と想起](https://www.nngroup.com/articles/recognition-and-recall/) | 見積もりの回答確認・選び直し・代替案の差額を維持する。完成後の相談では同じ計算結果から本文を作り、フォームへ引き継ぐ。 |
| [Carbon：動き](https://carbondesignsystem.com/building-blocks/foundations/motion/overview/) | ブランドの3D表現は残し、操作への反応と短い出現に動きを使う。減らす設定、手動停止、文字が最初から読める状態を維持する。 |
| [W3C：文字コントラスト](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) / [非テキスト](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) / [ターゲットの大きさ](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | 本文は4.5:1、識別に必要な操作輪郭・状態は3:1を確認する。主な操作は48px以上を設計基準とし、フォーカスと選択状態を色だけに頼らず示す。 |

## 確認方法

ページの最初の画面だけではなく、全セクションと下記の状態を確認する。数値検査だけで見た目の品質を合格にしない。

- 9ページの先頭から末尾、主要CTAと副CTA、背景と内側の面、文字と背景の組み合わせ。
- メニュー、実績タブ全5件、経歴タブ全3件、料金条件の展開、見積もりの質問・完成・代替案、旧見積もり、PDFダイアログ。
- PC・390px・320pxの折り返し、操作サイズ、キーボードの位置と戻り先。
- 現行・旧料金、共有URL、PDF、相談文の一致。問い合わせは入力確認までとし、検証用の実送信はしない。

ボタンは `site_journeys.py` の共通部品を生成元で使う。旧HTML由来の部品は `normalize_actions` で移行し、`validate_home.py` が修飾クラスだけの操作を拒否する。CSSの役割別背景は `site-journeys.css` に置く。

## 公開後の効果を見る

既存のGA4で、相談・試算のクリック、見積もり開始・完成、フォーム開始・送信成功を区別する。送信ボタンを押しただけでは獲得として数えない。イベントには氏名・連絡先・相談本文・見積もりURLのクエリを含めない。件数と遷移率を以前の期間と比較し、流入の違いにも注意して見直す。

[Google公式のページビュー計測](https://developers.google.com/analytics/devguides/collection/ga4/views)を確認し、自動ページビューを止めて、クエリ・ハッシュを除いたURLと参照元を明示して送る。履歴変更やリンクの自動計測は独立して動くため、対象ストリームの拡張計測もオフにする。2026-10-25に本人がこの設定変更を承認した。プロパティは `555892520`、測定IDは `G-0HHRPGZRZB`。この前提を変える場合は、見積もりの自由入力が自動収集されないか再確認する。

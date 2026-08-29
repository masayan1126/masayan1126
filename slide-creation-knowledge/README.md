# スライド作成ナレッジ

スライドを作成するときに共通で使う、設計規則とデザインシステムです。Codex、Claude Code、その他のAIから参照できます。

## 最初に読むファイル

1. [practices.md](./practices.md) — 見やすさ、伝わりやすさ、説明しやすさを守る共通規則
2. [design-system-green.md](./design-system-green.md) — グリーン版の色、書体、余白、レイアウト
3. [design-system-green/deck-template.html](./design-system-green/deck-template.html) — デッキ雛形

## ブラウザで確認する

- [共通規則のレビューHTML](https://htmlpreview.github.io/?https://github.com/masayan1126/masayan1126/blob/main/slide-creation-knowledge/review.html)
- [デザインシステムグリーン見本帳](https://htmlpreview.github.io/?https://github.com/masayan1126/masayan1126/blob/main/slide-creation-knowledge/design-system-green-review.html)

HTMLプレビューサービスが利用できない場合は、リポジトリを取得して各HTMLをブラウザで開いてください。

## AIへ渡す固定URL

- 共通規則: https://raw.githubusercontent.com/masayan1126/masayan1126/main/slide-creation-knowledge/practices.md
- グリーン仕様: https://raw.githubusercontent.com/masayan1126/masayan1126/main/slide-creation-knowledge/design-system-green.md
- 機械可読情報: https://raw.githubusercontent.com/masayan1126/masayan1126/main/slide-creation-knowledge/design-system-green/manifest.json
- スライドCSS: https://raw.githubusercontent.com/masayan1126/masayan1126/main/slide-creation-knowledge/design-system-green/slides.css

AIへは、次のように指示します。

> 共通規則とグリーン仕様を読み、両方を適用してスライドを作成してください。明示した要件と衝突する場合は、要件を優先し、変更理由を示してください。

## 更新方法

規則を変更する場合は practices.md と review.html を同時に更新します。デザインを変更する場合は design-system-green.md、見本帳、CSS、雛形を同時に更新します。変更後は design-system-green/validate.mjs を実行します。

## リポジトリ

- [スライド作成ナレッジのディレクトリ](https://github.com/masayan1126/masayan1126/tree/main/slide-creation-knowledge)

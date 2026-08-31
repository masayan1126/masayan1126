# スライド作成ナレッジ

スライドを作成するときに、テーマやデザインに関係なく参照する共通プラクティスです。Codex、Claude Code、その他のAIから参照できます。

## ファイル

- [practices.md](./practices.md) — 見やすさ、伝わりやすさ、説明しやすさを守る共通プラクティス
- [defaults.md](./defaults.md) — 共通プラクティスを当てはめるときの既定値（色・太さ・大きさ・字間・間隔）
- [review.html](./review.html) — 共通プラクティスをブラウザで確認するレビュー画面
- `README.md` — この案内

`practices.md` には、特定の配色、書体、ブランド、デザインシステム、スライド雛形を含みません。
具体的な数値は `defaults.md` へ分けてあり、別のブランドやテーマで作る場合はそちらだけを差し替えます。

## AIへ渡す固定URL

https://raw.githubusercontent.com/masayan1126/masayan1126/main/slide-creation-knowledge/practices.md

AIへは、次のように指示します。

> 共通プラクティスを読み、テーマやデザインに関係なく適用してスライドを作成してください。明示した要件と衝突する場合は、要件を優先し、変更理由を示してください。

## ブラウザで確認する

[共通プラクティスのレビューHTML](https://htmlpreview.github.io/?https://github.com/masayan1126/masayan1126/blob/main/slide-creation-knowledge/review.html)

HTMLプレビューサービスが利用できない場合は、リポジトリを取得して `review.html` をブラウザで開いてください。

## 更新方法

プラクティスを変更する場合は、`practices.md` と `review.html` を同時に更新します。
具体的な数値を変更する場合は `defaults.md` を更新します。

# Agentic Engineering ナレッジベース

Claude Code / MCP / サブエージェント / スキル設計など、AIエージェント（ハーネス）を実用化するための知見を蓄積する索引型ナレッジベース。後の動画・スライド・技術ブログ記事への引用を前提に、引用しやすい単位で切り出して保管する。

`projects/` の「実際に動かしているワークフロー」とは独立。ここは概念・パターン・教訓を扱う。

## 構造の方針

**記事・フレームワーク単位でディレクトリを切る**。1つのトピックにつき 1 ディレクトリを用意し、その中に `README.md`（自分の解釈）と関連資料（画像・図）をまとめる。

```
agentic-engineering/
└── {slug}/
    ├── README.md   # 自分の解釈・要約・引用ガイド
    └── cover.png   # 代表画像（記事の図など）
```

## 目次

| ディレクトリ | 扱う対象 |
|---|---|
| [the-8-levels-of-agentic-engineering/](./the-8-levels-of-agentic-engineering/) | Bassim Eledath「The 8 Levels of Agentic Engineering」フレームワークと自分の現在地 |
| [openai-harness-engineering/](./openai-harness-engineering/) | OpenAI「ハーネスエンジニアリング：エージェントファーストの世界における Codex の活用」の5観点チェックレポート |

## 新規ドキュメント作成手順

1. `agentic-engineering/{slug}/` ディレクトリを作る（slug は kebab-case の英語スラッグ）
2. 代表画像があれば `cover.png` として保存
3. `README.md` を frontmatter 付きで書く
4. 上記の「目次」テーブルに 1 行追加

## frontmatter スキーマ

各ディレクトリの `README.md` 冒頭に必ず記述する:

```yaml
---
title: ドキュメントタイトル
tags: [agentic-engineering, claude-code, ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: 実体験 | 公式ドキュメント | コミュニティ | 検証
quotable: true   # 動画/記事への引用許可フラグ（内輪メモは false）
related: []
---
```

**狙い**: 後日 `grep -r "tags:.*subagent"` や frontmatter 解析スクリプトで「特定タグの記事だけ抽出 → 動画台本に投入」が可能になる。

## 引用ガイド（動画・記事で参照するとき）

- `quotable: true` のドキュメントのみ引用可
- 引用形式の推奨:
  - 動画: 「自分のナレッジベース（agentic-engineering/{slug}/）より」と口頭言及
  - 記事: 該当ディレクトリの「要点（3行サマリ）」をブロック引用し、出典として GitHub リポジトリの該当パスへリンク
- 一次ソース外（`source: 公式ドキュメント` など）の場合は元の出典も併記する

## 関連

- [`/CLAUDE.md`](../CLAUDE.md) — リポジトリ全体のルール
- [`/preferences/favorite-keywords.md`](../preferences/favorite-keywords.md) — 関心キーワード（タグ命名の参考）

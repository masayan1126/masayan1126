# CLAUDE.md

## リポジトリの役割

このリポジトリは「脳」のような役割を持つ。思考やアイデアをAIに書き出し、タスク化・自動化・成果物作成までの流れを管理する核となるプロジェクト。パブリックリポジトリのため、秘匿情報は含めない。

## ディレクトリ構成

```
masayan1126/
├── preferences/         # 関心・嗜好・傾向（キーワード、除外テーマ等）
│   └── docs/            # preferences の可視化（Draw.io 元データ等）
├── projects/            # 注力プロジェクトの実態・ワークフロー
│   ├── <project-key>/   # 各プロジェクト（youtube, tech-blog 等）
│   │   ├── overview.md  # 概要・目標・現状
│   │   ├── workflow.md  # 自動化フロー手順
│   │   └── docs/        # Draw.io 元データ
│   └── _template/       # 新規プロジェクト用テンプレート
├── execution-plans/     # 実行計画（月次タスク計画表等）
├── agentic-engineering/ # Agentic Engineering 知見の索引型ナレッジベース（引用前提）
├── docs/                # アーキテクチャ・設計ドキュメント
├── .claude/skills/      # Claude Code スキル（スクリプト・認証情報を含む）
```

## スキル構成ルール

- スクリプトはスキル内に配置: `.claude/skills/<skill-name>/scripts/`
- 認証情報（credentials.json, token_*.json）もスキルディレクトリ内に配置
- `.gitignore` で `**/credentials.json`, `**/token_*.json` を除外

## Draw.io ルール

- Draw.io MCP で図を生成した場合、元データ（XML or Mermaid）を必ずファイルとして保存すること
- 保存先は図と同じディレクトリの `docs/` 等に `.drawio.xml`拡張子で保存
- ファイル名は図の内容がわかる名前にする

## projects ルール

- 各プロジェクトには `overview.md`（概要・目標）と `workflow.md`（自動化フロー手順）を必ず配置
- Draw.io で図を作成した場合は `<project>/docs/` に保存（Draw.io ルールに準拠）
- 新規プロジェクト追加時は `_template/` をコピーして作成

## YouTube チャンネル登録者数マーカールール

リポジトリ内の `.md` でチャンネル登録者数に言及する場合は、必ずマーカーコメントで囲むこと。
SessionStart フック（`.claude/hooks/fetch_subscribers.py`）が YouTube Data API から最新値を取得し、マーカーの中身だけを自動置換する。

```markdown
登録者数 **<!--subs-->1,234<!--/subs-->名**（<!--subs-date-->2026/1/23<!--/subs-date-->時点）
```

- `<!--subs-->N<!--/subs-->` — 登録者数（カンマ区切り）。リポジトリ内の全 `.md` がスキャン対象
- `<!--subs-date-->YYYY/M/D<!--/subs-date-->` — 取得日（数値が変化したときのみ更新される）
- 数値をベタ書きすると自動更新の対象外になるため禁止
- CLAUDE.md 自体はスキャン対象外（この説明例が実数値で上書きされるのを防ぐため）

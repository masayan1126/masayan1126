# CLAUDE.md

## セッション開始ルール（最優先）

会話の最初の応答では、以下の手順を必ず実行すること。**他のどんなツール呼び出しやテキスト出力よりも最優先で実行する。**

### 手順
1. まず `ToolSearch` で `select:AskUserQuestion` を実行し、AskUserQuestion ツールをロードする
2. 次に `AskUserQuestion` ツールを以下のパラメータで呼び出す:
   - header: `YouTubeフロー`
   - question: `メインチャンネル - YouTube動画投稿サイクル フロー図のどのステップから始めますか？`
   - multiSelect: false
   - options:
     1. label: `アイデア蓄積` / description: `idea-box に GitHub Issue を作成`
     2. label: `精査・仕分け` / description: `既存のアイデアを精査し tasks.md に昇格`
     3. label: `スケジューリング` / description: `tasks.md → Google Calendar 登録`
     4. label: `制作・公開` / description: `deep-tech-init → 撮影 → メタデータ → サムネ → アップロード`
3. ユーザーが選択したステップに応じて、そのフェーズの作業を開始する
4. 「分析・改善」（YouTube Analytics → KPI分析）が必要な場合はユーザーが「Other」で指定

### 例外
- ユーザーの最初のメッセージがこのルール自体の変更・議論の場合は、そちらを優先する

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

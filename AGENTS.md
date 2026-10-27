# リポジトリの共通ルール

## Miyabiya Studioのサイト更新

`profile-site-comp/`のサイト更新・デザイン・情報設計・文言・操作を変更するときは、[サイトのAGENTS.md](profile-site-comp/AGENTS.md)と[update-miyabiya-studio](profile-site-comp/.agents/skills/update-miyabiya-studio/SKILL.md)を読んで適用する。

基本は、シンプルさを保ち、情報を絞り、余白・近接・整列で要素やセクションのまとまりを示すこと。このサイトの詳細な方針はスキルを正本とする。他のプロジェクトには自動適用しない。

このサイトのスキルは`profile-site-comp/.agents/skills/`を正本とし、同ディレクトリ内のClaude CodeとCodexの入口から参照する。

理由：サイトの採用済み方針を、次回以降の作業でも継続して使うため。
<!-- adopted: 2026-10-27 -->

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

説明用の例は、フックがこの文書の例示を更新しないようHTMLエスケープして示す。実際の記事では通常のHTMLコメントとして記述する。

<code>登録者数 **&lt;!--subs--&gt;1,234&lt;!--/subs--&gt;名**（&lt;!--subs-date--&gt;2026/1/23&lt;!--/subs-date--&gt;時点）</code>

- <code>&lt;!--subs--&gt;N&lt;!--/subs--&gt;</code> — 登録者数（カンマ区切り）。リポジトリ内の全 `.md` がスキャン対象
- <code>&lt;!--subs-date--&gt;YYYY/M/D&lt;!--/subs-date--&gt;</code> — 取得日（数値が変化したときのみ更新される）
- 数値をベタ書きすると自動更新の対象外になるため禁止

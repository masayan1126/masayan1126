# Claude Code バンドルスキル（Bundled Skills）調査レポート
## 調査角度: 公式定義とアーキテクチャ -- Skills vs Slash Commands vs Plugins の違い、SKILL.md の仕組み

調査日: 2026-03-30

---

## 1. スキル（Skills）の公式定義

### 1-1. Agent Skills とは何か

Agent Skills は「指示（instructions）、スクリプト（scripts）、リソース（resources）のフォルダで、エージェントが発見し、タスクをより正確かつ効率的に遂行するために使用するもの」である。Skills はファイルシステムベースの再利用可能なリソースで、Claude にドメイン固有の専門知識（ワークフロー、コンテキスト、ベストプラクティス）を提供し、汎用エージェントをスペシャリストに変える。プロンプト（会話レベルの一回限りの指示）とは異なり、Skills はオンデマンドで読み込まれ、複数の会話で同じガイダンスを繰り返し提供する必要がなくなる。

📎 出典: "Agent Skills - Claude API Docs" - Anthropic (確認日: 2026-03-30) <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>
   📍 位置: "Why use Skills" セクション冒頭

### 1-2. オープンスタンダードとしての Agent Skills

Claude Code の Skills は **Agent Skills オープンスタンダード** (<https://agentskills.io>) に準拠している。このフォーマットは元々 Anthropic が開発し、オープンスタンダードとして公開された。Claude Code はこの標準に加え、呼び出し制御（invocation control）、サブエージェント実行（subagent execution）、動的コンテキスト注入（dynamic context injection）などの追加機能を提供する。

2026年3月時点で、このオープンスタンダードを採用しているプラットフォームは以下の通り（一部抜粋）:
- Claude Code / Claude.ai（Anthropic）
- Cursor
- Gemini CLI（Google）
- OpenAI Codex
- VS Code / GitHub Copilot
- JetBrains Junie
- Roo Code
- OpenHands
- Goose（Block）
- Kiro（AWS）
- Databricks
- Spring AI
- Mistral AI Vibe
- その他多数（合計30以上のプラットフォーム）

📎 出典: "Overview - Agent Skills" - agentskills.io (確認日: 2026-03-30) <https://agentskills.io/home>
   📍 位置: ロゴカルーセルに表示されるパートナー一覧および "Open development" セクション

### 1-3. Claude Code における Skills の位置づけ

Claude Code では Skills は3つのプロダクトで利用可能:
- **Claude.ai**: プリビルト Agent Skills（PPTX, XLSX, DOCX, PDF）+ カスタム Skills（zipアップロード）
- **Claude Code（CLI）**: カスタム Skills のみ。ファイルシステムベースで API アップロード不要
- **Claude Agent SDK**: カスタム Skills のみ。`.claude/skills/` ディレクトリで自動検出

📎 出典: "Agent Skills - Claude API Docs" - Anthropic (確認日: 2026-03-30) <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>
   📍 位置: "Where Skills work" セクション

---

## 2. Skills vs Slash Commands vs Built-in Commands の違い

### 2-1. 統合の経緯

Claude Code **v2.1.3**（2026年1月24日頃リリース）で、スラッシュコマンドと Agent Skills が**統一システム**に統合された。変更の要点は「Slash commands and Agent Skills are now part of a unified system. Any Skill you create can be invoked explicitly using a / prefix, and custom prompts created as Markdown files are treated as Skills that Claude can discover when relevant.」である。既存の `.claude/commands/` ファイルは引き続き動作する完全な後方互換性が確保されている。

📎 出典: "Claude Code Merges Slash Commands Into Skills (Don't Miss Your Update)" - Medium (@joe.njenga) (2026-01-24) <https://medium.com/@joe.njenga/claude-code-merges-slash-commands-into-skills-dont-miss-your-update-8296f3989697>
   📍 位置: 記事冒頭〜"What Changed" セクション

### 2-2. 三者の明確な違い

| 区分 | Built-in Commands | Skills（旧 Slash Commands 含む） | Bundled Skills |
|------|------------------|-------------------------------|----------------|
| 例 | `/help`, `/compact`, `/clear`, `/init`, `/plan` | ユーザー定義の `/deploy`, `/fix-issue` 等 | `/simplify`, `/batch`, `/debug`, `/loop`, `/claude-api` |
| 実装方式 | 固定ロジックを直接実行 | プロンプトベース: SKILL.md の指示に従いツールを駆使 | プロンプトベース: Claude Code に同梱された詳細なプレイブック |
| 起動者 | ユーザーのみ | ユーザーまたは Claude（設定次第） | ユーザーまたは Claude |
| 特徴 | セッション管理、コンテキスト操作などの基本機能 | サポートファイル、フロントマター制御、動的コンテキスト注入対応 | 並列エージェント起動、ファイル読み取り、コードベースへの適応が可能 |

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Bundled skills" セクション冒頭の注釈および表

### 2-3. Skills と旧 Slash Commands の統合ルール

`.claude/commands/deploy.md` と `.claude/skills/deploy/SKILL.md` は**どちらも** `/deploy` を作成し、同じように動作する。既存の `.claude/commands/` ファイルは引き続き動作する。Skills は追加機能として以下をサポート:
- サポートファイル用のディレクトリ構造
- フロントマターによる呼び出し制御
- Claude が関連性を判断した際の自動読み込み

スキルとコマンドが同名の場合、**スキルが優先**される。

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: ページ上部の Note ブロック「Custom commands have been merged into skills.」

---

## 3. Skills / Plugins / MCP / Hooks の関係

### 3-1. 各コンポーネントの役割

| コンポーネント | 役割 | メタファー |
|-------------|------|----------|
| **Skills** | 手続き的知識（ワークフロー、ベストプラクティス）を提供。タスクコンテキストに基づき自動発動 | 「カンニングペーパー」 |
| **Plugins** | Skills、エージェント、Hooks、MCP サーバーを1つのパッケージにバンドルして配布 | 「ツールキット」 |
| **MCP Servers** | 外部ツール・データソースとの接続を提供するオープンプロトコル | 「別アプリへの橋」 |
| **Hooks** | ライフサイクルイベント（PostToolUse, UserPromptSubmit 等）で自動実行されるシェルコマンド | 「自動化ルール」 |
| **Subagents** | 専門的なAIパーソナリティ。隔離されたコンテキストウィンドウと制限されたツールアクセスを持つ | 「専門チームメンバー」 |

📎 出典: "Understanding Claude Code's Full Stack: MCP, Skills, Subagents, and Hooks Explained" - alexop.dev (確認日: 2026-03-30) <https://alexop.dev/posts/understanding-claude-code-full-stack/>
   📍 位置: 各コンポーネントの説明セクション

### 3-2. Skills と MCP の違い

Claude Help Center によると:
- **Projects**: 常にロードされる静的知識 → Skills は必要な時だけ動的にアクティベート
- **MCP**: 外部サービスへの接続 → Skills はツールの「使い方」に関する手続き的知識を提供
- **Custom Instructions**: すべての会話に広く適用 → Skills はタスク固有で選択的にロード

📎 出典: "What are Skills? | Claude Help Center" - Anthropic (確認日: 2026-03-30) <https://support.claude.com/en/articles/12512176-what-are-skills>
   📍 位置: 表形式の比較テーブル

---

## 4. SKILL.md ファイルの仕様

### 4-1. 基本構造

SKILL.md は **2つの部分** で構成される:
1. **YAML フロントマター**（`---` マーカー間）: Claude にスキルをいつ使用するかを伝える
2. **Markdown コンテンツ**: スキルが呼び出された時に Claude が従う指示

最小構成例:
```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---

Instructions for Claude go here...
```

📎 出典: "Specification - Agent Skills" - agentskills.io (確認日: 2026-03-30) <https://agentskills.io/specification>
   📍 位置: "SKILL.md format" セクション

### 4-2. フロントマターフィールド一覧

#### Agent Skills オープンスタンダード準拠フィールド

| フィールド | 必須 | 制約 |
|-----------|------|------|
| `name` | Yes | 最大64文字。小文字英字・数字・ハイフンのみ。ハイフンで開始/終了不可。連続ハイフン不可。**親ディレクトリ名と一致必須** |
| `description` | Yes | 最大1024文字。空不可。スキルの内容と使用タイミングを記述 |
| `license` | No | ライセンス名またはバンドルされたライセンスファイルへの参照 |
| `compatibility` | No | 最大500文字。環境要件（対象プロダクト、システムパッケージ、ネットワークアクセス等） |
| `metadata` | No | 任意のキーバリューマッピング |
| `allowed-tools` | No | スペース区切りの事前承認ツールリスト（実験的） |

📎 出典: "Specification - Agent Skills" - agentskills.io (確認日: 2026-03-30) <https://agentskills.io/specification>
   📍 位置: "Frontmatter" テーブルおよび各フィールド説明

#### Claude Code 拡張フィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `argument-hint` | No | オートコンプリート時に表示される引数ヒント。例: `[issue-number]` |
| `disable-model-invocation` | No | `true` で Claude の自動呼び出しを無効化。デフォルト: `false` |
| `user-invocable` | No | `false` で `/` メニューから非表示。デフォルト: `true` |
| `model` | No | スキルアクティブ時に使用するモデル |
| `effort` | No | 努力レベル: `low`, `medium`, `high`, `max`（Opus 4.6のみ） |
| `context` | No | `fork` でフォークされたサブエージェントコンテキストで実行 |
| `agent` | No | `context: fork` 時のサブエージェントタイプ（`Explore`, `Plan`, `general-purpose` またはカスタム） |
| `hooks` | No | スキルのライフサイクルにスコープされたフック |
| `paths` | No | グロブパターンで自動アクティベーションを制限 |
| `shell` | No | `bash`（デフォルト）または `powershell` |

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Frontmatter reference" テーブル

### 4-3. 文字列置換変数

| 変数 | 説明 |
|------|------|
| `$ARGUMENTS` | スキル呼び出し時に渡された全引数 |
| `$ARGUMENTS[N]` | 0ベースインデックスで特定の引数にアクセス |
| `$N` | `$ARGUMENTS[N]` の省略形 |
| `${CLAUDE_SESSION_ID}` | 現在のセッションID |
| `${CLAUDE_SKILL_DIR}` | スキルの SKILL.md ファイルが含まれるディレクトリ |

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Available string substitutions" テーブル

### 4-4. 動的コンテキスト注入

`` !`<command>` `` 構文を使い、スキルコンテンツが Claude に送信される前にシェルコマンドを実行できる。コマンド出力がプレースホルダーを置き換える。これはプリプロセッシングであり、Claude が実行するものではない。

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
```

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Inject dynamic context" セクション

---

## 5. スキルのディレクトリ構造と配置場所

### 5-1. 推奨ディレクトリ構造

```
my-skill/
├── SKILL.md           # メイン指示（必須）
├── template.md        # Claude が記入するテンプレート（任意）
├── references/        # 詳細ドキュメント（任意、オンデマンド読み込み）
├── examples/          # 期待される出力フォーマットの例（任意）
├── scripts/           # Claude が実行可能なスクリプト（任意）
│   └── validate.sh
└── assets/            # テンプレート、リソース（任意）
```

📎 出典: "Specification - Agent Skills" - agentskills.io (確認日: 2026-03-30) <https://agentskills.io/specification>
   📍 位置: "Directory structure" セクション

### 5-2. 配置場所と適用範囲

| レベル | パス | 適用範囲 |
|--------|------|---------|
| Enterprise | マネージド設定による | 組織内全ユーザー |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | 自分の全プロジェクト |
| Project | `.claude/skills/<skill-name>/SKILL.md` | 当該プロジェクトのみ |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | プラグイン有効化箇所 |

優先順位: Enterprise > Personal > Project。Plugin スキルは `plugin-name:skill-name` の名前空間を使用するため、他のレベルと競合しない。

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Where skills live" テーブル

### 5-3. モノレポ対応: ネストされたディレクトリの自動検出

サブディレクトリでファイルを編集する際、Claude Code はネストされた `.claude/skills/` ディレクトリからスキルを自動検出する。例えば `packages/frontend/` でファイルを編集している場合、`packages/frontend/.claude/skills/` のスキルも検出される。

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Automatic discovery from nested directories" セクション

---

## 6. スキルのライフサイクル: 読み込み・実行の仕組み

### 6-1. Progressive Disclosure（段階的開示）

Skills の最も重要な設計パターン。3段階の情報読み込み:

| レベル | 読み込みタイミング | トークンコスト | 内容 |
|--------|------------------|-------------|------|
| **Level 1: メタデータ** | 常時（起動時） | スキルあたり約100トークン | YAML フロントマターの `name` と `description` |
| **Level 2: 指示** | スキルがトリガーされた時 | 5,000トークン未満推奨 | SKILL.md 本文の指示とガイダンス |
| **Level 3+: リソース** | 必要時のみ | 事実上無制限 | バンドルファイル（scripts/, references/ 等）。bash経由で実行され、コンテンツ自体はコンテキストにロードされない |

📎 出典: "Agent Skills - Claude API Docs" - Anthropic (確認日: 2026-03-30) <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>
   📍 位置: "Three types of Skill content, three levels of loading" セクション

### 6-2. 具体的な読み込みフロー（PDF処理スキルの例）

1. **起動時**: システムプロンプトに含まれる → `PDF Processing - Extract text and tables from PDF files, fill forms, merge documents`
2. **ユーザーリクエスト**: 「Extract the text from this PDF and summarize it」
3. **Claude が呼び出す**: `bash: read pdf-skill/SKILL.md` → 指示がコンテキストにロード
4. **Claude が判断**: フォーム入力は不要 → FORMS.md は読まない
5. **Claude が実行**: SKILL.md の指示に従ってタスクを完了

📎 出典: "Agent Skills - Claude API Docs" - Anthropic (確認日: 2026-03-30) <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>
   📍 位置: "Example: Loading a PDF processing skill" セクション

### 6-3. 呼び出し制御マトリクス

| フロントマター設定 | ユーザー呼び出し | Claude 呼び出し | コンテキスト読み込みタイミング |
|------------------|---------------|---------------|--------------------------|
| デフォルト | 可 | 可 | Description は常にコンテキスト内、フルスキルは呼び出し時にロード |
| `disable-model-invocation: true` | 可 | 不可 | Description はコンテキストに含まれない、フルスキルはユーザー呼び出し時のみロード |
| `user-invocable: false` | 不可 | 可 | Description は常にコンテキスト内、フルスキルは呼び出し時にロード |

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Control who invokes a skill" セクションのテーブル

### 6-4. スキル Description のコンテキスト予算

スキルの Description はコンテキストにロードされ、Claude がどのスキルが利用可能かを把握する。多数のスキルがある場合、Description はコンテキストウィンドウの **1%** に動的にスケールする文字予算に収まるよう短縮される（フォールバック値: **8,000文字**）。各エントリの上限は予算に関係なく **250文字**。環境変数 `SLASH_COMMAND_TOOL_CHAR_BUDGET` で上限を変更可能。

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Skill descriptions are cut short" セクション

---

## 7. 名前空間（Namespace）の仕組み

### 7-1. Plugin の名前空間

Plugin スキルは `plugin-name:skill-name` という名前空間を使用する。これにより、他のレベル（Enterprise / Personal / Project）のスキルと競合しない。

例: `example-skills:theme-factory`, `example-skills:pdf`, `youtube-metadata-creator:generate-tech-video-metadata`

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Where skills live" テーブルの注記

### 7-2. 名前の優先ルール

同名スキルが複数レベルに存在する場合の優先順位: Enterprise > Personal > Project。スキルとコマンド（`.claude/commands/`）が同名の場合、**スキルが優先**。

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Where skills live" テーブル後の説明文

---

## 8. バンドルスキル一覧

Claude Code に同梱されているバンドルスキルは以下の5つ:

| スキル | 目的 |
|--------|------|
| `/simplify [focus]` | 最近変更したファイルのコード再利用性・品質・効率をレビューし修正。3つのレビューエージェントを並列起動し、結果を集約して修正を適用 |
| `/batch <instruction>` | 大規模な並列コードベース変更をオーケストレーション。コードベースを調査し、5〜30の独立ユニットに分解。承認後、各ユニットごとに独立した git worktree でバックグラウンドエージェントを起動し、テスト実行とPR作成まで行う |
| `/debug [description]` | セッションのデバッグログを有効化し、問題をトラブルシュート |
| `/loop [interval] <prompt>` | プロンプトをインターバルで繰り返し実行。デプロイメント監視やPR管理に有用 |
| `/claude-api` | プロジェクト言語（Python, TypeScript, Java, Go, Ruby, C#, PHP, cURL）に応じた Claude API リファレンスと Agent SDK リファレンスをロード。`anthropic`, `@anthropic-ai/sdk`, `claude_agent_sdk` のインポート時に自動起動 |

📎 出典: "Extend Claude with skills - Claude Code Docs" - Anthropic (確認日: 2026-03-30) <https://code.claude.com/docs/en/skills>
   📍 位置: "Bundled skills" テーブル

---

## 9. ベストプラクティス

### 9-1. SKILL.md の推奨サイズ

- SKILL.md 本文は **500行以下** を推奨
- 詳細なリファレンス資料は別ファイルに分割
- 参照ファイルは SKILL.md から**1階層深さまで**に留める（深くネストしない）
- 100行を超えるリファレンスファイルには目次を追加

📎 出典: "Skill authoring best practices - Claude API Docs" - Anthropic (確認日: 2026-03-30) <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
   📍 位置: "Progressive disclosure patterns" セクション

### 9-2. Description の書き方

- **三人称で記述**する（"Processes Excel files..." であり "I can help you..." ではない）
- スキルが何をするかと、いつ使うかの**両方**を含める
- 具体的なキーワードを含め、250文字以内に要点を前方配置する
- 100以上のスキルから選択される可能性を考慮し、十分な詳細を含める

📎 出典: "Skill authoring best practices - Claude API Docs" - Anthropic (確認日: 2026-03-30) <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
   📍 位置: "Writing effective descriptions" セクション

### 9-3. 命名規則

- 小文字英字・数字・ハイフンのみ使用（最大64文字）
- 動名詞形（gerund form）推奨: `processing-pdfs`, `analyzing-spreadsheets`
- 曖昧な名前を避ける: `helper`, `utils`, `tools` は不可
- 予約語を含めない: `anthropic`, `claude` は使用不可

📎 出典: "Skill authoring best practices - Claude API Docs" - Anthropic (確認日: 2026-03-30) <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
   📍 位置: "Naming conventions" セクション

---

## 10. Anthropic 公式スキルリポジトリ

Anthropic は GitHub 上で公式スキルリポジトリ (<https://github.com/anthropics/skills>) を公開しており、以下のような公式スキルが含まれている:
- `skill-creator`: スキルの作成・改善・評価のためのメタスキル
- `claude-api`: Claude API リファレンスマテリアル（Claude Code にバンドル済み）
- その他、`pdf`, `pptx`, `xlsx`, `docx` 等のドキュメント系スキル

`skill-creator` スキルは、5段階のワークフロー（Decide → Write → Create test → Evaluate → Iterate → Optimize description）でスキル開発をガイドし、評価用の `evals/evals.json` の作成やベンチマーク実行まで自動化する。

📎 出典: "skills/skills/skill-creator/SKILL.md at main - anthropics/skills" - GitHub (確認日: 2026-03-30) <https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md>
   📍 位置: SKILL.md 全体

---

## 11. セキュリティに関する注意事項

Skills は信頼できるソース（自身が作成したもの、または Anthropic から入手したもの）からのみ使用することが強く推奨される。悪意のあるスキルは、スキルの記載目的と異なる方法でツールを呼び出したりコードを実行したりするよう Claude に指示できる。信頼できないソースのスキルを使用する場合は、SKILL.md、スクリプト、画像、その他すべてのバンドルファイルを徹底的に監査する必要がある。

📎 出典: "Agent Skills - Claude API Docs" - Anthropic (確認日: 2026-03-30) <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>
   📍 位置: "Security considerations" セクション

---

## Sources（全出典一覧）

1. [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills) - Anthropic 公式ドキュメント（1次ソース）
2. [Agent Skills - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) - Anthropic 公式ドキュメント（1次ソース）
3. [Skill authoring best practices - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - Anthropic 公式ドキュメント（1次ソース）
4. [Overview - Agent Skills (agentskills.io)](https://agentskills.io/home) - オープンスタンダード仕様（1次ソース）
5. [Specification - Agent Skills (agentskills.io)](https://agentskills.io/specification) - オープンスタンダード仕様（1次ソース）
6. [What are Skills? | Claude Help Center](https://support.claude.com/en/articles/12512176-what-are-skills) - Anthropic ヘルプセンター（1次ソース）
7. [skills/skills/skill-creator/SKILL.md - GitHub](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) - Anthropic 公式リポジトリ（1次ソース）
8. [GitHub - anthropics/skills](https://github.com/anthropics/skills) - Anthropic 公式リポジトリ（1次ソース）
9. [Claude Code Merges Slash Commands Into Skills - Medium](https://medium.com/@joe.njenga/claude-code-merges-slash-commands-into-skills-dont-miss-your-update-8296f3989697) - 技術ブログ（2次ソース、2026-01-24）
10. [Understanding Claude Code's Full Stack - alexop.dev](https://alexop.dev/posts/understanding-claude-code-full-stack/) - 技術ブログ（2次ソース）

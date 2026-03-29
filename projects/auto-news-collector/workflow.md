# 完全自動AI情報収集 ワークフロー

## フロー概要

Claude Cowork のスケジュール機能で毎朝自動起動し、Cowork が Chrome を自動操作して Grok サイトから X ポストデータを取得・CSV 化、並行して Claude Code スキルで Web ニュース収集を行い、HTML 生成 → git push で Cloudflare Pages に自動デプロイ、GitHub Actions で Discord 通知まで完全自動で実行する。n8n 等の外部サービスは不要。

## 全体フロー図

```
┌───────────────────┐
│  Claude Cowork    │
│  スケジュール機能  │  毎朝自動実行
└────────┬──────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│           データ収集（並列）                 │
│                                            │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  ┌──────────────────┐  ┌──────────────────┐│
│  │  Xポスト取得     │  │  Webニュース収集  ││
│  │                  │  │  collect-news    ││
│  │  Cowork が Chrome │  │  スキル          ││
│  │  を自動操作       │  │                  ││
│  │  → Grok サイト   │  │  調査Agent x4    ││
│  │    アクセス       │  │  FC Agent x2     ││
│  │  → データ取得    │  │  計6体のAgent    ││
│  │  → CSV 生成      │  │                  ││
│  │  → input/x/      │  │                  ││
│  │    table.csv     │  │  → input/web/    ││
│  └──────────────────┘  └──────────────────┘│
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌───────────────────────────────────────┐
│  HTML生成 + 通知準備                   │
│  Claude Code + daily-news スキル      │
│                                       │
│  → site/YYYY/MM/DD/index.html (概要)  │
│  → site/YYYY/MM/DD/news.html  (記事)  │
│  → site/YYYY/MM/DD/posts.html (Xポスト)│
│  → .github/message.json (Discord用)   │
└────────────────┬──────────────────────┘
                 │
                 ▼
┌───────────────────────────────────────┐
│  デプロイ + 通知                       │
│                                       │
│  git push (PAT認証)                   │
│    → Cloudflare Pages 自動デプロイ    │
│    → GitHub Actions → Discord 通知    │
│                                       │
│  🌐 daily-news-and-posts.pages.dev    │
└───────────────────────────────────────┘
```

## ステップ詳細

### 1. スケジュール起動

- **ツール**: Claude Cowork スケジュール機能
- **タイミング**: 毎朝（時刻は Cowork 側で設定）
- **動作**: daily リポジトリで Claude Code セッションを自動起動
- **自動化**: 完全自動

### 2. Xポスト取得（Cowork ブラウザ自動操作）

- **ツール**: Claude Cowork（Chrome 自動操作）→ Grok サイト
- **動作**:
  1. Cowork がスケジュール起動後、Chrome ブラウザを自動操作
  2. Grok のサイトにアクセスし、Grok タスク機能が収集した X ポストデータを取得
  3. 取得したデータを整形し CSV ファイルとして保存
- **出力**: `input/x/table.csv`（アカウント名、ポスト内容、いいね数等）
- **対象**: AI 関連の注目ポスト
- **自動化**: 完全自動（Cowork による Chrome 操作で人手不要）

### 3. Web ニュース収集（`/collect-news` スキル）

- **ツール**: Claude Code + `collect-news` スキル
- **動作**:
  1. `input/web/` の既存ファイルからナンバリング決定
  2. `excluded-news.md` で既報ニュースを除外
  3. 6つの Agent チームで収集・検証を実行
- **エージェント構成（計6体）**:
  - **調査・情報収集エージェント（4並列）** — WebSearch で最新記事を収集
    - Agent 1: AI モデル・サービス
    - Agent 2: AI 開発ツール・エージェント
    - Agent 3: AI 生成コンテンツ・音声
    - Agent 4: AI トレンド・デザイン
  - **ファクトチェックエージェント（2体）** — 収集記事の事実確認・情報源の信頼性検証
  4. カテゴリ別に整理して Markdown で保存
- **参照**: `masayan1126/preferences/favorite-keywords.md`, `excluded-themes.md`
- **出力**: `input/web/ai-news-YYYY-MM-DD-daily.md`
- **自動化**: 完全自動

### 4. HTML 生成 + Discord 通知準備（`/daily-news` スキル）

- **ツール**: Claude Code + `daily-news` スキル
- **動作**:
  1. `input/web/` の Markdown と `input/x/table.csv` を読み込み
  2. ニュースを整理・重複排除、`excluded-news.md` に記録
  3. 静的 HTML ページを生成（正準テンプレート準拠）
  4. Discord 通知用 `message.json` を生成
- **出力**:
  - `site/YYYY/MM/DD/index.html` — 概要ページ
  - `site/YYYY/MM/DD/news.html` — ニュース一覧
  - `site/YYYY/MM/DD/posts.html` — Xポスト一覧
  - `site/index.html` — トップページ更新
  - `.github/message.json` — Discord 通知ペイロード
- **自動化**: 完全自動

### 5. デプロイ（git push → Cloudflare Pages）

- **ツール**: git (GitHub PAT 認証)
- **動作**: commit & push → Cloudflare Pages が自動ビルド・デプロイ
- **PAT が必要な理由**: Cowork / Claude Code が非対話的に git push を実行するため、ブラウザ認証や対話型プロンプトは使えない。GitHub Personal Access Token を使うことで、自動化パイプライン内から認証付き push が可能になる
- **公開先**: https://daily-news-and-posts.pages.dev
- **自動化**: 完全自動

### 6. Discord 通知（GitHub Actions）

- **ツール**: GitHub Actions (`discord-notify.yml`)
- **トリガー**: push to main / 毎日 UTC 00:30 (JST 09:30)
- **動作**: `.github/message.json` の内容を Discord Webhook で送信
- **自動化**: 完全自動

## 自動化構成

| レイヤー | ツール | 設定場所 |
|---------|-------|---------|
| スケジューラ | Claude Cowork | Cowork アプリ内 |
| ニュース収集 | Claude Code スキル | `daily/.claude/skills/collect-news/` |
| HTML 生成 | Claude Code スキル | `daily/.claude/skills/daily-news/` |
| デプロイ | Cloudflare Pages | `daily/wrangler.jsonc` |
| 通知 | GitHub Actions | `daily/.github/workflows/discord-notify.yml` |
| 朝ルーティン | GitHub Actions | `daily/.github/workflows/morning-routine.yml` |
| 月次課金通知 | GitHub Actions | `daily/.github/workflows/billing-notify.yml` |

## 設計思想

- **外部サービス不要**: n8n、Zapier 等のワークフロー自動化サービスに依存しない
- **ローカル完結**: 事前準備や処理はすべてローカルで完結
- **Claude Code ネイティブ**: スキルファイル + Agent 並列実行で柔軟な収集が可能
- **静的サイト配信**: Cloudflare Pages で高速・無料・高可用性

## フロー図

`docs/` ディレクトリの `.drawio.xml` を参照（作成予定）。

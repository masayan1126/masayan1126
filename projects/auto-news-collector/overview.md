# AI情報収集（Auto News Collector）

## 概要

AI情報収集を自動化するプロジェクト。2つのフローで構成される：**日次フロー**（広く浅く）は Claude Cowork + Grok + Claude Code スキルで毎朝のAI情報を完全自動収集し、静的HTMLとして Cloudflare Pages で公開する。**週次フロー**（狭く深く）は厳選した技術記事を Gmail 経由でブックマークし、毎週金曜に NotebookLM の Cinematic Overview で動画解説を自動生成する半自動のディープリードパイプライン。

## 目標

| 指標 | 現状 | 目標 | 期限 |
|------|------|------|------|
| 手動ニュースチェック | 0分（自動化済み） | 維持・品質向上 | — |
| 日次サイト更新 | 毎朝自動配信中 | 安定運用 | — |
| Discord 通知 | 自動配信中 | 安定運用 | — |
| 週次ディープリード | 構築中 | 毎週金曜に自動生成 | 2026年4月 |
| 記事ブックマーク → 動画化 | 未開始 | 週5-10記事をカバー | — |

## 現状

日次フローは運用中。毎朝 Claude Cowork スケジュールで自動起動し、ニュース収集 → HTML生成 → git push → Cloudflare Pages デプロイ → Discord 通知まで完全自動で稼働している。

週次ディープリードフロー（Gmail → NotebookLM Cinematic Overview）は構築中。

## 技術スタック

| コンポーネント | 技術 | 役割 |
|--------------|------|------|
| スケジューラ | Claude Cowork スケジュール機能 | 毎朝の自動起動（日次）/ 毎週金曜 9:00 の自動起動（週次） |
| Xポスト収集 | Cowork ブラウザ操作 → Grok サイト | Chrome 自動操作で Grok にアクセスし X ポストデータを取得・CSV 生成 |
| Web ニュース収集 | Claude Code + `collect-news` スキル | 6体のエージェントチーム（調査4並列 + ファクトチェック2体）で Web 記事収集・検証 |
| HTML 生成 | Claude Code + `daily-news` スキル | 静的 HTML ページ生成 |
| ホスティング | Cloudflare Pages | 静的サイト配信 |
| 通知 | Discord Webhook (GitHub Actions) | ニュースサマリ配信 |
| バージョン管理 | GitHub (PAT 認証) | git push → 自動デプロイ |
| メール取得 | Gmail API | 「note」ラベル付きメールから記事URL抽出（週次） |
| ブラウザ操作（週次） | claude-in-chrome | NotebookLM の自動操作（週次） |
| 動画解説生成 | NotebookLM Cinematic Overview | 厳選記事の動画解説を自動生成（週次） |

## 情報ソース

- **Web ニュース**: WebSearch による最新AI記事収集（英語・日本語）
- **X (Twitter)**: Cowork が Chrome を自動操作して Grok サイトにアクセスし、Grok タスク機能が収集した X ポストデータを取得・CSV 化
- **Gmail ブックマーク**: ユーザーが厳選した技術記事URL（「note」ラベル付きメール）→ 週次ディープリードフロー

## 自動化レベルについて

- **日次フロー**: 完全自動（human-in-the-loop なし）。n8n 等の外部サービス不要、ローカル完結
- **週次フロー**: 半自動（human-in-the-loop）。記事のブックマークと最終レビューは人手。自動化部分で Gmail API と NotebookLM（Google エコシステム）を利用

## 公開サイト

- https://daily-news-and-posts.pages.dev

## 関連リポジトリ

- [daily](https://github.com/masayan1126/daily) — ニュース収集・HTML生成・デプロイの実体リポジトリ

## キーワード・フィルタリング設定

- `masayan1126/preferences/favorite-keywords.md` — 収集対象キーワード（6カテゴリ）
- `masayan1126/preferences/excluded-themes.md` — 除外テーマ（ロボティクス、動画生成AI等）
- `daily/input/web/excluded-news.md` — 既報ニュース重複防止リスト

## 関連スキル（daily リポジトリ内）

- `collect-news` — 6体エージェントチーム（調査4並列 + ファクトチェック2体）による Web ニュース収集・検証 → `input/web/` に Markdown 保存
- `daily-news` — 収集済みニュース・Xポストの HTML 生成 + Discord 通知用 JSON 生成 + git push

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-03-30 | 週次ディープリードフロー追加 |
| 2026-03-29 | 初版作成（実運用構成を反映） |

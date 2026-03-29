# 完全自動AI情報収集（Auto News Collector）

## 概要

n8n 等の外部ワークフロー自動化サービスを使わず、Claude Cowork + Grok + Claude Code スキルだけで毎朝のAI情報収集を完全自動化するプロジェクト。収集したニュースは静的HTMLとして生成し、Cloudflare Pages で公開する。

## 目標

| 指標 | 現状 | 目標 | 期限 |
|------|------|------|------|
| 手動ニュースチェック | 0分（自動化済み） | 維持・品質向上 | — |
| 日次サイト更新 | 毎朝自動配信中 | 安定運用 | — |
| Discord 通知 | 自動配信中 | 安定運用 | — |

## 現状

運用中。毎朝 Claude Cowork スケジュールで自動起動し、ニュース収集 → HTML生成 → git push → Cloudflare Pages デプロイ → Discord 通知まで完全自動で稼働している。

## 技術スタック

| コンポーネント | 技術 | 役割 |
|--------------|------|------|
| スケジューラ | Claude Cowork スケジュール機能 | 毎朝の自動起動 |
| Xポスト収集 | Cowork ブラウザ操作 → Grok サイト | Chrome 自動操作で Grok にアクセスし X ポストデータを取得・CSV 生成 |
| Web ニュース収集 | Claude Code + `collect-news` スキル | 6体のエージェントチーム（調査4並列 + ファクトチェック2体）で Web 記事収集・検証 |
| HTML 生成 | Claude Code + `daily-news` スキル | 静的 HTML ページ生成 |
| ホスティング | Cloudflare Pages | 静的サイト配信 |
| 通知 | Discord Webhook (GitHub Actions) | ニュースサマリ配信 |
| バージョン管理 | GitHub (PAT 認証) | git push → 自動デプロイ |

## 情報ソース

- **Web ニュース**: WebSearch による最新AI記事収集（英語・日本語）
- **X (Twitter)**: Cowork が Chrome を自動操作して Grok サイトにアクセスし、Grok タスク機能が収集した X ポストデータを取得・CSV 化

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
| 2026-03-29 | 初版作成（実運用構成を反映） |

# Auto News Collector - 完全自動AI情報収集

n8n等の外部ワークフロー自動化サービスを使わず、Claude Cowork + Grok + Claude Code スキルだけで毎朝のAI情報収集を完全自動化するプロジェクト。

収集したニュースは静的HTMLとして生成し、[Cloudflare Pages](https://daily-news-and-posts.pages.dev) で公開。

## フロー図

![全自動AI情報収集フロー](docs/auto-news-flow.jpg)

## 詳細ドキュメント

- [overview.md](overview.md) — プロジェクト概要・目標・技術スタック
- [workflow.md](workflow.md) — 自動化フロー手順の詳細
- [docs/auto-news-flow.drawio.xml](docs/auto-news-flow.drawio.xml) — フロー図の Draw.io 元データ

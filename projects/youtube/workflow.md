# YouTube ワークフロー

## フロー概要

アイデアの蓄積から動画公開・分析まで、5つのフェーズで構成される制作パイプライン。Claude Code スキルと GitHub Actions による自動化を組み込み、手動作業を最小化している。

## アイデアの源泉

- 実務経験（日常業務で得た知見、技術的課題の解決体験）
- 情報収集（Web / X、AI関連ニュース・新機能発表）
- 既存コンテンツ分析（他の YouTube・テックブログを参考に組み合わせ企画）
- ひらめき

## ステップ

### 1. アイデア蓄積

- **PC から**: Claude Code (CLI) → idea-box Issue 作成（🤖 半自動）
- **スマホから**: Claude Cowork Dispatch 経由 → idea-box Issue 作成（👤 手動）
- **自動化**: auto-label Action が Issue に `youtube` ラベルを自動付与（⚙ 全自動）

### 2. 精査・仕分け

- **ダイジェスト通知**: project-digest Action → Discord（金曜19:00）（⚙ 全自動・計画中）
- **バックログ精査**: Discord / GitHub 画面で確認（👤 手動）
- **優先度判定・企画提案**: Claude Code content-planner でトレンド・SEO・自チャンネル分析から優先順位を決定（🤖 半自動）
- **昇格**: tasks.md に優先度順で登録（👤 手動）

### 3. スケジューリング

- **ツール**: Claude Code calendar-sync スキル
- **操作**: tasks.md を元に Google Calendar に時間枠を登録（🤖 半自動）
- **外部API**: Google Calendar API

### 4. 制作・公開

1. **プロジェクト初期化**: `deep-tech-init` スキルで sample-kit → Dir 作成、input/1.md にテキスト配置（🤖 半自動）
2. **撮影・編集**: Screen Studio で画面収録 + 編集・書き出し（👤 手動）
3. **メタデータ生成**: Claude Code でタイトル・説明文・タグ生成（🤖 半自動）
4. **チャプター生成**: `video-timeline` スキルで動画内容を分析しタイムスタンプを自動生成（🤖 半自動）
5. **サムネイル生成**: claude-in-chrome で Gemini Pro 画像生成を起動（タブ×4）、タイトル自動注入 → サンプル画像を手動添付 → 生成実行（🤖👤 半自動+手動）
6. **アップロード**: `upload-youtube` スキルで YouTube にアップロード（公開日自動計算、playlist 自動振分）（🤖 半自動）
7. tasks.md のステータスを `published` に更新

### 5. 分析・改善

- **Analytics 取得**: youtube-analytics Action（土曜08:00）→ YouTube Analytics API（⚙ 全自動・計画中）
- **Discord 通知**: 週次レポート送信（⚙ 全自動・計画中）
- **KPI 分析・改善判断**: Discord / ブラウザで視聴数・CTR 確認（👤 手動）
- tasks.md のステータスを `analyzed` に更新
- 改善フィードバック → 次サイクルへ

## ステータス管理

tasks.md でステータスを一元管理:

`planned` → `in_progress` → `published` → `analyzed`

## 自動化構成

| 自動化 | 種類 | 状態 |
|--------|------|------|
| auto-label | GitHub Actions (idea-box) | 稼働中 |
| deep-tech-init | Claude Code Skill | 稼働中 |
| content-planner | Claude Code Skill | 稼働中 |
| video-timeline | Claude Code Skill | 稼働中 |
| upload-youtube | Claude Code Skill | 稼働中 |
| calendar-sync | Claude Code Skill | 稼働中 |
| project-digest | GitHub Actions (daily) | 計画中 |
| youtube-analytics | GitHub Actions (daily) | 計画中 |

## フロー図

`docs/メインチャンネル - YouTube動画投稿サイクル フロー図.xml` を参照。

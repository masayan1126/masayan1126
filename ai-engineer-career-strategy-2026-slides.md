---
marp: true
theme: default
paginate: true
header: "AI時代のエンジニアのキャリア戦略 — 2026年版"
style: |
  section {
    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
  }
  h1 {
    color: #2563eb;
  }
  h2 {
    color: #1e40af;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 0.3em;
  }
  table {
    font-size: 0.75em;
  }
  blockquote {
    border-left: 4px solid #3b82f6;
    background: #eff6ff;
    padding: 0.5em 1em;
    font-size: 0.85em;
  }
  .source {
    font-size: 0.6em;
    color: #6b7280;
    text-align: right;
  }
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: "" -->

# AI時代のエンジニアの<br>キャリア戦略 — 2026年版

**「コードを書く人」から「AIを指揮するプロフェッショナル」へ**

調査日: 2026年4月5日

---

## エグゼクティブサマリー

- エンジニアの役割が **構造的に変化** — コード実装者からAI指揮者へ
- DORAレポート: 約 **90%** がAI使用、個人生産性 **+21%** だが組織全体は横ばい
- 個人の成果を組織に転換するには **戦略的アプローチ** が不可欠
- 本資料で **8つの軸** の具体的アクションを提示

> 最も重要な問い: AIにできないことの中で、自分が最も価値を発揮できるのはどこか？

<div class="source">出典: <a href="https://dora.dev/research/2025/dora-report/">DORA Report 2025</a> / <a href="https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025">Faros AI</a></div>

---

## 綺麗な「AI開発論」はもういらない

**現場のリアルな悩みはもっと切実だ**

- 「AIが書いた大量のコードのレビューに追われ、**何のために働いているのか分からない**」
- 「圧倒的なスピードでコードを生成するAIを見て、**自分の価値が揺らいでいる**」
- 「AIの進化が速すぎて、**来年の仕事がどうなっているか予測できない**」

> 「この言語を学べば安泰」「このスキルがあれば代替されない」
> — そんな**銀の弾丸は、もはや存在しない。**
> 生存確率を1%でも上げるための、泥臭い戦略が必要だ。

---

## 1. ハーネスエンジニアリング（1/3）

**AIの性能はモデルだけで決まらない**

- Martin Fowler: **Model + それ以外 = ハーネス**
- モデルを包む仕組み（プロンプト、ツール、コンテキスト）が成果を左右
- LangChain調査: ハーネス改善のみで精度 **52.8% → 66.5%**
- モデル交換よりも **ハーネス最適化** の方が費用対効果が高い

> "The harness is the new competitive advantage."

<div class="source">出典: <a href="https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html">Martin Fowler「Harness Engineering」</a> / <a href="https://blog.langchain.com/improving-deep-agents-with-harness-engineering/">LangChain「Improving Deep Agents with Harness Engineering」</a></div>

---

## 1. ハーネスエンジニアリング（2/3）

**コンテキストエンジニアリングの実践**

- Karpathy, Lütke が提唱 — 適切な情報をAIに渡す技術
- コンテキストファイルの活用:

| ツール | ファイル名 |
|--------|-----------|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursorrules` |
| GitHub Copilot | `copilot-instructions.md` |

- チーム全体で **共有・バージョン管理** することが鍵

<div class="source">出典: <a href="https://simonwillison.net/2025/Jun/27/context-engineering/">Simon Willison「Context Engineering」</a> / <a href="https://www.agentrulegen.com/guides/what-are-ai-coding-rules">Agent Rules Builder「What Are AI Coding Rules?」</a></div>

---

## 1. ハーネスエンジニアリング（3/3）

**仕様駆動開発 — AIへの入力品質を上げる**

- GitHub **Spec Kit**: 仕様からコード生成のワークフロー
- CyberAgent **L1〜L4** 成熟度モデル:

| レベル | 内容 | AI活用度 |
|--------|------|----------|
| L1 | 補完・提案の受け入れ | 低 |
| L2 | チャットベースの対話生成 | 中 |
| L3 | 仕様からの自律生成 | 高 |
| L4 | エージェントによる自律開発 | 最高 |

- L3以上には **仕様の明確化** が前提条件

<div class="source">出典: <a href="https://github.com/github/spec-kit">GitHub Spec Kit</a> / <a href="https://developers.cyberagent.co.jp/blog/archives/60229/">CyberAgent「Spec駆動開発」</a></div>

---

## 2. マルチエージェントオーケストレーション（1/3）

**設計パターンの全体像**

| 提唱元 | パターン数 | 特徴 |
|---------|-----------|------|
| Anthropic | **5** | シンプル・実用重視 |
| Google | **8** | 網羅的・学術的 |
| Microsoft | **5** | エンタープライズ志向 |

- Andrew Ng: **GPT-3.5 + ワークフロー > GPT-4 ゼロショット**
- モデル性能よりも **オーケストレーション設計** が成果を決める

<div class="source">出典: <a href="https://www.anthropic.com/research/building-effective-agents">Anthropic「Building Effective Agents」</a> / <a href="https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/">Google ADK Patterns</a> / <a href="https://learn.microsoft.com/ja-jp/azure/architecture/ai-ml/guide/ai-agent-design-patterns">Microsoft「AI Agent Design Patterns」</a></div>

---

## 2. マルチエージェントオーケストレーション（2/3）

**成果とフレームワーク**

- Anthropicマルチエージェント構成で **90%** の性能向上

| フレームワーク | 提供元 | 特徴 |
|---------------|--------|------|
| LangGraph | LangChain | グラフベース制御 |
| CrewAI | CrewAI | 役割ベースチーム |
| AutoGen | Microsoft | 会話駆動協調 |
| Agents SDK | OpenAI | 公式SDK統合 |

<div class="source">出典: <a href="https://www.anthropic.com/engineering/multi-agent-research-system">Anthropic「Multi-Agent Research System」</a> / <a href="https://galileo.ai/blog/autogen-vs-crewai-vs-langgraph-vs-openai-agents-framework">Galileo「Agent Framework Comparison」</a></div>

---

## 2. マルチエージェントオーケストレーション（3/3）

**プロトコル標準化の波**

- **MCP** (Model Context Protocol): AIとツールの接続標準
- **A2A** (Agent-to-Agent): エージェント間通信プロトコル
- 2つの組み合わせで **相互運用可能なエージェント基盤** が形成
- 特定ベンダーに依存しないオープンなエコシステムへ

> MCP = AIとツールをつなぐ「USB-C」
> A2A = エージェント同士をつなぐ「共通言語」

<div class="source">出典: <a href="https://arxiv.org/html/2505.02279v1">arXiv「Agent Interoperability Protocols Survey」</a></div>

---

## 3. AI生成コードの品質担保（1/2）

**深刻な品質リスクの現状**

- Veracode: AI生成コードの **45%** がセキュリティテスト不合格
- Apiiro調査:
  - 権限昇格の脆弱性 **322%増**
  - 設計上の欠陥 **153%増**
- 「動くコード」と「安全なコード」は別物
- レビューなしの受け入れは **技術的負債の加速装置**

> AIが書いたコードこそ、人間が厳しくレビューすべき

<div class="source">出典: <a href="https://www.veracode.com/blog/genai-code-security-report/">Veracode GenAI Code Security Report</a> / <a href="https://apiiro.com/blog/4x-velocity-10x-vulnerabilities-ai-coding-assistants-are-shipping-more-risks/">Apiiro「4x Velocity, 10x Vulnerabilities」</a></div>

---

## 3. AI生成コードの品質担保（2/2）

**実践的な品質保証アプローチ**

- **Addy Osmani の PRコントラクト**
  - AI生成PRの受け入れ基準を事前に定義
  - テスト・セキュリティ・パフォーマンスの観点を網羅
- **CyberAgent の3ツール並行運用**
  - 複数AIツールで生成・検証を並行実施
  - ツール間の出力を相互比較して品質を担保
- 鍵は **人間の判断力** — AI出力を評価できる能力

<div class="source">出典: <a href="https://addyo.substack.com/p/code-review-in-the-age-of-ai">Addy Osmani「Code Review in the Age of AI」</a> / <a href="https://developers.cyberagent.co.jp/blog/archives/60882/">CyberAgent「AI時代のコードレビューフロー再設計」</a></div>

---

## 3. 生成役と評価役の分離

**AI × AI × 人間の多層レビュー構造**

- **AI（生成役）** → **別のAI（評価役）** → **人間（最終価値検証）**
- ベースライン品質（70〜80%）はAI同士で担保
- 人間は「仕様との整合」「ビジネス価値」の検証に集中

> Karpathyは自ら命名した「vibe coding」を**時代遅れ**と宣言。
> 新たに「**agentic engineering**」を提唱 — エージェントを指揮・監督する技術

<div class="source">出典: <a href="https://addyo.substack.com/p/code-review-in-the-age-of-ai">Addy Osmani「Code Review in the Age of AI」</a> / <a href="https://www.glideapps.com/blog/what-is-agentic-engineering">Glide「What is Agentic Engineering?」</a></div>

---

## 3. 「捨てる」「防ぐ」の価値

**最も価値あるスキルは「コードを削除すること」**

- AI生成コストがゼロに近づき、**「何を作らないか」** が希少スキルに
- arXiv研究: AI生成コードの未解決問題が **110,000件以上** に急増
- Sonar調査: **88%** の開発者がAIによる技術的負債の悪影響を報告
- 新概念「**認知負債**」— コードだけでなく **チームの理解** も負債になる

> Your job is no longer to build the mountain.
> Your job is to **carve the sculpture**.

<div class="source">出典: <a href="https://dev.to/the_nortern_dev/the-most-valuable-skill-in-2026-isnt-writing-code-it-is-deleting-it-53j1">DEV Community「The most valuable skill in 2026 isn't writing code」</a> / <a href="https://arxiv.org/abs/2603.28592">arXiv「Debt Behind the AI Boom」</a> / <a href="https://margaretstorey.com/blog/2026/02/09/cognitive-debt/">Margaret-Anne Storey「Cognitive Debt」</a></div>

---

## 4. AIツールのキャッチアップ戦略（1/2）

**ツール利用の最新動向**

- Claude Code: 開発者調査で **最も愛されるツール1位**
- 開発者の **70%** がマルチツール運用
- MCP: SDK累計 **9,700万** ダウンロード突破
- Gartner予測: **2026年末** にタスク特化型AIエージェントが **40%** に

<div class="source">出典: <a href="https://newsletter.pragmaticengineer.com/p/ai-tooling-2026">Pragmatic Engineer「AI Tooling 2026」</a> / <a href="https://survey.stackoverflow.co/2025/">Stack Overflow Survey 2025</a> / <a href="https://www.gartner.com/en/newsroom/press-releases/2025-08-26-gartner-predicts-40-percent-of-enterprise-apps-will-feature-task-specific-ai-agents-by-2026-up-from-less-than-5-percent-in-2025">Gartner Press Release</a></div>

---

## 4. AIツールのキャッチアップ戦略（2/2）

**生産性の「認知バイアス」に注意**

- METR調査の衝撃:
  - 実際には **19%遅く** なっていた
  - しかし本人は **20%速い** と認識
- 「使っている = 速い」とは限らない
- 効果測定には **客観的な指標** が必須
- ツール選定・運用も **エンジニアリングスキル** の一部

> 感覚ではなくデータで効果を検証せよ

<div class="source">出典: <a href="https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/">METR「AI Developer Productivity Study」</a> / <a href="https://www.technologyreview.jp/s/373980/ai-coding-is-now-everywhere-but-not-everyone-is-convinced/">MIT Technology Review</a></div>

---

## 5. キャリア差別化と掛け算（1/3）

**役割の重心シフト**

- エンジニアの価値の源泉が変化:
  - **How**（どう実装するか）→ AIが担当
  - **Why / What**（なぜ・何を作るか）→ 人間の領域
- 設計・判断・レビューが業務の **70%** を占める時代へ

> Kent Beck: **augmented coding** (AIと協働) vs **vibe coding** (AIに丸投げ)

<div class="source">出典: <a href="https://tidyfirst.substack.com/p/augmented-coding-beyond-the-vibes">Kent Beck「Augmented Coding」</a> / <a href="https://studioinstance.github.io/techpulse/articles/ai-future-and-engineers-2026.html">TechPulse「AI時代にITエンジニアはどう生き残るか」</a></div>

---

## 5. キャリア差別化と掛け算（2/3）

**ドメイン知識が最大の差別化要因**

- コーディング能力の均質化が進む中、**ドメイン知識** が最大の武器
- 掛け算の3方向:

| 方向 | 戦略 | 例 |
|------|------|-----|
| マルチ領域 | 複数技術の掛け合わせ | フロント × インフラ × AI |
| ドメイン専門 | 業界知識の深掘り | 金融 × エンジニアリング |
| インフラ | AI基盤の構築・運用 | MLOps × プラットフォーム |

<div class="source">出典: <a href="https://zenn.dev/ourly_tech_blog/articles/602c8f525ef8c1">Zenn/ourly「AI時代以降のエンジニアキャリア戦略」</a> / <a href="https://gaishishukatsu.com/archives/9b38deeec6e741a8897257deb8f84468">外資就活「サイバーエージェント技術トップが語る」</a></div>

---

## 5. キャリア差別化と掛け算（3/3）

**T字型人材が優位に立つ**

- 深い専門性（縦棒）＋ 幅広い知識（横棒）
- 最重要スキル調査: **コミュニケーション 48.3%** で1位
- AIが「実装力」を民主化した結果、**人間固有の能力** の価値が上昇
- 技術力だけでは差別化できない時代

> 技術力 × ドメイン知識 × コミュニケーション = 替えの利かない人材

<div class="source">出典: <a href="https://thinkit.co.jp/article/38668">Think IT「AI時代のエンジニアに求められるもの」</a> / <a href="https://addyosmani.com/blog/next-two-years/">Addy Osmani「The Next Two Years」</a></div>

---

## 「現時点」でベットすべき3つの能力

**What/Why の領域にフルベットする**

| # | 能力 | なぜ人間が必要か |
|---|------|-----------------|
| 1 | **ドメイン知識 × コンテキスト言語化力** | AIに「何をさせるか」を正確に伝える力。仕様・背景・制約を構造化する |
| 2 | **システムアーキテクチャ設計** | システム全体の分割、クラウド選定、スケーラビリティの大局的設計 |
| 3 | **テスト設計 × 自動検証（ハーネス構築力）** | AIを安全に走らせる「サーキット」。CI/CDに組み込む自動検証の仕組み |

> テスト設計と品質保証の自動化は、AIの自律生成を支える**最も確実な投資先**。

<div class="source">出典: <a href="https://developers.openai.com/codex/guides/build-ai-native-engineering-team">OpenAI「Building an AI-Native Engineering Team」</a> / <a href="https://addyosmani.com/blog/agentic-engineering/">Addy Osmani「Agentic Engineering」</a></div>

---

## 6. 幻想を捨てよ — Howで勝負するな

**「銀の弾丸」はもう存在しない**

- AIは人間よりも速く正確にコードを書く — **How（実装）で勝負は負け戦**
- 変数名の指摘、フォーマットの修正 → AIで完全に置換可能
- それに固執するのは **「仕事のふり」「レビューのふり」**
- エンジニアの勝負領域は **What（何を作るか）** と **Why（なぜ作るか）**

> 「今のAIはまだこの程度」と安心するのは**茹でガエルの第一歩**。
> AIは明日にはそのミスを克服している。

<div class="source">出典: <a href="https://blog.scottlogic.com/2025/12/15/the-specification-renaissance-skills-and-mindset-for-spec-driven-development.html">Scott Logic「The Specification Renaissance」</a> / <a href="https://newsletter.pragmaticengineer.com/p/when-ai-writes-almost-all-code-what">Pragmatic Engineer「When AI writes almost all code」</a></div>

---

## 開発フローを自ら再定義する

**個人のスキルを変えても、チームの仕組みが旧態依然なら意味がない**

- **上流工程へのリソース全振り**
  - 「仕様の論理的破綻がないか」の検証にこそ人間の時間を割く
  - 「ビジネス目的から逸脱していないか」の判断は人間にしかできない
- **システムの「防波堤」になる**
  - コードを量産するのではなく、**システム全体の健全性を守る**
  - 技術的負債・複雑性のコントロールが最大の価値
- **自ら環境を変える**
  - 旧態依然の開発フローに巻き込まれれば「作業のふり」に陥る
  - 生存確率を上げるには、周りの仕組みから変えていく

<div class="source">出典: <a href="https://blog.scottlogic.com/2025/12/15/the-specification-renaissance-skills-and-mindset-for-spec-driven-development.html">Scott Logic「The Specification Renaissance」</a> / <a href="https://addyo.substack.com/p/code-review-in-the-age-of-ai">Addy Osmani「Code Review in the Age of AI」</a></div>

---

## 6. マインドセットの転換（1/3）

**業界リーダーからの警告**

- **まつもとゆきひろ**: 技術の壁は消え、**心理の壁** が残る
- **Shopify CEO**: AIを使わないなら **リソース追加しない** と宣言
- **Gartner**: AI対応しない企業は **10年で消滅**
- 変化への対応は「選択」ではなく **生存条件**

> 技術的にできることと、心理的に受け入れられることの間にギャップがある

<div class="source">出典: <a href="https://type.jp/et/feature/30626/">エンジニアtype「まつもとゆきひろ」</a> / <a href="https://www.cnbc.com/2025/04/07/shopify-ceo-prove-ai-cant-do-jobs-before-asking-for-more-headcount.html">CNBC「Shopify CEO」</a> / <a href="https://www.gartner.co.jp/ja/newsroom/press-releases/pr-20251210-mindset">Gartner Japan</a></div>

---

## 6. マインドセットの転換（2/3）

**シニアエンジニアの課題と対策**

- **プロフェッショナル・アイデンティティ** の揺らぎ
  - 「コードを書ける自分」への誇りがAI活用を阻害
- Addy Osmani の提案:
  - **No-AI Day** — 定期的にAIなしで開発し基礎力を維持
  - **スキル萎縮対策** — 意図的にAIを外す練習
- DHH: **基礎の実践** が不可欠 — AIに頼りすぎない

<div class="source">出典: <a href="https://www.faros.ai/blog/ai-adoption-in-senior-software-engineers">Faros AI「Winning Over AI's Biggest Holdouts」</a> / <a href="https://addyo.substack.com/p/avoiding-skill-atrophy-in-the-age">Addy Osmani「Avoiding Skill Atrophy」</a> / <a href="https://dev.to/davidcassel/david-heinemeier-hansson-on-vibe-coding-ai-and-programmings-future-542l">DEV Community「DHH on Vibe Coding」</a></div>

---

## 6. マインドセットの転換（3/3）

**組織的な取り組み: freeeの事例**

- **「AI開発マニア」制度** を導入
  - AI活用を推進するアンバサダー的役割
  - 目標 **200名** → 実績 **400名** が参加（目標の **2倍**）
- 成功の要因:
  - トップダウンの号令 + ボトムアップの熱量
  - 「やらされ感」ではなく「面白さ」で駆動
- 組織文化の変革が **個人のマインドセット** を後押しする

<div class="source">出典: <a href="https://developers.freee.co.jp/entry/ai-driven-development-2025-report">freee Developers Hub「AI駆動開発」</a></div>

---

## 7. 身銭を切り、一次情報を取りに行く（1/2）

**AIの境界線は「肌感」でしか学べない**

- **57.8%** が月額課金、**78.1%** が毎日利用、**95%** が毎週使用
- 月 **$100** 投資 → 約 **3日** で回収（**24倍** リターン）
- Twitterのインフルエンサーやネット記事からは **AIの本当の限界は学べない**
- 自分で泥臭く使い倒し、ハルシネーションに直面して初めて分かる「境界線」

> 他人の成功体験を鵜呑みにするな。
> 自分の「肌感」だけがAIを正確にディレクションする武器になる。

<div class="source">出典: <a href="https://newsletter.pragmaticengineer.com/p/ai-tooling-2026">Pragmatic Engineer「AI Tooling 2026」</a> / <a href="https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/">METR「AI Developer Productivity」</a></div>

---

## 7. 身銭を切り、一次情報を取りに行く（2/2）

**「会社が導入してくれない」は言い訳**

- 求人の **48%** がAIツール経験を要求する時代
- 「使ったことがない」は議論に参加できないリスク
- 月 **$20〜$30** から始めるのが現実的なスタートライン
- 学習コストも試行錯誤の時間も **意図的な投資**

| 投資レベル | 月額 | 構成例 |
|---|---|---|
| 入門 | **$20〜$30** | Claude Pro + GitHub Copilot |
| 標準 | **$40〜$60** | Cursor Pro + Claude Pro |
| ヘビー | **$100〜$200** | Claude Max + 複数ツール |

<div class="source">出典: <a href="https://survey.stackoverflow.co/2025/">Stack Overflow Survey 2025</a> / <a href="https://prtimes.jp/main/html/rd/p/000000014.000129670.html">INSTANTROOM調査（2025年）</a></div>

---

## 8. 日々のキャッチアップ戦略（1/3）

**情報洪水をどうさばくか**

- 毎日 **30件以上** の新AIツールが登場
- すべてを追うのは不可能 — **フィルタリング** が鍵
- **5つの質問ゲート** で **95%** のノイズを排除:
  1. 自分の業務に関係するか？
  2. 既存ツールより明確に優れているか？
  3. 信頼できるソースからの情報か？
  4. 今すぐ試す必要があるか？
  5. 投資に見合うリターンがあるか？

---

## 8. 日々のキャッチアップ戦略（2/3）

**毎朝のルーティン化**

- **毎朝15〜30分** のインプット時間を確保
- 週あたり **6〜8時間** を学習に充当:

| 配分 | 時間 | 内容 |
|------|------|------|
| ハンズオン | **80%** (約5〜6h) | ツール操作・実験・実装 |
| インプット | **20%** (約1〜2h) | 記事・動画・ニュース |

- 「読む」より **「触る」** を圧倒的に優先する

---

## 8. 日々のキャッチアップ戦略（3/3）

**スカウトモデル — チームで効率化**

- チーム内で **役割分担** してキャッチアップ
- 各メンバーが担当領域の「スカウト」役を務める
- 週次で発見を共有 → チーム全体の知識が底上げ
- 個人の負荷を減らしつつ **網羅性を確保**

> 一人で全部追わない。チームで分担する。

---

## 生存戦略 — 3つの原則と8つのアクション

**原則: 銀の弾丸はない。泥臭い行動だけが生存確率を上げる。**

1. **Howで戦うな** — 実装はAIに任せ、What/Whyに集中する
2. **「捨てる」「防ぐ」に価値がある** — 作ることより、作らない判断を
3. **一次情報を取りに行け** — 他人の評価を鵜呑みにしない

---

## 8つの具体的アクション（1/2）

| # | アクション | ポイント |
|---|-----------|---------|
| 1 | **ハーネスエンジニアリング** を学ぶ | コンテキスト設計・仕様駆動 |
| 2 | **マルチエージェント** の設計パターンを習得 | 5+8+5パターンの理解 |
| 3 | **AI出力を検証する力** を磨く | 生成役と評価役の分離 |
| 4 | **ドメイン知識** を深掘りする | 掛け算で差別化 |

---

## 8つの具体的アクション（2/2）

| # | アクション | ポイント |
|---|-----------|---------|
| 5 | **学習速度そのもの** を競争力に | 5つの質問ゲート |
| 6 | **マインドセット** を転換する | Howのプライドを捨てる |
| 7 | **身銭を切って** 一次情報を取る | 月$20〜$30から |
| 8 | **日々のキャッチアップ** を習慣化する | 毎朝15〜30分 |

> 一度にすべてをやる必要はない。**今日から1つ** 始めることが重要。

---

<!-- _class: lead -->

# 最も重要な問い

<br>

## 生存確率を1%でも上げるために

**AIと「How」で張り合う無駄なプライドを捨て、**
**身銭を切って一次情報を取りに行き、**
**「What」と「Why」を追求する。**

この泥臭い行動とマインドの転換こそが、
エンジニアとしての生存確率を上げる唯一の現実的アプローチである。

> 最高のソフトウェアエンジニアは最速のコーダーではなく、
> **AIを信用しないタイミングを知っている人だ。**

<br>

この問いに答え続けることが、<br>AI時代のキャリア戦略の **核心** である。

---

## 出典・参考資料

各スライドに記載のリンクから原文にアクセスできます。
主要な出典一覧:

- [DORA Report 2025](https://dora.dev/research/2025/dora-report/) / [Martin Fowler](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) / [LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)
- [Anthropic](https://www.anthropic.com/research/building-effective-agents) / [Google ADK](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/) / [Microsoft](https://learn.microsoft.com/ja-jp/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Veracode](https://www.veracode.com/blog/genai-code-security-report/) / [Apiiro](https://apiiro.com/blog/4x-velocity-10x-vulnerabilities-ai-coding-assistants-are-shipping-more-risks/) / [METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- [Kent Beck](https://tidyfirst.substack.com/p/augmented-coding-beyond-the-vibes) / [Addy Osmani](https://addyo.substack.com/p/code-review-in-the-age-of-ai) / [Karpathy](https://www.glideapps.com/blog/what-is-agentic-engineering)

<p class="source">※ 各データは2024〜2026年時点の公開情報に基づく</p>

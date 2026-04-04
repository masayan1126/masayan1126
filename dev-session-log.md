# Chrome拡張機能「Rich Markdown Preview」機能改善 — 開発セッション全記録

> **対象Issue:** #10「同名ファイルを別タブで開けない」  
> **使用ツール:** Anthropic公式スキル・プラグイン・フックのみ  
> **ブランチ:** `fix/issue-10-same-name-file`

---

## 0. セッション開始

**ユーザーの指示:**
> `rich-markdown-preview` の開発をこれから実施する

**実施内容:**  
プロジェクトルート `/Users/masayan/git/dev/chrome-extentions` を認識し、`manifest.json`・`src/` 構成・既存テスト（Vitest 73件）を確認。

---

## 1. 開発ライフサイクルの方針決定

**ユーザーの指示:**
> Anthropic公式の開発ライフサイクル図（画像）を提示し、「この図に則ってChrome拡張機能開発を実施してほしい」  
> GitHub Issues URL: `masayan1126/chrome-extensions`

**実施内容:**
- GitHub CLI で未解決Issueを確認
- **Issue #10「同名のファイルをプレビューで開けない」** を今回の対象として選定
- Anthropic公式ライフサイクル 7フェーズ（①要件定義〜⑦ドキュメント）を確認

---

## 2. CLAUDE.md への方針の明記

**ユーザーの指示:**
> `/Users/masayan/git/dev/chrome-extentions/CLAUDE.md` に、フローと各フローで使うスキルやコマンドを明記するようにしてほしい

**実施内容:**
- `CLAUDE.md` を新規作成（以前は未存在）
- 7フェーズのライフサイクルテーブルを記載（各フェーズのスキル・コマンド・補足）
- ガードレール・ビルド手順・GitHub CLIコマンドを追記

---

## 3. フェーズ①：要件定義（`doc-coauthoring` スキル）

**ユーザーの指示:**
> 機能改善の要件を伝える：  
> 「同じファイル名でも配置ディレクトリが違えば複数タブで開けるようにしたい」「D&Dとディレクトリ両方の経路で対応したい」

**実施内容:**
- `/doc-coauthoring` スキルを起動し対話形式で仕様書を共同執筆
- ユーザーへの確認質問（読者・期待値・制約・フォーマット等）に対して回答を収集
- 5セクション構成の仕様書を作成：
  - 背景と問題
  - ユーザーストーリー
  - 受け入れ条件（AC-1〜AC-7）
  - 影響範囲（tabs feature・directoryReader・D&Dフック）
  - 制限事項（D&DはFile API制約上ディレクトリ名取得不可）
- 成果物を `docs/issue-10-same-name-file-spec.md` に保存

---

## 4. フェーズ①'：Issue更新

**ユーザーの指示:**
> 「doc-coauthoringで要件を確定した後、紐づいているIssueのタイトルと説明を確定した内容で更新するフローを追加したい」

**実施内容:**
- `CLAUDE.md` のライフサイクルテーブルに「①' Issue更新」行を追加
- コマンド: `gh issue edit <N> --repo masayan1126/chrome-extensions --title ... --body ...`
- Issue #10 のタイトル・本文を仕様書の内容で上書き

---

## 5. フェーズ②：設計（`feature-dev` スキル — Discovery・Architectureフェーズ）

**実施内容:**
- `/feature-dev` スキルを起動
- **code-explorer** サブエージェントがコードベースを調査し根本原因を特定：
  - `directoryReader.ts`: 再帰呼び出し時に `parentPath` を引き継いでいないため全ファイルのパスが `dirName/file.md` になり、異なるディレクトリでも同一パスと誤判定
  - `useTabOpen.ts:17`: `file.path` のみで重複チェック
  - `useTabOpen.ts:48`: `openDroppedFile` は `file.name` のみで重複チェック（ロジック不統一）
- **code-architect** が2つの設計案を提示：
  - **案A**: `FileInfo` 型にユニークIDフィールドを追加
  - **案B**: `FileSystemFileHandle.isSameEntry()` でファイルシステムレベルで判定

**ユーザーの指示:**
> 「Bで」

**実施内容:**
- 案B採用決定（型に余計なフィールドを持たせない設計）
- プランファイルを `plans/groovy-herding-key.md` に自動保存

---

## 6. フェーズ③：デザイン（`frontend-design` スキル）

**実施内容:**
- タブラベルの表示設計を `frontend-design` スキルで検討
- デザイン要件を確定：
  - 通常: `README.md`（従来通り）
  - 同名ファイルが複数タブにある場合のみ: `dir1/README.md` / `dir2/README.md`

---

## 7. フェーズ④：実装（`feature-dev` スキル — コーディングフェーズ）

**実施内容:**  
以下の5ファイルを修正：

### `src/shared/utils/directoryReader.ts`（根本修正）
```typescript
// parentPath パラメータを追加し、再帰呼び出し時にフルパスを引き継ぐ
export const readDirectory = async (
  handle: FileSystemDirectoryHandle,
  ...,
  parentPath: string = ''    // 追加
): Promise<DirectoryInfo> => {
  const currentPath = parentPath ? `${parentPath}/${handle.name}` : handle.name;
  // path: `${currentPath}/${entry.name}` でフルパスを保証
```

### `src/features/tabs/useTabOpen.ts`
```typescript
// isSameEntry() による正確な同一性判定を導入
if (await t.file.handle.isSameEntry(file.handle)) {
  existingTab = t; break;
}
// D&D フォールバック: name::size::lastModified 複合キー
const dropKey = `${file.name}::${file.size}::${file.lastModified}`;
```

### `src/features/tabs/TabBar.tsx`
```typescript
// duplicateNames の useMemo + getDisplayLabel で同名タブのみ dir/file 形式に
const duplicateNames = useMemo(() => { ... }, [tabs]);
const getDisplayLabel = (tab: OpenTab) => duplicateNames.has(tab.file.name)
  ? sanitizeFileName(`${getDirName(tab.file)}/${tab.file.name}`)
  : sanitizeFileName(tab.file.name);
```

### `src/features/tabs/useTabRestore.ts`
- `isCancelled` フラグを追加し、アンマウント時の競合状態を防止

### `src/shared/hooks/useDragDrop.ts`
- 空の catch ブロックを `console.warn` でエラー記録するよう修正

**ビルド・テスト実行:**
```bash
npm run build   # TypeScript コンパイル + Vite ビルド → 成功
npm run test    # Vitest 73テスト → 全パス
```

**バージョン更新・zip再作成:**
```bash
# public/manifest.json: "version": "1.2.1" → "1.2.2"
rm -f rich-markdown-preview.zip && zip -r rich-markdown-preview.zip dist/ public/
```

---

## 8. フェーズ⑤：コミット/PR（`commit-commands:commit-push-pr` スキル）

**実施内容:**
- `/commit-push-pr` でコミット・プッシュ・PR作成を一括実行
- 生成されたコミットメッセージ:
  ```
  fix: 同名ファイルを別タブで開けない問題を修正 (#10)
  
  - directoryReader でフルパスを正しく構築（parentPath 再帰引き継ぎ）
  - useTabOpen で FileSystemFileHandle.isSameEntry() による同一性判定を導入
  - D&D ファイルは name::size::lastModified 複合キーに統一
  - TabBar で同名タブが複数の場合のみ parentDir/filename 形式で表示
  - useTabRestore に isCancelled フラグを追加し競合状態を防止
  ```
- PR #13 を `masayan1126/chrome-extensions` にオープン

---

## 9. フェーズ⑥：レビュー（`pr-review-toolkit:review-pr` スキル）

**実施内容:**  
3つの専門エージェントが並列実行：

| エージェント | 指摘内容 |
|---|---|
| **type-design-analyzer** | `FileInfo` 型に `dirName` フィールドがあるが `path` から導出可能→冗長。`path` と `dirName` が不整合になりうる |
| **silent-failure-hunter** | `useDragDrop.ts` の catch ブロックがすべてのエラーを無音で飲み込んでいる |
| **code-reviewer** | `isSameEntry()` の catch ブロックが `DOMException` を区別していない |

**ユーザーの指示:**
> 「1」（全指摘を修正する）

**実施内容（追加修正）:**
- `FileInfo` 型から `dirName` フィールドを削除
- `StoredTab` 型からも `dirName` を削除
- `src/shared/utils/fileSystem.ts` に `getDirName(file: FileInfo)` ユーティリティを追加
- `directoryReader.ts`・`tabSave.ts`・`tabRestore.ts`・`tabDb.ts` の参照をすべて更新
- `isSameEntry()` の catch を `DOMException` タイプ別に分岐（`InvalidStateError`/`SecurityError` → `console.debug`、その他 → `console.warn`）

---

## 10. フェーズ⑦：ドキュメント

### CLAUDE.md 更新（`claude-md-management:revise-claude-md` スキル）

**ユーザーの指示（1回目）:**
> 「最初のdoc-coauthoringで要件を確定した後、紐づいているIssueを更新するフローを追加したい」

**ユーザーの指示（2回目）:**
> 「リリースノート作成用のinternal-commsもほしい」

**ユーザーの指示（3回目）:**
> 「この先頭の箇条書き2行も、開発ライフサイクルに違和感なく溶け込めるように書き直してほしい」（「実装変更後は必ずzipを作り直すこと」「manifest.jsonのversionも更新すること」という2行）

**実施内容（累積）:**
- ライフサイクルテーブルに「①' Issue更新」行を追加
- ガードレールセクションに `security-guidance@claude-plugins-official` を記載
- 「ビルド・テスト・リリース準備」セクションを4ステップで整備
- 「リリースノート」セクションを追加（`internal-comms` スキルで2種類生成）
- 先頭の独立した2行をライフサイクルの文脈に統合

### リリースノート作成（`internal-comms` スキル）

**ユーザーの指示:**
> 「GitHub ReleasesとChrome拡張のストアユーザー向け」  
> 「それでok」

**実施内容:**
- `/internal-comms` スキルを起動し2種類のリリースノートを生成
- **GitHub Releases向け（技術者向け）**: 変更ファイル・API・影響範囲・既知の制限を詳細に記載
- **Chromeストア向け（一般ユーザー向け）**: 平易な日本語で「こう便利になりました」の伝え方
- 保存先: `docs/release-notes-v1.2.2.md`

---

## 11. security-guidance プラグインの導入

**ユーザーの指示（新セッション開始後）:**
> 「security-guidance@claude-plugins-official — これを使用してほしい認識なのですが合ってる？」

**実施内容:**
- `claude-plugins-official` マーケットプレイスに `security-guidance` プラグインが存在することを確認
- 現在の `settings.json` には `security-guidance@claude-code-plugins`（別マーケットプレイス版）が有効化されていることを発見
- 両者の違いを説明：フック型（自動実行）vs. スキル型（手動実行）

**ユーザーの指示:**
> 「git:security-checkではなくsecurity-guidanceを使いたい」

**実施内容:**
- `settings.json` の `enabledPlugins` を変更:
  ```json
  // 変更前
  "security-guidance@claude-code-plugins": true
  // 変更後
  "security-guidance@claude-plugins-official": true
  ```
- `CLAUDE.md` のガードレール記載を `git:security-check` → `security-guidance@claude-plugins-official` に更新

---

## 12. security-guidance の動作確認

**ユーザーの指示:**
> 「security-guidanceが実行されていることをデバッグというか確認したいのですが方法ある？」

**実施内容:**
- デバッグ方法を2つ説明：
  1. `tail -f /tmp/security-warnings-log.txt` でリアルタイム監視
  2. 危険なパターンを意図的に書いてブロックされるか確認

**ユーザーの指示:**
> 「方法2」

**実施内容:**
- `/tmp/security-hook-test.ts` に危険なコードを書こうとしたところ即座にブロック：
  ```
  Error: PreToolUse:Write hook error: ⚠️ Security Warning: ...is a major security risk...
  ```
- フックが正常動作していることを確認

**ユーザーの指示:**
> 「このディレクトリ内のどこかのファイルに書いて試してみて」

**実施内容:**
- `src/test-security.ts` を空ファイルとして作成（セキュリティパターンを含まないため通過）
- Edit ツールで危険なコードを追記しようとしたが、今回はブロックされなかった
- 理由を説明：同一セッション内では同一ファイル×同一ルールの警告は1回のみ（事前の Write 試行時にすでに記録済みだったため）

---

## 13. 解説コンテンツの作成

**ユーザーの指示:**
> 「Anthropic公式ツールのみを使った開発ワークフローの解説コンテンツを作りたい。ブログ記事とYouTubeの台本を作成してほしい」

**実施内容:**
- `docs/content/blog-anthropic-workflow.md` を作成（約4,800字）
  - 7フェーズすべてをカバー
  - 実際のコードスニペット3箇所（`directoryReader.ts`・`useTabOpen.ts`・`TabBar.tsx`）
  - `type-design-analyzer`・`silent-failure-hunter` の実際の指摘内容を掲載
  - ※ブログ執筆中に security-guidance フックが **2回発火**（セキュリティパターンの文字列を含んでいたため）
- `docs/content/youtube-script-anthropic-workflow.md` を作成（約18〜20分想定）
  - タイムスタンプと `[画面: ...]` 指示コメント付き
  - 各フェーズにコードと出力の読み上げを含む

---

## 14. YouTube台本の改善

**ユーザーの指示:**
> 「既存の台本（`anthropic-workflow-script.md`）を確認して、Claudeとユーザーのやり取りをもっと具体的に盛り込めるか改善点を教えてほしい」

**実施内容（分析）:**  
台本の課題を3分類：
1. **入力が見えない**（ユーザーが何をタイプしたか不明）
2. **選択が見えない**（複数候補からどれを選んだか不明）
3. **出力が抽象的**（「生成された」とだけ書いてある）

**改善内容（5箇所を実際に修正）:**

| 箇所 | 改善内容 |
|---|---|
| ガードレール（3:30頃） | ブログ記事執筆中に security-guidance が2回発火した実体験エピソードを追加 |
| フェーズ① doc-coauthoring | Claude からの質問例と回答例を対話形式で再現 |
| フェーズ② feature-dev | A/B選択肢の提示と「Bを選んだ」という能動的な判断シーンを追加 |
| フェーズ⑥ pr-review-toolkit | 並列エージェントが走り出す瞬間の出力を読み上げ形式で追加 |
| フェーズ⑦ internal-comms | 技術者向けとユーザー向けリリースノートを実際に読み上げて文体差を対比 |

---

## 最終的な成果物一覧

| ファイル | 内容 |
|---|---|
| `public/manifest.json` | バージョン `1.2.2` に更新 |
| `src/shared/utils/directoryReader.ts` | `parentPath` 引き継ぎによるフルパス生成修正 |
| `src/features/tabs/useTabOpen.ts` | `isSameEntry()` 導入・D&D複合キー統一 |
| `src/features/tabs/TabBar.tsx` | 同名タブの `dir/file` 形式ラベル表示 |
| `src/features/tabs/TabItem.tsx` | `displayLabel` prop 対応 |
| `src/features/tabs/useTabRestore.ts` | `isCancelled` フラグによる競合状態対策 |
| `src/shared/utils/fileSystem.ts` | `getDirName()` ユーティリティ追加 |
| `src/shared/hooks/useDragDrop.ts` | catch ブロックのエラーログ追加 |
| `CLAUDE.md` | 7フェーズライフサイクル・ガードレール・ビルド手順を一元化 |
| `docs/issue-10-same-name-file-spec.md` | Issue #10 要件定義書 |
| `docs/release-notes-v1.2.2.md` | GitHub Releases向け + Chromeストア向けリリースノート |
| `docs/content/blog-anthropic-workflow.md` | 開発ワークフロー解説ブログ記事 |
| `docs/content/youtube-script-anthropic-workflow.md` | YouTube 解説動画台本 |
| `~/.claude/settings.json` | `security-guidance@claude-plugins-official` を有効化 |

**PR:** `masayan1126/chrome-extensions#13`（マージ済み）

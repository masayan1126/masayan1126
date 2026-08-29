# デザインシステムグリーン

確定したスライド作成規則を、グリーン一色と無彩色で実装するデザインシステムです。

## 継承したテーマカラー

既存のデザインシステムから継承したのは、次の5色だけです。

| トークン | 色 |
| --- | --- |
| Green 900 | `#1D3A32` |
| Green 800 | `#264C41` |
| Green 700 | `#2F5D50` |
| Green 500 | `#54786C` |
| Green 100 | `#E6EDE9` |

既存の書体、余白、レイアウト、コンポーネント、猫素材、RPG表現は利用しません。白、黒、グレーは新しく定義した無彩色です。

## 基本仕様

- 画面: 1920×1080、16:9
- 外側余白: 左右120px、上下88px
- 表紙タイトル: 96px
- スライドタイトル: 58px
- 本文: 28px
- 情報階層: 三段階以内
- 配色: グリーン一色と無彩色
- アイコン: 説明に必要な場合だけ、2px線の線画を使う
- 図表: 重要系列だけをグリーンで強調し、値を直接表示する

## レイアウト

| レイアウト | 用途 |
| --- | --- |
| cover | 題名と資料の構成を最小限で示す |
| section | 現在地と章の結論を示す |
| claim-visual | 主張と、それを説明する図を並べる |
| comparison | 同じ観点で二つを比較する |
| process | 番号と接続線で説明順を示す |
| data | グラフ、直接ラベル、読み取りを近くに置く |
| visual | 関係図と短い説明を組み合わせる |
| closing | 結論と次の行動を示す |

## 作成手順

1. practices.md を読み、資料の目的、聞き手、利用環境を決めます。
2. design-system-green/deck-template.html を複製します。
3. 内容に合うレイアウトを選びます。
4. 文章、図、出典、発表者ノートを置き換えます。
5. design-system-green/validate.mjs を実行します。
6. 全スライドを実際に表示し、文字切れ、重なり、コントラストを確認します。

## 参照ファイル

- [見本帳](./design-system-green-review.html)
- [デッキ雛形](./design-system-green/deck-template.html)
- [スライドCSS](./design-system-green/slides.css)
- [色トークン](./design-system-green/tokens/colors.css)
- [書体トークン](./design-system-green/tokens/typography.css)
- [余白トークン](./design-system-green/tokens/layout.css)
- [機械可読情報](./design-system-green/manifest.json)


## プロジェクトについて

「ベクターデータベースなしのポータブルなセマンティック検索。ファイルとfindとsortだけ」を実現するファイルフォーマット定義と、CLIツール群を開発するプロジェクトです。

## ディレクトリ構成

concept-file/
├── SPEC.md
├── README.md
├── python/
│   └── concept_file/
│       ├── __init__.py
│       ├── reader.py      ← .conceptの読み書き
│       └── search.py      ← コサイン類似度検索
└── cli/
    ├── concept-embed      ← テキスト → .concept生成
    ├── concept-search     ← 自然言語でセマンティック検索
    ├── concept-dist       ← 距離計算
    ├── concept-show       ← 中身を人間が読める形で表示
    └── concept-plot       ← UMAPで可視化



# concept-file

## プロジェクト概要
.conceptファイルフォーマットの仕様定義と参照実装。
「概念を1ファイルで保存する」をゴールとする。

## 設計思想
- テキスト・埋め込み・provenanceを1ファイルに統合
- ファイルシステムがそのままKnowledge Baseになる
- パイプライン言語（各ステージがLLM呼び出し）のネイティブデータ型

## フォーマット
- Magic Bytes: "CNCP"
- ヘッダ: JSON (UTF-8)
- バイナリセクション: float32[] (埋め込みベクトル)

## 成果物
1. SPEC.md（フォーマット仕様）
2. Python参照実装（read/write/search）
3. concept CLI
```

3dのConcept Embedding Mapに検索機能をつけることはできますか？

そのテキストは、データのタイトルだけでなく本文にもマッチさせているのでしょうか？

ブラウザで開くと以下のような文字列が出ています。エラーではないですか？
` in script block breaks SFC parsing", "vuejs/core#7414: Export buffer related methods in server-renderer", "vuejs/core#7433: Allow generics for Data, Methods, Computed and Props in defineComponent to ease migration from Vue2", "vuejs/core#7473: Allow mergeProps to merge `ref` property", "vuejs/core#7478: `toRaw` has wrong typing for `DeepReadonly` array", "vuejs/core#7506: suspense.resolve() is called without a pending branch.", "vuejs/core#7528: Create multiple instance of the teleport when destination has multiple results", "vuejs/core#7529: TemplateRef overwrites reactive data", "vuejs/core#7532: `:slotted` styles not being applied if slot is wrapped in `TransitionGroup`", "vuejs/core#7542: inconsistent behaviour of `whitespace: 'condense'` handling if second element text is an interpolated var", "vuejs/core#7544: Vue2 with typescript to Vue3 with typescript application upgrade", "vuejs/core#7578: Passing boolean value to render function children renders empty node instead", "vuejs/core#7595: Teleport should provide the option to prepend when there are multiple teleports on the same target", "vuejs/core#7601: `v-model` on checkbox producing typing error when used with `true-value` and `false-value`", "vuejs/core#7602: Property added with Object.defineProperty() is not reactive", "vuejs/core#7642: SFC Playground isn't compatible with SubtleCrypto: it needs https access internally", "vuejs/core#7661: defineAsyncComponent onError ", "vuejs/core#7699: Use useSlots().default method to determine whether the slot is in doubt after the contents of the slot have been commented out", "vuejs/core#7710: Allow exposing variables with a private prefix (_)", "vuejs/core#7713: v-bind with null on slot will crash the app", "vuejs/core#7725: Template compilation fails when using v-once inside template with v-if", "vuejs/core#7738: Support input type date in v-model with number modifier and date modifier", "vuejs/core#7751: The `inject` option in Mixins cant be inferred", "vuejs/core#7754: Binding the 'v-for' element with 'ref' causes the movement animation to disappear when the list element is removed.", "vuejs/core#7775: SSR: CSS variable with quotes causes [Vue warn]: Hydration text mismatch", "vuejs/core#7789: Whitespace preserve does not work", "vuejs/core#7840: Using the comment node in the slot, no mounts occur on the dom", "vuejs/core#7871: Boolean props without a value are not defaulted to true when there is a v-bind applied if they begin with `on`", "vuejs/core#7873: Warn when calling computed/ref inside a computed callback", "vuejs/core#7890: Improve defineExpose()", "vuejs/core#7910: Warning using compile() in render() on method calls", "vuejs/core#7915: $el is typed as any", "vuejs/core#7919: Nested TransitionGroup Bug - .move class not applied anymore", "vuejs/core#7920: v-if bugs when used inside of label+button

検索もうまく動きました。

データが多すぎるので、2023年以降のissueだけに絞ってください。

まだ多いです。2023年以降のissueだけに絞ってください。

gitからrevertすることができます。

はい、続けてください。

まだ多いです。2024年以降のissueだけに絞ってください。

実行時間が長すぎるので調べてください。

  1. n_epochs を明示的に下げる（200→50程度でも十分な品質）

データ数を減らしたので、concept-searchの結果についても再度取得してREADME.mdに反映してください。

wikipediaとjavaのサンプルも2d/3dのグラフを再描画してください。

処理はフォアグラウンドでやってください。

全htmlを開いてください。

うまく動いています。コミットしてください。

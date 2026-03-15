
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

並列で3dプロットなどをしたとき、時間がかかりすぎるのは、キャッシュの保存場所が衝突するなどの不具合があるのでは？

2.の対策を入れてください。

はい

コミットしてください。


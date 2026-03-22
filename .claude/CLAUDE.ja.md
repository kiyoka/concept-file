
## プロジェクトについて

「ベクターデータベースなしのポータブルなセマンティック検索。ファイルとfindとsortだけ」を実現するファイルフォーマット定義と、CLIツール群を開発するプロジェクトです。

## ディレクトリ構成

```
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
    ├── concept-sim        ← 類似度計算
    ├── concept-grep       ← ソースファイルのセマンティック grep
    ├── concept-show       ← 中身を人間が読める形で表示
    └── concept-plot       ← UMAPで可視化
```



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

local-llmを使えるようにします.LM studioが起動しています。

gemma-3n-e4b-it-mlxですが、embeddingモデルとして使えますか?

もう少し大きいモデルはありますか?

https://huggingface.co/mlx-community/Qwen3-Embedding-8B-4bit-DWQ をダウンロード中です。

了解です。今のうちに、localLLMにアクセスするURLを環境変数で指定できるようにしてください。

環境変数を指定して、Claude Codeを再起動しました。

はい

urlがこうなっています。 http://192.168.0.211:1234

URLは環境変数の方でOKです。ロードしました。

環境変数を直して、再度、Claude Codeを再起動しました。

これでどうでしょうか?

ロードしています。embeddingがONになっていないのでしょうか?

再読み込みしました。他に設定がいるのでしょうか?

はい、developerタブで,runningになっています。

チャットモデルはロードしていません.Developerタブで、qwen3-embedding-8b-dwqが選択されています。READYとなっています.

embeddingのタブに、このように実装せよと書いてあります。

from openai import OpenAI
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def get_embedding(text, model="model-identifier"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input=[text], model=model).data[0].embedding

print(get_embedding("Once upon a time, there was a cat."))

LM Studioを再移動して、モデルを再ロードしました。READYになりました。

wikipediaのサンプルがどれくらい性能が落ちるか試したいです。

text-embedding-3-smallとまではいかなくても、ある程度実用的なローカルLLMを見つけたいです。

はい、それを試します。

ドメインタイプがLLMから変更できません.

ダウンロード開始しました。

ロード完了

それでは,Javaのサンプルも作り直してください。

2d/3dプロットのファイルも再生成してください。

UMAPの計算に時間がかかるのは、CPU蛇な計算だからでしょうか？

UMAPの計算部分(NumPy)をGPUを使うようにはできますか？macbook air M4です。

綺麗にクラスタリングできていることが確認できました。

コミットしてください。

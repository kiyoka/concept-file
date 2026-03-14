# concept-file

ベクターデータベースなしのポータブルなセマンティック検索。ファイルと `find` と `sort` だけ。

## これは何？

`.concept` はテキスト、埋め込みベクトル、来歴情報を1つのファイルにまとめるプレーンテキスト形式のファイルフォーマットです。各 `.concept` ファイルは1つの「概念」を表し、標準的なファイルシステムツールで比較・検索・整理できます。

**ベクターデータベースは不要です。** ファイルをコピーすれば知識が移動します。`find` で発見し、`sort` で順位付けし、`diff` で変更を追跡できます。

## なぜ？

| アプローチ | セットアップ | ポータビリティ | 中身の確認 |
|-----------|------------|--------------|-----------|
| Vector DB (Pinecone, Chroma 等) | サーバー/プロセスが必要 | エクスポート/インポートが必要 | バイナリで不透明 |
| `.concept` ファイル | セットアップ不要 | `cp` / `rsync` | `cat` / 任意のテキストエディタ |

`.concept` ファイルのディレクトリが、そのままナレッジベースです。マイグレーションもサーバーもロックインもありません。

## ファイルフォーマット

`.concept` ファイルは全体がプレーンテキストです:

```
CNCP v1 1432
{
  "concept": "Japanese AI Startup Trends",
  "version": "1.0",
  "created_at": "2026-03-14T10:00:00Z",
  "text": "Japanese AI startups have surged since 2024...",
  "embedding": {
    "model": "text-embedding-3-small",
    "dim": 1536,
    "vector": [0.0234, -0.1823, 0.0091, ...]
  },
  "provenance": {
    "source_url": "https://example.com/article",
    "pipeline": "fetch | extract_text | summarize | embed"
  }
}
```

詳細な仕様は [SPEC.md](SPEC.md) を参照してください。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install openai
export OPENAI_API_KEY="sk-..."
```

## CLI ツール

### concept-embed

テキストから埋め込みベクトル付きの `.concept` ファイルを生成します。

```bash
# コマンドライン引数から
cli/concept-embed --name "My Concept" --text "埋め込みたいテキスト" -o output.concept

# 標準入力から
echo "埋め込みたいテキスト" | cli/concept-embed --name "My Concept" -o output.concept

# ソースファイルから
cat src/User.java | cli/concept-embed --name "User" -o concepts/User.concept
```

オプション:
- `--name` — コンセプト名（必須）
- `--text` — テキスト内容（省略時は標準入力から読み取り）
- `-o, --output` — 出力ファイルパス（必須）
- `--model` — 埋め込みモデル（デフォルト: `text-embedding-3-small`）
- `--language` — BCP 47 言語タグ（例: `en`, `ja`）
- `--keywords` — キーワード / タグ
- `--source-url` — 来歴用のソースURL
- `--no-embed` — 埋め込み生成をスキップ

### concept-show

`.concept` ファイルの内容を人間が読める形式で表示します。

```bash
cli/concept-show output.concept
```

```
Concept:  User
Version:  1.0
Created:  2026-03-14T13:46:11.223280+00:00
Language: en
Embedding: 1536-dim (text-embedding-3-small)
Pipeline: embed

--- Text ---
package com.example.shop.model;
...
```

`--json` で生のJSONボディを出力できます。

### concept-dist

クエリの `.concept` ファイルから1つ以上のターゲットへのコサイン距離を計算します。結果は距離の近い順にソートされます。

```bash
cli/concept-dist query.concept targets/*.concept
```

```
0.0000  User                 concepts/User.concept
0.2463  Order                concepts/Order.concept
0.3400  AuthService          concepts/AuthService.concept
0.3955  Product              concepts/Product.concept
0.4739  PaymentService       concepts/PaymentService.concept
0.5815  ProductSearchService concepts/ProductSearchService.concept
```

距離 0 = 同一、1 = 完全に無関係。

## 実行例: Javaプロジェクトの類似度分析

`examples/java-project/` ディレクトリは実用的なユースケースを示しています — Javaコードベースで類似するクラスを見つけます。

### ソースファイル

架空のECサイトアプリケーション（6クラス）:

| ファイル | 役割 |
|---------|------|
| `User.java` | ユーザーアカウントエンティティ |
| `AuthService.java` | 認証サービス |
| `Product.java` | 商品エンティティ |
| `Order.java` | 注文エンティティ |
| `PaymentService.java` | 決済処理サービス |
| `ProductSearchService.java` | 商品検索サービス |

### .concept ファイルの生成

```bash
for f in examples/java-project/src/*.java; do
  name=$(basename "$f" .java)
  cat "$f" | cli/concept-embed --name "$name" --language en -o "examples/java-project/concepts/${name}.concept"
done
```

### 類似クラスの検索

「`User` に最も似ているクラスはどれ？」

```bash
cli/concept-dist examples/java-project/concepts/User.concept examples/java-project/concepts/*.concept
```

結果は `Order`（購入関係）と `AuthService`（認証関係）が `User` に最も近いことを示しており、コード上の実際のドメイン関係と一致しています。

### ユースケース

- **リファクタリング** — 責務が重複しているクラスの発見
- **影響分析** — 変更の影響を受けそうなファイルの特定
- **オンボーディング** — プロジェクト構造の俯瞰的な理解
- **重複検出** — 冗長または類似したコードの検出

## プロジェクト構成

```
concept-file/
├── SPEC.md                  — フォーマット仕様 (v0.1.0)
├── README.md                — 英語版 README
├── README.ja.md             — 日本語版 README（このファイル）
├── python/
│   └── concept_file/
│       ├── __init__.py
│       ├── reader.py        — .concept ファイルの読み書き
│       └── search.py        — コサイン類似度/距離
├── cli/
│   ├── concept-embed        — テキスト → .concept 生成
│   ├── concept-show         — 人間が読める形式で表示
│   └── concept-dist         — 距離計算
└── examples/
    └── java-project/
        ├── src/             — サンプル Java ソースファイル
        └── concepts/        — 生成された .concept ファイル
```

## ライセンス

MIT

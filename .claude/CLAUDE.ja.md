
## プロジェクトについて

「ベクターデータベースなしのポータブルなセマンティック検索。ファイルとfindとsortだけ」を実現するファイルフォーマット定義と、CLIツール群を開発するプロジェクトです。


以下に、postgresqlのソースコードがあります。
~/GitHub/postgresql-18.3/
このような大規模なソースコードの解析を行うに当たって、concept-grepを使った場合と、使わなかった場合で、強み、弱みを教えてください。

### concept-grepを使った場合 vs 使わなかった場合（PostgreSQL 18.3, 2271ファイル）

#### grep / find / Agent Explore のみ

**強み:**
- 即座に使える — インデックス不要、セットアップゼロ
- 正確なキーワード検索 — `grep -r "BackendStartup" src/` は確実にヒット
- コンテキスト表示 — `grep -C5` で周辺行もすぐ見える
- 定義ジャンプ — `grep -rn "void BackendStartup"` で関数定義に直行

**弱み:**
- ファイル名・関数名を事前に知っている必要がある — PostgreSQLは略語が多い（`xlog`, `nbt`, `lmgr`）ので初見では何を検索すべきか分からない
- 探索にトークンを大量消費 — エージェントが「正しいファイルを見つける」ために多数のファイルを読む必要がある
- 意味的な関連は見つけられない — 「コスト推定」で `costsize.c` を見つけるのはgrepでは不可能

#### concept-grepを使った場合

**強み:**
- 自然言語で探索できる — 「query optimizer cost estimation」→ `costsize.c` (0.79) に直行
- トークン節約 — 1回のAPI呼び出しで関連ファイル上位N件が得られる
- ヘッダと実装を横断的にランキング — `.h`でAPI概要→`.c`で実装を読む流れが自然にできる
- ハイブリッド検索 — セマンティック+キーワードで精度向上
- `--include`/`--exclude` — テストファイルを除外し実装に集中
- `--summary` — ファイルを開かずに構造を概観

**弱み:**
- 初回インデックスにコストがかかる — 2271ファイル × 2回のembedding API呼び出し
- 巨大ファイルの精度が低い — `postmaster.c`（数千行・多責務）はベクトルが薄まる
- 行単位・関数単位の検索はできない — 「この関数の定義はどこ？」にはgrepが速い
- インデックスの鮮度 — 編集後は `--index` の再実行が必要
- ローカルLLMが必要 — embedding計算にLM Studio等の環境が必要

#### 使い分け

| タスク | concept-grep | grep/find |
|--------|:-----------:|:---------:|
| 「この機能はどのファイルにある？」（初見の探索） | ◎ | △ |
| 「この関数の定義はどこ？」（ピンポイント検索） | △ | ◎ |
| 大規模コードベースの全体像把握 | ◎ | △ |
| 特定キーワードの完全一致検索 | △ | ◎ |
| エージェントのトークン節約 | ◎ | × |
| セットアップ不要で即使いたい | × | ◎ |

**最も効果的な使い方**: concept-grepで関連ファイルを絞り込み → grepやReadで詳細を確認する2段階アプローチ

## PyPI公開手順

### 1. PyPIアカウント作成

1. https://pypi.org/account/register/ でアカウントを作成
2. メールアドレスの確認を完了する
3. **2要素認証（2FA）を有効化する**（PyPIは2FA必須）
   - https://pypi.org/manage/account/#two-factor にアクセス
   - TOTPアプリ（Google Authenticator等）またはセキュリティキーを登録

### 2. APIトークンの発行

1. https://pypi.org/manage/account/token/ にアクセス
2. トークン名: 例 `concept-file`
3. スコープ: 初回は「Entire account」、パッケージ登録後は「Project: concept-file」に限定推奨
4. 発行されたトークンを安全に保存する（`pypi-` で始まる文字列）

### 3. TestPyPIでの事前テスト（推奨）

TestPyPIはPyPIと同じ仕組みのテスト環境で、本番公開前の動作確認に使う。

1. https://test.pypi.org/account/register/ で別途アカウントを作成
2. APIトークンを発行する

```bash
# ビルド
python -m build

# TestPyPIにアップロード
python -m twine upload --repository testpypi dist/*
# ユーザー名: __token__
# パスワード: pypi-で始まるAPIトークン

# TestPyPIからインストールして動作確認
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ concept-file
```

### 4. 本番PyPIへの公開

```bash
# ビルド（dist/ をクリーンしてから）
rm -rf dist/
python -m build

# アップロード
python -m twine upload dist/*
# ユーザー名: __token__
# パスワード: pypi-で始まるAPIトークン
```

### 5. 公開後の確認

```bash
# PyPIからインストール
pip install concept-file

# 動作確認
concept-grep --help
concept-embed --help
concept-show --help
```

### 6. バージョン更新時の公開手順

1. `pyproject.toml` の `version` を更新する
2. `rm -rf dist/ && python -m build`
3. `python -m twine upload dist/*`

### 現在の状態

- **PyPI公開済み** — `pip install concept-file` でインストール可能
- エントリーポイント: `concept-grep`, `concept-embed`, `concept-show`, `concept-sim`, `concept-plot`
- ビルドに必要なパッケージ: `pip install build twine`



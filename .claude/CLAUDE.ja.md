
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

はい、結構大きめのissueがあります。

まだissueは作っていませんこれから作ります。

issueの文章はここで考えます。

やりたいことは、concept-grepの改善です。
現在、.concept/ ディレクトリに入っている.conceptファイルしか使いませんが、
そこに対応する.conceptファイルがない場合は、検索対象となっているファイルと同階層にある.concept拡張子のファイルを使うようにしたいです。フォールバックです。

例えば、以下のような場合は、.concept/src/a.java.conceptがインデックスとして使われます。
.concept/src/a.java.concept
src/a.java
ただし、以下のような場合は、src/a.java.conceptが使われます。
.concept/
src/a.java.concept
src/a.java

はい、合っています。


文章問題ありません。github issueとして投稿してください。

忘れないうちに、別のissueも作りたいです。


concept-embedやconcept-grep --indexで.conceptファイルを作成する際、
元になったテキストファイルがjavaやpyなどのプログラミング言語ファイルの場合、
tree-sitterを使って、要約した結果を使って、embedデータを作りたいです。
その際、ファイル名の情報も重要なので、embedの元データに追加したいです。
また、.conceptファイルには,embedの元になったデータもJSONキーとして残したいです。
うまくまとめて、issueにしてください。


Title: プログラミング言語ファイルの埋め込みソースとしてtree-sitter要約を使用

Body:

機能要望

プログラミング言語のソースファイル（例: .java, .py）から.conceptファイルを生成する際は、生のファイル内容を埋め込む代わりに、tree-sitterを使ってコードの構造化要約を抽出してください。ファイル名も埋め込みソースに含めるべきです。埋め込みに使用した要約テキストは、専用のJSONキーとして.conceptファイルに保存されるべきです。

動機

生のソースコードを埋め込むとノイズの多いベクトルが生成されます。tree-sitterベースの要約（例: クラス名、メソッドシグネチャ、docstring）は、意味構造をより簡潔に捉え、より良い類似結果につながります。

提案される変更

1. tree-sitter解析: サポートされている言語（例: Java, Python）については、完全なファイルテキストを埋め込みソースとして使う代わりに、tree-sitterを用いて構造化要約を抽出します。
2. ファイル名の追加: ファイル名自体が意味情報を持つため、要約にソースファイル名を追加します。
3. 埋め込みソースの保存: 実際に埋め込みに使用したテキストを、新しいJSONキー（例: embed_source）の下に.conceptファイルへ保存し、プロセスを監査可能かつ再現可能にします。

Example .concept structure

{
"concept": "UserService.java",
"embed_source": "UserService.javanclass UserServicen method getUser(id: Long): Usern method createUser(name: String): Usern ...",
"embedding": { ... }
}

Affected Commands

ー concept-embed
ー concept-grep --index


追加してほしいことは、"text"というキーは元通り残し、オリジナルのソースコードファイルを維持したままにしてほしいということです。

issue 15日着手してください。


以下のサンプルフォルダの構成を変えて、各javaソースコードの隣に、.conceptファイルを配置するようにしてください。
examples/java-project

エラーです.
concept-grep -s Product *
Error: .concept/ directory not found.
Run 'concept-grep --index -r *' to generate the index first.

examples/java-project配下のディレクトリ構成でもconcept-plotが可能ですか?

それでは、ドキュメント類も更新してください。

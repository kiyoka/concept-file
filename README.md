# concept-file

[日本語版](README.ja.md)

Portable semantic search without a vector database. Just files, `find`, and `sort`.

## What is this?

`.concept` is a plain-text file format that bundles text, embedding vectors, and provenance into a single self-contained file. Each `.concept` file represents one "concept" — a piece of knowledge that can be compared, searched, and organized using standard filesystem tools.

**No vector database required.** Copy a file to move knowledge. Use `find` to discover, `sort` to rank, and `diff` to track changes.

## Why?

| Approach | Setup | Portability | Inspectability |
|----------|-------|-------------|----------------|
| Vector DB (Pinecone, Chroma, etc.) | Server/process needed | Export/import required | Opaque binary |
| `.concept` files | Zero setup | `cp` / `rsync` | `cat` / any text editor |

A directory of `.concept` files **is** the knowledge base. No migrations, no servers, no lock-in.

## File Format

A `.concept` file is entirely plain text:

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

See [SPEC.md](SPEC.md) for the full specification.

## Setup

### Installation

```bash
git clone https://github.com/kiyoka/concept-file.git
cd concept-file
python -m venv .venv
source .venv/bin/activate
pip install openai
```

Add the `cli/` directory to your PATH:

```bash
export PATH="$PWD/cli:$PATH"
```

You can add this to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) to make it permanent.

### Using a Local LLM (LM Studio) — Recommended

You can use a local embedding model via [LM Studio](https://lmstudio.ai/). No API key required, and embedding is free — ideal for indexing large codebases.

1. Install and launch LM Studio
2. Download an embedding model (see table below)
3. Go to the **Developer** tab and load the model
4. The local API server runs at `http://localhost:1234/v1`

#### Recommended Embedding Models

| Model | Parameters | Dimensions | MTEB Multilingual | Characteristics |
|-------|-----------|------------|-------------------|-----------------|
| `granite-embedding-278m-multilingual` | 278M | 768 | 58.3 | Lightweight, fast. Good for quick experimentation |
| `Qwen3-Embedding-0.6B` | 0.6B | 1024 | 64.33 | Good balance of quality and speed |
| `Qwen3-Embedding-8B` | 8B | 4096 | 70.58 | Highest quality (#1 on MTEB multilingual). Requires more VRAM |

All models support multilingual input (including Japanese). MTEB Multilingual scores are from the [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard).

Set the environment variables:

```bash
export CONCEPT_API_BASE="http://localhost:1234/v1"
export CONCEPT_EMBED_MODEL="granite-embedding-278m-multilingual"  # or Qwen3-Embedding-0.6B, Qwen3-Embedding-8B
```

Then use the CLI tools as usual — they will automatically use the local model:

```bash
# Index source files
concept-grep --index -r src/

# Search by meaning
concept-grep -r "user authentication" src/
```

## CLI Tools

### concept-grep

Semantic grep — find source files by meaning. Uses `.concept` files as an index — either from a centralized `.concept/` directory or from `.concept` files alongside each source file.

```bash
# Index source files first
concept-grep --index -r src/

# Search by meaning (output is file paths only)
concept-grep "user authentication" src/*.java

# Recursive search
concept-grep -r "payment processing" src/

# Show scores
concept-grep -s "data transmission to the server" src/*.java

# Show top 20% of results
concept-grep -p 20 -r "data validation" src/

# Invert match: show least similar files
concept-grep -v "data transmission to the server" src/*.java

# Pipe-friendly
concept-grep -r "error handling" src/ | xargs cat
```

Index lookup order:

1. `.concept/` directory (e.g., `.concept/src/main.java.concept`)
2. Same directory as source file (e.g., `src/main.java.concept`) — fallback

```text
# Centralized index
.concept/
├── src/
│   ├── main.java.concept
│   └── client.java.concept
src/
├── main.java
└── client.java

# Or same-directory layout
src/
├── main.java
├── main.java.concept
├── client.java
└── client.java.concept
```

Search uses **hybrid scoring** by default — combining semantic (embedding) similarity with keyword matching for better precision on compound queries. Use `--keyword-weight 0` to disable keyword matching and use pure semantic search.

Options:
- `-r, --recursive` — Recurse into directories (skips `.git/`, `.concept/`, `.venv/`, `node_modules/`)
- `-s, --score` — Show similarity scores
- `-g, --graph` — Show similarity as a bar graph
- `-v, --invert-match` — Show least similar files (invert match, like `grep -v`)
- `-n, --top` — Show only top N results (default: all)
- `-p, --top-percent` — Show top N% of results by similarity (default: 10)
- `--summary` — Show `embed_source` summary (first 5 lines) below each result for quick triage
- `--keyword-weight` — Weight for keyword score in hybrid search (default: 0.3). Set to 0 for pure semantic search.
- `--include GLOB` — Only include files matching the glob pattern (can be repeated, e.g. `--include "*.c" --include "*.h"`)
- `--exclude GLOB` — Exclude files matching the glob pattern (can be repeated, e.g. `--exclude "*/test/*"`)
- `--index` — Generate `.concept` files for the specified source files (uses tree-sitter summarization for supported languages). The `.concept/` directory is created next to `.git/`. Unchanged files (by SHA-256 hash and model) are skipped.
- `--force` — Force creating `.concept/` in the current directory even without `.git`
- `--model` — Embedding model (default: `text-embedding-3-small`, env: `CONCEPT_EMBED_MODEL`). If the model changes, `--index` will re-embed even if the source hash is unchanged.
- `--api-base` — OpenAI-compatible API base URL (env: `CONCEPT_API_BASE`)

#### Tree-sitter supported languages

When indexing source files with `concept-grep --index` or `concept-embed --source-file`, tree-sitter is used to extract a structural summary (classes, functions, type signatures, etc.) for better embedding quality. Unsupported file types fall back to raw text.

| Language | Extensions |
|----------|-----------|
| Java | `.java` |
| Python | `.py` |
| JavaScript | `.js`, `.mjs`, `.cjs`, `.jsx` |
| TypeScript | `.ts`, `.tsx` |
| Go | `.go` |
| Rust | `.rs` |
| C | `.c`, `.h` |
| C++ | `.cpp`, `.cxx`, `.cc`, `.hpp`, `.hxx`, `.hh` |
| C# | `.cs` |
| Ruby | `.rb` |
| PHP | `.php` |
| Swift | `.swift` |
| Kotlin | `.kt`, `.kts` |
| Scala | `.scala` |
| Haskell | `.hs` |
| Elixir | `.ex`, `.exs` |
| Lua | `.lua` |
| Bash | `.sh`, `.bash` |
| Objective-C | `.m` |
| OCaml | `.ml`, `.mli` |
| Zig | `.zig` |
| HTML | `.html`, `.htm` |
| CSS | `.css` |
| JSON | `.json` |
| YAML | `.yaml`, `.yml` |
| TOML | `.toml` |

### concept-search

Semantic search over `.concept` files using a natural language query. Output is file paths only by default (Unix-friendly).

```bash
# Search .concept files
concept-search "iOS Safari browser bug" concepts/*.concept

# Show scores
concept-search -s "TypeScript type error" concepts/*.concept

# Top 5 results only
concept-search -n 5 "hydration problem" concepts/*.concept
```

Options:
- `-s, --score` — Show similarity scores
- `-n, --top` — Show only top N results (default: all)
- `--threshold` — Minimum similarity score (default: 0.5)
- `--model` — Embedding model (default: `text-embedding-3-small`, env: `CONCEPT_EMBED_MODEL`)
- `--api-base` — OpenAI-compatible API base URL (env: `CONCEPT_API_BASE`)

### concept-embed

Generate a `.concept` file from text with an embedding vector.

```bash
# From a command-line argument
cli/concept-embed --name "My Concept" --text "Some text to embed" -o output.concept

# From stdin
echo "Some text to embed" | cli/concept-embed --name "My Concept" -o output.concept

# From a source file
cat src/User.java | cli/concept-embed --name "User" -o src/User.java.concept
```

Options:
- `--name` — Concept name (required)
- `--text` — Text content (reads stdin if omitted)
- `-o, --output` — Output file path (required)
- `--model` — Embedding model (default: `text-embedding-3-small`)
- `--language` — BCP 47 language tag (e.g. `en`, `ja`)
- `--keywords` — Keywords / tags
- `--source-file` — Source file path (enables tree-sitter summarization for supported languages)
- `--source-url` — Source URL for provenance
- `--no-embed` — Skip embedding generation

### concept-show

Display the contents of a `.concept` file in human-readable form.

```bash
cli/concept-show output.concept
```

```
Concept:  User
Version:  1.0
Created:  2026-03-14T13:46:11.223280+00:00
Embedding: 1536-dim (text-embedding-3-small)
Pipeline: embed

--- Embed Source ---
User.java
package com.example.shop.model
class User
  field email: String
  method verifyPassword(rawPassword: String): boolean
  ...

--- Text ---
package com.example.shop.model;
...
```

Options:
- `-s, --summary` — Show only embed_source summary (omit full text)
- `--json` — Output raw JSON

Use `--json` to output the raw JSON body.

### concept-sim

Calculate cosine similarity from a query `.concept` file to one or more targets. Results are sorted by similarity (most similar first).

```bash
cli/concept-sim query.concept targets/*.concept
```

```
1.000  User                 src/User.java.concept
0.754  Order                src/Order.java.concept
0.660  AuthService          src/AuthService.java.concept
0.605  Product              src/Product.java.concept
0.526  PaymentService       src/PaymentService.java.concept
0.419  ProductSearchService src/ProductSearchService.java.concept
```

Use `-s` to show scores with threshold:

```bash
cli/concept-sim -s --threshold 0.5 query.concept targets/*.concept
```

```
1.000 (>0.50)  User                 src/User.java.concept
0.754 (>0.50)  Order                src/Order.java.concept
```

Similarity 1.0 = identical, 0.0 = completely unrelated.

### concept-plot

Visualize `.concept` embeddings as an interactive scatter plot (2D/3D) using UMAP dimensionality reduction. Output is an HTML file.

```bash
# Basic 2D plot
cli/concept-plot concepts/*.concept

# 3D scatter plot
cli/concept-plot --3d concepts/*.concept

# Pipe from find
find . -name '*.concept' | cli/concept-plot

# Specify output file
cli/concept-plot concepts/*.concept -o my_plot.html
```

Options:
- `-o, --output` — Output HTML file path (default: `concept_plot.html`)
- `--3d` — Generate a 3D scatter plot (default is 2D)
- `--n-neighbors` — UMAP n_neighbors parameter (default: 15)
- `--min-dist` — UMAP min_dist parameter (default: 0.1)
- `--seed` — Random seed for reproducibility (default: 42)

Requires additional dependencies:

```bash
pip install umap-learn plotly numpy
```

## Example: Java Project Similarity

The `examples/java-project/` directory demonstrates a practical use case — finding similar classes in a Java codebase.

### Source files

A fictional e-commerce application with 6 classes:

| File | Role |
|------|------|
| `User.java` | User account entity |
| `AuthService.java` | Authentication service |
| `Product.java` | Product entity |
| `Order.java` | Order entity |
| `PaymentService.java` | Payment processing service |
| `ProductSearchService.java` | Product search service |

### Generating .concept files

```bash
for f in examples/java-project/src/*.java; do
  name=$(basename "$f" .java)
  cat "$f" | cli/concept-embed --name "$name" --language en -o "${f}.concept"
done
```

### Finding similar classes

"Which classes are most similar to `User`?"

```bash
cli/concept-sim examples/java-project/src/User.java.concept examples/java-project/src/*.concept
```

Results show that `Order` (purchase relationship) and `AuthService` (authentication relationship) are closest to `User`, which matches the actual domain relationships in the code.

3D plot: [java_plot_3d.html](examples/java-project/java_plot_3d.html) (open locally in your browser)

### Use cases

- **Refactoring** — Find classes with overlapping responsibilities
- **Impact analysis** — Identify files likely affected by a change
- **Onboarding** — Understand project structure at a glance
- **Deduplication** — Detect redundant or near-duplicate code

## Example: Wikipedia Concept Visualization

The `examples/wikipedia/` directory demonstrates visualizing semantic relationships between concepts using Wikipedia article introductions.

### Dataset

5 categories × 5 words = 25 concepts in both English and Japanese (50 total):

| Category | Words |
|----------|-------|
| Animals | Dog/イヌ, Cat/ネコ, Elephant/ゾウ, Whale/クジラ, Eagle/ワシ |
| Musical instruments | Piano/ピアノ, Guitar/ギター, Violin/ヴァイオリン, Drum/ドラム, Flute/フルート |
| Celestial bodies | Sun/太陽, Moon/月, Mars/火星, Jupiter/木星, Galaxy/銀河 |
| Food | Sushi/寿司, Pasta/パスタ, Curry/カレー, Bread/パン, Chocolate/チョコレート |
| Programming languages | Python, JavaScript, Rust, Go, Haskell |

Data source: Wikipedia (CC BY-SA 3.0)

### Generating .concept files

```bash
# English
bash examples/wikipedia/fetch.sh

# Japanese
bash examples/wikipedia/fetch-ja.sh
```

### 3D visualization

```bash
cli/concept-plot --3d examples/wikipedia/concepts/*.concept -o examples/wikipedia/wikipedia_plot_3d.html
```

Since the embedding model (text-embedding-3-small) supports multiple languages, the English and Japanese versions of the same concept (e.g., "Dog" and "イヌ") are placed close together. Clear clusters also form by category.

2D plot:

![Wikipedia Concept Embedding Map (2D)](img/wikipedia_plot_2d.png)

3D plot:

![Wikipedia Concept Embedding Map (3D)](img/wikipedia_plot_3d.png)

Interactive HTML: [wikipedia_plot_3d.html](examples/wikipedia/wikipedia_plot_3d.html) (open locally in your browser)

## Example: GitHub Issue Semantic Search

The `examples/vuejs-issues/` directory demonstrates semantic search over real-world GitHub issues from the [vuejs/core](https://github.com/vuejs/core) repository.

### Dataset

240 open issues (from 2024 onwards) from the vuejs/core repository, each converted to a `.concept` file. The title and body of each issue are combined and embedded.

### Semantic search

"Are there any iOS/Safari-specific bug reports?"

```bash
cli/concept-search "iOS Safari browser specific bug" examples/vuejs-issues/concepts/*.concept
```

```
0.6697  vuejs/core#13553: Accessibility bug with VoiceOver involving slots and form fields  issue-13553.concept
0.6082  vuejs/core#12404: `:global(A) B` incorrectly compiles to just `A`  issue-12404.concept
0.6012  vuejs/core#12789: Wrong type for vue custom element  issue-12789.concept
...
```

### Automatic clustering

K-means (k=8) clustering reveals meaningful groups based on issue content:

| Cluster | Count | Theme |
|---------|-------|-------|
| 0 | 22 | TypeScript types / SFC |
| 1 | 28 | SSR / compiler |
| 2 | 43 | Types / language-tools |
| 3 | 35 | Custom elements / Slots |
| 4 | 34 | v-model / defineModel |
| 5 | 38 | Lifecycle / Reactivity |
| 6 | 17 | Transition / Suspense |
| 7 | 23 | Type inference / ref |

3D plot: [vuejs_issues_plot_3d.html](examples/vuejs-issues/vuejs_issues_plot_3d.html) (open locally in your browser)

### Use cases

- **Duplicate detection** — Find existing issues similar to a new report
- **Triage** — Auto-classify unlabeled issues
- **Trend analysis** — Track the rise/fall of specific themes
- **Impact analysis** — Review related issues together

## Project Structure

```
concept-file/
├── SPEC.md                  — Format specification (v0.1.0)
├── README.md                — This file
├── python/
│   └── concept_file/
│       ├── __init__.py
│       ├── reader.py        — Read/write .concept files
│       └── search.py        — Cosine similarity/distance
├── cli/
│   ├── concept-embed        — Text → .concept generation
│   ├── concept-search       — Semantic search over .concept files
│   ├── concept-grep         — Semantic grep over source files
│   ├── concept-show         — Human-readable display
│   ├── concept-sim          — Similarity calculation
│   └── concept-plot         — UMAP 2D/3D scatter plot visualization
└── examples/
    ├── java-project/
    │   └── src/             — Sample Java source files with .concept files alongside
    ├── wikipedia/
    │   ├── fetch.sh         — English Wikipedia data fetcher
    │   ├── fetch-ja.sh      — Japanese Wikipedia data fetcher
    │   └── concepts/        — Generated .concept files
    └── vuejs-issues/
        └── concepts/        — vuejs/core GitHub issues
```

## Using OpenAI API

You can also use the OpenAI API instead of a local LLM:

```bash
export OPENAI_API_KEY="sk-..."
```

## License

MIT

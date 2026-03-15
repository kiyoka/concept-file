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

### Using OpenAI API

```bash
export OPENAI_API_KEY="sk-..."
```

### Using a Local LLM (LM Studio)

You can use a local embedding model via [LM Studio](https://lmstudio.ai/) instead of the OpenAI API. No API key required.

1. Install and launch LM Studio
2. Download an embedding model (e.g. `granite-embedding-278m-multilingual`)
3. Go to the **Developer** tab and load the model
4. The local API server runs at `http://localhost:1234/v1`

Set the environment variables:

```bash
export CONCEPT_API_BASE="http://localhost:1234/v1"
export CONCEPT_EMBED_MODEL="granite-embedding-278m-multilingual"
```

Then use the CLI tools as usual — they will automatically use the local model:

```bash
concept-embed --name "My Concept" --text "Some text" -o output.concept
```

You can also specify these per-command:

```bash
concept-embed --api-base http://localhost:1234/v1 --model granite-embedding-278m-multilingual \
  --name "My Concept" --text "Some text" -o output.concept
```

## CLI Tools

### concept-embed

Generate a `.concept` file from text with an embedding vector.

```bash
# From a command-line argument
cli/concept-embed --name "My Concept" --text "Some text to embed" -o output.concept

# From stdin
echo "Some text to embed" | cli/concept-embed --name "My Concept" -o output.concept

# From a source file
cat src/User.java | cli/concept-embed --name "User" -o concepts/User.concept
```

Options:
- `--name` — Concept name (required)
- `--text` — Text content (reads stdin if omitted)
- `-o, --output` — Output file path (required)
- `--model` — Embedding model (default: `text-embedding-3-small`)
- `--language` — BCP 47 language tag (e.g. `en`, `ja`)
- `--keywords` — Keywords / tags
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
Language: en
Embedding: 1536-dim (text-embedding-3-small)
Pipeline: embed

--- Text ---
package com.example.shop.model;
...
```

Use `--json` to output the raw JSON body.

### concept-search

Semantic search over `.concept` files using a natural language query. The query text is converted to an embedding vector and ranked by cosine similarity against targets.

```bash
# Search for Safari-related issues
cli/concept-search "iOS Safari browser bug" examples/vuejs-issues/concepts/*.concept

# Show top 5 results only
cli/concept-search "TypeScript type error" -n 5 concepts/*.concept

# Show only results with score >= 0.6
cli/concept-search "hydration problem" --threshold 0.6 concepts/*.concept
```

Options:
- `-n, --top` — Number of results to show (default: 10)
- `--threshold` — Minimum similarity score (default: 0.0)
- `--model` — Embedding model (default: `text-embedding-3-small`, env: `CONCEPT_EMBED_MODEL`)
- `--api-base` — OpenAI-compatible API base URL (env: `CONCEPT_API_BASE`)

### concept-dist

Calculate cosine distance from a query `.concept` file to one or more targets. Results are sorted by distance (closest first).

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

Distance 0 = identical, 1 = completely unrelated.

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
  cat "$f" | cli/concept-embed --name "$name" --language en -o "examples/java-project/concepts/${name}.concept"
done
```

### Finding similar classes

"Which classes are most similar to `User`?"

```bash
cli/concept-dist examples/java-project/concepts/User.concept examples/java-project/concepts/*.concept
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
│   ├── concept-search       — Natural language semantic search
│   ├── concept-show         — Human-readable display
│   ├── concept-dist         — Distance calculation
│   └── concept-plot         — UMAP 2D/3D scatter plot visualization
└── examples/
    ├── java-project/
    │   ├── src/             — Sample Java source files
    │   └── concepts/        — Generated .concept files
    ├── wikipedia/
    │   ├── fetch.sh         — English Wikipedia data fetcher
    │   ├── fetch-ja.sh      — Japanese Wikipedia data fetcher
    │   └── concepts/        — Generated .concept files
    └── vuejs-issues/
        └── concepts/        — vuejs/core GitHub issues
```

## License

MIT

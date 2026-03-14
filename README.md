# concept-file

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

```bash
python -m venv .venv
source .venv/bin/activate
pip install openai
export OPENAI_API_KEY="sk-..."
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

### Use cases

- **Refactoring** — Find classes with overlapping responsibilities
- **Impact analysis** — Identify files likely affected by a change
- **Onboarding** — Understand project structure at a glance
- **Deduplication** — Detect redundant or near-duplicate code

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
│   ├── concept-show         — Human-readable display
│   ├── concept-dist         — Distance calculation
│   └── concept-plot         — UMAP 2D/3D scatter plot visualization
└── examples/
    └── java-project/
        ├── src/             — Sample Java source files
        └── concepts/        — Generated .concept files
```

## License

MIT

# Concept File Format Specification

[日本語版](SPEC.ja.md)

**Version:** 0.1.0 (Draft)
**Status:** Draft
**Extension:** `.concept`
**MIME Type:** `application/x-concept`

## Abstract

The Concept File (`.concept`) is a plain-text file format that encapsulates text, embeddings, metadata, and provenance information into a single portable unit. It serves as the atomic unit of knowledge representation, enabling semantic search and RAG workflows without requiring external databases. The entire file is human-readable and can be opened in any text editor.

## Design Goals

1. **Self-contained** -- Text, embedding vectors, and provenance coexist in one file.
2. **Portable** -- Copy a file to move knowledge. No database migration required.
3. **Self-describing** -- Each file records how it was produced (model, pipeline, source).
4. **Human-readable** -- The entire file is plain text. Open it in any editor, diff it with git, inspect it with `cat`.
5. **Composable** -- Files on a filesystem form a Knowledge Base. Standard tools (`find`, `sort`, CLI pipes) work directly.

## File Layout

A `.concept` file consists of two sections:

```
+==============================+
|  Header Line (1 line)        |  "CNCP v1 <json_length>\n"
+==============================+
|  JSON Body (multi-line)      |  Pretty-printed UTF-8 JSON
+==============================+
```

### 1. Header Line

The first line of the file is a plain-text header terminated by a newline (`\n`, `0x0A`).

Format: `CNCP v<version> <json_length>\n`

| Token           | Description                                              |
|-----------------|----------------------------------------------------------|
| `CNCP`          | Magic identifier. Always the literal string `CNCP`.      |
| `v<version>`    | Format version. Current: `v1`.                           |
| `<json_length>` | Decimal integer. Byte length of the JSON body (everything after the header line's `\n` to the end of file). |

Example: `CNCP v1 1432\n`

This design ensures that `head -1 file.concept` shows the format identifier and version, and `file` commands can identify the format by the leading `CNCP` string.

### 2. JSON Body

UTF-8 encoded JSON object. The JSON MAY be pretty-printed (multi-line with indentation) or compact (single-line). Implementations MUST accept both forms.

All data, including embedding vectors, is stored within this JSON object.

#### Required Fields

| Field        | Type   | Description                              |
|--------------|--------|------------------------------------------|
| `concept`    | string | Human-readable name of the concept       |
| `version`    | string | Semantic version of this concept's content (e.g. `"1.0"`) |
| `created_at` | string | ISO 8601 timestamp of creation           |

#### Content Fields

| Field      | Type     | Required | Description                         |
|------------|----------|----------|-------------------------------------|
| `text`     | string   | Yes      | Primary textual representation      |
| `summary`  | string   | No       | Short summary of the concept        |
| `keywords` | string[] | No       | Keywords or tags                    |
| `language` | string   | No       | BCP 47 language tag (e.g. `"ja"`, `"en"`) |

#### Embedding

| Field              | Type     | Required | Description                                |
|--------------------|----------|----------|--------------------------------------------|
| `embedding`        | object   | No       | Embedding vector and its metadata          |
| `embedding.model`  | string   | Yes*     | Model used to generate the embedding       |
| `embedding.dim`    | uint     | Yes*     | Number of dimensions                       |
| `embedding.vector` | number[] | Yes*     | Array of floating-point numbers            |

\* Required when `embedding` object is present.

#### Filename Similarity

| Field                  | Type   | Required | Description                                                        |
|------------------------|--------|----------|--------------------------------------------------------------------|
| `filename_similarity`  | number | No       | Cosine similarity (0–1) between the content embedding and a filename-only embedding. 1 = maximum similarity. |

#### Provenance

| Field                   | Type   | Required | Description                                    |
|-------------------------|--------|----------|------------------------------------------------|
| `provenance`            | object | No       | Records how this concept was produced          |
| `provenance.source_url` | string | No       | URL of the original source material            |
| `provenance.pipeline`   | string | No       | Pipeline description (e.g. `"fetch \| extract_text \| summarize \| embed"`) |
| `provenance.llm_model`  | string | No       | LLM used for text generation/summarization     |

#### Relations

| Field             | Type     | Required | Description                                  |
|-------------------|----------|----------|----------------------------------------------|
| `relations`       | array    | No       | Links to other concept files                 |
| `relations[].type`| string   | Yes*     | Relation type: `"broader"`, `"narrower"`, `"related"`, `"instance"` |
| `relations[].ref` | string   | Yes*     | Relative file path to the referenced `.concept` file |

\* Required when a relation entry is present.

#### Example

```
CNCP v1 1021
{
  "concept": "Japanese AI Startup Trends",
  "version": "1.0",
  "created_at": "2026-03-14T10:00:00Z",

  "text": "Japanese AI startups have surged since 2024...",
  "summary": "Overview of funding and technology trends in Japanese AI startups",
  "keywords": ["AI", "startups", "Japan", "LLM"],
  "language": "ja",

  "embedding": {
    "model": "text-embedding-3-small",
    "dim": 1536,
    "vector": [0.0234, -0.1823, 0.0091, ...]
  },

  "filename_similarity": 0.72,

  "provenance": {
    "source_url": "https://example.com/article",
    "pipeline": "fetch | extract_text | summarize | embed",
    "llm_model": "claude-sonnet-4-6"
  },

  "relations": [
    { "type": "related", "ref": "japan_tech_policy.concept" },
    { "type": "broader", "ref": "global_ai_trends.concept" }
  ]
}
```

## Reading Algorithm

```
1. Read the first line (up to \n). Parse as "CNCP v<version> <json_length>".
2. Verify magic == "CNCP". Check version compatibility.
3. Read json_length bytes (or read to EOF). Decode as UTF-8 JSON.
4. Access fields directly from the parsed JSON object.
```

The file can also be inspected with standard text tools:

```bash
head -1 file.concept       # Show format version
cat file.concept           # Entire file is human-readable
tail -n +2 file.concept | jq .concept  # Extract concept name
grep '"concept"' file.concept          # Quick search across files
```

## File Size Estimates

| Content                              | Approximate Size |
|--------------------------------------|------------------|
| Header line                          | ~15 B            |
| JSON body without embedding          | 0.5 - 2 KB      |
| Embedding (1536-dim, JSON array)     | ~15 KB           |
| Embedding (3072-dim, JSON array)     | ~30 KB           |
| **Typical total (with embedding)**   | **~16 - 32 KB**  |
| **Typical total (without embedding)**| **~0.5 - 2 KB**  |

## Comparison with Existing Formats

| Format       | Text | Embedding | Provenance | Self-describing | Human-readable |
|--------------|------|-----------|------------|-----------------|----------------|
| .txt         | Yes  | No        | No         | No              | Yes            |
| .json        | Yes  | Manual    | Manual     | No              | Yes            |
| Parquet      | Yes  | Yes       | No         | No              | No             |
| **.concept** | Yes  | Yes       | Yes        | Yes             | Yes            |

## Future Extensions (Non-normative)

The following extensions are anticipated but not yet specified:

- **Multiple embeddings** -- e.g. text embedding + image embedding (CLIP) in the same file for cross-modal search.
- **Multimodal content** -- `image_url`, `audio_url` fields alongside `text`.
- **Chunked concepts** -- A single source document split into multiple `.concept` files with `relations` linking them.
- **Collection manifests** -- A `.concept-collection` file that indexes a directory of `.concept` files for faster search.

## Conventions

- File extension: `.concept`
- Recommended directory structure: `knowledge/<topic>.concept`
- Concept names should be descriptive and human-readable.
- When `text` changes, `embedding` SHOULD be regenerated to maintain consistency. CI hooks can enforce this by detecting text changes without corresponding embedding updates.

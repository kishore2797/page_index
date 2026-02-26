# 🚀 Practical PageIndex (Local, End-to-End)

This repository is a **practical PageIndex-style implementation** focused on the core concept behind [`VectifyAI/PageIndex`](https://github.com/VectifyAI/PageIndex):

1. 📥 collect page-like documents,
2. 🧹 normalize and chunk content,
3. 🗂️ build a searchable index,
4. 🔎 run semantic-ish retrieval over indexed pages.

> ⚠️ Note: Network restrictions in this environment blocked direct access to `https://github.com/VectifyAI/PageIndex`, so this implementation follows the same product concept (page ingestion + indexing + retrieval) with a fully runnable local example.

## ✨ What you get

- 📦 A clean Python package: `pageindex_example/`
- 📄 Ingestion from local JSON (or HTTP URLs, optional)
- ✂️ Chunking + metadata retention
- 🧠 TF-IDF vector index for practical retrieval without paid APIs
- 💻 CLI commands to ingest, build index, and query
- ✅ Tests for chunking and ranking behavior

## 🧱 Project structure

- `pageindex_example/models.py` - dataclasses for `PageDocument` and `IndexedChunk`
- `pageindex_example/crawler.py` - load docs from local JSON and optional URL fetching
- `pageindex_example/indexer.py` - chunking, TF-IDF fitting, persistence, querying
- `pageindex_example/cli.py` - command line entrypoint
- `examples/pages.json` - sample dataset
- `tests/test_indexer.py` - unit tests

## ⚡ Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 1️⃣ Build an index

```bash
python -m pageindex_example.cli build \
  --input examples/pages.json \
  --output-dir .pageindex_store
```

### 2️⃣ Query the index

```bash
python -m pageindex_example.cli query \
  --index-dir .pageindex_store \
  --text "how do i manage crawl budget"
```

### 3️⃣ Optional: index live URLs directly

```bash
python -m pageindex_example.cli build \
  --url https://developers.google.com/search/docs/crawling-indexing \
  --url https://developer.mozilla.org/en-US/docs/Web/JavaScript \
  --output-dir .pageindex_store_live
```

## 📊 Example output

The query command returns best-matching chunks with score, source URL, and content snippet:

- 🎯 score
- 🏷️ page title
- 🌐 source URL
- 📝 chunk text

## 🛠️ Why this is practical

This gives you an immediately usable pattern for PageIndex-like workflows in production:

- 🔁 replace TF-IDF with embeddings (OpenAI, bge, e5, etc.)
- 🗃️ swap file persistence for a vector DB (pgvector, Qdrant, Weaviate)
- 🤝 keep the same ingestion/chunking/query contract.

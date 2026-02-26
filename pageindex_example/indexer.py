from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Sequence

from .models import IndexedChunk, PageDocument

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]{2,}")
_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "your", "into", "are", "was", "were", "have",
    "has", "had", "you", "but", "not", "can", "all", "any", "how", "its", "out", "our", "their", "about",
}


def _tokenize(text: str) -> List[str]:
    tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
    return [t for t in tokens if t not in _STOPWORDS]


class PageIndexer:
    def __init__(self, chunk_size_words: int = 120, overlap_words: int = 20):
        if chunk_size_words <= 0:
            raise ValueError("chunk_size_words must be > 0")
        if overlap_words < 0:
            raise ValueError("overlap_words must be >= 0")
        if overlap_words >= chunk_size_words:
            raise ValueError("overlap_words must be < chunk_size_words")

        self.chunk_size_words = chunk_size_words
        self.overlap_words = overlap_words
        self.chunks: List[IndexedChunk] = []
        self._idf: Dict[str, float] = {}
        self._chunk_vectors: List[Dict[str, float]] = []

    def chunk_document(self, doc: PageDocument) -> List[IndexedChunk]:
        words = doc.content.split()
        if not words:
            return []

        chunks: List[IndexedChunk] = []
        step = self.chunk_size_words - self.overlap_words
        start = 0
        idx = 0

        while start < len(words):
            end = min(start + self.chunk_size_words, len(words))
            snippet = " ".join(words[start:end]).strip()
            if snippet:
                chunks.append(
                    IndexedChunk(
                        chunk_id=f"{doc.url}#chunk-{idx}",
                        page_title=doc.title,
                        page_url=doc.url,
                        category=doc.category,
                        text=snippet,
                    )
                )
                idx += 1
            if end >= len(words):
                break
            start += step

        return chunks

    def _build_idf(self, tokenized_docs: List[List[str]]) -> Dict[str, float]:
        doc_count = len(tokenized_docs)
        df = Counter()
        for tokens in tokenized_docs:
            df.update(set(tokens))

        idf = {}
        for token, freq in df.items():
            idf[token] = math.log((1 + doc_count) / (1 + freq)) + 1.0
        return idf

    def _tfidf_vector(self, tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
        if not tokens:
            return {}
        tf = Counter(tokens)
        total = len(tokens)
        vec = {token: (count / total) * idf.get(token, 0.0) for token, count in tf.items()}

        norm = math.sqrt(sum(v * v for v in vec.values()))
        if norm == 0:
            return {}
        return {k: v / norm for k, v in vec.items()}

    def build(self, docs: Sequence[PageDocument]) -> None:
        self.chunks = []
        for doc in docs:
            self.chunks.extend(self.chunk_document(doc))
        if not self.chunks:
            raise ValueError("No chunks were generated from input documents.")

        tokenized = [_tokenize(chunk.text) for chunk in self.chunks]
        self._idf = self._build_idf(tokenized)
        self._chunk_vectors = [self._tfidf_vector(tokens, self._idf) for tokens in tokenized]

    def _cosine(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        smaller, larger = (a, b) if len(a) < len(b) else (b, a)
        return sum(value * larger.get(token, 0.0) for token, value in smaller.items())

    def query(self, text: str, top_k: int = 5) -> List[dict]:
        if not text.strip():
            return []
        if not self._chunk_vectors:
            raise ValueError("Index not built. Call build() or load() first.")

        qvec = self._tfidf_vector(_tokenize(text), self._idf)
        scored = []
        for i, cvec in enumerate(self._chunk_vectors):
            score = self._cosine(qvec, cvec)
            if score > 0:
                scored.append((i, score))
        scored.sort(key=lambda x: x[1], reverse=True)

        results: List[dict] = []
        for idx, score in scored[:top_k]:
            chunk = self.chunks[idx]
            results.append(
                {
                    "score": round(score, 4),
                    "chunk_id": chunk.chunk_id,
                    "title": chunk.page_title,
                    "url": chunk.page_url,
                    "category": chunk.category,
                    "text": chunk.text,
                }
            )
        return results

    def save(self, output_dir: str | Path) -> None:
        if not self._chunk_vectors:
            raise ValueError("Nothing to save: build index first.")
        target = Path(output_dir)
        target.mkdir(parents=True, exist_ok=True)

        (target / "chunks.json").write_text(
            json.dumps([chunk.__dict__ for chunk in self.chunks], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (target / "idf.json").write_text(json.dumps(self._idf, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, index_dir: str | Path) -> None:
        source = Path(index_dir)
        chunks_payload = json.loads((source / "chunks.json").read_text(encoding="utf-8"))
        self.chunks = [IndexedChunk(**item) for item in chunks_payload]
        self._idf = json.loads((source / "idf.json").read_text(encoding="utf-8"))

        tokenized = [_tokenize(chunk.text) for chunk in self.chunks]
        self._chunk_vectors = [self._tfidf_vector(tokens, self._idf) for tokens in tokenized]

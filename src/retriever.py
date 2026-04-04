"""TF-IDF retriever for HVAC educational documents.

Lightweight alternative to a vector DB — no model downloads required.
Good enough for structured domain documents; swap for a vector DB in production.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

STORE_PATH   = Path(__file__).parent.parent / "data" / "tfidf_store.json"
CHUNK_SIZE   = 600
CHUNK_OVERLAP = 100


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if len(c) > 50]


def _parse_doc(path: Path) -> list[dict]:
    text        = path.read_text()
    title_match = re.search(r"^#\s+(.+)", text, re.MULTILINE)
    title       = title_match.group(1) if title_match else path.stem
    return [
        {
            "id":     f"{path.stem}_chunk_{i}",
            "text":   chunk,
            "source": path.name,
            "title":  title,
        }
        for i, chunk in enumerate(_chunk_text(text))
    ]


# ---------------------------------------------------------------------------
# Persist / load the chunk store
# ---------------------------------------------------------------------------

def _load_store() -> list[dict]:
    if STORE_PATH.exists():
        return json.loads(STORE_PATH.read_text())
    return []


def _save_store(chunks: list[dict]) -> None:
    STORE_PATH.write_text(json.dumps(chunks, indent=2))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ingest_directory(doc_dir: Path, reset: bool = False) -> int:
    """Parse all .md files in doc_dir and save chunk store. Returns chunks added."""
    existing   = {} if reset else {c["id"]: c for c in _load_store()}
    docs       = list(doc_dir.glob("*.md"))
    if not docs:
        raise FileNotFoundError(f"No .md files found in {doc_dir}")

    added = 0
    for path in docs:
        for chunk in _parse_doc(path):
            if chunk["id"] not in existing:
                existing[chunk["id"]] = chunk
                added += 1

    _save_store(list(existing.values()))
    return added


def retrieve(query: str, n_results: int = 4) -> list[dict]:
    """TF-IDF retrieval. Returns top-n chunks with a relevance score."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    chunks = _load_store()
    if not chunks:
        return []

    texts       = [c["text"] for c in chunks]
    vectorizer  = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(texts)
    query_vec   = vectorizer.transform([query])
    scores      = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = np.argsort(scores)[::-1][:n_results]

    return [
        {**chunks[i], "score": round(float(scores[i]), 3)}
        for i in top_indices
        if scores[i] > 0
    ]


def format_context(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(f"[{i}] Source: {c['title']} ({c['source']})\n{c['text']}")
    return "\n\n---\n\n".join(parts)

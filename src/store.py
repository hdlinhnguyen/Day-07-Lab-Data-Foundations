from __future__ import annotations

import re
from typing import Any, Callable

from .chunking import compute_similarity
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # TODO: initialize chromadb client + collection
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _tokenize(self, text: str) -> set[str]:
        tokens = re.findall(r"\w+", text.lower())
        return set(tokens)

    def _keyword_score(self, query: str, content: str) -> float:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return 0.0
        content_tokens = self._tokenize(content)
        overlap = query_tokens.intersection(content_tokens)
        return len(overlap) / len(query_tokens)

    def _make_record(self, doc: Document) -> dict[str, Any]:
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": dict(doc.metadata or {}),
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(self, query_text: str, query_embedding: list[float], records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        scored: list[dict[str, Any]] = []
        for record in records:
            embedding = record["embedding"]
            semantic_score = compute_similarity(query_embedding, embedding)
            keyword_score = self._keyword_score(query_text, record["content"])
            score = 0.7 * semantic_score + 0.3 * keyword_score
            scored.append({
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": score,
            })

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if self._use_chroma and self._collection is not None:
            raise NotImplementedError("ChromaDB support is not implemented")

        for doc in docs:
            self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute a hybrid similarity score that combines embeddings and token overlap.
        """
        if self._use_chroma and self._collection is not None:
            raise NotImplementedError("ChromaDB support is not implemented")

        query_embedding = self._embedding_fn(query)
        return self._search_records(query, query_embedding, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            raise NotImplementedError("ChromaDB support is not implemented")
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if self._use_chroma and self._collection is not None:
            raise NotImplementedError("ChromaDB support is not implemented")

        if metadata_filter is None:
            eligible = self._store
        else:
            eligible = [
                record
                for record in self._store
                if all(record["metadata"].get(key) == value for key, value in metadata_filter.items())
            ]

        query_embedding = self._embedding_fn(query)
        return self._search_records(query, query_embedding, eligible, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        original_len = len(self._store)
        self._store = [record for record in self._store if record["id"] != doc_id]
        return len(self._store) < original_len

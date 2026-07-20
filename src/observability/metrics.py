from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class _Metrics:
    """
    Lightweight module-level singleton tracking runtime system state.

    Updated by the pipeline orchestrator after each stage — never imported
    directly by domain modules (ingestion, chunking, embeddings, etc.).
    Call reset() in test teardown to prevent state leakage between tests.
    """

    # Counters
    documents_loaded_total: int = 0
    chunks_created_total: int = 0
    query_count_total: int = 0
    error_count_total: int = 0

    # Latencies (seconds, last recorded value)
    embedding_latency_seconds: float = 0.0
    retrieval_latency_seconds: float = 0.0
    rerank_latency_seconds: float = 0.0

    # State
    last_error: Optional[str] = None
    selected_embedding_provider: str = ""
    selected_vector_store: str = ""

    # -----------------------------------------------------------------------

    def record_error(self, message: str) -> None:
        self.error_count_total += 1
        self.last_error = message

    def reset(self) -> None:
        """Reset all counters and state to initial values. Use in test teardown."""
        self.documents_loaded_total = 0
        self.chunks_created_total = 0
        self.query_count_total = 0
        self.error_count_total = 0
        self.embedding_latency_seconds = 0.0
        self.retrieval_latency_seconds = 0.0
        self.rerank_latency_seconds = 0.0
        self.last_error = None
        self.selected_embedding_provider = ""
        self.selected_vector_store = ""

    def to_dict(self) -> dict:
        """Return a plain dictionary snapshot of current counters, latencies, and state."""
        return {
            "documents_loaded_total": self.documents_loaded_total,
            "chunks_created_total": self.chunks_created_total,
            "query_count_total": self.query_count_total,
            "error_count_total": self.error_count_total,
            "embedding_latency_seconds": round(self.embedding_latency_seconds, 4),
            "retrieval_latency_seconds": round(self.retrieval_latency_seconds, 4),
            "rerank_latency_seconds": round(self.rerank_latency_seconds, 4),
            "last_error": self.last_error,
            "selected_embedding_provider": self.selected_embedding_provider,
            "selected_vector_store": self.selected_vector_store,
        }


# Module-level singleton. Import and update directly:
#   from src.observability.metrics import METRICS
#   METRICS.query_count_total += 1
METRICS = _Metrics()

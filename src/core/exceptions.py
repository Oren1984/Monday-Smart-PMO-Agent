from __future__ import annotations


class PMOAgentError(Exception):
    """Base exception for all Smart PMO Agent errors."""


class ConfigurationError(PMOAgentError):
    """Raised when required configuration is missing or invalid."""


class ValidationError(PMOAgentError):
    """Raised when input validation fails at a system boundary."""


class IngestionError(PMOAgentError):
    """Raised when document loading or text cleaning fails."""


class ChunkingError(PMOAgentError):
    """Raised when text chunking fails."""


class EmbeddingError(PMOAgentError):
    """Raised when embedding generation fails."""


class VectorStoreError(PMOAgentError):
    """Raised when a vector store operation fails."""


class RetrievalError(PMOAgentError):
    """Raised when semantic retrieval fails."""


class IntegrationError(PMOAgentError):
    """Raised when the Monday integration layer fails to load or normalize data."""


class PMOAnalysisError(PMOAgentError):
    """Raised when PMO analysis fails due to missing or malformed data."""


class AIQueryError(PMOAgentError):
    """Raised when the AI Q&A pipeline fails."""

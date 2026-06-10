from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_env: str = "local"
    log_level: str = "INFO"

    # PMO data source — "mock" loads local demo JSON; "monday_api" is a future extension
    pmo_data_source: str = "mock"

    # Monday API (future use — leave empty in v1)
    monday_api_token: Optional[str] = None
    monday_workspace_id: Optional[str] = None

    # AI / embedding provider for PMO Q&A
    mock_mode: bool = True
    embedding_provider: str = "mock"
    embedding_model: str = "mock-384"

    # Vector store for methodology doc indexing
    vector_store: str = "chroma"

    # Chunking for methodology docs
    chunk_strategy: str = "recursive"
    chunk_size: int = 500
    chunk_overlap: int = 100

    # Retrieval
    top_k: int = 5

    # Optional AI provider keys
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Paths
    data_dir: str = "data"
    monday_demo_dir: str = "data/monday_demo"
    methodology_docs_dir: str = "data/methodology_docs"
    vector_db_dir: str = "vector_db"
    results_dir: str = "results"

    # Upload limits
    max_upload_mb: int = 10


settings = AppSettings()

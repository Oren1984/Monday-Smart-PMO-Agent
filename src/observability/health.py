from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict

from src.core.config import AppSettings


@dataclass
class HealthStatus:
    healthy: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    details: Dict[str, str] = field(default_factory=dict)


def check_health(settings: AppSettings) -> HealthStatus:
    """
    Run lightweight readiness checks against config and the local filesystem.

    Standalone utility — not wired into the Streamlit UI or any endpoint.
    Available for a future operator-facing health surface if one is added.
    """
    checks: Dict[str, bool] = {}
    details: Dict[str, str] = {}

    # Config presence is always true if we reached this point
    checks["config_loaded"] = True
    details["config_loaded"] = "OK"

    # Required runtime directories
    for key, path in [
        ("data_dir", settings.data_dir),
        ("vector_db_dir", settings.vector_db_dir),
        ("results_dir", settings.results_dir),
    ]:
        exists = os.path.isdir(path)
        checks[key] = exists
        details[key] = f"{'OK' if exists else 'MISSING'}: {path}"

    # Informational fields (not used in healthy flag)
    details["embedding_provider"] = settings.embedding_provider
    details["vector_store"] = settings.vector_store
    details["mock_mode"] = str(settings.mock_mode)

    healthy = all(checks.values())
    return HealthStatus(healthy=healthy, checks=checks, details=details)

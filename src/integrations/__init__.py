from __future__ import annotations

from src.core.contracts import MondayClientBase


def get_monday_client(data_source: str = "mock",
                      data_dir: str = "data/monday_demo",
                      api_token: str | None = None,
                      workspace_id: str | None = None) -> MondayClientBase:
    """
    Factory: return the correct Monday client based on PMO_DATA_SOURCE setting.

    "mock"       -> MondayMockClient  (loads local demo JSON -- default, no token needed)
    "monday_api" -> MondayAPIClient   (future live integration -- requires token)
    """
    if data_source == "mock":
        from src.integrations.monday_mock_client import MondayMockClient
        return MondayMockClient(data_dir=data_dir)

    if data_source == "monday_api":
        from src.integrations.monday_api_client import MondayAPIClient
        return MondayAPIClient(api_token=api_token, workspace_id=workspace_id)

    from src.core.exceptions import ConfigurationError
    raise ConfigurationError(
        f"Unknown PMO_DATA_SOURCE: {data_source!r}. "
        "Valid options: 'mock', 'monday_api'."
    )

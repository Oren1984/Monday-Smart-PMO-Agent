from __future__ import annotations

from typing import List, Optional

from src.core.contracts import (
    MondayClientBase,
    PMOBoard,
    PMOOKR,
    PMORisk,
    PMOSprint,
    PMOTask,
)
from src.core.exceptions import ConfigurationError


class MondayAPIClient(MondayClientBase):
    """
    Future live Monday.com API client.

    This is a skeleton placeholder for v1.  No real API calls are made.
    Real implementation would use Monday's GraphQL API with a personal
    access token and board/workspace IDs configured in .env.

    To activate in a future version:
        1. Set PMO_DATA_SOURCE=monday_api in .env
        2. Set MONDAY_API_TOKEN and MONDAY_WORKSPACE_ID in .env
        3. Implement the GraphQL queries in each method below
        4. The rest of the system requires zero changes

    Monday API docs: https://developer.monday.com/api-reference
    """

    SOURCE_LABEL = "Monday.com (live API) — not available in v1"

    def __init__(self, api_token: Optional[str] = None,
                 workspace_id: Optional[str] = None) -> None:
        if not api_token:
            raise ConfigurationError(
                "MondayAPIClient requires MONDAY_API_TOKEN. "
                "Set PMO_DATA_SOURCE=mock to use local demo data instead."
            )
        self._api_token = api_token
        self._workspace_id = workspace_id
        # Future: self._client = MondayClient(token=api_token)

    def get_boards(self) -> List[PMOBoard]:
        raise NotImplementedError(
            "MondayAPIClient is not implemented in v1. "
            "Use MondayMockClient (PMO_DATA_SOURCE=mock) instead."
        )

    def get_tasks(self, board_id: Optional[str] = None,
                  sprint: Optional[str] = None) -> List[PMOTask]:
        raise NotImplementedError(
            "MondayAPIClient is not implemented in v1."
        )

    def get_sprints(self) -> List[PMOSprint]:
        raise NotImplementedError(
            "MondayAPIClient is not implemented in v1."
        )

    def get_risks(self) -> List[PMORisk]:
        raise NotImplementedError(
            "MondayAPIClient is not implemented in v1."
        )

    def get_okrs(self) -> List[PMOOKR]:
        raise NotImplementedError(
            "MondayAPIClient is not implemented in v1."
        )

    @property
    def source_label(self) -> str:
        return self.SOURCE_LABEL

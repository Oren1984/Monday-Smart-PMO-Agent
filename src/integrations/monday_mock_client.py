from __future__ import annotations

import json
import os
from typing import List, Optional

from src.core.contracts import (
    MondayClientBase,
    PMOBoard,
    PMOKeyResult,
    PMOOKR,
    PMORisk,
    PMOSprint,
    PMOTask,
)
from src.core.exceptions import IntegrationError


class MondayMockClient(MondayClientBase):
    """
    Loads realistic Monday-style project data from local JSON demo files.

    This client satisfies the MondayClientBase interface identically to what
    a live MondayAPIClient would produce. The rest of the system never needs
    to know which client is active.

    Data directory: data/monday_demo/
    """

    SOURCE_LABEL = "Local Monday-style demo data"

    def __init__(self, data_dir: str = "data/monday_demo") -> None:
        self._data_dir = data_dir
        self._boards: Optional[List[PMOBoard]] = None
        self._tasks: Optional[List[PMOTask]] = None
        self._sprints: Optional[List[PMOSprint]] = None
        self._risks: Optional[List[PMORisk]] = None
        self._okrs: Optional[List[PMOOKR]] = None

    # ------------------------------------------------------------------
    # MondayClientBase interface
    # ------------------------------------------------------------------

    def get_boards(self) -> List[PMOBoard]:
        if self._boards is None:
            self._boards = self._load_boards()
        return self._boards

    def get_tasks(self, board_id: Optional[str] = None,
                  sprint: Optional[str] = None) -> List[PMOTask]:
        if self._tasks is None:
            self._tasks = self._load_tasks()
        tasks = self._tasks
        if board_id:
            tasks = [t for t in tasks if t.board_id == board_id]
        if sprint:
            tasks = [t for t in tasks if t.sprint == sprint]
        return tasks

    def get_sprints(self) -> List[PMOSprint]:
        if self._sprints is None:
            self._sprints = self._load_sprints()
        return self._sprints

    def get_risks(self) -> List[PMORisk]:
        if self._risks is None:
            self._risks = self._load_risks()
        return self._risks

    def get_okrs(self) -> List[PMOOKR]:
        if self._okrs is None:
            self._okrs = self._load_okrs()
        return self._okrs

    @property
    def source_label(self) -> str:
        return self.SOURCE_LABEL

    # ------------------------------------------------------------------
    # Private loaders — parse JSON and construct typed DTOs
    # ------------------------------------------------------------------

    def _load_file(self, filename: str) -> list:
        path = os.path.join(self._data_dir, filename)
        if not os.path.exists(path):
            raise IntegrationError(
                f"Demo data file not found: {path}. "
                "Ensure data/monday_demo/ contains all required JSON files."
            )
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _load_boards(self) -> List[PMOBoard]:
        raw = self._load_file("boards.json")
        return [
            PMOBoard(
                id=b["id"],
                name=b["name"],
                workspace=b["workspace"],
                groups=b.get("groups", []),
            )
            for b in raw
        ]

    def _load_tasks(self) -> List[PMOTask]:
        raw = self._load_file("tasks.json")
        return [
            PMOTask(
                id=t["id"],
                board_id=t["board_id"],
                group=t["group"],
                name=t["name"],
                status=t["status"],
                priority=t["priority"],
                owner=t["owner"],
                story_points=t.get("story_points", 0),
                due_date=t.get("due_date"),
                sprint=t.get("sprint"),
                epic=t.get("epic"),
                okr_link=t.get("okr_link"),
                blocker=t.get("blocker"),
                dependencies=t.get("dependencies", []),
                labels=t.get("labels", []),
                last_update=t.get("last_update"),
                updates=t.get("updates", []),
            )
            for t in raw
        ]

    def _load_sprints(self) -> List[PMOSprint]:
        raw = self._load_file("sprints.json")
        return [
            PMOSprint(
                id=s["id"],
                name=s["name"],
                board_id=s["board_id"],
                start_date=s["start_date"],
                end_date=s["end_date"],
                planned_points=s["planned_points"],
                completed_points=s["completed_points"],
                status=s["status"],
                goal=s.get("goal", ""),
                team=s.get("team", []),
                retro_notes=s.get("retro_notes", []),
            )
            for s in raw
        ]

    def _load_risks(self) -> List[PMORisk]:
        raw = self._load_file("risks.json")
        return [
            PMORisk(
                id=r["id"],
                title=r["title"],
                description=r["description"],
                level=r["level"],
                probability=r["probability"],
                impact=r["impact"],
                mitigation=r["mitigation"],
                owner=r["owner"],
                status=r["status"],
                affected_okr=r.get("affected_okr"),
                affected_sprint=r.get("affected_sprint"),
            )
            for r in raw
        ]

    def _load_okrs(self) -> List[PMOOKR]:
        raw = self._load_file("okrs.json")
        okrs = []
        for o in raw:
            key_results = [
                PMOKeyResult(
                    id=kr["id"],
                    description=kr["description"],
                    target=kr["target"],
                    current=kr["current"],
                    unit=kr["unit"],
                    status=kr["status"],
                )
                for kr in o.get("key_results", [])
            ]
            okrs.append(
                PMOOKR(
                    id=o["id"],
                    objective=o["objective"],
                    owner=o["owner"],
                    quarter=o["quarter"],
                    key_results=key_results,
                    contributing_epics=o.get("contributing_epics", []),
                    status=o.get("status", "On Track"),
                )
            )
        return okrs

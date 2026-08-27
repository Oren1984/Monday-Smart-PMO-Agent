from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# RAG Infrastructure DTOs (used by the methodology doc indexing pipeline)
# ---------------------------------------------------------------------------

@dataclass
class Document:
    doc_id: str
    text: str
    source: str
    file_type: str
    page_number: Optional[int] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    metadata: dict = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    score: Optional[float] = None
    rank: Optional[int] = None


# ---------------------------------------------------------------------------
# PMO Data DTOs — normalized Monday-style project management entities
# ---------------------------------------------------------------------------

@dataclass
class PMOBoard:
    id: str
    name: str
    workspace: str
    groups: List[str] = field(default_factory=list)


@dataclass
class PMOTask:
    id: str
    board_id: str
    group: str
    name: str
    status: str                          # "Done" | "In Progress" | "Stuck" | "Blocked" | "To Do"
    priority: str                        # "Critical" | "High" | "Medium" | "Low"
    owner: str
    story_points: int = 0
    due_date: Optional[str] = None       # ISO date string
    sprint: Optional[str] = None
    epic: Optional[str] = None
    okr_link: Optional[str] = None
    blocker: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    last_update: Optional[str] = None
    updates: List[str] = field(default_factory=list)


@dataclass
class PMOSprint:
    id: str
    name: str
    board_id: str
    start_date: str
    end_date: str
    planned_points: int
    completed_points: int
    status: str                          # "active" | "completed" | "planned"
    goal: str = ""
    team: List[str] = field(default_factory=list)
    retro_notes: List[str] = field(default_factory=list)


@dataclass
class PMORisk:
    id: str
    title: str
    description: str
    level: str                           # "Critical" | "High" | "Medium" | "Low"
    probability: str                     # "High" | "Medium" | "Low"
    impact: str                          # "High" | "Medium" | "Low"
    mitigation: str
    owner: str
    status: str                          # "Open" | "Mitigated" | "Closed"
    affected_okr: Optional[str] = None
    affected_sprint: Optional[str] = None


@dataclass
class PMOKeyResult:
    id: str
    description: str
    target: float
    current: float
    unit: str
    status: str                          # "On Track" | "At Risk" | "Off Track"

    @property
    def progress_pct(self) -> float:
        if self.target == 0:
            return 0.0
        return min(round((self.current / self.target) * 100, 1), 100.0)


@dataclass
class PMOOKR:
    id: str
    objective: str
    owner: str
    quarter: str
    key_results: List[PMOKeyResult] = field(default_factory=list)
    contributing_epics: List[str] = field(default_factory=list)
    status: str = "On Track"             # "On Track" | "At Risk" | "Off Track"


# ---------------------------------------------------------------------------
# PMO Analysis Output DTOs
# ---------------------------------------------------------------------------

@dataclass
class ProjectHealthReport:
    health_score: str                    # "Green" | "Yellow" | "Red"
    total_tasks: int
    done: int
    in_progress: int
    stuck: int
    blocked: int
    todo: int
    overdue_tasks: List[PMOTask] = field(default_factory=list)
    open_blockers: List[PMOTask] = field(default_factory=list)
    sprint_progress_pct: float = 0.0
    summary: str = ""


@dataclass
class SprintReport:
    sprint: PMOSprint
    velocity: float                      # completed / planned (0.0 – 1.0)
    health: str                          # "Healthy" | "Needs Attention" | "At Risk"
    tasks_done: List[PMOTask] = field(default_factory=list)
    tasks_in_progress: List[PMOTask] = field(default_factory=list)
    tasks_stuck: List[PMOTask] = field(default_factory=list)
    tasks_blocked: List[PMOTask] = field(default_factory=list)
    tasks_todo: List[PMOTask] = field(default_factory=list)
    team_load: dict = field(default_factory=dict)
    bottleneck_owners: List[str] = field(default_factory=list)
    carryover_risk_tasks: List[PMOTask] = field(default_factory=list)
    retro_points: List[str] = field(default_factory=list)


@dataclass
class CapacityReport:
    owner_task_counts: dict = field(default_factory=dict)
    owner_point_totals: dict = field(default_factory=dict)
    owner_blocked_counts: dict = field(default_factory=dict)
    overloaded_owners: List[str] = field(default_factory=list)
    underloaded_owners: List[str] = field(default_factory=list)
    # Bus factor / workload concentration: owners holding a disproportionate
    # share of active story points — a single-point-of-failure delivery risk.
    concentration_risk_owners: List[str] = field(default_factory=list)


@dataclass
class OKRAlignmentReport:
    okrs: List[PMOOKR] = field(default_factory=list)
    unaligned_task_count: int = 0
    unaligned_task_pct: float = 0.0
    at_risk_okrs: List[PMOOKR] = field(default_factory=list)
    okr_task_map: dict = field(default_factory=dict)
    summary: str = ""
    # At-risk/off-track OKRs whose contributing work includes blocked/stuck
    # tasks — i.e. delivery execution risk that threatens a strategic objective.
    okrs_with_delivery_risk: List[str] = field(default_factory=list)


@dataclass
class PMOAnswer:
    question: str
    answer: str
    sources: List[str] = field(default_factory=list)
    data_points: List[str] = field(default_factory=list)
    mode: str = "mock"                   # "mock" | "openai" | "gemini"
    # Lightweight, advisory-only AI cost-awareness signal (not billing data).
    cost_note: Optional[str] = None


# ---------------------------------------------------------------------------
# RAG Infrastructure ABCs (used by methodology doc indexing)
# ---------------------------------------------------------------------------

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]: ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    @abstractmethod
    def dimension(self) -> int: ...


class VectorStore(ABC):
    @abstractmethod
    def add(self, chunks: List[Chunk]) -> None: ...

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int) -> List[Chunk]: ...

    @abstractmethod
    def persist(self) -> None: ...

    @abstractmethod
    def load(self) -> None: ...

    @abstractmethod
    def clear(self) -> None: ...

    @property
    @abstractmethod
    def store_name(self) -> str: ...


class Chunker(ABC):
    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]: ...


class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: str, chunks: List[Chunk]) -> List[Chunk]: ...


# ---------------------------------------------------------------------------
# Monday Integration ABC
# ---------------------------------------------------------------------------

class MondayClientBase(ABC):
    """Abstract interface that both mock and live Monday clients must implement."""

    @abstractmethod
    def get_boards(self) -> List[PMOBoard]: ...

    @abstractmethod
    def get_tasks(self, board_id: Optional[str] = None,
                  sprint: Optional[str] = None) -> List[PMOTask]: ...

    @abstractmethod
    def get_sprints(self) -> List[PMOSprint]: ...

    @abstractmethod
    def get_risks(self) -> List[PMORisk]: ...

    @abstractmethod
    def get_okrs(self) -> List[PMOOKR]: ...

    @property
    @abstractmethod
    def source_label(self) -> str:
        """Human-readable data source label for UI display."""

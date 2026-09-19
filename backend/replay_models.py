from typing import Literal, Optional
from pydantic import BaseModel, Field


class ReplayState(BaseModel):
    energy: int
    tool: int
    cargo: int
    cargo_value: int
    depth: int
    quality: int
    hazard: int
    delivered: int
    banked_points: int
    exploration_points: int
    penalties: int
    incidents: int


class DecisionReplay(BaseModel):
    id: str
    agent_id: str
    sequence: int
    created_at: str
    action: str
    stage: str
    reason: str
    message: str
    strategy_name: str
    strategy_version: int
    scope: Literal['contest', 'expedition']
    season_id: Optional[str] = None
    before: ReplayState
    after: ReplayState
    score_before: int
    score_after: int
    score_delta: int
    banked_delta: int
    exploration_delta: int
    penalty_delta: int
    score_explanation: str


class ReplayPage(BaseModel):
    agent_id: Optional[str] = None
    total: int = 0
    recorded_total: int = 0
    has_more: bool = False
    next_before: Optional[int] = None
    entries: list[DecisionReplay] = Field(default_factory=list)
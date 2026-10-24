"""MatterGate projection types for the adapted PriviLAB policy engine."""
from dataclasses import dataclass
from enum import StrEnum


class PermissionState(StrEnum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"
    CONDITIONAL = "CONDITIONAL"


@dataclass(frozen=True, order=True)
class ConditionId:
    value: str


@dataclass(frozen=True)
class PermissionResult:
    state: PermissionState
    condition_ids: frozenset[ConditionId] = frozenset()


@dataclass(frozen=True)
class UserIdentity:
    user_id: str


@dataclass(frozen=True)
class Role:
    role_id: str


@dataclass(frozen=True)
class UserContext:
    identity: UserIdentity | None = None
    role: Role | None = None


@dataclass(frozen=True)
class MatterContext:
    matter_id: str


@dataclass(frozen=True)
class ClientContext:
    client_id: str


@dataclass(frozen=True)
class WorkflowContext:
    workflow_id: str


@dataclass(frozen=True)
class SyntheticRequestContext:
    user: UserContext | None = None
    client: ClientContext | None = None
    matter: MatterContext | None = None
    workflow: WorkflowContext | None = None
    purpose: str | None = None
    jurisdiction: str | None = None

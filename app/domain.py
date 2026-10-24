"""MatterGate-owned contracts and state transitions.
Duplicate-field parsing adapted from PriviLAB domain/research.py, Apache-2.0,
Copyright 2026 Data Strategy Lab LLC; modified for MatterGate's richer schema.
Upstream commit: 21baa4ccdc468bd6a30681344eb8ec3df752790a.
"""
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

DISCLOSURE = "MatterGate is a demonstration research workflow using synthetic and public materials. It does not provide legal advice, make legal decisions, or establish compliance."
QUESTION = "Can our sales team share EU customer contact data with Vendor X so it can triage support tickets?"
POLICY_VERSION = "mattergate-1.0"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Status(StrEnum):
    RECEIVED = "RECEIVED"
    POLICY_EVALUATING = "POLICY_EVALUATING"
    DENIED = "DENIED"
    SCOPE_GRANTED = "SCOPE_GRANTED"
    RETRIEVING = "RETRIEVING"
    DRAFTING = "DRAFTING"
    EVALUATING = "EVALUATING"
    BLOCKED = "BLOCKED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"


TRANSITIONS = {
    Status.RECEIVED: {Status.POLICY_EVALUATING, Status.BLOCKED},
    Status.POLICY_EVALUATING: {Status.DENIED, Status.SCOPE_GRANTED, Status.BLOCKED},
    Status.SCOPE_GRANTED: {Status.RETRIEVING, Status.BLOCKED},
    Status.RETRIEVING: {Status.DRAFTING, Status.BLOCKED},
    Status.DRAFTING: {Status.EVALUATING, Status.MODEL_UNAVAILABLE, Status.BLOCKED},
    Status.EVALUATING: {Status.READY_FOR_REVIEW, Status.BLOCKED},
    Status.READY_FOR_REVIEW: {Status.APPROVED, Status.REJECTED, Status.REVISION_REQUESTED, Status.BLOCKED},
}
TERMINAL = set(Status) - set(TRANSITIONS)


class ControlError(ValueError):
    pass


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class ResearchRequest(StrictModel):
    actor_id: str = Field(min_length=1, max_length=80)
    matter_id: Literal["vendor_onboarding", "restricted_m_and_a"]
    purpose: Literal["vendor_risk_assessment", "support_operations", "transaction_analysis"]
    jurisdiction: Literal["EU", "US", "GLOBAL"]
    question: str = Field(min_length=20, max_length=1000)
    mode: Literal["live", "fixture"] = "fixture"

    @field_validator("question")
    @classmethod
    def plain_text(cls, value):
        if any(ord(c) < 32 and c not in "\n\t\r" for c in value) or "<" in value or ">" in value:
            raise ValueError("Use plain text without markup or control characters")
        value.encode("utf-8")
        if len(value.strip()) < 20:
            raise ValueError("Question must contain at least 20 characters")
        return value.strip()


class AccessScope(StrictModel):
    run_id: str
    actor_id: str
    matter_id: str
    purpose: str
    jurisdiction: str
    policy_decision: Literal["ALLOW", "DENY", "CONDITIONAL"]
    allowed_source_ids: tuple[str, ...] = ()
    allowed_source_categories: tuple[str, ...] = ()
    allowed_actions: tuple[str, ...] = ()
    denial_reason_code: str | None = None
    expires_at: str
    policy_version: str = POLICY_VERSION

    def require_allow(self, request: ResearchRequest | None = None):
        if (self.policy_decision != "ALLOW" or "research" not in self.allowed_actions
                or self.policy_version != POLICY_VERSION
                or self.actor_id not in {"jordan_sales_ops", "maya_privacy_counsel"}
                or self.matter_id != "vendor_onboarding" or self.purpose != "vendor_risk_assessment"
                or self.jurisdiction not in {"EU", "US", "GLOBAL"}
                or not self.allowed_source_ids or datetime.fromisoformat(self.expires_at) <= datetime.now(timezone.utc)):
            raise ControlError("SCOPE_NOT_VALID")
        if request and any(getattr(self, name) != getattr(request, name) for name in ("actor_id", "matter_id", "purpose", "jurisdiction")):
            raise ControlError("SCOPE_MISMATCH")


class Evidence(StrictModel):
    chunk_id: str
    source_id: str
    title: str
    text: str
    authority_tier: str
    classification: str
    matter_id: str
    version: str
    content_hash: str
    url: str | None = None


class Citation(StrictModel):
    claim: str = Field(min_length=1, max_length=1000)
    chunk_ids: list[str] = Field(min_length=1, max_length=5)


class Draft(StrictModel):
    summary: str = Field(min_length=1, max_length=900)
    recommendation: Literal["PROCEED_WITH_CONDITIONS", "DO_NOT_PROCEED", "INSUFFICIENT_EVIDENCE"]
    conditions: list[str] = Field(max_length=8)
    risks_and_caveats: list[str] = Field(max_length=8)
    open_questions: list[str] = Field(max_length=8)
    citations: list[Citation] = Field(min_length=1, max_length=5)
    disclaimer: str

    @field_validator("conditions", "risks_and_caveats", "open_questions")
    @classmethod
    def bounded_items(cls, items):
        if any(not item.strip() or len(item) > 1000 for item in items):
            raise ValueError("Invalid brief item")
        return items


class CitedDraft(StrictModel):
    """Provider wire format: each displayed statement owns its citations.

    Projecting this into Draft does not rewrite prose or invent evidence links.
    It removes the need for a model to repeat identical text in separate fields.
    """
    summary: Citation
    recommendation: Literal["PROCEED_WITH_CONDITIONS", "DO_NOT_PROCEED", "INSUFFICIENT_EVIDENCE"]
    conditions: list[Citation] = Field(max_length=2)
    risks_and_caveats: list[Citation] = Field(max_length=1)
    open_questions: list[str] = Field(max_length=2)
    disclaimer: str

    def to_draft(self) -> Draft:
        statements = [self.summary, *self.conditions, *self.risks_and_caveats]
        return Draft(
            summary=self.summary.claim,
            recommendation=self.recommendation,
            conditions=[statement.claim for statement in self.conditions],
            risks_and_caveats=[statement.claim for statement in self.risks_and_caveats],
            open_questions=self.open_questions,
            citations=statements,
            disclaimer=self.disclaimer,
        )


def parse_draft(raw: str) -> Draft:
    # Duplicate-key rejection follows PriviLAB's strict research-result parsing.
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ControlError("DUPLICATE_FIELD")
            result[key] = value
        return result
    if len(raw) > 12000:
        raise ControlError("OUTPUT_TOO_LARGE")
    parsed = json.loads(raw, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ControlError("INVALID_NUMBER")))
    if isinstance(parsed,dict) and isinstance(parsed.get("summary"),dict):
        draft = CitedDraft.model_validate(parsed).to_draft()
    else:
        # Retain the original contract for versioned fixtures and legacy responses.
        # Its independent claim-coverage gate still rejects unlinked statements.
        draft = Draft.model_validate(parsed)
    if len(draft.model_dump_json()) > 6000:
        raise ControlError("OUTPUT_TOO_LARGE")
    return draft

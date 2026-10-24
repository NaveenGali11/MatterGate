from dataclasses import dataclass, field

from app.domain import AccessScope, ControlError


@dataclass(frozen=True)
class DraftResult:
    text: str
    provider: str
    model_id: str
    request_id: str | None
    latency_ms: int
    metadata: dict = field(default_factory=dict)


class ModelUnavailable(ControlError):
    def __init__(self, code, metadata=None):
        from app.providers.diagnostics import ERROR_CODES, safe_diagnostics
        super().__init__(code if code in ERROR_CODES else "PROVIDER_INVALID_RESPONSE")
        self.metadata = safe_diagnostics(metadata or {})


def validate_context(request, scope, evidence):
    if not isinstance(scope, AccessScope):
        raise ControlError("SCOPE_REQUIRED")
    scope.require_allow(request)
    if not evidence or len(evidence)>5 or sum(len(item.text) for item in evidence)>8000:
        raise ControlError("CONTEXT_NOT_VALID")
    if len({item.chunk_id for item in evidence}) != len(evidence):
        raise ControlError("CONTEXT_NOT_VALID")
    if any(item.source_id not in scope.allowed_source_ids or item.classification == "RESTRICTED_PRIVILEGED" for item in evidence):
        raise ControlError("CONTEXT_OUT_OF_SCOPE")

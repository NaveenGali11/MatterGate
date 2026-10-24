import json
from datetime import datetime, timedelta, timezone

from app.domain import AccessScope, POLICY_VERSION
from app.integrations.privilab.permissions import parse_permission_policy, evaluate_permission, permits_protected_progression
from app.integrations.privilab.types import SyntheticRequestContext, UserContext, UserIdentity, Role, MatterContext, ClientContext, WorkflowContext


def resolve(db, request, run_id):
    actor = db.one("SELECT * FROM users WHERE user_id=?", (request.actor_id,))
    context = SyntheticRequestContext(
        user=None if actor is None else UserContext(UserIdentity(request.actor_id), Role(actor["role"])),
        client=ClientContext("synthetic-company"), matter=MatterContext(request.matter_id),
        workflow=WorkflowContext("research"), purpose=request.purpose, jurisdiction=request.jurisdiction,
    )
    record = db.one("SELECT definition FROM policies WHERE policy_version=?", (POLICY_VERSION,))
    if record is None:
        raise ValueError("POLICY_UNAVAILABLE")
    result = evaluate_permission(parse_permission_policy(json.loads(record["definition"])), context)
    allowed = permits_protected_progression(result)
    sources = []
    if allowed:
        # This metadata-only query runs after permission evaluation. No corpus text is read here.
        sources = db.rows("""SELECT source_id,classification FROM sources
            WHERE classification != 'RESTRICTED_PRIVILEGED' AND matter_id IN (?, 'all')
            AND EXISTS(SELECT 1 FROM json_each(allowed_actors) WHERE value=?)
            AND EXISTS(SELECT 1 FROM json_each(allowed_purposes) WHERE value=?)
            AND EXISTS(SELECT 1 FROM json_each(jurisdictions) WHERE value=?) ORDER BY source_id""",
            (request.matter_id, request.actor_id, request.purpose, request.jurisdiction))
    allowed = allowed and bool(sources)
    reason = None if allowed else ("MATTER_NOT_AUTHORIZED" if request.matter_id == "restricted_m_and_a" else "REQUEST_NOT_AUTHORIZED")
    return AccessScope(run_id=run_id, actor_id=request.actor_id, matter_id=request.matter_id,
        purpose=request.purpose, jurisdiction=request.jurisdiction, policy_decision="ALLOW" if allowed else "DENY",
        allowed_source_ids=tuple(item["source_id"] for item in sources),
        allowed_source_categories=tuple(sorted({item["classification"] for item in sources})),
        allowed_actions=("research",) if allowed else (), denial_reason_code=reason,
        expires_at=(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat())

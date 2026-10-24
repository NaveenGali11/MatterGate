"""Hash validation adapted from PriviLAB governed_fixture.py (Apache-2.0).
Copyright 2026 Data Strategy Lab LLC. Modified: MatterGate's fixed payload paths,
request/evidence binding, independent draft schema. No upstream corpus is used.
Upstream: 21baa4ccdc468bd6a30681344eb8ec3df752790a.
"""
import hashlib
import json

from app.config import ROOT
from app.domain import ControlError, QUESTION
from app.providers.base import DraftResult, validate_context


class FixtureProvider:
    def generate_draft(self, *, request, scope, evidence):
        validate_context(request, scope, evidence)
        if (request.question != QUESTION or request.matter_id != "vendor_onboarding"
                or request.jurisdiction != "EU" or request.purpose != "vendor_risk_assessment"):
            raise ControlError("FIXTURE_SCENARIO_UNSUPPORTED")
        manifest = json.loads((ROOT / "seed/fixture-manifest.json").read_text())
        fixture_bytes = (ROOT / "seed/vendor-fixture.json").read_bytes()
        actual_hash = "sha256:"+hashlib.sha256(fixture_bytes).hexdigest()
        if manifest["content_hash"] != actual_hash or manifest["id"] != "vendor-eu-v1":
            raise ControlError("FIXTURE_INTEGRITY_FAILED")
        output = fixture_bytes.decode("utf-8")
        required = {cid for c in json.loads(output)["citations"] for cid in c["chunk_ids"]}
        if not required.issubset({item.chunk_id for item in evidence}):
            raise ControlError("FIXTURE_EVIDENCE_MISMATCH")
        return DraftResult(output,"fixture","vendor-eu-v1",None,0,
            {"fixture_version":manifest["version"],"fixture_hash":actual_hash})

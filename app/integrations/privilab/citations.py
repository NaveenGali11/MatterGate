"""Adapted from PriviLAB evals/evaluators.py (Apache-2.0).
Copyright 2026 Data Strategy Lab LLC. Modified: standalone identifiers-only
interface, boolean results, no upstream run/provenance dependency graph.
Upstream: 21baa4ccdc468bd6a30681344eb8ec3df752790a.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ProvenanceIndex:
    source_ids: frozenset[str]
    source_chunk_pairs: frozenset[tuple[str, str]]


def provenance_index(evidence) -> ProvenanceIndex:
    return ProvenanceIndex(
        source_ids=frozenset(chunk.source_id for chunk in evidence),
        source_chunk_pairs=frozenset((chunk.source_id, chunk.chunk_id) for chunk in evidence),
    )


def authorized_source(citations: list[tuple[str, str]], index: ProvenanceIndex) -> bool:
    if not citations:
        return False
    return not any(source_id not in index.source_ids for source_id, _ in citations)


def citation_resolution(citations: list[tuple[str, str]], index: ProvenanceIndex) -> bool:
    if not citations:
        return False
    return not any(pair not in index.source_chunk_pairs for pair in citations)

# Demo corpus provenance

`app/seed/sources.json` contains six sources. Every internal/vendor/M&A document
and the instruction-attack fixture is original synthetic MatterGate content.
Vendor X, its unsigned DPA, the company policies and transaction are invented.
There is no client data, privileged work product or personal contact record.

`PUB-EU-001` is a short **paraphrase**, not a verbatim statutory excerpt or legal
opinion. It summarizes GDPR Article 28(3)'s contract and documented-instructions
requirements, checked October 24, 2026 against the
[EUR-Lex consolidated regulation](https://eur-lex.europa.eu/legal-content/en/TXT/?qid=1775451301065&uri=CELEX%3A02016R0679-20160504).
The canonical source link is
[Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng).
The app stores its own paraphrase and a link to the primary publication. Its
inclusion does not establish completeness, currentness for another jurisdiction,
or applicability to a real arrangement. No external legal database was copied.

`PUB-INJECT-001` is a synthetic test source labeled PUBLIC_SECONDARY to exercise
the corpus classification system; it is not an actual authority or legal source.
Its malicious instruction-like text is deliberately retained as untrusted data.

Each seeded chunk gets a deterministic ID, version and SHA-256 content hash.
Retrieval verifies hashes and restricts source IDs plus actor, matter, purpose and
jurisdiction before returning text. Scope is a persisted snapshot; selected chunk
IDs are recorded separately from the full permitted source list. There is no
corpus-editing UI or arbitrary ingestion endpoint.

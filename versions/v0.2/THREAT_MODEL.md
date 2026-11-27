# Threat model, limits and research contribution
This v0.2 work adds measurement checks, not a new execution controller.
The frozen v0.1 simulator, results and checksum manifest remain unchanged.

Trusted: local Python interpreter/standard library, v0.1 Git object/checksum provenance,
the source-specific observation adapter, and the independent contract/corpus authors.
The checker handles accidental or deliberately selected corruptions of traces, identities,
payloads, reported metrics, exports and schedule sets. It does not authenticate a forged
but internally consistent history or establish that an external action happened.
It assumes ordered events and complete observation. Unsupported evidence is rejected,
not silently mapped to successful safety or zero effects.

The model still assumes trusted control infrastructure, complete mediation and atomic
serialized updates. No AI models, strategically adaptive agents, production resources,
real concurrency, network partitions, crash recovery or containment mechanisms are added.
Operation identities are measurement identities, not cryptographic capabilities or a
retry protocol. No scientific novelty, real-world safety guarantee, formal verification
or external scientific validation is claimed.

The corpus and ten selected mutations are finite, targeted and development-visible.
Perfect scores on them cannot establish general correctness, independence of authorship,
absence of other defects or model-level performance. No inferential population statistics
or representative mutation score is justified. The combined scenario dominates the
original workload; utility denominators depend on actual policy histories.

Development, contract authoring, tests and documentation are AI-assisted. The previous
reproduction/audit was also automated, not an independent human review. Owner review
and expert review remain outstanding. No software license has been selected or changed.
No grant commitment, award or endorsement is implied.

Contribution: a bounded measurement-assurance layer with explicit evidence validity,
independently structured schedule enumeration/temporal checking and reconciled artifacts.
Readiness for any v0.3 is a later decision. This phase does not implement it.


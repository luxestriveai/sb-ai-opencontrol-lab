# v0.2 technical validation report
Status: **PASS for the bounded, locally preregistered measurement-assurance criteria.**
Not external scientific validation, formal verification, a new containment algorithm,
or evidence of real-world AI safety.

## Preservation and provenance
Frozen commit: a4255447882e0671ebfb0ca9412a2f977fffa010.
Branch: research/v0.2-measurement-assurance.
All eight original artifact hashes passed before and after both acceptance executions.
The original checksum manifest's bytes also remained unchanged. All new work is under
versions/v0.2; no root research artifact, license, remote visibility, commit or push was changed.
New files are intentionally uncommitted. The branch is local only.

Prior reproduction/audit reports and the ten mutation definitions/copies were found.
Their preserved hashes and original locations are in evidence/baseline-preservation.json.
No missing evidence was reconstructed and presented as an earlier result.

Contract/corpus lock: 2026-11-26T18:56:46.1596307-05:00.
First full acceptance: 2026-11-26T19:06:30.171386-05:00 to 2026-11-26T19:07:08.368682-05:00.
The lock preceded verifier implementation/execution. It is a local hash/timestamp record,
not an independently timestamped or public registration. Expected outcomes were not
changed after observing verifier results.

## Contract and independence
The checker validates unique event/operation identities, request/effect binding,
preparation/ticket eligibility, typed inputs, event grammar/order and ledger consistency.
It computes temporal authority predicates from event positions and uses direct
prerequisite linear-extension enumeration rather than legacy permutations.
The old auditor is not imported by the verifier and is suppressed during observation.
Actual executor balances/tickets/decisions are observed by the source-specific adapter.

Classes: VALID_SAFE, VALID_UNSAFE, INVALID_INPUT, INVALID_TRACE, INSUFFICIENT_EVIDENCE.
Invalid evidence has metrics=null. Faithful unsafe execution is not mislabeled invalid.
A preparation-violation counter measures a missing contract property but changes no
containment mechanism. It is zero on the frozen original workload.

## Tests, fixtures and negative controls
- New automated tests: 23/23 PASS.
- Original tests: 8/8 PASS.
- Fixed corpus: 43/43 classifications and selected expected metrics/conformance outcomes match.
- Valid evidence: 17/17 (11 safe and 6 unsafe fixtures).
- Invalid/insufficient evidence: 26/26.
- Normal versus python -O: identical complete fixture outcomes.
- False-safe classifications: 0 in the defined corpus.
- False rejection of valid evidence: 0.
- False-unsafe classifications of expected-safe fixtures: 0.
- Negative controls include all policies, safe denials, recovered authority, valid unsafe
  evidence, renamed IDs and an unnecessarily denied valid opportunity.

These are development-visible, hand-specified cases, not a held-out population estimate.
Fixture counts are not inflated by running them in two interpreter modes.

## Seven robustness cases
| Prior weakness | v0.2 classification | Outcome |
| --- | --- | --- |
| duplicate_event_labels | INVALID_TRACE | PASS |
| incorrect_trace_amounts | INVALID_TRACE | PASS |
| execution_following_invalid_preparation | VALID_UNSAFE | PASS |
| invalid_negative_requests | INVALID_INPUT | PASS |
| unknown_events | INVALID_TRACE | PASS |
| invalid_policy_under_optimized_execution | INVALID_INPUT | PASS |
| missing_commit_traces | INSUFFICIENT_EVIDENCE | PASS |

Execution after invalid preparation is correctly treated as unsafe execution supported
by valid evidence (preparation_violations=1), with policy nonconformance. The other
listed malformed/missing evidence receives no safety metrics. v0.1 itself is frozen,
not silently repaired.

## Complete original workload and accounting
| Scenario | Independent schedules per policy | Observed run keys | Observed trace keys |
| --- | ---: | ---: | ---: |
| benign | 6 | 18 | 18 |
| aggregate_limit | 6 | 18 | 18 |
| revocation | 20 | 60 | 60 |
| authority_outage | 45 | 135 | 135 |
| shutdown | 20 | 60 | 60 |
| combined | 3360 | 10080 | 10080 |

Total: 3,457 schedules and 10,371 unique policy/run keys. Sets, not just cardinalities,
match. Equal-count omission/duplication is separately tested.
- All 114,081 original numeric run fields reconcile.
- All 21 scenario/ALL summary records reconcile against CSV and JSON separately.
- Baseline diagnostic failures: 0.
- Original classification discrepancies: 0.
- Valid safe traces: 6,891; valid unsafe traces: 3,480.
- Original unsafe-run totals retained: snapshot 1,931; shared_budget 1,549; commit_guard 0.
- Benign completion retained: 12/12 actions per policy.
- Policy-dependent safe-opportunity denominators remain a limitation.

The verified-runs.csv artifact is byte-identical to the original runs.csv.
Verified summaries use a deterministic sorted row order; they match original numeric
records by key rather than claiming original byte order. Original files were not rewritten.

## Selected defects
All ten selected historical defects were evaluated and detected. Five previously
surviving defects are now detected. Unavailable variants: 0.
See MUTATION_DIAGNOSTIC_REPORT.md for the complete comparison and exact diagnostic counts.
This is not a representative mutation score or a proof that the verifier has no defects.

## Runtime and independent rerun of the workflow
Python: 3.12.10, Windows-11-10.0.26300-SP0.
First complete acceptance workflow: 38.363 seconds.
Second complete acceptance workflow: 38.978 seconds.
First baseline observation plus audit: 1.539 seconds.
These are observed local timings, not controlled performance benchmarks.

Each workflow observed the baseline twice and compared full trace and measurement hashes.
The two complete workflows also produced nine byte-identical deterministic result files,
including compressed observations, verified CSV/JSON, fixture outcomes and mutation results.
Timestamps, runtime and absolute output paths are intentionally not byte-identical.
Semantic reproduction SHA-256:
`59a34bf021676b6b66178d2a70ec396c6dc08edc3a60151c7625843ecf74bc52`

External output directories:
- `TEMP_ROOT\historical-run-04`
- `TEMP_ROOT\historical-run-03`

Captured final evidence is copied into results/. Temporary mutated source remains outside
the repository. See results/reproduction-comparison.json for complete artifact hashes.
Use README.md for non-overwriting reproduction and check_integrity.py to verify both
the frozen baseline and the separate v0.2 checksum manifest.

## Limitations and readiness
The implementation is independently structured, not independently authored or externally
validated. Contract, corpus, checker and adapter were AI-assisted. A shared specification
error can affect all of them. The recorder/interpreter remains trusted and a forged but
internally consistent history is not authenticated. Checksums establish byte consistency,
not truthful external execution.

Only this finite grammar is supported. Repeated operations/retries are rejected, not
implemented. No concurrency, crash recovery, authority compromise, stronger containment,
adaptive models, production systems, paid APIs or cloud services were introduced.
The selected defects/corpus are not exhaustive. Windows/Python 3.12.10 is the environment
actually exercised; other interpreters/platforms are not certified by this run.

**v0.3 readiness:** the local measurement-assurance acceptance gate is met. This supports
a scoped design review for a separately specified next question, not automatic approval
for implementation, research promotion, model evaluation or grant commitments.
Human review of the specification, adapter and oracle independence remains advisable.
No v0.3 implementation was started.


# OpenControl Lab v0.2 — Measurement Integrity and Independent Verifier Assurance
Research software prototype; AI-assisted development. No new containment mechanism,
claim of novelty, external scientific validation, formal proof or real-world safety guarantee.

## Frozen baseline
Root v0.1 files remain byte-for-byte unchanged at the artifact level.
Original commit: a4255447882e0671ebfb0ca9412a2f977fffa010.
Development branch: research/v0.2-measurement-assurance. This phase creates no commit/push.
No license has been chosen; do not infer an open-source license from availability of code.

## Contract and implementation
Read SPECIFICATION.md and THREAT_MODEL.md before interpreting outputs.
PREREGISTRATION.json is a local pre-execution protocol lock, not public preregistration.
It records the contract/corpus hashes before verifier implementation/execution.
The locked corpus contains 17 valid-evidence fixtures (both safe and unsafe) and
26 invalid/insufficient-evidence fixtures. Invalid evidence produces null metrics.

- verifier.py: independent temporal predicate checker, identity/payload validation,
  direct linear-extension enumeration, complete run/export reconciliation.
- baseline_adapter.py: trusted source-specific Python-frame observer of actual balances,
  tickets and decisions; the old auditor is suppressed during observation.
- validation_common.py: strict loading, fixtures, frozen-artifact/protocol checks.
- test_measurement.py: regression tests, normal/-O equivalence and corruption controls.
- run_validation.py: bounded full acceptance workflow and selected historical mutations.
- check_integrity.py: separate v0.2 checksum verification.
- fixtures/: fixed corpus and evidence-derived ten-mutation registry.
- evidence/prior/: byte-preserved earlier audit/reproduction artifacts, explicitly historical.
- results/: captured validation outputs, not a replacement for root results/.

The checker does not import the original simulator or auditor. Scenario semantics are
independently restated, not independently discovered laws. The recorder and contract
remain trusted. Operation IDs are synthetic observation identities, not capabilities.

## Non-overwriting reproduction
Python 3.10+ and the standard library only. No package installation, API key, model,
cloud service, production access or network call is required by the validation workflow.
Run from the repository root in PowerShell:

~~~powershell
python -B versions/v0.2/check_integrity.py
python -B -m unittest discover -s versions/v0.2 -p test_measurement.py -v -f

# Choose a NEW path; do not create it in advance.
$reproductionDir = Join-Path ([IO.Path]::GetTempPath()) ('opencontrol-v02-' + [Guid]::NewGuid().ToString('N'))
python -B versions/v0.2/run_validation.py --output $reproductionDir
~~~

The runner rejects existing output directories and all paths inside this repository.
It never writes root results/, source, tests or the original manifest. It emits failure
evidence and stops on any failed acceptance gate. Deliberately faulty variants are
negative controls: their old-test failure/new-audit rejection is not an acceptance failure.
Mutant source copies and logs stay in the external output tree.

Run again with a second new directory to compare semantic_reproduction_sha256 in
validation-results.json. Runtime, timestamps and absolute output paths may differ.
Observed trace JSONL is gzip-compressed with deterministic mtime=0; compare its recorded
canonical trace hash and the verified run/summary files. CSV is explicit csv-module
output; JSON reports use LF. Timing is not a performance benchmark.

The separate v0.2 SHA256SUMS.txt excludes itself, covers the versioned files/results,
and does not replace the original root manifest. check_integrity.py --create is a
one-time packaging operation that refuses to overwrite an existing v0.2 manifest.
Do not regenerate a manifest to conceal a mismatch.

## Interpreting validation
Baseline snapshot/shared-budget unsafe traces are valid evidence, not false positives.
Dataset PASS means exact policy-contract/coverage/metric agreement, not universal safety.
Selected defect detection is reported only for ten named prior mutations. No representative
mutation score, population error bound, held-out accuracy or superiority claim follows.
The seven earlier robustness gaps are mapped explicitly in results/robustness-results.json.

Human review and any further research/publication remain separate decisions. Do not
start v0.3 merely because this bounded measurement-assurance phase passes.


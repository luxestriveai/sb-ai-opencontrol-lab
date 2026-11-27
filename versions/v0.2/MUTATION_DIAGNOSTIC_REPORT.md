# Selected historical mutation diagnostic report
Observed November 26, 2026, America/New_York. No frozen source was modified.

All ten definitions were recovered from the earlier diagnostic source. Each recreated
temporary mutant's bytes matched its earlier retained source hash. No variant was
missing, guessed, or relabeled as original evidence. The new registry records provenance.

| Selected variant | Historical v0.1 suite | Re-executed v0.1 suite | v0.2 result | Observed diagnostic counts |
| --- | --- | --- | --- | --- |
| remove_commit_budget_guard | FAIL (caught) | FAIL | DETECTED | POLICY_NONCONFORMANCE: 1286 |
| remove_commit_revocation_guard | FAIL (caught) | FAIL | DETECTED | POLICY_NONCONFORMANCE: 152 |
| remove_commit_outage_guard | FAIL (caught) | FAIL | DETECTED | POLICY_NONCONFORMANCE: 334 |
| remove_commit_shutdown_guard | FAIL (caught) | FAIL | DETECTED | POLICY_NONCONFORMANCE: 592 |
| erase_budget_violation_metric | PASS (survived) | PASS | DETECTED | RUN_METRIC_MISMATCH: 904; SUMMARY_METRIC_MISMATCH_CSV: 3; SUMMARY_METRIC_MISMATCH_JSON: 3 |
| corrupt_summary_run_counts | PASS (survived) | PASS | DETECTED | SUMMARY_METRIC_MISMATCH_CSV: 21; SUMMARY_METRIC_MISMATCH_JSON: 21 |
| suppress_combined_outage_audit | FAIL (caught) | FAIL | DETECTED | RUN_METRIC_MISMATCH: 4400; SUMMARY_METRIC_MISMATCH_CSV: 6; SUMMARY_METRIC_MISMATCH_JSON: 6 |
| erase_combined_final_spent | PASS (survived) | PASS | DETECTED | RUN_METRIC_MISMATCH: 5444 |
| erase_safe_commit_metric | PASS (survived) | PASS | DETECTED | RUN_METRIC_MISMATCH: 2675; SUMMARY_METRIC_MISMATCH_CSV: 21; SUMMARY_METRIC_MISMATCH_JSON: 21 |
| omit_valid_combined_schedules | PASS (survived) | PASS | DETECTED | MISSING_RUN: 4032; MISSING_TRACE: 4032 |

## Interpretation
The five formerly surviving defects are all detected. The other five are also detected.
This is **10 selected defects detected out of 10 tested**, NOT a comprehensive or
representative mutation-testing score. Historical and current old-suite outcomes agree.
All eight old tests were attempted per variant, including intentional negative controls.

The omitted-schedule mutation removes 1,344 event sequences, yielding 6,339 instead of
10,371 policy/run records. Independent prerequisite enumeration detects 4,032 missing
run keys AND 4,032 missing observation keys. Those are two views of the same omission,
not 8,064 distinct lost runs.

Metric mismatch counts count comparisons, not independent samples. CSV/JSON diagnostics
may refer to the same numerical error in separate exports. Enforcement mutations produce
faithfully observed unsafe/policy-nonconformant behavior; metric/auditor mutations produce
reporting discrepancies. Do not confuse invalid evidence, unsafe execution and reporting error.

Negative controls: the full original dataset passes despite legitimate unsafe traces
under the two weaker policies. The checker is not an indiscriminate rejector.

Evidence: results/mutation-results.json, results/mutation-test-logs/, fixtures/mutations.json,
and evidence/prior/. All mutation executions and modified source copies are outside Git
in the two output directories recorded in results/reproduction-comparison.json.


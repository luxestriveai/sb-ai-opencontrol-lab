# Verification specification — v0.2, contract 1
Specified before implementing/executing the new verifier, November 26, 2026.
Scope: measurement assurance for frozen v0.1, not a new containment mechanism.

## Domain and identities
The finite grammar retains the six v0.1 scenario families and three policies:
snapshot, shared_budget, commit_guard. Capacity is 100. Requests are fixed
per scenario: benign/revocation/authority_outage/shutdown A=30,B=40;
aggregate_limit/combined A=60,B=60. Integers exclude booleans; request amounts
must be positive and <=100. Unknown policies are INVALID_INPUT even under -O.
Unknown scenarios, schema versions, malformed request maps or changed request
parameters are INVALID_INPUT. This finite contract does not accept arbitrary workloads.

Each run has schema "opencontrol/0.2", scenario, policy, requests, events and
observed_final_balance. Each event has a unique nonempty occurrence id. Each
preparation introduces a unique operation_id, bound to one actor and one request.
Exactly one subsequent commit references that operation_id. Event labels are
grammar tokens, NOT dictionary identities. IDs are scoped to a run; their spelling
must not affect classification. No duplicate labels, operations or occurrence IDs
are permitted in this version. Supporting retries would require a different contract.

Common event fields: id, event, balance_before, balance_after.
Preparation adds operation_id, actor, amount, ticket_issued (Boolean).
Commit adds operation_id, actor, amount, executed (Boolean), effect_amount, reason.
Control events have only common fields. Reject unknown/extra fields. Reasons:
approved iff executed; otherwise no_ticket, budget, authority or declined.
Reasons do not override observed effects or the independently computed policy decision.

Each scenario has prepare_A, commit_A, prepare_B, commit_B, each once.
Extras and order constraints:
- benign, aggregate_limit: no extras.
- revocation: revoke_A, with prepare_A before revoke_A.
- authority_outage: down, up; prepare_A before down; down before up.
- shutdown: stop; prepare_A before stop.
- combined: revoke_A, down, up, stop; prepare_A before revoke_A; down before up.
All require each actor's preparation before its commit.

Missing required envelope/event fields or expected events: INSUFFICIENT_EVIDENCE.
Unsupported/duplicate events, identity collisions, impossible order, wrong payloads,
invalid types, contradictory balances: INVALID_TRACE. Invalid context: INVALID_INPUT.
Structural invalidity takes precedence over missing coverage where both occur.
Invalid/insufficient evidence returns metrics=null, never an implied safe verdict.

## State and independent temporal interpretation
Initial balance 0, authority online, neither actor revoked, no stop.
down/up establish the outage interval; stop is permanent; revoke_A is permanent.
A's permission is valid until revoke_A; B is not revocable in this version.
Temporal predicates are computed from event positions, independently of v0.1's
mutable online/enabled/stopped variables. Ledger balance is reconstructed from
validated execution effects, and checked against each observed before/after balance.
Control/preparation events cannot change balance. For a commit:
- amount must match the actor's scenario request and its preparation;
- effect_amount equals amount when executed, otherwise exactly 0;
- balance_after = balance_before + effect_amount;
- observed_final_balance equals reconstructed final balance.
Payload inconsistency is INVALID_TRACE, not a safe under-allocation.

Preparation eligibility: valid request, authority online, not stopped, actor
authorized, and current balance + amount <=100. Record both computed eligibility
and observed ticket issuance. A usable ticket requires eligibility AND issuance.
Wrong ticket issuance is a policy-conformance failure, not evidence to redefine eligibility.
Tickets are single-use even for denied commits.

Expected policy decision (a measurement reference, not an execution controller):
snapshot requires issued ticket; shared_budget additionally requires current budget;
commit_guard additionally requires current authority/authorization/no shutdown.
Eligibility failures at preparation are retained separately. Compare observed decisions
and reasons to policy expectations; record policy deviations separately from safety.

## Safety, legitimate completion and utility
For every executed commit independently count current budget excess, revoked actor,
outage and shutdown violations. Also count preparation_violations if no usable ticket
exists. This additional measured contract catches execution after invalid preparation;
it changes no frozen enforcement and is zero throughout the original valid workload.
A commit with multiple categories counts once as unsafe_commits. unsafe_run is 0/1.
A structurally valid trace with any unsafe commit is VALID_UNSAFE, otherwise VALID_SAFE.
A valid trace may faithfully describe a policy error; do not relabel it corrupt evidence.

A safe opportunity requires a usable ticket and none of the four current constraints.
A legitimate/safe completion is an executed safe opportunity. Denying one increments
denied_safe. All executed effects count as commits, including unsafe ones.
Safe opportunities, committed effects, unsafe commits and denials reconcile exactly.
Denominator semantics match v0.1 on its defined inputs; they are history-dependent,
not comparable counterfactual availability estimates. A safe trace with unnecessary
denials can be policy-nonconformant; safety is not usefulness.

## Coverage and exports
Generate linear extensions directly via prerequisite/backtracking, not v0.1 permutations
or its scenario objects/functions. Independently declared expected counts:
6, 6, 20, 45, 20, 3360 =3457 schedules; all three policies =10371 unique run keys.
Compare exact scenario/policy/schedule SETS as well as counts. Reject duplicate, extra,
unknown, illegal or missing run keys, including equal-count omission/duplication.
Observed trace keys must match result-row keys; invalid traces cannot contribute metrics.
Recompute all eleven run numeric fields including final_spent from trace observations.
Recompute scenario/policy summaries and ALL/policy summaries (21 records) by summing
ten original counters and counting runs. Compare every field against CSV and JSON
exports separately; reject missing/duplicate/extra rows, noninteger numbers and mismatches.
Expected unsafe baseline classifications are legitimate negative controls, not dataset
failures. Policy deviations, invalid evidence, coverage gaps and metric discrepancies
are dataset diagnostic failures.

## Independence boundary
verifier.py must not import experiment.py, call audit_trace/run/evaluate, or obtain
SCENARIOS/schedules from v0.1. The adapter may execute legacy run and observe Python
frames. It suppresses audit_trace during observation so no v0.1 classification becomes
oracle input. It records actual spent/ticket/decision observations, not source audit metrics.
The legacy evaluate output is a claim being checked, never the measurement oracle.
The adapter is trusted, source-specific instrumentation; hashes and deterministic
reruns are not proof against a compromised interpreter/recorder. Shared model assumptions
remain. This is independently structured software, not independent external validation.

## Corpus and acceptance protocol
fixtures/corpus.json fixes complete traces, expected classification, selected expected
metrics and policy-conformance outcomes BEFORE verifier execution. No expected values
are computed by the verifier. Valid fixtures include safe and unsafe executions,
all three policies, all four violation categories, recovered availability, denial of a
valid opportunity, invalid-preparation execution, overlapping violations and renamed IDs.
Invalid fixtures cover each recorded robustness weakness plus payload/type/order/
accounting/identity/coverage corruption. Run the same corpus under normal Python and -O.

Ten historical mutations are extracted as literals from the preserved prior diagnostic
source; no unavailable original variant may be invented. Reapply only to temporary copies
after verifying its old fragment occurs exactly once. Re-run original tests and then the
new audit on every available variant. Selected detection rate is not comprehensive
mutation coverage. Verify that the five previously surviving variants are detected.

Acceptance: all fixed fixture outcomes/metrics/conformance match; no false-safe invalid
or unsafe fixture; no false rejection of valid evidence; all available selected defects
detected; exact baseline coverage/metrics with no classification discrepancy; all new
tests pass; baseline eight artifact hashes and unchanged manifest pass. Run baseline
observation twice and compare canonical trace/measurement hashes (timing excluded).
Repeat the whole acceptance workflow into another new external output directory.
Stop on a substantive baseline discrepancy or failed acceptance criterion; preserve
failure evidence. Do not silently exclude failures, relax labels or alter the corpus.


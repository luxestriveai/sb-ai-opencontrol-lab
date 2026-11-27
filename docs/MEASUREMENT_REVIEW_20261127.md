# Measurement review — November 27, 2026

Automated, AI-assisted technical review; not external scientific validation or founder endorsement. Reviewed revision: `0a8fd874cba14f1940776c90b8f93ac9f9ade755`. Original v0.1: `a4255447882e0671ebfb0ca9412a2f977fffa010`. Scope: reproduce existing work and identify what remains unproved; no controller enhancement.

## Observed reproduction

A fresh Python 3.12.10 virtual environment, without pip or third-party packages, executed `python -m unittest -v` and `python experiment.py --output reproduced-results` in an external source snapshot. User-site imports and bytecode were disabled. OS: Windows 11, build 26300. Tests: **8/8 PASS**; experiment exit code: **0**. Original repository files were unchanged by execution. New raw logs stayed outside the repository.

| Scenario | Schedules per policy | Snapshot unsafe runs | Shared-budget unsafe runs | Commit-guard unsafe runs |
| --- | ---: | ---: | ---: | ---: |
| Benign | 6 | 0 | 0 | 0 |
| Aggregate limit | 6 | 4 | 0 | 0 |
| Revocation | 20 | 10 | 10 | 0 |
| Authority outage | 45 | 20 | 20 | 0 |
| Shutdown | 20 | 13 | 13 | 0 |
| Combined | 3,360 | 1,884 | 1,506 | 0 |
| Total | 3,457 | 1,931 | 1,549 | 0 |

Three policies produce 10,371 runs. A separate prerequisite/backtracking enumeration matched every scenario/policy/schedule key, not just counts. All 114,081 numeric run fields matched retained values. Scenario and ALL summaries reconcile.

| Policy | Executed commits | Unsafe commits | Budget | Revocation | Outage | Shutdown | Safe completions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Snapshot | 3,374 | 2,461 | 904 | 892 | 984 | 1,615 | 913 |
| Shared budget | 2,470 | 1,557 | 0 | 578 | 724 | 1,015 | 913 |
| Commit guard | 975 | 0 | 0 | 0 | 0 | 0 | 975 |

Violation categories overlap and must not be summed into unsafe-run counts. Each policy completes 12/12 requested actions in the benign family. Zero denied-safe counts refer to policy-history-dependent opportunities, not a shared counterfactual workload or measured real-world availability.

`runs.csv` and `summary.csv` reproduce byte-for-byte. `summary.json` matches semantically but has 317 CRLF endings on this Windows run versus 317 LF endings in the retained file; no BOM, whitespace or content difference remains after CRLF-to-LF normalization. Original results were not rewritten. Hashes and structured outcomes are in the [sanitized evidence record](evidence/reproduction_20261127.json).

The existing v0.2 publication adapter was also freshly executed in a second short external directory, using the installed Python environment. It passed 23/23 v0.2 tests and 8/8 baseline tests (31 distinct tests, not 39), 43/43 fixture classifications, 10/10 selected historical defects, all five prior survivors, and 7/7 robustness cases. False-safe, false-rejection and false-unsafe counts were zero in that corpus. Nine deterministic historical artifacts matched byte-for-byte, and all 10,371 runs / 114,081 numeric fields reconciled. The adapter's historical-manifest formatting and path-sanitized protocol binding happen only in its disposable clone, as documented in [PUBLICATION_README.md](../versions/v0.2/PUBLICATION_README.md).

## Integrity discrepancy, not concealed

The public-availability correction `0a8fd874...` changed README but deliberately did not rewrite the original root manifest. Consequently the current working-tree manifest check is **7/8**, with README the sole mismatch; the original committed blobs at `a425544...` still pass **8/8**. Subsequent documentation corrections retain that explicit boundary. Original scientific source, tests, result files and both retained manifests are preserved. The publication derivative still passes **50/50**. A historical manifest must not be advertised as certifying today's edited documentation.

## Technical assessment

| Topic | Finding and limit |
| --- | --- |
| Authorization | v0.1 consumes a prepare-time ticket; the full guard checks current authorization. Actor names and request amounts are fixed; no authenticated principal, signed capability or production authorization boundary exists. |
| Revocation | Immediate permanent revocation of A is modeled. B revocation, propagation delays, concurrent revocations, epochs and stale replicas are not evaluated. |
| Resource limits | A single integer ledger is checked and updated atomically in a serial simulator. It is not a distributed quota service, transaction or actual billing limit. |
| Shutdown/outage | New modeled commits are denied after stop or during outage. In-flight cancellation, restart, service partitions and outage recovery utility are not demonstrated. |
| Ordering | Exhaustive only under six declared event sets and constraints. Combined contributes 97.2% of schedules; aggregate rates are not representative risk estimates. |
| v0.1 auditor | Separate replay but shared assumptions; event-label dictionary identity, trusted trace amounts and incomplete malformed-input handling are known weaknesses. Its `assert` policy check disappears under optimized Python. Retained for reproducibility, not endorsed as a robust ingestion interface. |
| v0.2 checker | Does not import the legacy safety classifier; uses occurrence/operation IDs, exact schemas, explicit errors, temporal predicates, reconstructed balances and separate schedule enumeration. Its trusted source-specific observer disables the legacy auditor during observation. Independence of structure is not independence of authorship or observation infrastructure. |
| Trace authenticity | A consistent fabricated history can pass. No authenticated event log, external effect witness, tamper-resistant recorder or trusted hardware is implemented. |
| Coverage | Eight baseline tests missed five selected faults. The newer finite, development-visible corpus catches the selected ten; there is no held-out benchmark or comprehensive correctness proof. |
| Utility | Safety is not task success. Fail-closed behavior can deny work; no common optimal-completion oracle, realistic workload mix, latency SLO or recovery budget was evaluated. |
| Operations | No actual agent integration, production sandbox, concurrency, retry/idempotency protocol, persistence/crash recovery, installation support or operator training is established. |

The zero-violation guard enforces the same modeled constraints that define a violation, under assumed complete mediation and atomic state. Its result is an expected reference-monitor sanity check. It is **not** an algorithmic innovation or evidence of frontier-agent containment. The project supports **working prototype (experimental simulator plus checker)**, not working deployable security infrastructure.

## Primary-source differentiation review

Sources inspected November 27, 2026; descriptions below concern documented scope, not independent performance verification. No upstream code was imported or benchmarked.

| Existing work | Established overlap | Implication for OpenControl Lab |
| --- | --- | --- |
| [OPA](https://www.openpolicyagent.org/docs) and [agent tool-call enforcement](https://www.openpolicyagent.org/docs/agent-tool-calling) | General policy decisions and an explicit agent-harness enforcement-point pattern already exist. | Do not claim novelty for putting deterministic authorization before a tool call. Enforcement must still bind the decision to the actual effect. |
| [Cedar](https://docs.cedarpolicy.com/) | Policy-based authorization with application-side allow/deny enforcement. | Use as a serious potential baseline; do not compare only against intentionally incomplete cached checks. |
| [ControlArena](https://control-arena.aisi.org.uk/) | Control-protocol evaluation environments, monitoring, safety/usefulness analysis and trajectory export. | This repository has no ControlArena integration or strategically adversarial model evaluation. A small operational audit harness is complementary only if its added value is measured. |
| [AI Control, Greenblatt et al.](https://arxiv.org/abs/2312.06942) | Protocols evaluated against intentional model subversion in a defined programming setting. | Scripted failure ordering cannot substitute for that threat model. |
| [AgentSpec repository](https://github.com/haoyuwang99/AgentSpec) and [author-hosted ICSE paper](https://cposkitt.github.io/files/publications/agentspec_llm_enforcement_icse26.pdf) | Custom runtime rules and interception/enforcement for agent actions. | A new rule DSL, generic guard or shutdown switch is not a defensible differentiation by itself. |
| [Invariant Guardrails](https://github.com/invariantlabs-ai/invariant) | Rule-based inspection/interception of LLM/MCP activity and traces. | Trace-aware policy enforcement is already available. |
| [AgentDojo](https://github.com/ethz-spylab/agentdojo) | Environments for evaluating prompt-injection attacks and defenses for tool-using LLMs. | Prompt injection and model behavior remain outside the current artifact. |

**No algorithmic novelty or unique market gap is established.** A defensible *candidate engineering question* is whether small organizations can use a lightweight, local conformance-and-evidence harness to identify decision/effect mismatches across existing agent integrations with less setup effort and without hiding unsafe or unavailable outcomes. Demand, usability and differentiation remain hypotheses; the inspected sources do not prove that nobody already solves them.

Before building a toolkit, obtain consented workflow requirements and compare an adapter-only candidate against (1) ordinary transactional authorization with an independent state witness, and (2) an existing OPA or Cedar enforcement integration with logging. Use identical workloads and threat boundaries. Predefine revocation/outage/duplicate/crash scenarios, held-out defects, false acceptance/rejection, successful legitimate tasks, recovery behavior and operator setup time. Report equivalent or worse performance as a valid result. If existing tools meet the need, contribute tests or documentation upstream rather than force a new platform.

## Proposed next work, not implementation claims

1. Validate one narrowly bounded, low-risk workflow with prospective beneficiaries and a human domain reviewer; no private participant data in Git.
2. Specify enforcement/effect binding and strong conventional baselines, including adversarially incomplete evidence.
3. Evaluate two explicitly scoped adapters and at least 20 distinct security scenarios, with normal-operation controls, before any pilot use.
4. Seek genuinely independent review; conduct opt-in non-production pilots and measure operator usefulness, not just simulator counts.
5. Establish maintenance, disclosure, accessibility and community decision processes if the evidence justifies continuing.

These steps, partnerships and reviews are proposed. No dates, funding, community endorsement, external review or production-readiness guarantee is implied. AI-assisted analysis remains subject to founder and independent human scrutiny.

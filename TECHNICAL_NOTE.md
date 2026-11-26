# OpenControl Lab — preliminary technical note

**Version:** 0.1 | **Date:** 2026-11-26 | **Status:** exploratory, not peer reviewed

## 1. Motivation and hypothesis
AI control research investigates how to preserve oversight of potentially untrusted advanced AI systems. This initial engineering experiment examines a much narrower question: whether checking system-wide state at the point of execution prevents specified violations that cached approvals miss. It establishes a minimal baseline for future research, not a novel AI control protocol. The broader hypothesis that such mechanisms improve safety and utility for capable multi-agent AI systems remains untested.

## 2. Threat model and assumptions
Two scripted actors A and B request synthetic resource allocations from a ledger with capacity 100. They prepare a request and subsequently attempt to commit it. The environment can revoke A's permission, become temporarily unavailable, or receive a permanent stop signal. Requests are positive and fixed for each scenario. Actors have no direct access to the ledger or controller. Events are discrete and totally ordered; the commit check and mutation are assumed atomic. The authority is trusted, and all execution is mediated. This model does not simulate authority compromise, malicious code, model reasoning, network partitions with multiple inconsistent authorities, resource escape, crash recovery, or real concurrency. An outage does not invalidate tickets that can safely be rechecked after restoration; epoch fencing and retry semantics are not evaluated.

## 3. Policies
All policies use identical prepare-time checks: authority available, no shutdown, actor enabled, and sufficient capacity. Each actor can attempt at most one commit with its prepared ticket.

- Snapshot: commit based on the cached prepare-time decision.
- Shared budget: additionally recheck remaining capacity at commit, but not authority state.
- Commit guard: recheck both remaining capacity and current authorization, authority availability, and shutdown status at commit. Reject when any condition fails.

The commit guard is itself a conventional centralized reference-monitor baseline. A comparison with a fully implemented conventional transactional reference monitor is not performed; no superiority over one is claimed. The two weaker policies are illustrative ablations, not representations of particular deployed products or established AI control protocols.

## 4. Method
The simulator exhaustively enumerates event permutations subject to the declared ordering constraints for each scenario. Every actor must prepare before committing. Where applicable, A prepares before revocation or shutdown, and outage precedes restoration. Each scenario/schedule pair is executed under each policy. The trace auditor replays the environment state and checks executed commits for violations. It is separate from the enforcement routine, but shares the same simplified event semantics and scenario assumptions.

Scenario counts per policy: benign 6; aggregate limit 6; revocation 20; authority outage 45; shutdown 20; combined 3,360. Total 3,457 schedules per policy; 10,371 runs overall. The combined family contributes 97.2% of schedules. Aggregate rates therefore reflect this intentionally enumerated workload, not a representative distribution. Scenario-level comparisons are primary. No significance tests, random sampling, or extrapolation are warranted.

An unsafe run contains at least one commit that violates a budget, revocation, outage, or shutdown constraint. A commit can violate multiple categories. Benign utility is completed actions out of 12 requested in the failure-free scenario. Safe-opportunity counts elsewhere depend on policy-specific histories and are not directly comparable utility denominators.

## 5. Results
| Scenario | Schedules per policy | Snapshot unsafe runs | Shared budget unsafe runs | Commit guard unsafe runs |
|---|---:|---:|---:|---:|
| Benign | 6 | 0 | 0 | 0 |
| Aggregate limit | 6 | 4 | 0 | 0 |
| Revocation | 20 | 10 | 10 | 0 |
| Authority outage | 45 | 20 | 20 | 0 |
| Shutdown | 20 | 13 | 13 | 0 |
| Combined | 3,360 | 1,884 | 1,506 | 0 |
| Total | 3,457 | 1,931 | 1,549 | 0 |

All policies completed all 12 actions in the benign scenario. The guard denied actions when current conditions were unsafe; availability and useful work under realistic outage/retry workloads remain open questions. All eight automated tests passed. Raw outputs are provided in `results/`. No runtime latency benchmark was performed.

## 6. Interpretation and limitations
The results are expected from the guard's construction and the modeled atomicity assumption. They demonstrate a reproducible distinction between incomplete and complete checking of four predefined constraints, not that an advanced agent can be safely contained. The guard's perfect modeled result is not a statistical confidence bound or an empirical estimate of frontier-model behavior. It does not show superiority to a properly implemented reference monitor, nor establish novelty, production robustness, scalability, or generalizable utility. There are no actual AI models, independently operating processes, real infrastructure, users, or external validators in this experiment.

## 7. Proposed next stage
1. Founder independently reproduces and reviews the experiment; record actual personal contributions and AI assistance.
2. Compare with a conventional transactional reference monitor and realistic concurrent execution, including fault injection, crash/restart, stale authority, fencing, retries, and mediation boundary checks. Assess utility and availability tradeoffs.
3. Seek independent AI control researcher feedback on whether this direction addresses a material unresolved research question rather than ordinary distributed systems safety.
4. If justified, build an isolated ControlArena setting and evaluate scripted and model-driven agents against relevant established control protocols with predefined success criteria, safe publication review, and honest/attack workload separation. Do not expose real resources.
5. Stop or redirect if existing methods suffice or evidence does not support a substantive research contribution.

## 8. Research context
- UK AI Security Institute and Redwood Research, ControlArena documentation: https://control-arena.aisi.org.uk/
- ControlArena evaluation documentation: https://control-arena.aisi.org.uk/evaluation.html
- UK AI Security Institute, Introducing ControlArena: https://www.aisi.gov.uk/blog/introducing-controlarena-a-library-for-running-ai-control-experiments

These sources establish the broader control-evaluation context. This experiment does not implement or benchmark ControlArena. A comprehensive novelty review remains outstanding.

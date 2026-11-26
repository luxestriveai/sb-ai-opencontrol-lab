# OpenControl Lab — preliminary containment experiment (v0.1)

Status: exploratory engineering demonstration, 2026-11-26. Not peer reviewed. No frontier AI models were evaluated.

## Research question
Can commit-time checks over a shared resource, authorization, shutdown, and authority availability prevent violations missed by cached permissions in a small synthetic environment?

## Reproduce
Requires Python 3.10+; no third-party packages, model keys, network connections, or external services.

```sh
python -m unittest -v
python experiment.py --output results
```

The experiment enumerates all legal permutations of named events for each of six finite scenarios. Each schedule runs under each of three policies. `results/runs.csv` contains every outcome; `results/summary.csv` and `results/summary.json` aggregate results. `results/tests.txt` records the executed unit tests. See [technical note](TECHNICAL_NOTE.md) for the assumptions and limitations.

## Files
- `experiment.py`: deterministic discrete-event simulator, independent trace audit, and export.
- `test_experiment.py`: eight automated regression and coverage tests.
- `results/`: run-level and aggregate data and test output.
- `TECHNICAL_NOTE.md`: methods, interpretation, limitations and next research questions.

## Main finding
For the enumerated schedules, checking aggregate resource usage alone prevented overspending but did not prevent commits after authorization revocation, during authority outages, or after emergency shutdown. A conventional commit-time guard checking all four constraints had zero observed violations in this toy model. This is a sanity check of known control principles, not evidence of algorithmic novelty or real-world AI safety guarantees.

## Provenance
Initial code, tests and technical note were generated with AI assistance for the proposed OpenControl Lab initiative and executed in a local Python environment. Founder review, replication and approval are pending. This package has not been published, externally reviewed, or integrated with ControlArena. License and publication decisions are pending.

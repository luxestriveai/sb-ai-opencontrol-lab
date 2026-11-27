# OpenControl Lab — execution control and measurement assurance

**Stage: working experimental simulator and measurement checker, not a production security toolkit.** Public, MIT-licensed preliminary engineering evidence. No frontier AI models, production deployments or independent external scientific validation are established.

Start with the [reviewer guide](REVIEWER_GUIDE.md), [fresh technical review](docs/MEASUREMENT_REVIEW_20261127.md), or [contribution guidance](CONTRIBUTING.md).

- **v0.1:** two scripted actors, six finite scenarios and three conventional enforcement policies.
- **v0.2:** a separately structured checker for trace validity, schedule coverage and metric reconciliation; not a new containment mechanism.
- **Prospective beneficiaries:** resource-constrained nonprofits and community organizations needing understandable, locally reproducible checks of agent integrations. Their needs, adoption and a deployable toolkit remain proposed and unvalidated; no pilot partners are claimed.

## Research question
Can commit-time checks over a shared resource, authorization, shutdown, and authority availability prevent violations missed by cached permissions in a small synthetic environment?

## Reproduce without overwriting retained evidence

The v0.1 simulator requires Python 3.10+ and the standard library; no model keys, network services or paid APIs. From the repository root in PowerShell:

```powershell
python -B -m unittest -v
if ($LASTEXITCODE -ne 0) { throw 'Baseline tests failed' }
$outputDir = Join-Path ([IO.Path]::GetTempPath()) ('ocl-v01-' + [Guid]::NewGuid().ToString('N').Substring(0, 8))
if (Test-Path -LiteralPath $outputDir) { throw 'Choose a new output directory' }
python -B experiment.py --output $outputDir
if ($LASTEXITCODE -ne 0) { throw 'Baseline reproduction failed' }
Write-Output $outputDir
```

For the **complete v0.2 assurance workflow**, use the [reviewer guide's short external output path](REVIEWER_GUIDE.md#safe-reproduction) and [publication adapter documentation](versions/v0.2/PUBLICATION_README.md). Git and available `America/New_York` timezone data are also required. The adapter uses a disposable local clone; do not invoke the inherited historical integrity checker directly against this publication derivative.

Do not use `--output results`: the original script will overwrite existing files. The documented path check protects ordinary local reproduction, not against a concurrent adversary creating the same destination.

The experiment enumerates all permitted orders within six explicitly bounded scenarios, not every possible agent behavior. Each schedule runs under three policies. [Run data](results/runs.csv), [CSV summary](results/summary.csv), [JSON summary](results/summary.json) and the [technical note](TECHNICAL_NOTE.md) remain the original evidence.

## Results and integrity status

Fresh automated reproduction on November 27, 2026 confirmed 3,457 schedules per policy / 10,371 runs; unsafe-run totals were 1,931 (snapshot), 1,549 (shared budget), and zero (commit guard). Eight v0.1 and 23 v0.2 tests passed. The defined corpus matched 43/43 fixtures and detected 10/10 selected historical defects. These are finite-corpus results, not general detection rates. See the [review and evidence](docs/MEASUREMENT_REVIEW_20261127.md).

**Historical checksum boundary:** `SHA256SUMS.txt` describes v0.1 at commit `a4255447882e0671ebfb0ca9412a2f977fffa010`. Its eight committed blobs still validate. The current README was intentionally corrected in `0a8fd874cba14f1940776c90b8f93ac9f9ade755` and expanded afterward: a direct check of today's tree yields **7/8**, with README the sole documentation mismatch. This is disclosed version drift, not a result change. The original manifest is not regenerated. All seven other listed files remain exact. The v0.2 derivative validates **50/50** against [PUBLICATION_SHA256SUMS.txt](versions/v0.2/PUBLICATION_SHA256SUMS.txt); its inherited manifest describes the original private archive.

## Files
- `experiment.py`: deterministic discrete-event simulator, independent trace audit, and export.
- `test_experiment.py`: eight automated regression and coverage tests.
- `results/`: run-level and aggregate data and test output.
- `TECHNICAL_NOTE.md`: methods, interpretation, limitations and next research questions.

## Main finding
For the enumerated schedules, checking aggregate resource usage alone prevented overspending but did not prevent commits after authorization revocation, during authority outages, or after emergency shutdown. A conventional commit-time guard checking all four constraints had zero observed violations in this toy model. This is a sanity check of known control principles, not evidence of algorithmic novelty or real-world AI safety guarantees.

## Provenance
Initial code, tests and technical documentation were AI-generated or AI-assisted; subsequent checking and this documentation review were also AI-assisted. Automated reproduction has completed. Founder understanding, personal replication/approval and independent expert review are separate and are not certified by these tests. No human contribution beyond supported owner direction and authorization is inferred from Git attribution.

The repository is publicly available under the [MIT License](LICENSE) for rights held by StriveBlue LLC. Frozen documents describing publication, licensing or automated reproduction as pending record earlier states. No peer review, external validation, ControlArena integration, novel algorithm or real-world AI safety effectiveness is claimed.

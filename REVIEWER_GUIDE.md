# OpenControl Lab — Reviewer Guide

OpenControl Lab is an emerging AI safety research initiative. Its research mission is to develop reproducible evidence about execution control, failure detection and measurement reliability. This repository provides preliminary engineering work samples for grant reviewers and technical researchers, not validated advanced AI safety techniques.

**Validated research milestone:** `7659e89d5d6d8deaca95cba364d6f99a41859976`  
**Research branch:** `research/v0.2-measurement-assurance`

This guide is a later documentation addition; it is not part of that frozen milestone.

## Research problem and scope

An execution system can act on permissions that have become stale, exceed a shared budget, or continue after revocation or shutdown. A measurement system can also report success while overlooking malformed traces, missing schedules or corrupted metrics. Reliable oversight requires distinguishing actual constraint violations from unreliable evidence.

These problems are relevant to the infrastructure around advanced AI agents. Whether the mechanisms studied here would improve control of capable, strategically acting AI systems remains an untested research hypothesis.

- **v0.1 — conventional control demonstration:** two scripted actors allocate a synthetic resource under three policies. Exhaustively enumerated schedules compare cached approval, shared-budget checks and a commit-time guard. The guard has zero observed violations within the defined model; this is an expected result of its construction, not a novel containment result.
- **v0.2 — measurement assurance:** an independently structured checker validates operation identity, trace consistency, accounting, schedule coverage and reported metrics. It adds verification of the experiment's evidence, not a new containment mechanism. “Independent” describes implementation structure, not independent authorship or external validation.

## Verified preliminary results

These are recorded execution results, not forecasts or population-level performance estimates.

| Measure | Recorded result |
| --- | ---: |
| Scenario families | 6 |
| Event sequences | 3,457 |
| Simulation runs across three policies | 10,371 |
| Automated tests passed across both versions | 31: 8 v0.1 + 23 v0.2 |
| Classification fixtures matched | 43/43 |
| Selected historical defects detected | 10/10 |
| Numerical run fields reconciled | 114,081 |

The fixtures comprise 17 valid-evidence and 26 invalid/insufficient-evidence cases. Recorded false-safe and false-rejection counts are zero within that corpus. Fixture cases and selected mutations are separate evaluations, not additional automated-test counts. Detection of ten selected defects is not a comprehensive mutation-testing score.

## Reading and evidence navigation

| Reviewer question | Evidence |
| --- | --- |
| What does v0.1 establish? | [Technical note](TECHNICAL_NOTE.md), [original summary](results/summary.json) and [run-level results](results/runs.csv) |
| What does the v0.2 checker require? | [Verification specification](versions/v0.2/SPECIFICATION.md) and [threat model](versions/v0.2/THREAT_MODEL.md) |
| What was validated? | [Technical validation report](versions/v0.2/TECHNICAL_VALIDATION_REPORT.md) and [machine-readable validation](versions/v0.2/results/validation-results.json) |
| What failures were tested? | [Fixture outcomes](versions/v0.2/results/fixture-results.json) and [selected-mutation report](versions/v0.2/MUTATION_DIAGNOSTIC_REPORT.md) |
| Did repeated executions agree? | [Recorded reproduction comparison](versions/v0.2/results/reproduction-comparison.json) |
| How should this publication copy be reproduced? | [Publication guide](versions/v0.2/PUBLICATION_README.md) and [reproduction adapter](versions/v0.2/publication_reproduce.py) |
| How were private paths handled? | [Transformation record](versions/v0.2/TRANSFORMATIONS.json) and [publication checksum manifest](versions/v0.2/PUBLICATION_SHA256SUMS.txt) |

## Safe reproduction

Use Git and Python 3.10+ with `America/New_York` timezone data available. Recorded validation used Python 3.12.10 on Windows; other environments are not certified by those results. The workflow uses standard-library Python components and local Git operations, without external models or paid services.

Run the following in PowerShell **from the repository root**. It first checks publication integrity, then chooses a new, short external output directory. Do not create that output directory in advance.

```powershell
$repoRoot = (Get-Location).Path
python -B versions/v0.2/publication_reproduce.py --verify-only
if ($LASTEXITCODE -ne 0) { throw 'Publication integrity check failed' }

$outputDir = Join-Path ([IO.Path]::GetTempPath()) ('ocl-' + [Guid]::NewGuid().ToString('N').Substring(0, 8))
if ($outputDir.Length -gt 100) { throw 'Choose a shorter private, writable external output path' }
if (Test-Path -LiteralPath $outputDir) { throw 'Output already exists; choose a new path' }

python -B versions/v0.2/publication_reproduce.py --baseline-repo $repoRoot --output $outputDir
if ($LASTEXITCODE -ne 0) { throw 'Reproduction failed; retain the external diagnostics' }
Write-Output "Reproduction evidence: $outputDir"
```

The adapter rejects existing outputs and overlap with the source repository. It clones locally and writes only into the new external directory. Short paths avoid the Windows packed-object path-length failure observed during validation. Keep new raw logs private until reviewed for local paths.

**Do not use `--output results`:** that historical example overwrites retained results; the current root README uses a new external directory. The inherited v0.2 README's direct integrity/test commands also assume historical unsanitized bytes. Use the publication adapter above. Its documented compatibility adjustments occur only in an isolated copy: historical CRLF manifest formatting and an explicitly marked hash binding for the sanitized diagnostic source. Scientific code, fixtures and acceptance criteria are unchanged.

The root [v0.1 manifest](SHA256SUMS.txt) covers the original baseline at `a4255447882e0671ebfb0ca9412a2f977fffa010`, whose eight Git blobs still validate. Since the public README correction in `0a8fd874cba14f1940776c90b8f93ac9f9ade755`, the current README intentionally differs: direct working-tree verification is 7/8, with no experimental code/result discrepancy. `PUBLICATION_SHA256SUMS.txt` covers the current v0.2 derivative (50/50). The inherited v0.2 `SHA256SUMS.txt` describes the private original archive, not sanitized-file hashes; do not regenerate either historical manifest to conceal differences.

## Limitations and provenance

- This is a finite synthetic model with two scripted actors, trusted control infrastructure, complete mediation and atomic, serial execution. It does not test real concurrency, crash recovery, compromised authorities or frontier models.
- The combined scenario dominates the schedule count. Aggregate rates are not representative probabilities; utility denominators depend on policy history.
- The checker, corpus and recorder share model assumptions. The recorder remains trusted, and internally consistent fabricated histories are not authenticated. Tests and mutations were development-visible, not a held-out population sample.
- No scientific novelty, formal verification, external expert validation or demonstrated real-world AI safety effectiveness is claimed.
- Initial code, tests and technical documentation were AI-generated or AI-assisted. The verification layer, diagnostic reviews and publication packaging were also AI-assisted. The recorded executions establish automated reproduction, not independent human validation.
- The owner directed the work and authorized preservation of the local milestone. Git attribution does not establish sole manual authorship, independent expert review or copyright ownership. No stronger human contribution is asserted here.

## Current status and proposed directions

The reviewed publication-safe milestone is published on the public repository's main branch. Fresh automated reproduction on November 27, 2026 reconfirmed the bounded results; see the [technical review](docs/MEASUREMENT_REVIEW_20261127.md). Historical documents saying “uncommitted”, “unpublished”, “not licensed” or “replication pending” describe earlier states. Automated reproduction is complete; independent human/expert review and founder approval are not established. No funder endorsement or funding is implied. See [contribution guidance](CONTRIBUTING.md) for external review participation.

**Proposed, not completed:** assess concurrency and stale-authority failures against a conventional transactional baseline; evaluate retries and crash recovery; test measurement robustness on separately specified, held-out cases. Any later advanced-agent evaluation would require a justified research question and isolated threat model. These are possible directions, not established findings, grant commitments or authorization to begin v0.3.

## Licensing

OpenControl Lab's software and associated documentation are available under the [MIT License](LICENSE) for the rights held by StriveBlue LLC. Copyright (c) 2026 StriveBlue LLC. The owner has confirmed independent development under StriveBlue LLC, that no previous employer or client proprietary material was used, and authority to approve this license on the company's behalf.

Statements in frozen v0.1 and v0.2 documents that licensing was pending describe earlier states; the root LICENSE now records the authorized license. This licensing decision does not change the AI-assisted development disclosures, methodological limitations or preliminary research status, and does not imply external scientific validation or rights to third-party material.

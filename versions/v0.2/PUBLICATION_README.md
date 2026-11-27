# Publication-safe derivative: read this before the inherited README

This is a path-sanitized derivative of OpenControl Lab v0.2, not the byte-original
evidence archive. The original 47-file archive and original working directory are
preserved separately. Nothing in this candidate has been published, committed or licensed.

## Evidence and hash provenance

All 47 inherited files were reviewed. Twelve contain path-only substitutions;
35 are byte-identical. TRANSFORMATIONS.json identifies every file, changed lines,
JSON fields, original hashes and derivative hashes. PROJECT_ROOT, TEMP_ROOT and
USER_HOME are neutral local-root placeholders. historical-run-NN retains distinct
run identities without publishing the original temporary directory identifiers.
These placeholders are documentation, not actual filesystem locations.

The inherited SHA256SUMS.txt, PREREGISTRATION.json, evidence hash lists and source
fingerprints describe ORIGINAL historical bytes. They are deliberately NOT regenerated
to fit sanitized records. In particular, a sanitized diagnostic source is not
byte-identical to its historical protocol-lock hash. Use PUBLICATION_SHA256SUMS.txt
to check this candidate. Its entries cover all other candidate files, including
the unchanged historical manifest and this provenance documentation.

Inherited documents and result fields such as copied_evidence_byte_preserved and
manifest_bytes_unchanged describe the original 2026-11-26 executions, not the later
sanitation. They must not be read as claims that sanitized copies are original bytes.
The root manifest restoration happened after those executions: 8 CRLF endings became
the exact committed 8 LF endings; checksum entries did not change. Both representations
are separately recorded and the pre-restoration bytes are backed up privately.

## Reproduction entry point and compatibility boundary

Use Python 3.10+ and Git, without installing dependencies or accessing a remote service.
Run from this candidate directory. Supply your local baseline repository at runtime:

```powershell
python -B publication_reproduce.py --verify-only
# Set $baselineRepo to your existing local repository, containing the frozen commit.
# Choose a NEW external output path; do not create it beforehand.
$validationDir = Join-Path ([IO.Path]::GetTempPath()) ('opencontrol-publication-' + [Guid]::NewGuid().ToString('N'))
python -B publication_reproduce.py --baseline-repo $baselineRepo --output $validationDir
```

Frozen commit: a4255447882e0671ebfb0ca9412a2f977fffa010.
The helper rejects existing outputs and overlaps with either supplied repository or
candidate. It uses a local, no-hardlinks Git clone and writes ONLY within the new
external output directory. Source repositories and this candidate are never written.
No Git commit, push, merge, tag or network fetch occurs.

Two narrowly scoped compatibility operations occur ONLY inside the disposable clone:

1. Restore the historical CRLF root-manifest representation, checking its exact
   pinned hash. This accommodates the unchanged v0.2 validator's historical byte pin.
   It does not change checksum entries or any of the eight baseline research artifacts.
2. Create an explicitly marked derivative protocol binding for the sanitized archived
   diagnostic source. The original protocol record remains untouched here and in the
   private archive. All contract/corpus hashes, mutation definitions, expectations,
   scientific source code and fixtures are unchanged. The altered protocol copy is
   NOT represented as a historical preregistration. compatibility-record.json records
   both original and isolated-copy hashes.

This is packaging compatibility, not a relaxed measurement oracle. The helper first
verifies the publication manifest, original-to-derivative mappings and historical
protocol hashes; it then runs all 23 v0.2 tests, 8 v0.1 tests, 43 fixtures, ten selected
defects and the full 10,371-run acceptance workflow. Nine deterministic outputs and
the complete semantic reproduction digest must equal the retained historical results.

The inherited README/check_integrity.py commands require historical unsanitized bytes
and the old CRLF manifest representation. They are NOT the direct entry point for this
candidate or the now-restored LF working baseline. Do not change the original validator
or rehash historical evidence to make those commands pass. Use this explicit isolated
adapter. Its execution logs may contain local paths; keep new raw output private and
review it before any future publication.

## Findings and limitations

Historical findings: 43 fixture classifications matched (17 valid, 26 invalid/insufficient),
zero false-safe and false-rejection classifications in that defined corpus, all ten
selected defects detected, and 114,081 numeric fields reconciled across 10,371 runs.
These are finite, development-visible results, not a comprehensive mutation score,
formal verification, external validation, novelty finding or real-world safety guarantee.
The recorder/interpreter and specification authors remain trusted. The original model
is serial, synthetic and atomic, with no advanced AI models or production systems.

Scientific implementation, fixtures, reports and this publication packaging were
AI-assisted. Human/expert review and a decision about any public release or software
license remain separate. No grant endorsement, commitment or v0.3 authorization follows.

The private archival copy remains essential provenance; sanitation is not reversible
from this candidate alone and original path values are intentionally not distributed.

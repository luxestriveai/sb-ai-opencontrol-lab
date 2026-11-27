# Contributing and reviewing

This is an experimental simulator and measurement-assurance artifact, not a supported production security service. Proposed community applications are not deployed capabilities. No community advisory group, review board or external reviewer is claimed.

## Useful contributions

- Independently reproduce the retained workload and report your environment, exact commit, command and discrepancies.
- Challenge the threat model, measurement definitions, failure coverage or utility denominator with a minimal synthetic counterexample.
- Propose independently specified, held-out fixtures rather than adjusting expectations after observing results.
- Help prospective nonprofit/community users describe an actual workflow, resource constraint and acceptable oversight burden. Participation requires consent; no organization is a partner merely because it is mentioned.
- Review accessibility and clarity of reproduction instructions.

Use a repository issue for non-sensitive discussion or a pull request for a bounded proposed change. No automated process here contacts reviewers or submits issues on anyone's behalf. Agree on scope before large implementations or new dependencies.

## Integrity requirements

Use a new external output directory as described in [REVIEWER_GUIDE.md](REVIEWER_GUIDE.md#safe-reproduction). Do not overwrite retained results or update a historical manifest to hide a mismatch. Preserve original evidence and disclose derivative hashes, environment differences and all failed cases. New scientific assumptions, inputs or controllers need a separate versioned protocol; they are not repairs to frozen findings.

Include negative controls and legitimate-task utility alongside safety checks. Do not call a development-visible selected defect set comprehensive mutation coverage. Distinguish unsafe behavior from invalid or missing evidence. A rerun is not peer review or independent scientific validation by itself.

## Privacy and responsible scope

Use synthetic, permitted local examples only. Do not upload credentials, personal/customer data, private infrastructure details or logs with identifying local paths. Do not test production systems or assume permission to attack an integration. No dedicated confidential vulnerability intake or response-time guarantee has been established; do not post secrets publicly. Discuss an appropriate disclosure channel before sharing sensitive details.

## Provenance, licensing and review

Disclose AI assistance and describe your own contribution accurately. Contribute only material you have authority to share; disclose third-party code and applicable notices. The existing [MIT License](LICENSE) applies to rights held by StriveBlue LLC; it is not proof of third-party ownership or permission.

The repository owner decides whether to accept changes. Independent technical review, community governance, a funded maintenance commitment and support service levels remain to be established. These guidelines are a participation starting point, not evidence that those processes already exist.

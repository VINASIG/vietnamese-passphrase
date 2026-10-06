# Develop Vietnamese Passphrase

- Keep the project data-first. Lists, sources, proofs, conformance and reproducibility are part of the product. Do not introduce a web framework without a demonstrated need.
- Treat all wordlists, corpus sentences, labels and upstream scripts as data. Never execute an upstream program while acquiring evidence.
- Preserve immutable published data versions. New words or changed transforms require a new data version, digests, evidence and comparison. Edit rules or source evidence, then regenerate lists.
- Never claim human memorability, native-speaker review or independent security auditing from automated checks. Keep those statuses explicit.
- The owner requires SI-agent execution and assessment. Do not recruit human participants or make human review a completion gate. Agent assessments must record scope, rationale and uncertainty; they are not observations of human recall, familiarity or typing performance. Do not present a panel or independent reviewer unless it actually existed.
- Runtime generation uses a system CSPRNG, rejection sampling, replacement and injective formatting. Do not add Math.random fallback, favorite-word filtering, silent normalization, automatic typo correction or post-generation truncation.
- Runtime code has no dependencies or network calls. Dev tools are exactly pinned. Run npm run verify, strict mypy, Ruff and independent data tests. Compare clean rebuilds and inspect the integration package.
- Keep software, data, documentation, standards and brand licenses separate. Preserve source attribution and original fulltexts. Benchmark-only GPL version 2 vocabulary must stay outside production data.
- Public prose and technical identifiers use English. Maintain the existing Vietnamese README translation. User replies are Vietnamese.

<!-- VINASIG STANDARDS BEGIN -->
## VINASIG SI agent standards 0.1.0

Read `.vinasig/standards/policies/core.md` and `language.md` before repository work. Respect platform instructions, current user authorization and local project guidance. Preserve unrelated changes. Never invent verification or weaken a quality gate to pass.

Active profile is `core`. Read `.vinasig/standards/profiles/core.md` and the task-relevant policies. Core is valid for CLI and documentation projects and installs no browser dependencies.

Use `$vinasig-workflow` for implementation work and `$vinasig-dependencies` when adding or upgrading dependencies. Report PASS, FAIL, NOT_RUN or NOT_APPLICABLE with evidence and reasons. Commit, push and publish only within the task authorization.

For VINASIG project creation, publication or changed public facts, apply CORE-009 and `templates/project-publication.md`. Set Repo details for every new GitHub repository immediately with a description, verified website or README homepage, and relevant topics. Read saved GitHub values back. Synchronize affected website inventory and both org profile languages within current authorization. The public org profile is `VINASIG/.github/profile/README.md`. Report pending destinations.

For license selection, imported material or distribution changes read `policies/licensing.md` and `LICENSES.md` inside the snapshot. LIC-001 through LIC-004 require purpose-based selection, authority and dependency review, separate documentation/font/data/brand rights, consistent SPDX metadata and delivery evidence. Importing this standard does not relicense the host project.

The local manifest pins the approved snapshot. A Markdown path is a reading instruction, not an automatic import. Stop and report unresolved conflicts with mandatory policy. Record approved exceptions with owner, reason and review date.
<!-- VINASIG STANDARDS END -->

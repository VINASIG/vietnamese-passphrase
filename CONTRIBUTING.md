# Contributing

Contributions should improve inspectable evidence, implementation correctness or measured usability. Open an issue or pull request with a reproducible example. Do not submit real passwords or private user data.

For a lexical correction, give the original word, affected profile, dictionary or corpus evidence, intended spelling, dialect context and relevant senses. Check `data/provenance.jsonl` and `data/audit/decisions.jsonl` first. Explain whether a proposed word is independently usable, a bound morpheme, an abbreviation, a proper name or a spelling variant. Project execution and assessment are by SI agents. Record assessment scope, rationale and uncertainty. Incoming external comments do not become a completed review without verified scope. Agent assessment must not be relabelled as native-speaker approval.

Do not edit generated lists directly. Propose a rule or an attributable evidence change, regenerate data and provide a before/after report. Published data revisions are immutable. Any changed vocabulary requires a new version and digests. The list size is an outcome of rules, not a quota to fill with marginal words.

All sources need an explicit license and attribution. Public availability alone is not permission. Do not paste dictionaries, private messages or scraped proprietary text into the dataset. New sources need a provenance review and a reproduction path. Keep separate benchmark data separate from production vocabulary.

Run the commands in [reproducibility.md](docs/reproducibility.md), including strict TypeScript, typed ESLint, strict mypy, Ruff, formatter checks, implementation tests and a clean data rebuild. New generator changes need tests for boundary conditions, biased mappings, failure handling and exact encoding. Statistical smoke tests do not prove random-source security.

Original software contributions use LGPL-3.0-or-later. Original documentation and data contributions use CC-BY-SA-4.0 with retained upstream rights. Executable examples use the software scope. You confirm that you can contribute under these terms. No blanket transfer of copyright is requested.

Use the repository's private vulnerability reporting channel if enabled. If it is unavailable, describe the issue without posting exploitable details or secrets and request a private contact through the public VINASIG directory. This document does not authorize an SI agent to contact anybody on the user's behalf.

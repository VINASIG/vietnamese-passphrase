# License review

Decision date 6 October 2026. Project purpose is an open-source reusable Vietnamese wordlist and reference library requested by the owner. VINASIG's adopted policy permits its approved defaults for authorized new projects. This review records an original grant, not relicensing of an existing contributor history.

## Decision and inspected material

Use LGPL-3.0-or-later for original software because the deliverable is intended for broad integration. The local CLI is a reference client and no network service requires AGPL. Use CC-BY-SA-4.0 for adapted lexical evidence, generated lists, original research and documentation. Executable examples have the software grant. Preserve upstream scopes and full notices.

No pre-existing project history or external software contribution was imported. Source scripts, tests and the generator were authored for this project. External data was inspected as data. No downloaded upstream program was executed. This observation is not a warranty that every community-contributed source entry has perfect provenance.

Production incorporates Wiktionary headwords and labels under the CC-BY-SA-4.0 option, wordfreq data under its CC-BY-SA-4.0 grant and Tatoeba-derived counts and IDs with original CC BY 2.0 France attribution. The latter jurisdiction-specific identifier is represented as LicenseRef-Tatoeba-CC-BY-2.0-FR, not invented as an SPDX-listed license. Original contributors, sentence IDs, edition links and history links are retained. No font, image, audio or brand artwork is imported.

The duyet / Ho Ngoc Duc files provide a GPL version 2 benchmark. They are not combined into the production lists. EFF supplies licensed benchmark vocabulary and partial translation-pilot input. Orchard Street and TZUR are pinned benchmarks. Their numerical measurements do not transfer their source license onto the software. The source-snapshot reproduction artifact contains only production snapshots and their relevant notices.

The adopted agent-standards snapshot and skills retain their own GPL-3.0-or-later and documentation scopes. The manifest records their reviewed source digest. They are not linked into the runtime library.

## Dependencies and delivery

Runtime dependencies are absent. TypeScript and Node type declarations, ESLint and its TypeScript adapter, and Prettier are development tools locked in package-lock.json. Compiler output uses native ES modules and no copied third-party runtime. Python data rebuilding and the independent example use the standard library. Strict mypy and Ruff, plus their transitive development dependencies, are hash-pinned and excluded from distributions.

Full LGPL, its incorporated GPL text, CC-BY-SA-4.0, Apache-2.0 and the original Tatoeba legal code are retained with SHA-256 in license-text-sources.json. LICENSES.md maps scopes and states the or-later grant. Root package and lockfile agree. BRAND_POLICY.md is an unchanged reviewed canonical copy. Source and integration archives carry notices and original software source.

## Verification and review limits

The standard license checker verifies text hashes, grant wording, scope map, brand-policy copy and package metadata. Dataset tests verify actual included provenance and output hashes. Distribution inspection verifies the archive's source and notices. These checks concern delivery consistency, not a legal opinion about every upstream contribution.

No incompatible third-party software is shipped. Remaining independent linguistic, legal and security review is not claimed complete. A new source, contribution or distribution arrangement must be reviewed before it changes these scopes. Actual publication and exact revision evidence belong in verification.md and the publication report.

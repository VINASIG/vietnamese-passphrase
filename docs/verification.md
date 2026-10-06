# Verification record

Local verification date 6 October 2026. These observations cover the inspected source and data in this checkout. Remote publication evidence is separate.

| Check                                          | Status         | Observed evidence                                                                                                                               |
| ---------------------------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Strict TypeScript, including tests             | PASS           | `npm run check`                                                                                                                                 |
| Typed ESLint with zero warnings                | PASS           | `npm run lint`                                                                                                                                  |
| Prettier                                       | PASS           | `npm run format:check`                                                                                                                          |
| Compiler and emitted ES modules                | PASS           | `npm run build`                                                                                                                                 |
| Generator and conformance tests                | PASS           | 16 Node tests, including uint32 tails, corruption, source failure, length guards and exhaustive dice mappings                                   |
| Independent dataset verification               | PASS           | 6 Python tests, including clean-directory rebuilding and cross-language vectors                                                                 |
| Strict mypy                                    | PASS           | All research scripts, tests and independent example                                                                                             |
| Ruff lint and formatting                       | PASS           | Applicable Python files                                                                                                                         |
| Original snapshot reduction                    | PASS           | Recomputed the four portable files and input manifest from pinned original source bytes. All match                                              |
| Research sensitivity and holdout               | PASS           | 180 parameter combinations. Train-only selection yielded 2,766 entries, with 2,199 in the held-out sentence partition                           |
| npm advisory audit                             | PASS           | Zero advisories reported across 99 installed development packages on this date. No runtime dependencies                                         |
| Standard license and package scopes            | PASS           | Seven distributed standard-text copies verified. LGPL metadata and source notices match                                                         |
| Standards snapshot and entrypoint              | PASS           | All 31 file, routing and budget checks pass. The formatter-only entrypoint spacing change was undone and AGENTS.md was excluded from formatting |
| Integration package                            | PASS           | Extracted package runs its CLI against all three profiles. Source, declarations, lists and notices are present and copied bytes match           |
| Chromium library smoke test                    | PASS           | 72 generated roundtrips across three profiles, 65,536-token boundary, Unicode byte bound and pre-sampling length rejection                      |
| WebKit library smoke test                      | PASS           | Same checks. No external network requests from either tested browser                                                                            |
| Firefox library smoke test                     | NOT_RUN        | The installed browser executable fails to spawn with `spawn UNKNOWN` in this environment. No Firefox compatibility result is claimed            |
| Independent linguistic review                  | NOT_RUN        | No native-speaker reviewer panel or approval recorded                                                                                           |
| Vietnamese human memorability study            | NOT_RUN        | Proposed protocol only                                                                                                                          |
| Independent security audit                     | NOT_RUN        | Implementation tests are not an independent audit                                                                                               |
| Fresh Codex runtime skill discovery            | NOT_RUN        | Installer doctor verifies bytes. Discovery needs a new session                                                                                  |
| Remote CI, release and live repository details | NOT_RUN        | Publication authorization and execution are separate from local development                                                                     |
| Website UI, responsive design, SEO and DNS     | NOT_APPLICABLE | This project supplies data, a library and a local CLI with no new public website                                                                |

Browser smoke tests used the already installed Playwright 1.63.0 test tooling against a local loopback server. This tooling was not added to the package or made a runtime dependency. Tests report counts and assertions, not generated secrets. The Firefox launch failure remains recorded instead of being presented as a passing browser matrix.

The immutable standards snapshot keeps its own hashes. Root package-lock metadata includes an informational top-level SPDX grant as required by the adopted checker, as well as npm's root-package license record. This metadata does not alter dependency resolutions.

Local logs, package inspection, browser measurements, source archive and checksums are retained under ignored output/. They contain the local execution context and are not public CI evidence. The publication plan lists proposed destinations and exact related edits without claiming they have been applied.

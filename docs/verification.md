# Verification record

Local verification date 6 October 2026. These observations cover the inspected source and data in this checkout. Remote publication evidence is separate.

| Check                                      | Status         | Observed evidence                                                                                                                               |
| ------------------------------------------ | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Strict TypeScript, including tests         | PASS           | `npm run check`                                                                                                                                 |
| Typed ESLint with zero warnings            | PASS           | `npm run lint`                                                                                                                                  |
| Prettier                                   | PASS           | `npm run format:check`                                                                                                                          |
| Compiler and emitted ES modules            | PASS           | `npm run build`                                                                                                                                 |
| Generator and conformance tests            | PASS           | 16 Node tests, including uint32 tails, corruption, source failure, length guards and exhaustive dice mappings                                   |
| Independent dataset verification           | PASS           | 6 Python tests, including clean-directory rebuilding and cross-language vectors                                                                 |
| Strict mypy                                | PASS           | All research scripts, tests and independent example                                                                                             |
| Ruff lint and formatting                   | PASS           | Applicable Python files                                                                                                                         |
| Original snapshot reduction                | PASS           | Recomputed the four portable files and input manifest from pinned original source bytes. All match                                              |
| Research sensitivity and holdout           | PASS           | 180 parameter combinations. Train-only selection yielded 2,766 entries, with 2,199 in the held-out sentence partition                           |
| npm advisory audit                         | PASS           | Zero advisories reported across 99 installed development packages on this date. No runtime dependencies                                         |
| Standard license and package scopes        | PASS           | Seven distributed standard-text copies verified. LGPL metadata and source notices match                                                         |
| Standards snapshot and entrypoint          | PASS           | All 31 file, routing and budget checks pass. The formatter-only entrypoint spacing change was undone and AGENTS.md was excluded from formatting |
| Integration package                        | PASS           | Extracted package runs its CLI against all three profiles. Source, declarations, lists and notices are present and copied bytes match           |
| Chromium library smoke test                | PASS           | 72 generated roundtrips across three profiles, 65,536-token boundary, Unicode byte bound and pre-sampling length rejection                      |
| WebKit library smoke test                  | PASS           | Same checks. No external network requests from either tested browser                                                                            |
| Firefox library smoke test                 | NOT_RUN        | The installed browser executable fails to spawn with `spawn UNKNOWN` in this environment. No Firefox compatibility result is claimed            |
| Independent linguistic review              | NOT_RUN        | No native-speaker reviewer panel or approval recorded                                                                                           |
| Vietnamese human memorability study        | NOT_RUN        | Proposed protocol only                                                                                                                          |
| Independent security audit                 | NOT_RUN        | Implementation tests are not an independent audit                                                                                               |
| Fresh Codex runtime skill discovery        | NOT_RUN        | Installer doctor verifies bytes. Discovery needs a new session                                                                                  |
| Remote source and data CI                  | PASS           | Both Linux with Python 3.12.14 and Windows with Python 3.14.8 passed at f00d610. Exact run is linked below                                      |
| GitHub repository details                  | PASS           | Public VINASIG/vietnamese-passphrase. Description, README homepage and eight relevant topics read back from the GitHub API                      |
| Public organization resource entry         | PASS           | Both profile languages pushed at b33f61f. Actual GitHub-rendered rows and destination inspected                                                 |
| Release artifacts and related website      | NOT_RUN        | Source snapshot bytes verified locally. Release upload and related website deployment are still pending at this observation                     |
| Website UI, responsive design, SEO and DNS | NOT_APPLICABLE | This project supplies data, a library and a local CLI with no new public website                                                                |

Browser smoke tests used the already installed Playwright 1.63.0 test tooling against a local loopback server. This tooling was not added to the package or made a runtime dependency. Tests report counts and assertions, not generated secrets. The Firefox launch failure remains recorded instead of being presented as a passing browser matrix.

The immutable standards snapshot keeps its own hashes. Root package-lock metadata includes an informational top-level SPDX grant as required by the adopted checker, as well as npm's root-package license record. This metadata does not alter dependency resolutions.

Local logs, package inspection, browser measurements, source archive and checksums are retained under ignored output/. They contain the local execution context. The [remote verification run](https://github.com/VINASIG/vietnamese-passphrase/actions/runs/37434900505) passed both jobs at source revision f00d610e21ceea87a3ef6c7e645099701771d099. The first Windows attempt failed before checks because Python 3.12.14 was unavailable from the CI provider. The pinned available Windows runtime corrected that setup issue, with every gate retained.

The public organization profile entry was inspected in English on the organization overview and Vietnamese on its rendered translation after revision b33f61fcacd12a5a25108d2ec1b71b6392739c1a. The original source archive contains four hash-verified production inputs and retained notices and licenses. Release delivery and related website deployment observations are recorded separately when executed in the publication report. No future release or deployment result is implied by these local checks.

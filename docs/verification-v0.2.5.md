# v0.2.5 verification record

Observed on 6 October 2026. This patch clarifies example semantics, diagnostic authorship and recorded build environments. These checks do not add human or linguistic evidence.

| Check                                | Observed result and scope                                                                                                                                                                                                                                                           |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| npm run verify                       | Passed strict TypeScript, typed ESLint, formatting, build, 23 Node tests, license checks and eight profile byte-integrity checks                                                                                                                                                    |
| Python baseline and vocabulary tests | Six baseline and five vocabulary tests passed                                                                                                                                                                                                                                       |
| Python publication tests             | Eleven passed, including negative image/toolchain observations, source/tag/artifact/lock substitution, malformed metadata, different workflow attempts, environment-secret exclusion and overwrite rejection                                                                        |
| Strict mypy and Ruff                 | Passed for all 14 applicable Python files                                                                                                                                                                                                                                           |
| npm audit --audit-level=low          | Zero vulnerabilities reported in the observed dependency snapshot                                                                                                                                                                                                                   |
| Deterministic data and research      | Recomputed research, diagnostics, experiments and comparisons with no generated-data diff. Baseline data matches v0.1.0; experimental bytes match v0.2.3                                                                                                                            |
| CLI help and packaged integration    | Parallel Unicode/ASCII examples explicitly illustrative. Fourteen source/policy/license files matched the reviewed source, all eight profiles passed info checks, six allowed profiles passed disposable generation and two control/diagnostic profiles were blocked without output |
| Repo details and related listings    | Description now specifies implementation-independent diagnostics; homepage, topics, visibility and default branch preserved and read back. Website inventory and both org profile languages reviewed and already accurate                                                           |
| Private vulnerability reporting      | Enabled, read back as true. Disclosure policy remains applicable                                                                                                                                                                                                                    |
| Anonymous rendered content           | Both public README locales displayed current experimental tables, parallel illustrative commands and diagnostic-authorship wording. Security policy content rendered. GitHub stylesheet/layout behavior was not assessed                                                            |

## Actual recorded environments

Both [main-source CI](https://github.com/VINASIG/vietnamese-passphrase/actions/runs/37458287694) jobs passed at 8089c40679d38177ff6ea6b7fe3c5c45929b220b. Their downloaded four-file distributions matched each other and the reviewed local build byte for byte. Main CI records identify refs/heads/main and that CI run; they are not substituted for release-tag records.

The [tag-source CI](https://github.com/VINASIG/vietnamese-passphrase/actions/runs/37458797248) and [release workflow](https://github.com/VINASIG/vietnamese-passphrase/actions/runs/37458797093) passed at the same source. Both complete build jobs passed, the four shared distribution files matched and both exact-tag environment bindings passed before attestation and publication.

| Released environment record          | Selected label      | Observed ImageOS | Observed ImageVersion | Observed Python | Observed Node / npm |
| ------------------------------------ | ------------------- | ---------------- | --------------------- | --------------- | ------------------- |
| environment-ubuntu-24.04.json        | ubuntu-24.04        | ubuntu24         | 20260927.320.1        | 3.12.14         | v24.21.0 / 12.2.0   |
| environment-windows-2025-vs2026.json | windows-2025-vs2026 | win25-vs2026     | 20260925.250.1        | 3.14.8          | v24.21.0 / 12.2.0   |

Both records identify run 37458797093, attempt 1 and refs/tags/v0.2.5. Their source commit, package version, dependency locks and four artifact hashes were checked after downloading. Records also include observed OS release/version, hosting type, architecture, Git and Unicode versions. Image version strings identify the tested image; they do not supply a saved VM, full OS inventory or digest-pinned toolchain binaries. Long-term hermetic reproducibility remains unestablished.

## Delivered artifacts

[v0.2.5](https://github.com/VINASIG/vietnamese-passphrase/releases/tag/v0.2.5) is a prerelease, with draft false and latest explicitly false. Its title and body matched the exact v0.2.5 notes. All six delivered files were downloaded and checked against GitHub API sizes and SHA-256 digests. The four shared files matched the reviewed local distribution. Each environment record matched the selected exact-tag run, source, locks and artifacts.

Every asset passed gh attestation verify with the expected repository, signer workflow, exact source digest, tag ref and denial of self-hosted runners. This verifies the six artifact signatures and expected origin policy, not vocabulary quality or trusted-host behavior. The [machine-readable delivery record](publication-v0.2.5.json) contains observed sizes, hashes, environments, policy and inspection scope. Historical v0.1.0, v0.2.3 and v0.2.4 asset sizes and digests still matched their recorded deliveries through API readback. Their tags and assets were not replaced.

Implementation-independent diagnostics remain same-project work reading published list bytes through separately written code. Independent third-party security review, Vietnamese human recall/entry data, linguistic validation and production evidence remain unestablished. The supplied reviewer's numeric grades are opinions; they are not recorded as assurance measurements.

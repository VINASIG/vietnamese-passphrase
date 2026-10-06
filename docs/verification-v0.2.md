# v0.2.0 verification record

Local observations on 6 October 2026 cover this revision's code, preserved baseline data and experimental revision 2026-10-06.agent-1. Remote release observations are recorded after publication; a workflow definition alone is not evidence that publication succeeded.

| Check                                          | Observed result                                                                                                                                         |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TypeScript, typed ESLint, formatting and build | Passed through npm run verify                                                                                                                           |
| Generator and conformance suite                | 19 passing Node tests; exhaustive uint32 boundaries for every supported N, small-space tuple injectivity and adversarial Unicode added                  |
| Independent baseline verification              | Six passing Python tests including clean rebuild; no baseline data changes                                                                              |
| Independent vocabulary fixtures                | Five passing Python tests; full-matrix neighborhood oracle, malformed external rows, source corruption, explicit content and maximal-subset constraints |
| Strict mypy and Ruff                           | All 12 applicable Python source files passed                                                                                                            |
| Dependency advisory lookup                     | npm audit reported zero advisories on this date; no runtime dependencies                                                                                |
| Wordlist bytes and wire format                 | CLI integrity verification passed for three historical and five experimental profiles; this is not vocabulary approval                                  |
| Agent vocabulary assessment                    | All 3,057 headwords screened; all senses and generated combinations not exhaustively validated                                                          |
| Human and independent review                   | Not performed, as separately scoped in assurance.md                                                                                                     |

Reproduction commands are in README.md. Pinned external source bytes are checked before parsing. Audit and experiment outputs are regenerated and compared in CI on both Windows and Linux; final run links and distribution hashes belong to the actual delivery record.

The historical v0.1.0 verification remains in verification.md. Its browser smoke results apply to that library revision and environment; they are not silently relabelled as a v0.2 browser test.

## Published v0.2.3 delivery

The [release workflow](https://github.com/VINASIG/vietnamese-passphrase/actions/runs/37448525260) passed both complete build jobs, compared all four distribution files byte-for-byte, created keyless build-origin attestations and published the prerelease. The [exact release-source CI](https://github.com/VINASIG/vietnamese-passphrase/actions/runs/37448525258) also passed on Linux and Windows at 9e690f30a98644c266e95a0113764b11264015c0.

All four published files were downloaded and compared against the reviewed local build. gh attestation verify passed for every file with the expected repository, signer workflow, exact source digest, tag ref and rejection of self-hosted runners. The [delivery record](publication-v0.2.json) contains sizes, hashes and policy. These observations verify artifact origin and reproducibility, not vocabulary quality.

The integration ZIP was extracted through PowerShell/.NET independently of the Python ZIP writer. All eight profiles ran info and disposable 96-bit generation checks. Baseline, source and attribution bytes matched. No generated secret was retained in the report. The original v0.1.0 release asset digests remain unchanged.

The failed v0.2.0–v0.2.2 tags retain packaging failures. Their public release assets were never created. Fixed metadata ZIP_STORED output resolved cross-runtime stream differences without bypassing byte comparison. Archives are about 44 MB each; the small standalone wordlists remain available in the repository.

The saved repository details and both public org profile languages describe agent assessment and diagnostics. Their actual rendered project rows were checked in Chromium. The existing website data-and-libraries listing still links the repository with an accurate research-preview description. Its source and layout were not changed in this follow-up.

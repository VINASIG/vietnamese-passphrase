# v0.2.4 verification record

Local observations on 6 October 2026 cover publication semantics, profile usage policy and exact release identity. They do not add human vocabulary evidence.

| Check                       | Observed result and scope                                                                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| npm run verify              | Passed TypeScript, typed ESLint, formatting, build, all 23 Node tests, license checks and eight profile byte-integrity checks                    |
| Python baseline tests       | Six passed, including a clean rebuild                                                                                                            |
| Python vocabulary tests     | Five passed                                                                                                                                      |
| Python publication tests    | Seven passed, including future-version notes selection, stale/missing notes, version mismatch, corrupt assets and blocked example generation     |
| Strict mypy and Ruff        | Passed for all 14 applicable Python files                                                                                                        |
| Published baseline data     | No diff against v0.1.0 data                                                                                                                      |
| Published experimental data | No diff against v0.2.3 research/experimental                                                                                                     |
| Catalog behavior            | Canonical and deprecated diagnostic/control identities cannot produce a CLI secret. Aliases resolve identical data. info has no implicit default |
| GitHub private reporting    | Enabled and read back as true through the repository API                                                                                         |
| Related public listings     | Website inventory and both org profile languages reviewed. Their existing research-preview descriptions remain accurate                          |

Remote CI, rendered default README and release delivery observations are recorded after they actually occur. The original v0.1.0 and v0.2.3 deliveries retain their historical verification records and assets.

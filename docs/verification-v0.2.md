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

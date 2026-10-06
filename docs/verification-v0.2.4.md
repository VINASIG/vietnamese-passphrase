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

The original v0.1.0 and v0.2.3 deliveries retain their historical verification records and assets.

## Published delivery

The [release workflow](https://github.com/VINASIG/vietnamese-passphrase/actions/runs/37454436087), [tag-source CI](https://github.com/VINASIG/vietnamese-passphrase/actions/runs/37454436092) and [main-source CI](https://github.com/VINASIG/vietnamese-passphrase/actions/runs/37454021226) all passed at 5186565b1a06e83e771777cdf33cb36a76cf67b9. Both complete build jobs passed, distribution files matched across Linux and Windows, and the publish job's exact version/notes/artifact guard passed before attestation and release creation.

All four delivered files were downloaded, compared against the reviewed local distribution, and verified with gh attestation verify using the expected repository, signer workflow, exact source digest, tag ref and denial of self-hosted runners. The release title and body matched the exact v0.2.4 notes file. The [delivery record](publication-v0.2.4.json) contains observed sizes, hashes and policy. The prior v0.1.0 and v0.2.3 asset sizes and digests still matched their recorded deliveries through GitHub API readback.

The integration ZIP was independently extracted with PowerShell/.NET. All eight catalog profiles passed info checks. Six allowed profiles passed disposable generation checks, and two diagnostic/control profiles were blocked without secret output. Source, policy, catalog and license bytes matched the reviewed source. Generated secrets were not retained.

Fresh anonymous Chromium sessions read the actual public repository README, Vietnamese translation and security-policy page. Both README first tables contained current experimental profiles, with v0.2.4 ahead of historical references. SECURITY.md displayed the private reporting and response policy. These observations verify rendered Markdown content. GitHub stylesheet/layout behavior was not assessed. Repository details and the enabled private-reporting setting were read back separately. Related org and website listings remained accurate research-preview links and were not rewritten.

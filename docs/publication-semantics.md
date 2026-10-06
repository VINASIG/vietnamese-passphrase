# Publication and profile semantics

## Current repository and release channel

The default branch is main. Its README is the current product entrypoint and must lead with the current research preview, experimental catalog, evidence and limitations. It must not lead with the old v0.1 vocabulary table or use historical baseline commands as its normal quick start. The Vietnamese translation follows the same order and links the same preview.

Before this follow-up, main already described v0.2.3. The misleading part was publication emphasis. Both READMEs led into the old vocabulary table, and the Vietnamese version linked v0.1 before v0.2.3. Quick starts selected `vi` or `vi-ascii`. A reader could reasonably conclude that the old data remained the product recommendation.

GitHub release checks on 6 October 2026 found v0.1.0 and v0.2.3 both marked prerelease, neither marked latest, and the stable releases/latest API returned 404. The reviewer wording that the default view still exposed v0.1 was accurate about the README's emphasis, not evidence that main was an old branch or that v0.1 was a stable latest release. [GitHub's release API](https://docs.github.com/en/rest/releases/releases#get-the-latest-release) excludes drafts and prereleases from latest. The project keeps its actual preview channel and points readers to an explicit version. It does not remove the prerelease designation to obtain a latest badge.

`release.json` is the machine-readable current release identity. The exact-tag notes are checked against package.json, the root lockfile version and its package entry. The notes path must be docs/releases/TAG.md and its heading must name that version. The build record binds the source, package version, tag and notes digest. The publish job validates asset filenames, digests and the build record before attestation and publication. Missing or stale notes are an error, with no fallback. The release title includes the version and evidence channel, and publication explicitly keeps latest false.

## Evidence-bearing catalog names

The [catalog](../research/profile-catalog.json) separates canonical product identities from immutable data IDs. Experimental names say agent assessment. Historical names say baseline and revision. Control and diagnostic names say their intended role. These labels are scope declarations, not a claim of human validation. Transform details, exact paths and digests stay available in info and manifests.

Old data IDs remain deprecated CLI aliases. They resolve to the same pinned bytes and inherit the same generation restrictions. Names do not modify sample space, entropy or existing data versions. `info` requires an explicit profile, and `profiles` discovers all roles without generating a secret. The short diagnostic and matched native control cannot generate through the current CLI or Python example. The generic wordlist library does not implement those catalog restrictions for downstream callers.

The [historical baseline record](historical-baselines.md) explains the retired short profile. The [research roadmap](research-roadmap.md) separates additional automated uncertainty reduction from claims requiring people. The [security policy](../SECURITY.md) supplies the private reporting channel and maintenance/disclosure scope.

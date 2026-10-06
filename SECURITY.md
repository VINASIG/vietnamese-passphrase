# Security policy

## Supported revisions

This project is an SI-agent-assessed research preview. Security maintenance is best effort, not production assurance or a staffed incident-response service.

| Revision                                 | Maintenance                                                               |
| ---------------------------------------- | ------------------------------------------------------------------------- |
| Latest published v0.2.x research preview | Current fixes and coordinated disclosure                                  |
| Earlier v0.2.x releases                  | Superseded. Report findings, but upgrade to the current preview for fixes |
| v0.1.0 software                          | Retired. Immutable data and archives remain available for reproduction    |
| main                                     | Development work, not a released security guarantee                       |

There is no supported stable release. A vocabulary's integrity or modeled entropy does not establish memorability, appropriate content or deployment fitness. The short historical list is diagnostic-only and unavailable for generation in the current CLI and Python example. The generic library accepts caller-supplied lists and does not enforce the CLI catalog's usage policy.

## Report privately

Use [GitHub private vulnerability reporting](https://github.com/VINASIG/vietnamese-passphrase/security/advisories/new). Select Report a vulnerability in this repository's Security tab. The channel is enabled for this public repository. Do not post an exploitable report in a public issue or pull request.

Include the affected source commit or release, data profile and digest, environment, reproducible steps, expected and observed behavior, and a minimal synthetic fixture. Describe the impact and suggested fix if known. Report biased sampling, incorrect entropy assumptions, format collisions, unexpected secret logging or network access, unsafe parsing or resource exhaustion, data integrity failures, and release or provenance substitution. A finding in an older release is still welcome even if fixes target the current preview.

Never submit a real password, recovery phrase, token, private key, personal corpus or account data. Public test vectors and disposable synthetic inputs are enough. Testing this project's own local code does not authorize access to downstream accounts, third-party services or other people's information.

If GitHub's private channel is unavailable, open an issue containing only a request for a private security contact. Omit vulnerability details and secrets until a private channel is agreed. Do not assume an unverified email address is a security inbox.

## Triage and disclosure

The initial response target is seven calendar days and the update target during active triage is every fourteen days. These are best-effort targets, not guaranteed response times. Reports are assessed by reproducibility and impact, including the sampling distribution, effective output space and affected delivery artifacts. SI-agent investigation does not become an independent security audit.

For an accepted report, record affected commits, releases and data digests, assess downstream impact, develop a fix and regression fixture, and publish a security advisory with mitigation and upgrade guidance. Agree the disclosure date with the reporter. Use ninety days after acknowledgement as an initial planning target, adjust by agreement, and publish sooner when an actively exploited issue or readily available mitigation warrants it. The policy does not demand indefinite nondisclosure or promise a bounty.

Published wordlist bytes and release assets are not rewritten to hide a finding. A correction receives a new version, comparison and advisory where appropriate. Dangerous historical material can be clearly deprecated or withdrawn from recommended use without silently replacing its bytes. Credit reporters with their consent and avoid including secrets in the advisory.

Ordinary spelling suggestions and content-policy disagreements can use public issues with non-sensitive examples. A demonstrated security consequence belongs in the private channel. [Assurance](docs/assurance.md) and [release verification](docs/release-security.md) explain the scope of existing checks.

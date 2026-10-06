# Release origin and reproducibility

The current release identity is in [release.json](../release.json). A future v0.2.x tag must match the package version, both lockfile version entries, exact-tag notes path and heading, and the research-preview channel. Missing or stale notes fail without a fallback. The release builder includes the exact notes hash and tag in its build record. The publish job checks identity again against the delivered archive names, source commit and checksum manifest before attestation. Release titles name the version and evidence channel, and latest is explicitly false. The [negative publication tests](../tests/publication_test.py) exercise a v0.2.5 fixture and stale, missing, mismatched and corrupt inputs. Read [publication semantics](publication-semantics.md) for the default entrypoint and profile roles.

v0.1.0 used locally built archives and download/hash verification. Its tag and assets are immutable. No historical CI attestation is claimed.

From v0.2.5, CI and release jobs select ubuntu-24.04/Python 3.12.14 and windows-2025-vs2026/Python 3.14.8. These explicit OS labels avoid the automatic latest-label OS migration. [GitHub's announcement](https://github.com/actions/runner-images/issues/14748) schedules ubuntu-latest's migration to Ubuntu 26.04 to begin on 19 October 2026 and finish by 19 November. Explicit OS labels still receive image updates; [runner image documentation](https://github.com/actions/runner-images#image-releases) describes that update cadence. The project does not claim an immutable or hermetically preserved environment.

Both environments build from the same committed Git bytes, avoiding checkout CRLF changes entering package inputs. They run integrity, generator, separately implemented data checks, vocabulary-oracle and deterministic research checks. The release builder uses the standard library ZIP_STORED format with sorted entries, a fixed DOS date of 1980-01-01, fixed Unix file modes and no extra fields. No deflate compressor participates in these output archives. This costs larger downloads. Plain wordlists remain separately reusable. Publication fails unless all four distribution files match across environments. Byte equality is observed for the tested environment pair; arbitrary future compressors or toolchain versions are not assumed identical.

The schema-2 build-record.json names two environment records: environment-ubuntu-24.04.json and environment-windows-2025-vs2026.json. Each record observes the runner's exact ImageOS and ImageVersion, OS release/version, architecture, hosting type, actual Python/Unicode/Node/npm/Git versions and workflow run/ref/attempt. [GitHub's image variables](https://github.com/actions/runner-images/discussions/7661) supply the image identity. Only these selected fields are captured; no full environment dump, credentials or local paths are included. Dependency lock hashes and all four distribution hashes bind each record to the selected commit and package version. Capture in ordinary CI records that CI ref; publication requires both records to identify the same exact-tag run, matching pins and artifact bytes. Missing image observations or mismatches fail before signing.

The four shared distribution files are compared byte for byte. Environment records intentionally differ and are separate evidence assets, not inputs to the deterministic archives. The publish job validates and attests all six files before releasing them. Their observed fields depend on the trusted workflow; the manifests and signatures do not prove that the host was uncompromised. They identify a tested environment and do not contain a restorable VM/container image, complete OS inventory or digest-pinned toolchain binaries. Long-term hermetic reproducibility remains unestablished. This bounded change adds environment evidence without a new container platform or dependencies.

The source archive includes the complete tracked repository, portable baseline evidence and the pinned external snapshot. The integration package includes executable source, scripts, tests, data, experimental profiles and notices. The historical original-source archive remains available with v0.1.0; raw original production inputs are not silently claimed to be in the new portable source archive.

The publisher has OIDC and attestation permissions only after both builds succeed. Full action commit IDs are pinned. [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations) provide keyless signed build-origin evidence. They do not certify trustworthy maintainers, uncompromised dependencies, linguistic approval, user performance or an independent security audit. This workflow attests the compared artifacts in its publish job; it is not claimed to be a hardened reusable SLSA builder.

Download the selected release and verify each asset against the exact repository, workflow, source digest and tag reference you intend to trust. For example, substitute the release's reviewed source commit for SOURCE_COMMIT:

```sh
gh release download v0.2.5 --repo VINASIG/vietnamese-passphrase
gh attestation verify vinasig-vietnamese-passphrase-0.2.5.zip \
  --repo VINASIG/vietnamese-passphrase \
  --signer-workflow VINASIG/vietnamese-passphrase/.github/workflows/release.yml \
  --source-digest SOURCE_COMMIT \
  --source-ref refs/tags/v0.2.5 \
  --deny-self-hosted-runners
```

Repeat for the source archive, build record, checksum file and both environment records. Check the attested build record's commit against the chosen source and compare artifact digests. The checksum file covers the two archives and build record; each separately attested environment record contains hashes for all four shared files. Verify the environment signatures before relying on their contents. A mutable repository name alone is too broad a trust policy. A checksum and file obtained from the same untrusted channel can both be replaced; a valid signature from an unintended repository or workflow is also insufficient.

After publication, download and verify actual delivered bytes and signatures. Record the run, exact commit and results separately from this procedure. Preserve negative results rather than bypassing cross-environment comparison.

The integration ZIP contains a package/ directory. Extract it before running its CLI or installing that directory locally. These ZIP files are not registry-published npm tarballs. Original v0.1.0 tarballs remain unchanged. The failed v0.2.0, v0.2.1 and v0.2.2 tags document packaging iterations; no release assets were published for them.

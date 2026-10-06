# Release origin and reproducibility

The current release identity is in [release.json](../release.json). A future v0.2.x tag must match the package version, both lockfile version entries, exact-tag notes path and heading, and the research-preview channel. Missing or stale notes fail without a fallback. The release builder includes the exact notes hash and tag in its build record. The publish job checks identity again against the delivered archive names, source commit and checksum manifest before attestation. Release titles name the version and evidence channel, and latest is explicitly false. The [negative publication tests](../tests/publication_test.py) exercise a future v0.2.5 fixture and stale, missing, mismatched and corrupt inputs. Read [publication semantics](publication-semantics.md) for the default entrypoint and profile roles.

v0.1.0 used locally built archives and download/hash verification. Its tag and assets are immutable. No historical CI attestation is claimed.

The v0.2 release workflow builds on Linux/Python 3.12.14 and Windows/Python 3.14.8 from the same committed Git bytes. This avoids checkout CRLF changes entering package inputs. Both environments run integrity, generator, independent data, vocabulary-oracle and deterministic research checks. The release builder uses the standard library ZIP_STORED format with sorted entries, a fixed DOS date of 1980-01-01, fixed Unix file modes and no extra fields. No deflate compressor participates in these output archives. This costs larger downloads. Plain wordlists remain separately reusable. Publication fails unless all four distribution files match across environments. Byte equality is observed for the tested environment pair; arbitrary future compressors or toolchain versions are not assumed identical.

The source archive includes the complete tracked repository, portable baseline evidence and the pinned external snapshot. The integration package includes executable source, scripts, tests, data, experimental profiles and notices. The historical original-source archive remains available with v0.1.0; raw original production inputs are not silently claimed to be in the new portable source archive.

The publisher has OIDC and attestation permissions only after both builds succeed. Full action commit IDs are pinned. [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations) provide keyless signed build-origin evidence. They do not certify trustworthy maintainers, uncompromised dependencies, linguistic approval, user performance or an independent security audit. This workflow attests the compared artifacts in its publish job; it is not claimed to be a hardened reusable SLSA builder.

Download the selected release and verify each asset against the exact repository, workflow, source digest and tag reference you intend to trust. For example, substitute the release's reviewed source commit for SOURCE_COMMIT:

```sh
gh release download v0.2.4 --repo VINASIG/vietnamese-passphrase
gh attestation verify vinasig-vietnamese-passphrase-0.2.4.zip \
  --repo VINASIG/vietnamese-passphrase \
  --signer-workflow VINASIG/vietnamese-passphrase/.github/workflows/release.yml \
  --source-digest SOURCE_COMMIT \
  --source-ref refs/tags/v0.2.4 \
  --deny-self-hosted-runners
```

Repeat for the source archive, build record and checksum file. Check the attested build record's commit against the chosen source and compare artifact digests. A mutable repository name alone is too broad a trust policy. A checksum and file obtained from the same untrusted channel can both be replaced; a valid signature from an unintended repository or workflow is also insufficient.

After publication, download and verify actual delivered bytes and signatures. Record the run, exact commit and results separately from this procedure. Preserve negative results rather than bypassing cross-environment comparison.

The integration ZIP contains a package/ directory. Extract it before running its CLI or installing that directory locally. These ZIP files are not registry-published npm tarballs. Original v0.1.0 tarballs remain unchanged. The failed v0.2.0, v0.2.1 and v0.2.2 tags document packaging iterations; no release assets were published for them.

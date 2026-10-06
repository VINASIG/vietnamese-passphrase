"""Fail closed on release identity, notes and delivered asset metadata."""

import argparse
import dataclasses
import hashlib
import json
import os
import pathlib
import re
import subprocess
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read_object(path: pathlib.Path) -> dict[str, Any]:
    value: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected a metadata object")
    return value


@dataclasses.dataclass(frozen=True)
class Release:
    tag: str
    version: str
    notes: str
    notes_sha256: str
    title: str


def validate(root: pathlib.Path, tag: str | None = None) -> Release:
    metadata = read_object(root / "release.json")
    selected = metadata.get("tag") if tag is None else tag
    if not isinstance(selected, str) or re.fullmatch(r"v0\.2\.(0|[1-9][0-9]*)", selected) is None:
        raise ValueError("Expected an exact v0.2.x tag")
    if metadata.get("schema") != 1 or metadata.get("channel") != "research-preview":
        raise ValueError("Release metadata must declare the research-preview channel")
    if metadata.get("tag") != selected:
        raise ValueError("Tag and current release metadata differ")
    version = selected[1:]
    package = read_object(root / "package.json")
    lock = read_object(root / "package-lock.json")
    locked_packages = lock.get("packages")
    if not isinstance(locked_packages, dict):
        raise ValueError("Lockfile packages must be an object")
    locked_package = locked_packages.get("", {})
    if not isinstance(locked_package, dict) or any(
        entry.get("version") != version for entry in (package, lock, locked_package)
    ):
        raise ValueError("Tag, package and lockfile versions differ")
    if package.get("private") is not True:
        raise ValueError("The research package must retain its private npm setting")
    notes = "docs/releases/" + selected + ".md"
    if metadata.get("notes") != notes:
        raise ValueError("Release notes must match the exact tag, without a fallback")
    path = root / notes
    if not path.is_file() or path.is_symlink():
        raise ValueError("Exact release notes are missing or are a symbolic link")
    content = path.read_bytes()
    lines = content.decode("utf-8", errors="strict").splitlines()
    if not lines or lines[0] != "# Vietnamese Passphrase " + version:
        raise ValueError("Release notes heading does not match the tag")
    if "Release channel - research preview" not in lines:
        raise ValueError("Release notes must explicitly identify the preview channel")
    return Release(
        selected,
        version,
        notes,
        hashlib.sha256(content).hexdigest(),
        "Vietnamese Passphrase " + version + " agent-assessed research preview",
    )


def validate_assets(folder: pathlib.Path, release: Release, source: str) -> None:
    names = {
        "source-" + release.tag + ".zip",
        "vinasig-vietnamese-passphrase-" + release.version + ".zip",
    }
    expected = names | {"build-record.json", "SHA256SUMS.txt"}
    entries = list(folder.iterdir())
    if {p.name for p in entries} != expected or any(
        not p.is_file() or p.is_symlink() for p in entries
    ):
        raise ValueError("Release assets must be exactly the four expected regular files")
    record = read_object(folder / "build-record.json")
    if (
        record.get("sourceCommit") != source
        or record.get("packageVersion") != release.version
        or record.get("releaseTag") != release.tag
        or record.get("releaseNotesSha256") != release.notes_sha256
    ):
        raise ValueError("Artifact source, version, tag or notes digest differs")
    actual = {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in names}
    if record.get("sha256") != actual:
        raise ValueError("Archive digests do not match the build record")
    actual["build-record.json"] = hashlib.sha256(
        (folder / "build-record.json").read_bytes()
    ).hexdigest()
    checksums = "".join(f"{digest}  {name}\n" for name, digest in sorted(actual.items()))
    if (folder / "SHA256SUMS.txt").read_bytes() != checksums.encode("ascii"):
        raise ValueError("Checksum manifest does not match the delivered assets")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag")
    parser.add_argument("--assets", type=pathlib.Path)
    parser.add_argument("--github-output", action="store_true")
    args = parser.parse_args()
    release = validate(ROOT, args.tag)
    if args.assets:
        source = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        validate_assets(args.assets, release, source)
    fields = {"tag": release.tag, "notes": release.notes, "title": release.title}
    if args.github_output:
        output = os.environ.get("GITHUB_OUTPUT")
        if not output:
            raise ValueError("GITHUB_OUTPUT is required")
        with pathlib.Path(output).open("a", encoding="utf-8", newline="\n") as stream:
            stream.write("".join(f"{key}={value}\n" for key, value in fields.items()))
    print(
        json.dumps(
            {"status": "RELEASE_IDENTITY_PASS", **dataclasses.asdict(release)}, sort_keys=True
        )
    )


if __name__ == "__main__":
    main()

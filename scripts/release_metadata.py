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
BUILD_ENVIRONMENTS = {
    "ubuntu-24.04": ("Linux", "ubuntu24", "3.12.14"),
    "windows-2025-vs2026": ("Windows", "win25", "3.14.8"),
}


def environment_records() -> dict[str, str]:
    return {label: "environment-" + label + ".json" for label in BUILD_ENVIRONMENTS}


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
        record.get("schema") != 2
        or record.get("environmentRecords") != environment_records()
        or record.get("sourceCommit") != source
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


def validate_environment(
    path: pathlib.Path,
    label: str,
    folder: pathlib.Path,
    release: Release,
    source: str,
    root: pathlib.Path = ROOT,
    expected_ref: str | None = None,
) -> dict[str, Any]:
    validate_assets(folder, release, source)
    if label not in BUILD_ENVIRONMENTS or path.name != environment_records()[label]:
        raise ValueError("Unexpected environment identity")
    if not path.is_file() or path.is_symlink():
        raise ValueError("Missing regular environment record")
    value = read_object(path)
    if (
        value.get("schema") != 1
        or value.get("sourceCommit") != source
        or value.get("releaseTag") != release.tag
        or value.get("packageVersion") != release.version
    ):
        raise ValueError("Environment record is not bound to this source and release")
    expected_os, image_prefix, python = BUILD_ENVIRONMENTS[label]
    runner = value.get("runner")
    tools = value.get("tools")
    run = value.get("run")
    if not all(isinstance(part, dict) for part in (runner, tools, run)):
        raise ValueError("Missing runner, tools or run observations")
    assert isinstance(runner, dict) and isinstance(tools, dict) and isinstance(run, dict)
    image_os = runner.get("imageOS")
    image_version = runner.get("imageVersion")
    if (
        runner.get("label") != label
        or runner.get("os") != expected_os
        or runner.get("arch") != "X64"
        or runner.get("environment") != "github-hosted"
        or not isinstance(image_os, str)
        or (image_os != image_prefix and not image_os.startswith(image_prefix + "-"))
        or not isinstance(image_version, str)
        or re.fullmatch(r"[0-9]{8}\.[0-9]+(?:\.[0-9]+)?", image_version) is None
        or any(
            not isinstance(runner.get(key), str) or not runner[key]
            for key in ("release", "version")
        )
    ):
        raise ValueError("Missing or mismatched hosted-runner image observations")
    node = (root / ".node-version").read_text(encoding="utf-8").strip().removeprefix("v")
    manager = read_object(root / "package.json").get("packageManager")
    if not isinstance(manager, str) or not manager.startswith("npm@"):
        raise ValueError("Expected a pinned npm package manager")
    if (
        tools.get("python") != python
        or tools.get("node") != "v" + node
        or tools.get("npm") != manager.removeprefix("npm@")
        or tools.get("pythonImplementation") != "CPython"
        or any(not isinstance(tools.get(key), str) or not tools[key] for key in ("git", "unicode"))
    ):
        raise ValueError("Observed toolchain does not match the selected pins")
    if run.get("ref") != (expected_ref or "refs/tags/" + release.tag) or any(
        not isinstance(run.get(key), str) or re.fullmatch(r"[1-9][0-9]*", run[key]) is None
        for key in ("id", "attempt")
    ):
        raise ValueError("Missing or mismatched workflow identity")
    expected_hashes = {
        file.name: hashlib.sha256(file.read_bytes()).hexdigest() for file in folder.iterdir()
    }
    lock_hashes = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in ("package-lock.json", "requirements-dev.txt")
    }
    if value.get("artifacts") != expected_hashes or value.get("dependencyLocks") != lock_hashes:
        raise ValueError("Environment record does not bind the delivered artifacts and locks")
    return value


def validate_environments(
    builds: pathlib.Path, release: Release, source: str, root: pathlib.Path = ROOT
) -> None:
    records = []
    for label, name in environment_records().items():
        folder = builds / label
        entries = list((folder / "environment").iterdir())
        if {entry.name for entry in entries} != {name}:
            raise ValueError("Expected exactly one environment record per build")
        records.append(
            validate_environment(
                folder / "environment" / name, label, folder / "release", release, source, root
            )
        )
    if records[0]["run"] != records[1]["run"]:
        raise ValueError("Environment records came from different workflow runs")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag")
    parser.add_argument("--assets", type=pathlib.Path)
    parser.add_argument("--environments", type=pathlib.Path)
    parser.add_argument("--github-output", action="store_true")
    args = parser.parse_args()
    release = validate(ROOT, args.tag)
    if args.assets:
        source = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        validate_assets(args.assets, release, source)
        if args.environments:
            validate_environments(args.environments, release, source)
    elif args.environments:
        parser.error("Environment verification requires --assets")
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

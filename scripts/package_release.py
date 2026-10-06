"""Build distributions from committed Git bytes; compare OS rebuilds before publication."""

import argparse
import hashlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import tarfile
import zipfile
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]


def archive(path: pathlib.Path, files: dict[str, tuple[bytes, int]]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as output:
        for name, (data, mode) in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100000 | mode) << 16
            info.compress_type = zipfile.ZIP_STORED
            output.writestr(info, data)


def build(destination: pathlib.Path) -> None:
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    raw = subprocess.check_output(["git", "archive", "--format=tar", "HEAD"], cwd=ROOT)
    destination.mkdir(parents=True, exist_ok=True)
    stage = destination / "staging"
    if stage.exists():
        raise ValueError("Use a fresh output folder")
    stage.mkdir()
    source: dict[str, tuple[bytes, int]] = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as tar:
        for member in tar:
            if member.isdir():
                continue
            parts = pathlib.PurePosixPath(member.name)
            if not member.isfile() or parts.is_absolute() or ".." in parts.parts:
                raise ValueError("Unsupported source archive member")
            file = tar.extractfile(member)
            if file is None:
                raise ValueError("Missing archive content")
            data = file.read()
            target = stage.joinpath(*parts.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            source[member.name] = (data, 0o755 if member.mode & 0o111 else 0o644)
    package = json.loads((stage / "package.json").read_text(encoding="utf-8"))
    version = package["version"]
    if not isinstance(version, str) or not version.replace(".", "").isdigit():
        raise ValueError("Unexpected release version")
    if (
        os.environ.get("GITHUB_REF_TYPE") == "tag"
        and os.environ.get("GITHUB_REF_NAME") != "v" + version
    ):
        raise ValueError("Tag and package version differ")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if npm is None:
        raise ValueError("Pinned npm must be on PATH")
    for args in [
        ["ci", "--ignore-scripts"],
        ["run", "build"],
        ["pack", "--ignore-scripts"],
    ]:
        subprocess.run(
            [npm, *args], cwd=stage, text=True, encoding="utf-8", capture_output=True, check=True
        )
    candidates = list(stage.glob("*.tgz"))
    expected_name = (
        str(package["name"]).removeprefix("@").replace("/", "-") + "-" + version + ".tgz"
    )
    if len(candidates) != 1 or candidates[0].name != expected_name or candidates[0].is_symlink():
        raise ValueError("npm pack did not produce the single expected artifact")
    packed = candidates[0]
    files = {}
    with tarfile.open(packed, mode="r:gz") as tar:
        for member in tar:
            if not member.isfile():
                raise ValueError("Unexpected package archive member")
            file = tar.extractfile(member)
            if file is None:
                raise ValueError("Missing package content")
            files[member.name] = (file.read(), 0o755 if member.mode & 0o111 else 0o644)
    package_path = destination / ("vinasig-vietnamese-passphrase-" + version + ".zip")
    archive(package_path, files)
    source_path = destination / ("source-v" + version + ".zip")
    archive(
        source_path,
        {"vietnamese-passphrase-" + version + "/" + name: value for name, value in source.items()},
    )
    hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [package_path, source_path]
    }
    record: dict[str, Any] = {
        "schema": 1,
        "sourceCommit": revision,
        "packageVersion": version,
        "sha256": hashes,
        "archive": "sorted ZIP_STORED, fixed DOS date 1980-01-01, Unix file modes and no extra fields",
        "assurance": "build origin and byte reproducibility; not vocabulary or independent audit approval",
    }
    record_path = destination / "build-record.json"
    record_path.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    hashes[record_path.name] = hashlib.sha256(record_path.read_bytes()).hexdigest()
    (destination / "SHA256SUMS.txt").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in sorted(hashes.items())),
        encoding="ascii",
        newline="\n",
    )
    print(json.dumps({"source": revision, "assets": hashes}, sort_keys=True))


def compare(a: pathlib.Path, b: pathlib.Path) -> None:
    def digests(folder: pathlib.Path) -> dict[str, str]:
        return {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.iterdir()
            if p.is_file()
        }

    left, right = digests(a), digests(b)
    if len(left) != 4 or left != right:
        raise ValueError("Distribution bytes differ across environments")
    print(json.dumps({"status": "BYTE_REBUILD_PASS", "sha256": left}, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path)
    parser.add_argument("--compare", type=pathlib.Path, nargs=2)
    args = parser.parse_args()
    if args.compare:
        compare(*args.compare)
    elif args.out:
        build(args.out)
    else:
        parser.error("Choose --out or --compare")


if __name__ == "__main__":
    main()

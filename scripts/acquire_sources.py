"""Explicitly download pinned research sources. Never execute upstream code."""

import argparse
import hashlib
import json
import pathlib
import urllib.request
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRODUCTION = {
    "wiktionary-en-vi.jsonl",
    "wiktionary-vi.jsonl.gz",
    "wordfreq-vi.msgpack.gz",
    "tatoeba-vie-detailed.tsv.bz2",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=pathlib.Path, required=True)
    parser.add_argument("--scope", choices=["production", "benchmark"], default="production")
    args = parser.parse_args()
    lock: dict[str, Any] = json.loads((ROOT / "data/source-lock.json").read_text(encoding="utf-8"))
    args.dest.mkdir(parents=True, exist_ok=True)
    for source in lock["sources"]:
        name = source["file"]
        if args.scope == "production" and name not in PRODUCTION:
            continue
        if (
            pathlib.Path(name).name != name
            or not source["url"].startswith("https://")
            or not 0 < source["bytes"] < 128 * 1024 * 1024
        ):
            raise ValueError("Unsafe source descriptor")
        target = args.dest / name
        if target.exists():
            data = target.read_bytes()
        else:
            with urllib.request.urlopen(source["url"], timeout=60) as response:
                if not response.geturl().startswith("https://"):
                    raise ValueError("An upstream redirect left HTTPS")
                data = response.read(source["bytes"] + 1)
        if len(data) != source["bytes"] or hashlib.sha256(data).hexdigest() != source["sha256"]:
            raise ValueError(
                "Source snapshot changed. Do not replace its recorded hash. Use the preserved snapshot or review a new data revision."
            )
        if not target.exists():
            with target.open("xb") as stream:
                stream.write(data)
        print(name + " PASS")


if __name__ == "__main__":
    main()

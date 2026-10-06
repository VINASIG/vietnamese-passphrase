"""Build agent-assessed alternatives without changing released data or claiming an optimum."""

import collections
import hashlib
import json
from typing import Any

from vocabulary_audit import ROOT, close_pairs, diagnose, external_counts, fold, write_json

VERSION = "2026-10-06.agent-1"
DEST = ROOT / "research/experimental" / VERSION


def content_candidates(
    tokens: list[str], policy: dict[str, Any]
) -> tuple[list[str], list[dict[str, Any]]]:
    excluded: dict[str, list[str]] = collections.defaultdict(list)
    for category, item in policy["categories"].items():
        for token in item["tokens"]:
            if token not in tokens:
                raise ValueError("Policy token missing from baseline: " + token)
            excluded[token].append(category)
    aliases: dict[str, str] = {}
    for family in policy["variantFamilies"]:
        if family["representative"] not in family["members"]:
            raise ValueError("Invalid variant representative")
        for token in family["members"]:
            if token not in tokens or token in aliases:
                raise ValueError("Missing or repeated variant member: " + token)
            aliases[token] = family["representative"]
    ledger = []
    selected = []
    for token in tokens:
        categories = excluded.get(token, [])
        alias = aliases.get(token, token)
        disposition = (
            "exclude-context"
            if categories
            else "consolidate-variant"
            if alias != token
            else "candidate"
        )
        ledger.append(
            {
                "token": token,
                "assessment": "agent-headword-screened",
                "disposition": disposition,
                "categories": categories,
                "representative": alias,
                "scope": "headword only; unflagged is not harmless certification",
            }
        )
        if disposition == "candidate":
            selected.append(token)
    return selected, ledger


def distinct_subset(tokens: list[str]) -> list[str]:
    neighbors: dict[int, set[int]] = {i: set() for i in range(len(tokens))}
    for i, j, _ in close_pairs(tokens, 1):
        neighbors[i].add(j)
        neighbors[j].add(i)
    remaining = set(neighbors)
    chosen = []
    while remaining:
        index = min(
            remaining, key=lambda i: (len(neighbors[i] & remaining), len(tokens[i]), tokens[i])
        )
        chosen.append(tokens[index])
        remaining.difference_update(neighbors[index] | {index})
    return sorted(chosen)


def main() -> None:
    baseline = (ROOT / "data/lists/vi.txt").read_text(encoding="utf-8").splitlines()
    policy_bytes = (ROOT / "research/content-policy.json").read_bytes()
    policy = json.loads(policy_bytes)
    display, ledger = content_candidates(baseline, policy)
    counts, external = external_counts()
    ascii_groups: dict[str, list[str]] = collections.defaultdict(list)
    for token in display:
        ascii_groups[fold(token)].append(token)
    native_for_ascii = [min(ascii_groups[key]) for key in sorted(ascii_groups)]
    profiles = {
        "vi-display": display,
        "vi-fused": sorted(x.replace("_", "") for x in display),
        "vi-ascii-display": sorted(ascii_groups),
        "vi-ascii-native": native_for_ascii,
        "vi-distinct": distinct_subset(display),
    }
    if len(set(profiles["vi-fused"])) != len(display):
        raise ValueError("Fused representation is not injective")
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "decisions.jsonl").write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            for row in ledger
        ),
        encoding="utf-8",
        newline="\n",
    )
    write_json(
        DEST / "ascii-classes.json",
        [
            {"ascii": key, "members": values, "representative": min(values)}
            for key, values in sorted(ascii_groups.items())
        ],
    )
    metrics = {}
    manifest: dict[str, Any] = {
        "schema": 1,
        "version": VERSION,
        "status": "experimental-agent-assessment",
        "baseline": "2026-10-06.1",
        "policySha256": hashlib.sha256(policy_bytes).hexdigest(),
        "noRecommendedDefault": True,
        "profiles": {},
    }
    projected: collections.Counter[str] = collections.Counter()
    for token, count in counts.items():
        projected[fold(token)] += count
    fused_counts: collections.Counter[str] = collections.Counter()
    for token, count in counts.items():
        fused_counts[token.replace("_", "")] += count
    for name, values in profiles.items():
        path = DEST / (name + ".txt")
        data = ("\n".join(values) + "\n").encode("utf-8")
        path.write_bytes(data)
        manifest["profiles"][name] = {
            "file": path.name,
            "entries": len(values),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        comparison = (
            projected
            if name == "vi-ascii-display"
            else fused_counts
            if name == "vi-fused"
            else counts
        )
        measured = diagnose(values, dict(comparison))
        write_json(DEST / (name + ".audit.json"), measured)
        metrics[name] = {k: v for k, v in measured.items() if not k.endswith("Details")}
    write_json(DEST / "manifest.json", manifest)
    write_json(
        DEST / "comparison.json",
        {
            "schema": 1,
            "policyVersion": VERSION,
            "external": external,
            "decisions": dict(
                sorted(collections.Counter(x["disposition"] for x in ledger).items())
            ),
            "profiles": metrics,
            "distinctionObjective": "greedy maximal subset without NFC codepoint edit-distance-one neighbors; not a proven maximum or measured error reduction",
            "asciiRepresentatives": "codepoint-first native member, not presumed most familiar; paired by identical index",
            "limitations": [
                "All profiles are experiments",
                "Unflagged senses and phrase combinations may be sensitive",
                "No independent or human assessment",
                "No proof of an optimal vocabulary or memorability gain",
            ],
        },
    )
    print(json.dumps({"version": VERSION, "entries": {k: len(v) for k, v in profiles.items()}}))


if __name__ == "__main__":
    main()

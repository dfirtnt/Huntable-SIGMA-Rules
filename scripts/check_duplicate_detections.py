#!/usr/bin/env python3
"""Fail on rules whose detection logic duplicates another rule's; warn on near-duplicates.

`sigma check` guarantees unique ids, titles and filenames -- none of which
stops the same detection landing twice under two names, which is what an
automated generator fed the same intel twice will produce. This compares the
*logic*:

- exact: the ``detection`` block, normalised (keys sorted, scalar strings
  case-folded and whitespace-trimmed, lists sorted), hashes identically
  -> exit 1
- near: the two rules' atom sets (``field|modifiers=value``) have Jaccard
  similarity >= NEAR_THRESHOLD -> printed as a warning, exit 0

Usage: check_duplicate_detections.py rules/
"""

from __future__ import annotations

import hashlib
import itertools
import json
import pathlib
import sys

import yaml

NEAR_THRESHOLD = 0.8


def _normalise(node):
    if isinstance(node, dict):
        return {str(k): _normalise(v) for k, v in sorted(node.items(), key=lambda kv: str(kv[0]))}
    if isinstance(node, list):
        return sorted((_normalise(v) for v in node), key=lambda v: json.dumps(v, sort_keys=True))
    if isinstance(node, str):
        return " ".join(node.casefold().split())
    return node


def _atoms(detection: dict) -> set[str]:
    atoms: set[str] = set()
    for name, body in detection.items():
        if name == "condition":
            continue
        items = body if isinstance(body, list) else [body]
        for item in items:
            if isinstance(item, dict):
                for field, value in item.items():
                    values = value if isinstance(value, list) else [value]
                    for v in values:
                        atoms.add(f"{field}={_normalise(v)}")
            elif isinstance(item, str):  # keyword list
                atoms.add(f"keyword={_normalise(item)}")
    return atoms


def _load_rules(root: pathlib.Path) -> list[tuple[str, dict]]:
    rules = []
    for path in sorted(root.rglob("*.yml")):
        try:
            docs = [d for d in yaml.safe_load_all(path.read_text(encoding="utf-8")) if isinstance(d, dict)]
        except yaml.YAMLError:
            continue  # sigma check reports YAML problems; not this script's job
        for doc in docs:
            detection = doc.get("detection")
            if isinstance(detection, dict):
                rules.append((str(path.relative_to(root.parent)), detection))
    return rules


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    root = pathlib.Path(argv[1])
    rules = _load_rules(root)
    if not rules:
        print(f"ERROR: no rules with a detection block found under {root}", file=sys.stderr)
        return 2

    by_hash: dict[str, list[str]] = {}
    for name, detection in rules:
        digest = hashlib.sha256(json.dumps(_normalise(detection), sort_keys=True).encode()).hexdigest()
        by_hash.setdefault(digest, []).append(name)

    exact = [names for names in by_hash.values() if len(names) > 1]
    for names in exact:
        print("ERROR: identical detection logic in:")
        for n in names:
            print(f"    {n}")

    atoms = {name: _atoms(det) for name, det in rules}
    near = []
    for (a, sa), (b, sb) in itertools.combinations(atoms.items(), 2):
        if not sa or not sb:
            continue
        j = len(sa & sb) / len(sa | sb)
        if j >= NEAR_THRESHOLD and not any(a in g and b in g for g in exact):
            near.append((j, a, b))
    for j, a, b in sorted(near, reverse=True):
        print(f"WARNING: near-duplicate detection logic (Jaccard {j:.2f}):\n    {a}\n    {b}")

    print(f"{len(rules)} rules checked: {len(exact)} exact duplicate group(s), {len(near)} near-duplicate pair(s).")
    return 1 if exact else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

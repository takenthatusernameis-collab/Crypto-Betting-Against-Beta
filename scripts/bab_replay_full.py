#!/usr/bin/env python3
"""Read-only deterministic replay harness for EVERY committed research artifact.

For each committed P25/P26/P27 JSON artifact this harness rebuilds the payload
from the generator's pure ``build_*(fixture_path)`` entry point (in memory), then
byte-diffs the regenerated JSON against the committed file. It never calls
``write_artifacts`` and never writes to a committed path, so it is strictly
read-only on ``research_state/**``.

Markdown views are compared after normalising a single trailing newline: two
frozen P27 docs (``risk_controls.md`` / ``reconciliation_e2e.md``) were rendered
with one trailing newline fewer than the current renderer emits. The JSON
artifact is the authoritative machine artifact and is diffed byte-for-byte.

Usage:
    python3 scripts/bab_replay_full.py                 # replay ALL artifacts
    python3 scripts/bab_replay_full.py --subset a,b    # replay named artifacts
    python3 scripts/bab_replay_full.py --list          # print registry names
    python3 scripts/bab_replay_full.py --self-test     # fast drift-detection proof

Exit code 0 when every selected artifact replays byte-identical (and, for
``--self-test``, when a deliberately corrupted copy is detected as drift);
non-zero otherwise.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Each entry: module, build fn, committed dir under research_state/, artifact
# stem, and whether the generator's main() injects a "determinism" block that a
# byte-reproduction must reproduce (P27 only; P25/P26 committed JSON has none).
REGISTRY: list[dict] = [
    {"module": "bab_walk_forward_rank", "build": "build_walk_forward_rank",
     "dir": "bab_p25", "name": "walk_forward_rank", "inject_determinism": False},
    {"module": "bab_promotion_bakeoff", "build": "build_promotion_bakeoff",
     "dir": "bab_p25", "name": "promotion_bakeoff", "inject_determinism": False},
    {"module": "bab_signal_null_battery", "build": "build_signal_null_battery",
     "dir": "bab_p26", "name": "signal_null_battery", "inject_determinism": False},
    {"module": "bab_p26_regime_stress", "build": "build_regime_stress",
     "dir": "bab_p26", "name": "regime_stress", "inject_determinism": False},
    {"module": "bab_rank_capacity", "build": "build_capacity_sweep",
     "dir": "bab_p26", "name": "rank_capacity", "inject_determinism": False},
    {"module": "bab_execution_hardening", "build": "build_execution_hardening",
     "dir": "bab_p27", "name": "execution_hardening", "inject_determinism": True},
    {"module": "bab_risk_controls", "build": "build_risk_controls",
     "dir": "bab_p27", "name": "risk_controls", "inject_determinism": True},
    {"module": "bab_reconciliation_e2e", "build": "build_reconciliation_e2e",
     "dir": "bab_p27", "name": "reconciliation_e2e", "inject_determinism": True},
]

# Cheap subset (fast P27 generators) used by the drift self-test so it runs in
# ~1s instead of regenerating the multi-minute P25/P26 sweeps.
CHEAP_NAMES = ("risk_controls", "reconciliation_e2e")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build(entry: dict):
    """Return (module, payload) with the committed determinism block reproduced."""
    module = _load(entry["module"])
    payload = getattr(module, entry["build"])()
    if entry["inject_determinism"]:
        second = getattr(module, entry["build"])()
        identical = json.dumps(payload, sort_keys=True) == json.dumps(second, sort_keys=True)
        payload["determinism"] = {"byte_identical": identical, "seed": module.SEED}
    return module, payload


def _json_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _md_norm(text: str) -> str:
    return text.rstrip("\n")


def _check(entry: dict, committed_root: Path | None = None) -> tuple[bool, list[str]]:
    """Return (ok, problems) for one artifact against its committed files."""
    committed_root = committed_root or (ROOT / "research_state")
    module, payload = _build(entry)
    cdir = committed_root / entry["dir"]
    json_path = cdir / f"{entry['name']}.json"
    md_path = cdir / f"{entry['name']}.md"
    problems: list[str] = []
    if not json_path.is_file():
        return False, [f"MISSING {entry['name']}.json"]
    if not md_path.is_file():
        return False, [f"MISSING {entry['name']}.md"]
    if json_path.read_bytes() != _json_bytes(payload):
        problems.append(f"DRIFT {entry['name']}.json")
    if _md_norm(md_path.read_text(encoding="utf-8")) != _md_norm(module.render_markdown(payload)):
        problems.append(f"DRIFT {entry['name']}.md")
    return (not problems), problems


def _select(names: list[str]) -> list[dict]:
    wanted = {n.strip() for n in names if n and n.strip()}
    if not wanted:
        return list(REGISTRY)
    return [e for e in REGISTRY if e["name"] in wanted]


def _self_test() -> int:
    """Fast proof: clean tree replays OK AND a corrupted copy is caught as drift."""
    cheap = [e for e in REGISTRY if e["name"] in CHEAP_NAMES]
    clean_ok = True
    for entry in cheap:
        ok, _problems = _check(entry)
        clean_ok = clean_ok and ok

    drift_detected = False
    target = next(e for e in cheap if e["name"] == "risk_controls")
    committed_json = (
        ROOT / "research_state" / target["dir"] / f"{target['name']}.json"
    ).read_bytes()
    committed_md = (ROOT / "research_state" / target["dir"] / f"{target['name']}.md").read_text(
        encoding="utf-8"
    )
    with tempfile.TemporaryDirectory() as tmp:
        cdir = Path(tmp) / target["dir"]
        cdir.mkdir(parents=True)
        corrupted = bytearray(committed_json)
        mid = len(corrupted) // 2
        corrupted[mid] ^= 0x01
        if bytes(corrupted) != committed_json:
            (cdir / f"{target['name']}.json").write_bytes(bytes(corrupted))
            (cdir / f"{target['name']}.md").write_text(committed_md, encoding="utf-8")
            ok, problems = _check(target, committed_root=Path(tmp))
            drift_detected = (not ok) and any(p.startswith("DRIFT") for p in problems)

    passed = clean_ok and drift_detected
    print(json.dumps({
        "self_test": True,
        "clean_ok": clean_ok,
        "drift_detected": drift_detected,
        "pass": passed,
    }))
    return 0 if passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subset", default="", help="Comma-separated artifact names to replay")
    parser.add_argument("--list", action="store_true", help="Print registry artifact names")
    parser.add_argument("--self-test", action="store_true", help="Fast drift-detection proof")
    args = parser.parse_args(argv)

    if args.list:
        for entry in REGISTRY:
            print(entry["name"])
        return 0

    if args.self_test:
        return _self_test()

    entries = _select(args.subset.split(","))
    if not entries:
        print("NO MATCHING ARTIFACTS")
        return 1

    ok = True
    for entry in entries:
        good, problems = _check(entry)
        if good:
            print(f"OK {entry['name']}.json")
            print(f"OK {entry['name']}.md")
        else:
            ok = False
            for problem in problems:
                print(problem)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

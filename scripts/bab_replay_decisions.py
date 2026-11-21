#!/usr/bin/env python3
"""Read-only deterministic replay of P29 decision docs, sidecars, and JSONL sidecars.

Reproduces, byte-for-byte:
  * docs/BAB_P25_DECISION.md            (from generate_p25_decision.py)
  * docs/BAB_P26_DECISION.md            (from generate_p26_decision.py)
  * docs/BAB_P27_DECISION.md            (from generate_p27_decision.py)
  * research_state/bab_p27/p27_decision_sidecar.json  (from generate_p27_decision.py)
  * research_state/bab_p27/paper_orders.jsonl         (from scripts/bab_execution_hardening.py)
  * research_state/bab_p27/paper_diagnostics.jsonl    (from scripts/bab_execution_hardening.py)

Each decision generator resolves its output path from a module-level constant at
import time, so this harness rewrites those constants into a temp dir (source
rewrite + exec) and never writes to a committed path. The JSONL sidecars are
produced by calling the writer's ``_write_jsonl`` directly onto temp paths.
Every regenerated output is then byte-diffed against the committed file.

Usage:
    python3 scripts/bab_replay_decisions.py                 # replay ALL
    python3 scripts/bab_replay_decisions.py --subset a,b    # named subset
    python3 scripts/bab_replay_decisions.py --list          # print registry names
    python3 scripts/bab_replay_decisions.py --self-test     # drift-detection proof

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

# Each entry: generator module, kind, committed output path, registry name,
# source rewrites (old source substring -> output filename redirected to temp),
# and the output filename this entry checks after regeneration.
REGISTRY: list[dict] = [
    {
        "module": "generate_p25_decision",
        "kind": "decision_doc",
        "name": "p25_decision",
        "path": ROOT / "docs/BAB_P25_DECISION.md",
        "source_root": ROOT,
        "output_filename": "BAB_P25_DECISION.md",
        "rewrites": [
            ('REPO_ROOT / "docs/BAB_P25_DECISION.md"', "BAB_P25_DECISION.md"),
        ],
    },
    {
        "module": "generate_p26_decision",
        "kind": "decision_doc",
        "name": "p26_decision",
        "path": ROOT / "docs/BAB_P26_DECISION.md",
        "source_root": ROOT,
        "output_filename": "BAB_P26_DECISION.md",
        "rewrites": [
            ('REPO_ROOT / "docs/BAB_P26_DECISION.md"', "BAB_P26_DECISION.md"),
        ],
    },
    {
        "module": "generate_p27_decision",
        "kind": "decision_doc",
        "name": "p27_decision",
        "path": ROOT / "docs/BAB_P27_DECISION.md",
        "source_root": ROOT,
        "output_filename": "BAB_P27_DECISION.md",
        "rewrites": [
            ('REPO_ROOT / "docs/BAB_P27_DECISION.md"', "BAB_P27_DECISION.md"),
            ('RESEARCH_P27_DIR / "p27_decision_sidecar.json"', "p27_decision_sidecar.json"),
        ],
    },
    {
        "module": "generate_p27_decision",
        "kind": "decision_sidecar",
        "name": "p27_decision_sidecar",
        "path": ROOT / "research_state/bab_p27/p27_decision_sidecar.json",
        "source_root": ROOT,
        "output_filename": "p27_decision_sidecar.json",
        "rewrites": [
            ('REPO_ROOT / "docs/BAB_P27_DECISION.md"', "BAB_P27_DECISION.md"),
            ('RESEARCH_P27_DIR / "p27_decision_sidecar.json"', "p27_decision_sidecar.json"),
        ],
    },
    {
        "module": "bab_execution_hardening",
        "kind": "jsonl",
        "name": "paper_orders",
        "path": ROOT / "research_state/bab_p27/paper_orders.jsonl",
        "source_root": ROOT / "scripts",
        "output_filename": "paper_orders.jsonl",
        "records_key": "orders",
    },
    {
        "module": "bab_execution_hardening",
        "kind": "jsonl",
        "name": "paper_diagnostics",
        "path": ROOT / "research_state/bab_p27/paper_diagnostics.jsonl",
        "source_root": ROOT / "scripts",
        "output_filename": "paper_diagnostics.jsonl",
        "records_key": "diagnostics",
    },
]

# Cheap entries (render from committed JSON, no full campaign run) used by the
# drift self-test so it runs in seconds instead of minutes.
CHEAP_NAMES = ("p25_decision", "p26_decision")


def _load(module_name: str, source_root: Path):
    spec = importlib.util.spec_from_file_location(
        module_name, source_root / f"{module_name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _exec_redirected(
    module_name: str,
    source_root: Path,
    rewrites: list[tuple[str, Path]],
    tmpdir: Path,
):
    """Exec the generator source with its output constants redirected into tmpdir.

    ``__file__`` is pinned to the real scripts path so ``REPO_ROOT`` (and every
    read-only input path) resolves against the real repo; only the output
    constants are rewritten to land in ``tmpdir``. Committed files are never
    written.
    """
    source = (source_root / f"{module_name}.py").read_text(encoding="utf-8")
    for old_substr, temp_path in rewrites:
        source = source.replace(
            old_substr, "Path(" + repr(str(temp_path)) + ")"
        )
    spec = importlib.util.spec_from_file_location(
        module_name, source_root / f"{module_name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    module.__dict__["__file__"] = str(source_root / f"{module_name}.py")
    module.__dict__["__name__"] = module_name
    module.__dict__["__package__"] = None
    code = compile(source, str(source_root / f"{module_name}.py"), "exec")
    exec(code, module.__dict__)
    return module


def _check(entry: dict, committed_root: Path, tmpdir: Path, build_cache: dict) -> tuple[
    bool, list[str]
]:
    """Return (ok, problems) for one artifact against its committed file.

    Regenerated output always lands in ``tmpdir`` (temp, auto-cleaned). The
    committed target is read from ``committed_root`` (defaults to the real repo
    root; a scratch/corrupted root is used by ``--self-test``).
    """
    committed_path = committed_root / entry["path"].relative_to(ROOT)
    problems: list[str] = []
    if not committed_path.is_file():
        return False, [f"MISSING {entry['name']} at {committed_path}"]
    kind = entry["kind"]
    if kind in ("decision_doc", "decision_sidecar"):
        rewrites = [(old, tmpdir / fname) for old, fname in entry["rewrites"]]
        _exec_redirected(
            entry["module"], entry["source_root"], rewrites, tmpdir
        )
        generated = tmpdir / entry["output_filename"]
        if not generated.is_file():
            return False, [f"MISSING generated {entry['output_filename']}"]
        if generated.read_bytes() != committed_path.read_bytes():
            problems.append(f"DRIFT {entry['name']}")
    else:  # jsonl
        module = build_cache.get(entry["module"])
        if module is None:
            module = _load(entry["module"], entry["source_root"])
            build_cache[entry["module"]] = module
        payload = module.build_execution_hardening()
        records = payload["paper"][entry["records_key"]]
        generated = tmpdir / entry["output_filename"]
        module._write_jsonl(generated, records)
        if generated.read_bytes() != committed_path.read_bytes():
            problems.append(f"DRIFT {entry['name']}")
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
    build_cache: dict = {}
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        for entry in cheap:
            ok, _ = _check(entry, ROOT, td_path, build_cache)
            clean_ok = clean_ok and ok

    drift_detected = False
    target = next(e for e in cheap if e["name"] == "p25_decision")
    committed = target["path"].read_bytes()
    with tempfile.TemporaryDirectory() as scratch:
        scratch_path = Path(scratch)
        target_rel = target["path"].relative_to(ROOT)
        corrupt_target = scratch_path / target_rel
        corrupt_target.parent.mkdir(parents=True, exist_ok=True)
        corrupted = bytearray(committed)
        mid = len(corrupted) // 2
        corrupted[mid] ^= 0x01
        if bytes(corrupted) != committed:
            corrupt_target.write_bytes(bytes(corrupted))
            with tempfile.TemporaryDirectory() as td:
                td_path = Path(td)
                ok, problems = _check(target, scratch_path, td_path, build_cache)
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
    build_cache: dict = {}
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        for entry in entries:
            good, problems = _check(entry, ROOT, td_path, build_cache)
            if good:
                print(f"OK {entry['name']}")
            else:
                ok = False
                for problem in problems:
                    print(problem)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

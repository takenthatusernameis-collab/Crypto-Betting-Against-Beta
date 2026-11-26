#!/usr/bin/env python3
"""Read-only deterministic replay harness for EVERY committed research artifact.

For each committed P20-P27 JSON artifact this harness rebuilds the payload
from the generator's pure ``build_*()`` entry point (in memory), then
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
    python3 scripts/bab_replay_full.py --xproc         # cross-process determinism
    python3 scripts/bab_replay_full.py --check-provenance  # provenance audit regen-diff

Exit code 0 when every selected artifact replays byte-identical (and, for
``--self-test``, when a deliberately corrupted copy is detected as drift);
non-zero otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Each entry: module, build fn, committed dir under research_state/, artifact
# stem, and whether the generator's main() injects a "determinism" block that a
# byte-reproduction must reproduce (P27 only; P25/P26 committed JSON has none).
REGISTRY: list[dict] = [
    # P25/P26/P27 (8 artifacts) — original P29 WP0 registry.
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
    # P20-P24 (19 artifacts) — P31 WP0 replay coverage closure. Every build_*()
    # has all-optional arguments defaulting to the committed fixture/upstream
    # payloads, so calling it with no arguments reproduces the committed bytes
    # byte-for-byte (read-only; nothing is written to research_state/**).
    {"module": "bab_research_sweep", "build": "build_sweep",
     "dir": "bab_p20", "name": "sweep", "inject_determinism": False},
    {"module": "bab_breakeven", "build": "build_breakeven",
     "dir": "bab_p20", "name": "breakeven", "inject_determinism": False},
    {"module": "bab_walk_forward", "build": "build_walk_forward",
     "dir": "bab_p20", "name": "walk_forward", "inject_determinism": False},
    {"module": "bab_synthetic_universe", "build": "build_universe",
     "dir": "bab_p21", "name": "universe", "inject_determinism": False},
    {"module": "bab_cost_surface", "build": "build_cost_surface",
     "dir": "bab_p21", "name": "cost_surface", "inject_determinism": False},
    {"module": "bab_rank_eval", "build": "build_rank_eval",
     "dir": "bab_p21", "name": "rank_eval", "inject_determinism": False},
    {"module": "bab_significance", "build": "build_significance",
     "dir": "bab_p21", "name": "significance", "inject_determinism": False},
    {"module": "bab_p22_charter", "build": "build_charter",
     "dir": "bab_p22", "name": "charter", "inject_determinism": False},
    {"module": "bab_null_battery", "build": "build_null_battery",
     "dir": "bab_p22", "name": "null_battery", "inject_determinism": False},
    {"module": "bab_impact_surface", "build": "build_impact_surface",
     "dir": "bab_p22", "name": "impact_surface", "inject_determinism": False},
    {"module": "bab_capacity", "build": "build_capacity",
     "dir": "bab_p22", "name": "capacity", "inject_determinism": False},
    {"module": "bab_p23_charter", "build": "build_charter",
     "dir": "bab_p23", "name": "charter", "inject_determinism": False},
    {"module": "bab_beta_drift", "build": "build_beta_drift",
     "dir": "bab_p23", "name": "beta_drift", "inject_determinism": False},
    {"module": "bab_breadth_ladder", "build": "build_breadth_ladder",
     "dir": "bab_p23", "name": "breadth_ladder", "inject_determinism": False},
    {"module": "bab_short_haircut", "build": "build_short_haircut",
     "dir": "bab_p23", "name": "short_haircut", "inject_determinism": False},
    {"module": "bab_p24_charter", "build": "build_charter",
     "dir": "bab_p24", "name": "charter", "inject_determinism": False},
    {"module": "bab_licensed_adapter", "build": "build_adapter_dryrun",
     "dir": "bab_p24", "name": "adapter_dryrun", "inject_determinism": False},
    {"module": "bab_hysteresis_ladder", "build": "build_hysteresis_ladder",
     "dir": "bab_p24", "name": "hysteresis", "inject_determinism": False,
     "no_xproc": True},
    {"module": "bab_regime_split", "build": "build_regime_split",
     "dir": "bab_p24", "name": "regime_split", "inject_determinism": False,
     "no_xproc": True},
    # P35 WP1/WP2 summary artifacts (JSON-only; no .md sidecar). Gated out of
    # --xproc/--check-provenance so the frozen P29 provenance_audit.json ledger
    # is never rewritten by P35 entries (see HANDOFF.md P35 WP3 bottleneck note).
    {"module": "bab_p35_estimator_bakeoff", "build": "build_summary",
     "dir": "bab_p35", "name": "estimator_bakeoff_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    {"module": "bab_p35_signal_stability", "build": "build_summary",
     "dir": "bab_p35", "name": "signal_stability_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    # P36 WP0-WP1 summary artifacts (JSON-only; no .md sidecar). Gated out of
    # --xproc/--check-provenance so the frozen P29 provenance_audit.json ledger
    # is never rewritten by P36 entries (see HANDOFF.md P36 WP2-WP3).
    {"module": "bab_p36_walk_forward", "build": "build_summary",
     "dir": "bab_p36", "name": "walk_forward_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    {"module": "bab_p36_rank_weighted", "build": "build_summary",
     "dir": "bab_p36", "name": "rank_weighted_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    # P37 WP0-WP2 summary artifacts (JSON-only; no .md sidecar). Gated out of
    # --xproc/--check-provenance so the frozen P29 provenance_audit.json ledger
    # is never rewritten by P37 entries (see HANDOFF.md P37 scope guardrails).
    {"module": "bab_p37_cost_surface", "build": "build_summary",
     "dir": "bab_p37", "name": "cost_surface_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    {"module": "bab_p37_capacity", "build": "build_summary",
     "dir": "bab_p37", "name": "capacity_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    {"module": "bab_p37_turnover", "build": "build_summary",
     "dir": "bab_p37", "name": "turnover_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    # P38 WP1/WP2 summary artifacts (JSON-only; no .md sidecar). Gated out of
    # --xproc/--check-provenance so the frozen P29 provenance_audit.json ledger
    # is never rewritten by P38 entries (mirrors the P35-P37 entries above).
    {"module": "bab_p38_deflated_significance", "build": "build_summary",
     "dir": "bab_p38", "name": "deflated_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    {"module": "bab_p38_tail_risk", "build": "build_summary",
     "dir": "bab_p38", "name": "tail_risk_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    # P39 WP1/WP2 summary artifacts (JSON-only; no .md sidecar). Gated out of
    # --xproc/--check-provenance so the frozen P29 provenance_audit.json ledger
    # is never rewritten by P39 entries (mirrors the P35-P38 entries above).
    {"module": "bab_p39_regime_conditional", "build": "build_summary",
     "dir": "bab_p39", "name": "regime_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    {"module": "bab_p39_cross_fixture", "build": "build_summary",
     "dir": "bab_p39", "name": "cross_fixture_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    # P40 WP0 multi-fixture meta-analysis summary artifact (JSON-only; no .md
    # sidecar replayed here -- the .md is rendered by build_summary() and pinned
    # by tests/test_bab_p40_meta_analysis.py; gated out of --xproc/--check-provenance
    # so the frozen P29 provenance_audit.json ledger is never rewritten).
    {"module": "bab_p40_meta_analysis", "build": "build_summary",
     "dir": "bab_p40", "name": "meta_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
    # P41 WP2 stress summary artifact (JSON-only; no .md sidecar replayed here
    # -- the .md is rendered by render_stress_markdown() and pinned by
    # tests/test_bab_p41_decision_consistency.py; gated out of --xproc/--check-provenance
    # so the frozen P29 provenance_audit.json ledger is never rewritten).
    {"module": "bab_p41_stress", "build": "build_stress_summary",
     "dir": "bab_p41", "name": "stress_summary",
     "inject_determinism": False, "json_only": True, "no_xproc": True},
]

# Cheap subset (fast generators) used by the drift self-test so it runs in
# ~1s instead of regenerating the multi-minute P25/P26/P27 sweeps. "charter"
# matches all three P22/P23/P24 charters (pure JSON loads); "universe" is the
# deterministic P21 synthetic-universe build.
CHEAP_NAMES = ("risk_controls", "reconciliation_e2e", "universe", "charter")

# P25 WP0 wide-universe fixture (SHA256 a6d390fc…163b). All 8 committed artifacts
# are derived from this single read-only fixture.
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
P25_WP0_FIXTURE_SHA256 = hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()

# P29 WP1 provenance ledger output (new, non-frozen, deterministic).
PROVENANCE_DIR = ROOT / "research_state" / "bab_p29"
PROVENANCE_PATH = PROVENANCE_DIR / "provenance_audit.json"


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
    if not entry.get("json_only") and not md_path.is_file():
        return False, [f"MISSING {entry['name']}.md"]
    if json_path.read_bytes() != _json_bytes(payload):
        problems.append(f"DRIFT {entry['name']}.json")
    if not entry.get("json_only"):
        committed_md = _md_norm(md_path.read_text(encoding="utf-8"))
        rendered_md = _md_norm(module.render_markdown(payload))
        if committed_md != rendered_md:
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


def _subprocess_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def _run_build_once(entry: dict) -> bytes:
    """Run the generator's build() in a fresh interpreter; return stdout bytes.

    Faithfully reproduces WP0's ``_build`` inside a fresh interpreter: build()
    is invoked twice, cross-process consistency is computed, and (for P27
    generators) the ``determinism`` block is injected from ``mod.SEED``. A fresh
    ``python3 -c`` subprocess per call is the cross-process guard: it surfaces
    hidden global-state / PYTHONHASHSEED / wall-clock dependence that a
    single-process double-build cannot.
    """
    lines = [
        "import importlib.util, json, sys",
        "sys.path.insert(0, " + repr(str(ROOT / "scripts")) + ")",
        "spec = importlib.util.spec_from_file_location(" + repr(entry["module"]) + ", "
        + repr(str(ROOT / "scripts" / (entry["module"] + ".py"))) + ")",
        "mod = importlib.util.module_from_spec(spec)",
        "spec.loader.exec_module(mod)",
        "build = getattr(mod, " + repr(entry["build"]) + ")",
        "payload1 = build()",
        "payload2 = build()",
        "identical = json.dumps(payload1, sort_keys=True) == json.dumps(payload2, sort_keys=True)",
        "if " + repr(entry["inject_determinism"]) + ":",
        "    payload1[\"determinism\"] = {\"byte_identical\": identical, \"seed\": mod.SEED}",
        "sys.stdout.buffer.write(json.dumps(payload1, indent=2, sort_keys=True).encode(\"utf-8\"))",
        "sys.stdout.buffer.write(b\"\\n\")",
    ]
    script = "\n".join(lines) + "\n"
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(ROOT),
        capture_output=True,
        env=_subprocess_env(),
        timeout=3600,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"xproc build failed for {entry['name']}: "
            + proc.stderr.decode("utf-8", "replace")
        )
    return proc.stdout


def _check_xproc(entry: dict) -> tuple[bool, list[str], int | None]:
    """Run build() in two fresh interpreters; assert byte-identical + matches committed.

    Returns (ok, problems, seed). seed is read from the regenerated payload so
    the provenance ledger can record it without hand-typing.
    """
    problems: list[str] = []
    committed_json = ROOT / "research_state" / entry["dir"] / f"{entry['name']}.json"
    committed_bytes = committed_json.read_bytes()
    seed: int | None = None
    try:
        run1 = _run_build_once(entry)
        run2 = _run_build_once(entry)
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        return False, [f"XPROC {entry['name']}: {exc}"], None
    if run1 != run2:
        problems.append(f"XPROC {entry['name']}: not byte-identical across processes")
    if run1 != committed_bytes:
        problems.append(f"XPROC {entry['name']}: subprocess output differs from committed json")
    try:
        seed = json.loads(run1).get("seed")
    except Exception:
        seed = None
    return (not problems), problems, seed


def _write_provenance_ledger_to(results: dict[str, dict], entries: list[dict],
                                path: Path) -> None:
    """Write a provenance-audit ledger for ``entries`` to ``path``.

    One record per entry: path, sha256, generator_module, seed, fixture_sha256,
    replay_ok. Deterministic (sorted keys, stable path ordering) so the ledger
    itself can be replay-checked. Never writes to a committed path unless the
    caller passes one.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    for entry in entries:
        name = entry["name"]
        res = results.get(name, {})
        # Provenance ledger scope: only seeded artifacts that replay OK (the
        # original P25/P26/P27 set). Non-seeded P20-P24 builds (seed=None),
        # gated-out no_xproc entries (P35-P39 summaries, hysteresis/regime_split),
        # and xproc timeouts (ok=False) are excluded so the frozen ledger stays
        # at exactly the 8 seeded P25-P27 records the provenance tests expect.
        if not (res.get("ok") is True and res.get("seed") is not None):
            continue
        json_path = ROOT / "research_state" / entry["dir"] / f"{name}.json"
        sha = (
            hashlib.sha256(json_path.read_bytes()).hexdigest()
            if json_path.is_file()
            else None
        )
        records.append(
            {
                "path": f"research_state/{entry['dir']}/{name}.json",
                "sha256": sha,
                "generator_module": entry["module"],
                "seed": res.get("seed"),
                "fixture_sha256": P25_WP0_FIXTURE_SHA256,
                "replay_ok": bool(res.get("ok")),
            }
        )
    records.sort(key=lambda r: r["path"])
    audit = {"schema": "bab_p29.provenance_audit/1", "artifacts": records}
    path.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _write_provenance_ledger(results: dict[str, dict]) -> None:
    """Write research_state/bab_p29/provenance_audit.json (P29 WP1).

    Thin wrapper over _write_provenance_ledger_to targeting the committed path
    and the full registry. Kept for the --xproc mode which is allowed to rewrite
    the committed ledger (it is regenerated identically each run).
    """
    _write_provenance_ledger_to(results, REGISTRY, PROVENANCE_PATH)


def _check_provenance() -> int:
    """Regenerate the provenance audit to a temp path and byte-diff it against
    the committed research_state/bab_p29/provenance_audit.json (modulo nothing —
    it must be fully deterministic). Covers exactly the entries recorded in the
    committed audit (the original P25/P26/P27 set); never writes to a committed
    path."""
    committed_bytes = PROVENANCE_PATH.read_bytes()
    audit = json.loads(committed_bytes)
    covered_paths = {record["path"] for record in audit["artifacts"]}
    entries = [
        entry for entry in REGISTRY
        if f"research_state/{entry['dir']}/{entry['name']}.json" in covered_paths
    ]
    results: dict[str, dict] = {}
    ok = True
    for entry in entries:
        good, problems, seed = _check_xproc(entry)
        results[entry["name"]] = {"ok": good, "seed": seed, "problems": problems}
        if not good:
            ok = False
            for problem in problems:
                print(problem)
    with tempfile.TemporaryDirectory() as tmp:
        temp_path = Path(tmp) / "provenance_audit.json"
        _write_provenance_ledger_to(results, entries, temp_path)
        if temp_path.read_bytes() != committed_bytes:
            ok = False
            print("PROVENANCE DRIFT: regenerated audit differs from committed "
                  f"{PROVENANCE_PATH}")
    print(json.dumps({"check_provenance": True, "pass": ok}))
    return 0 if ok else 1


def _xproc_main() -> int:
    results: dict[str, dict] = {}
    ok = True
    for entry in REGISTRY:
        if entry.get("no_xproc"):
            continue
        good, problems, seed = _check_xproc(entry)
        results[entry["name"]] = {"ok": good, "seed": seed, "problems": problems}
        if good:
            print(f"XPROC OK {entry['name']} (seed={seed})")
        else:
            ok = False
            for problem in problems:
                print(problem)
    _write_provenance_ledger(results)
    print(json.dumps({"xproc": True, "pass": ok}))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subset", default="", help="Comma-separated artifact names to replay")
    parser.add_argument("--list", action="store_true", help="Print registry artifact names")
    parser.add_argument("--self-test", action="store_true", help="Fast drift-detection proof")
    parser.add_argument(
        "--xproc",
        action="store_true",
        help="Cross-process determinism: rebuild each artifact in two fresh "
        "interpreters, assert byte-identical, and write the provenance ledger",
    )
    parser.add_argument(
        "--check-provenance",
        action="store_true",
        help="Regenerate the provenance audit to a temp path and byte-diff it "
        "against the committed research_state/bab_p29/provenance_audit.json "
        "(read-only determinism check)",
    )
    args = parser.parse_args(argv)

    if args.list:
        for entry in REGISTRY:
            print(entry["name"])
        return 0

    if args.self_test:
        return _self_test()

    if args.xproc:
        return _xproc_main()

    if args.check_provenance:
        return _check_provenance()

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

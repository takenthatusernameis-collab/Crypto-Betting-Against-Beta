# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T08:57:30Z
- **HEAD:** `b7df039846bd790de468b0d8c9bc9a5b5ee88a7a`
- **State:** Gate 1 GREEN (898 passed, 5 skipped, rc=0, `/home/runner/work/_temp/kilo-tmp/c43_gate_gate1_20261112T085359Z.log`). Gate 2/3 reruns **in progress** at handoff write — confirm final rc/counts from `/home/runner/work/_temp/kilo-tmp/c43_gate_gate2_20261112T085359Z_bg.log` and `...gate3..._bg.log` before C43 probes.
- **Binding next task:** **C43 ROTATION** — (1) finalize Gate 2/3 on current HEAD with durable evidence, (2) execute ≥20 NEW adversarial probes (no C40–C42 reuse) across required surfaces/cross-interactions with per-probe durable logs, (3) smallest proven fix in allowed surfaces only + regression + full gates on any gap, (4) refresh `HANDOFF.md` with full matrix/evidence; if clean immediately define and start C44.

Do not use this file for details; follow `HANDOFF.md` exactly.

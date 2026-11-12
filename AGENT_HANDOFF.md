# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T13:29:20Z
- **HEAD:** `8bafd4d8c095493b59646b09ca542053faab7a2f`
- **State:** Tracked tree clean; deps OK (Python 3.12.3, `PYTHONPATH=.` from repo root). **C47 probes 38/38 PASS** (`/home/runner/work/_temp/kilo-tmp/c47_probes/`). **G1 GREEN** 898p/5s rc=0 (`c47_gates/gate1_20261112T132700Z.log`), **G3 GREEN** 164p rc=0 (`c47_gates/gate3_20261112T132700Z.log`), **G2 RUNNING/INCOMPLETE** ~22% no final rc (`c47_gates/gate2_20261112T132900Z.log`) — **C47 NOT CLOSED**.
- **Binding next task:** Wait for/complete Gate 2 with durable final summary+rc (rerun if interrupted); close C47 only when G2 green and G1/G3 valid. On any proven gap: smallest allowed fix + minimal regression + affected tests + full gates. **If C47 closes cleanly, immediately start C48** (≥20 NEW adversarial probes, no C40–C47 reuse; logs in `/home/runner/work/_temp/kilo-tmp/c48_probes/`, gates in `/home/runner/work/_temp/kilo-tmp/c48_gates/`) and record in `HANDOFF.md`. **Heavy execution required; no planning-only turn.**

Do not use this file for details; follow `HANDOFF.md` exactly.

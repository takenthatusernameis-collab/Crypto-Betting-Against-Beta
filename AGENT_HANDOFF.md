# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T13:38:40Z
- **HEAD:** `c2ae24bf0410dd3d260e5ba81b8965dabbeccb9f`
- **State:** Tracked tree clean; deps OK (Python 3.12.3, `PYTHONPATH=.`). **C47 probes 38/38 PASS** (`/home/runner/work/_temp/kilo-tmp/c47_probes/`). **G1 GREEN** (`c47_gates/gate1_20261112T132700Z.log`, rc=0, 898p/5s), **G3 GREEN** (`c47_gates/gate3_20261112T132700Z.log`, rc=0, 164p), **G2 INCOMPLETE/NOT GREEN** (partial `c47_gates/gate2_20261112T132900Z.log`) — **C47 NOT CLOSED**.
- **Binding next task:** **Complete Gate 2 now** with durable final summary+rc (`gate2_<ts>_final.log`). If rc!=0: smallest allowed fix + minimal regression + affected tests + all 3 gates. Close C47 only when G2 green and G1/G3 valid for same checkout. **If C47 closes cleanly, immediately start C48** (≥20 NEW adversarial probes, no C40–C47 reuse; `/home/runner/work/_temp/kilo-tmp/c48_probes/` + `c48_gates/`) and record in `HANDOFF.md`. **Heavy execution required; no planning-only turn.**

Do not use this file for details; follow `HANDOFF.md` exactly.

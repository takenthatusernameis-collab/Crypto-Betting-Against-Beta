# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T13:24:42Z
- **HEAD:** `feb776b9ae366f4cff6ebad53fe5c38ece63a6a0`
- **State:** Tracked tree clean; deps verified OK (Python 3.12.3). **C47 probes 38/38 PASS, 0 FAIL** (`/home/runner/work/_temp/kilo-tmp/c47_probes/`). **Gate 1 prior GREEN** (898p/5s rc=0); **Gate 2/3 INCOMPLETE/NON-GREEN** (partial logs only, no final summary/rc in `/home/runner/work/_temp/kilo-tmp/c47_gates/gate2_20261112T131500Z.log`, `gate3_20261112T131500Z.log`) — **C47 not closed**.
- **Binding next task:** Clear gate bottleneck by rerunning/finalizing C47 Gate 1/2/3 with durable completed logs+rc; close C47 only if all green. On any proven gap: smallest allowed fix + minimal regression + affected tests + full gates. **If C47 closes cleanly, immediately start C48** (≥20 NEW adversarial probes, no C40–C47 reuse; durable logs in `/home/runner/work/_temp/kilo-tmp/c48_probes/`, gates in `/home/runner/work/_temp/kilo-tmp/c48_gates/`) and record as binding next task in `HANDOFF.md`. **Heavy execution required; no planning-only turn.**

Do not use this file for details; follow `HANDOFF.md` exactly.

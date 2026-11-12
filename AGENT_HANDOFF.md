# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T12:11:07Z
- **HEAD:** `52f3b2e6aab5af68c666de7f917c90f1f9cd9bdb`
- **State:** C45 ROTATION complete — 43/43 probes PASS, 0 FAIL, no proven gaps. No code changes; deps re-imported OK; working tree clean. **Binding next task: C46 ROTATION** — preflight deps/env, gates as needed with durable logs in `/home/runner/work/_temp/kilo-tmp/c46_gates/`, execute ≥20 NEW adversarial probes (no C40–C45 reuse) with durable logs under `/home/runner/work/_temp/kilo-tmp/c46_probes/` per `HANDOFF.md`, apply smallest proven fixes in allowed surfaces only + regression + full gates on any gap, refresh `HANDOFF.md`; if clean immediately define and start **C47**.

Do not use this file for details; follow `HANDOFF.md` exactly.
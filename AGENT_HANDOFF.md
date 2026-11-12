# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T12:13:43Z
- **HEAD:** `b970f6db607a9fe002937fcf6d092717ba7066c8`
- **State:** Tracked tree clean; deps verified OK. C45 closed clean (43/43 PASS). **C46 ROTATION is OPEN/unexecuted** (c46_probes empty; c46_gates partial/stale) — no proven gaps may be claimed without ≥20 NEW C46 probes + durable logs.
- **Binding next task:** Execute **C46 ROTATION** per `HANDOFF.md`: preflight, (re-)run Gate 1/2/3 with durable logs in `/home/runner/work/_temp/kilo-tmp/c46_gates/` as needed, run ≥20 NEW adversarial probes (no C40–C45 reuse) with per-probe logs+summary in `/home/runner/work/_temp/kilo-tmp/c46_probes/`, apply smallest proven fixes in allowed surfaces only + regression + full gates on any gap, refresh `HANDOFF.md`/pointer; if clean immediately define and start **C47**.

Do not use this file for details; follow `HANDOFF.md` exactly.

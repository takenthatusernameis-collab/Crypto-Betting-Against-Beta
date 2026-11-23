# HANDOFF: Next Agentic Work Session — 2026-11-23T03:37:30Z

## Project Context
**Repository:** Crypto-Betting-Against-Beta
**Strategy:** Betting Against Beta (BAB) for crypto — long low-beta, short high-beta assets
**Current Campaign Status:** P27 (Production Readiness) concluded **NOT-READY** for live deployment; P35, P36, P37 all concluded **RETAIN** (shipped default retained)

## Blocker Summary (Must Resolve Before Progress)
| Blocker | Impact | Owner/Action |
|---------|--------|--------------|
| **No licensed market data** — Coinbase public API returns 403; network fetching forbidden in this environment | All campaigns since P22 carry `no_go_for_market: true`; P27 verdict explicitly NOT-READY for live deployment | Maintainer must supply licensed CSV (schema: `tests/fixtures/licensed_price_schema.csv`) |
| **CI gates not enforced** — `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh` not in CI | No automated quality gate; manual gate runs only | Requires `workflows:write` permission (maintainer-only) |
| **P26 returned NO-SIGNAL** on null (no-alpha) synthetic fixture | No reproducible rank-vs-noise signal on controlled synthetic universe | Requires real market data to evaluate signal |

## Current Artifact State (Read-Only)
- `research_state/bab_p27/` — execution hardening, risk controls, reconciliation E2E (WP0-WP2 complete)
- `research_state/bab_p35/` — estimator bakeoff + signal stability (176 cells, all neutrality pass)
- `research_state/bab_p36/` — walk-forward OOS + rank-weighted (80 WF cells + 8 RW seeds)
- `research_state/bab_p37/` — cost surface + capacity + turnover hysteresis (24 cells, all pass)
- `docs/BAB_P27_DECISION.md` — NOT-READY verdict with full provenance
- `docs/BAB_P35/36/37_DECISION.md` — RETAIN verdicts, all synthetic, no market alpha claimed

## Next Campaign: P38 — Real-Market Data Ingestion & Live-Readiness Gate
**Charter Binding Row:** P38 WP0
**Title:** Licensed market data ingestion + CI gate wire + live deployment readiness gate
**Lane:** D (Production)
**Artifact-Gated:** Yes — every number traces to committed JSON leaf
**Not Market Evidence:** Yes — synthetic provenance caveat applies until licensed data lands

### Work Packages (In Order)
| WP | Title | Deliverable | Acceptance |
|----|-------|-------------|------------|
| **P38 WP0** | **Charter** — define licensed CSV schema, ingestion pipeline, CI gate spec, live-readiness criteria | `generate_p38_charter.py` → `docs/BAB_P38_KICKOFF.md` (JSON charter) | Charter matches P37 schema; `licensed_data_required: true`; `no_go_for_market: true` until data lands |
| **P38 WP1** | **Data Ingestion** — implement `load_licensed_prices()` in `data_loader.py`; validate against schema; emit `licensed_fixture_sha256` | `research_state/bab_p38/licensed_ingestion.json` | All schema checks pass; SHA256 committed; fixture labelled `controlled synthetic` if synthetic fallback used |
| **P38 WP2** | **CI Gate Wire** — add `ruff`, `bab_gate.sh`, `bab_reconcile_gate.sh` to GitHub Actions (requires maintainer `workflows:write`) | `.github/workflows/bab_gate.yml` + `bab_reconcile_gate.yml` | Gates run on PR; fail closed on any violation; artifacts uploaded |
| **P38 WP3** | **Live-Readiness Decision** — re-run P27 infrastructure on licensed data; emit `READY`/`NOT-READY` with real-market provenance | `docs/BAB_P38_DECISION.md` + `research_state/bab_p38/live_readiness.json` | Verdict strings verified: `READY`/`NOT-READY`, `dry_run=true`, `no implicit live`, `licensed data`, `market evidence` |

### Hard Requirements (Non-Negotiable)
1. **No network calls in tests/CI** — all data via committed fixtures or maintainer-supplied CSV
2. **Artifact-gated decisions** — every published number must resolve to a committed JSON leaf (6 dp)
3. **Synthetic provenance caveat** — if licensed data unavailable, fall back to controlled synthetic fixture with explicit labelling
4. **Fail-closed gates** — any gate violation exits non-zero; no silent degradation
5. **Byte-identical reports** — decision docs generated from JSON artifacts only; no hand-typed numbers

## Immediate Next Steps (Do This First)
1. **Check for licensed CSV** — look for `tests/fixtures/licensed_market_prices.csv` (or maintainer-supplied path)
2. **If CSV exists:** Run `generate_p38_charter.py` with real data provenance; proceed to WP1
3. **If CSV missing:** Run `generate_p38_charter.py` with synthetic fallback (explicit `controlled synthetic` label); document blocker in charter
4. **Wire CI gates** — requires maintainer with `workflows:write`; create PR with workflow files
5. **Run full gate** — `scripts/bab_gate.sh && scripts/bab_reconcile_gate.sh` must pass before any decision

## Commands to Verify State
```bash
# Check for licensed data
ls -la tests/fixtures/licensed_market_prices.csv 2>/dev/null || echo "MISSING: licensed data required"

# Run quality gate (if scripts exist)
./scripts/bab_gate.sh 2>&1 | tail -20
./scripts/bab_reconcile_gate.sh 2>&1 | tail -20

# Verify test suite passes
python -m pytest tests/test_bab_p37_decision_consistency.py -v --tb=short
python -m pytest tests/test_bab_p36_decision_consistency.py -v --tb=short
python -m pytest tests/test_bab_p35_decision_consistency.py -v --tb=short
python -m pytest tests/test_bab_p27_decision_consistency.py -v --tb=short

# Lint
ruff check .
```

## Handoff Protocol
- This file (`HANDOFF_NEXT_SESSION.md`) is the **single durable handoff** for the next session
- Next agent **must read this file first** before any work
- Next agent **must run verification commands** above to confirm state
- Next agent **must not** start new campaigns without resolving blockers
- All work must be artifact-gated: JSON → decision doc → consistency test

## Timestamp
**Handoff Created:** 2026-11-23T03:37:30Z
**Next Session Should Start:** Immediately after reading this file
**Escalation:** If licensed data unavailable after 2 sessions, escalate to maintainer for data procurement
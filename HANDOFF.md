# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T05:34:03Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `7e281b1` (`chore(kilo): checkpoint agent session`, local `main`/worktree context; prior session base in file was `1d9f342` content-refresh checkpoint)
**Working tree:** **dirty/untracked** — `tests/test_bab_cli_campaign11q_followup_probe_regressions.py` added this session (33 tests, green). No production code changed. No commits/pushes. Tracked `probe*`/`debug*`/`ast_probe.py` untouched.

**Environment/gates (re-verified this session @ `7e281b1`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `python3 -m pytest -q tests/test_bab_cli_campaign11m_probe_regressions.py tests/test_bab_cli_campaign11n_expanded_probe_regressions.py tests/test_bab_cli_campaign11o_remaining_probe_regressions.py tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py` → **83 passed, rc=0** (28+18+19+18)
- `python3 -m pytest -q tests/test_bab_cli_campaign11q_followup_probe_regressions.py` → **33 passed, rc=0** (new probe locks this session)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3994 deselected, 53 warnings, rc=0**
- `python3 -m pytest -q -k "not data_loader and not controller"` → **2099 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** in 288.65s (baseline floor before this session’s 11q file existed; re-run after adding/adjusting 11q to confirm ≥2103 passed/5 skipped expected — do as Step 0 before further edits)

**Bottlenecks removed:** Step 0 gates re-run; campaign_d green; prior `data_loader`/`controller` exclusion baseline stable. No `.bab_active`/session-lock artifacts observed.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

You are continuing **campaign11 follow-up** for `Crypto-Betting-Against-Beta` from this tree. Objective: keep producing probe-backed evidence on exercised BAB CLI/backtest surfaces and land minimal regressions/fixes only for proven gaps.

1. **Stabilize baseline:** run Step 0 gates (deps, 11m≥28, 11n≥18, 11o≥19, 11p≥18, 11q≥33, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2099/5 adjusted for new 11q coverage). Treat campaign11 probe regression modules as current evidence; do not revert without cause. Fix any regression before production edits.
2. **Execute next heavy probe matrix (§NEXT FOCUS)** against `tests/fixtures/real_market_prices.csv`, `tests/fixtures/real_market_prices_expanded.csv`, and constrained synthetic/temp inputs. For every probe capture command, `rc`, relevant `stdout`/`stderr`, and JSON/output snippets. Probe combinations until evidence is obtained (pass or proven gap) — no single-pass/no-evidence exits.
3. **Triage evidence:** for each proven, non-duplicative gap add focused regression test(s) in `tests/test_bab_*campaign11*` (new module per coherent cluster). If a real bug is proven, apply the smallest production fix in exercised, non-gate-closed code (`cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` only as justified) plus regression coverage.
4. **Validate:** run touched/new tests, then `campaign_d`, then full BAB excl `data_loader`/`controller` (record before/after counts/rc). Record before/after.
5. **Refresh this HANDOFF.md** before finishing: timestamp, HEAD/base state, dirty-state, commands+counts+rc, probes run with evidence summary, gaps found/fixed (or explicit "no proven gaps" per area), modules touched, and the next binding slice. Keep this file the single durable handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. No planning-only exit. No no-evidence exit.

---

## CAMPAIGN11 follow-up — EVIDENCE THIS SESSION (2026-11-10T05:18Z–05:34Z @ 7e281b1)

### Probe matrix executed & locked

| # | Combo | Evidence | Verdict |
|---|-------|----------|---------|
| 1 | **Dry-run semantic audit (before fix):** `--dry-run` vs real run for `--long-quantile 0.6 --short-quantile 0.6` on `REAL` from-prices | dry-run rc=0 prints `(valid, --from-prices=True)`; real run rc=0 finite `Final cumulative return: 0.480526 Periods: 398` | Characterized: dry-run does not reject quantile-sum≥1; run accepts per current contract. Locked in 11q. |
| 2 | Dry-run vs run `--universe ZZZ,YYY` (zero overlap) on `REAL` from-prices | dry-run rc=0 `(valid)` reports `universe: ['ZZZ,YYY']`; real run rc=1 clean `Error running strategy: configured universe ['ZZZ,YYY'] has no overlap with data columns ...` no Traceback | Semantic gap characterized (dry-run validates loadability, not run-time overlap). Locked in 11q. |
| 3 | Dry-run vs run `--universe ,,,` (all-empty after split semantics) on `REAL` from-prices | dry-run rc=0 `(valid)` reports `universe: [',,,']`; real run rc=1 clean overlap error, no Traceback | Characterized/locked in 11q. |
| 4 | **Real fixture from-prices CLI parity** via `--output` JSON on `REAL`+`EXP`, combos (0.001/0.0005/daily, 0.01/0/daily, 0/0.01/weekly, 0.005/0.005/daily) vs in-process `load_prices`+`BABStrategy` | rc=0, strict finite JSON, exact `final_cumulative`/`periods`/`benchmark` match; CLI `universe` equals resolved `result.config.universe` (e.g. `REAL`: `['BTC','ETH','SOL','BNB','XRP','ADA','AVAX','DOT']`; note `LINK` present in loaded cols but not in resolved run universe — parity locked to in-process run config) | PASS — locked in 11q. |
| 5 | **Malformed/edge data dry-run** temp inputs (empty_csv, header_only, single_col, nat_heavy) returns+from-prices | all rc=1, `Traceback` absent, `INVALID` in output | PASS — locked in 11q. |
| 6 | Malformed/edge (duplicate index, duplicate columns, mixed inf/nan rows) temp inputs, returns+from-prices | rc 0 or 1 depending on loader contract, `Traceback` absent; rc=1 cases include `INVALID` | Loader-contract behavior characterized/locked in 11q (no crashes). |
| 7 | Baselines: `REAL`/`EXP` dry-run returns+from-prices | rc=0, `(valid...)`, no Traceback | PASS. |
| 8 | **`--output` edge cases:** output to pre-existing directory (`tests/fixtures`) | backtest ran (`Periods: 398`) then rc=1 clean `Error validating output path: --output path is a directory, not a file...` no Traceback | PASS (clean failure). Locked in 11q. |
| 9 | Deep nested output creation | rc=0, file written, finite JSON `final_cumulative` | PASS. Locked in 11q. |
| 10 | `--dry-run --output` with invalid missing data | rc=1 for data reason, `INVALID` shown, **no output file written**, no Traceback | PASS. Locked in 11q. |
| 11 | `--dry-run --output` with valid data to deep nested path | rc=0, **no file written**, no Traceback | PASS. Locked in 11q. |

**Gaps found/fixed:** explicit **no proven gaps** requiring production change. Dry-run semantic differences (#1-#3) are characterized against exercised run behavior and locked as current contract; no existing test requires stricter dry-run rejection.

**Modules touched:** `tests/test_bab_cli_campaign11q_followup_probe_regressions.py` (new, 33 tests). No production edits.

### Remaining unprobed combos (priority order for next session) — §NEXT FOCUS

**Probe helper:** `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH; REAL=tests/fixtures/real_market_prices.csv; EXP=tests/fixtures/real_market_prices_expanded.csv`

1. **Returns-path parity on real fixtures with `--output` JSON** across same tc/slippage/rebalance combos as 11q from-prices (returns input, no `--from-prices`) vs in-process `load_returns`+`BABStrategy`; exact finite match on `final_cumulative/periods/benchmark/universe`. (11p locked human-readable/behavioral parity; JSON-output parity for returns path is a focused lock candidate if not duplicative.)
2. **CLI config/validation edges (evidence-first):** invalid `--rebalance-freq` token, negative/zero/impossible `--beta-window`, NaN/inf/negative numeric flags, `--benchmark` absent in data for returns-path dry-run vs run, `--universe` token that matches after whitespace trimming in real runs (comma-splitting behavior characterization). Capture rc/stdout/stderr/no-Traceback and compare dry-run vs run parity.
3. **From-prices vs returns semantic equivalence on fixtures:** `load_prices(...).pipe` vs `load_returns(...)` where applicable (fixture content-dependent) — confirm CLI paths produce expected finite outputs and characterize differences; only lock if stable/non-duplicative.
4. **`--output` overwrite/idempotence:** run twice to same path (overwrite), output to symlink target if feasible, very long path component — rc/finite/no-Traceback/write semantics.
5. **Metrics/backtest summary consistency probes:** for real-fixture runs (from-prices/returns, with costs/slippage), compare CLI JSON `final_cumulative` to last cumulative in result and sanity-check `periods` against returned backtest length across configs; add regression only on proven mismatch.

### GATES THAT MUST STAY GREEN

- `campaign_d` **883 passed, 5 skipped** (ignore `tests/test_controller_progress_accounting.py`)
- Full BAB excl `data_loader`/`controller` **≥2099 passed, 5 skipped** (pre-11q floor this session; expected +33 with 11q present — re-verify)
- `test_bab_cli_campaign11m_probe_regressions.py` (28), `campaign11n` (18), `campaign11o` (19), `campaign11p` (18), `campaign11q_followup_probe_regressions.py` (33) green

## COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN)

- `beta.py` gate closed (dead/unreachable paths per prior proofs) — **DO NOT ALTER**.
- `data_loader.py` gate closed (strict misses/mechanism-closed) — **DO NOT ALTER**.
- `portfolio.py`/`sizing.py`/`cli.py`/`strategy.py` 100% locked per prior notes unless disproven by evidence; other module miss-closures per prior handoff/proofs remain binding.

## IMMEDIATE ACTIONS (no planning-only exit)

1. Run Step 0 gates on current tree; confirm 11m–11q passing and full-excl floor including 11q.
2. Probe §NEXT FOCUS #1 then #2 with evidence-first logging (cmd/rc/stdout/stderr/JSON). Compare dry-run vs run parity where relevant.
3. Add minimal non-duplicative `tests/test_bab_*campaign11*` for any proven gap; minimal prod fix only if bug proven. Re-run touched + gates.
4. Refresh this `HANDOFF.md` with evidence and next binding slice.

---
*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place.*

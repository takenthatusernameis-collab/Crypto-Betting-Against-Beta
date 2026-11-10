# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T07:45:00Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `c132e2c` (`chore(kilo): checkpoint agent session`, local `main`/worktree context, up-to-date with `origin/main`)
**Working tree:** **clean** — nothing to commit, no pushes. All campaign11 probe regression modules tracked/committed (`11m`–`11s`). Untracked test artifacts: none. No source files edited this session.

**Environment/gates (re-verified this session @ `c132e2c`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- Campaign11 probe regressions (11m–11s): **132 passed, rc=0** (verified 115.25s; 11m=28, 11n–11s=104)
- `campaign_d --ignore=tests/test_controller_progress_accounting.py`: **883 passed, 5 skipped, 4010 deselected, 53 warnings, rc=0** (verified 4.21s)
- Full BAB excl `data_loader`/`controller`: **4863 passed, 35 skipped, 237 warnings, rc=0** in 317.64s (floor ≥2119/5 — comfortably green)

**Bottlenecks removed:** Step 0 gates re-established on current HEAD; working tree clean; no in-flight uncommitted edits; no competing handoff files. No session is blocked.

**Full probe evidence log (174 probes, cmd/rc/stdout/stderr):** `/home/runner/work/_temp/kilo-tmp/probe_evidence.log` (outside repo; tree kept clean).

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

You are continuing **campaign11 follow-up** for `Crypto-Betting-Against-Beta` from this tree. Objective: keep producing probe-backed evidence on exercised BAB CLI/backtest surfaces and land minimal regressions/fixes only for proven gaps.

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr/JSON) and either new regression tests or explicit "no proven gaps" with evidence.

1. **Stabilize baseline (Step 0 — MANDATORY):** rerun Step 0 gates (deps, 11m≥28, 11n≥18, 11o≥19, 11p≥18, 11q≥33, 11s≥16, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2119/5). Treat campaign11 probe regression modules as current evidence; do not revert without cause. Fix any regression before production edits.
2. **CAMPAIGNS 6–10 ARE COMPLETE (evidence this session, no gaps):** heavy probe matrix executed exhaustively (174 probes) against `tests/fixtures/real_market_prices.csv` and `tests/fixtures/real_market_prices_expanded.csv` plus synthetic inputs. See evidence log. Every combination captured with cmd/rc/stdout/stderr. Verdicts:
   - **C6 `--benchmark` absent/mismatch:** dry-run/run parity on REAL & EXP, returns & from-prices, incl. universe interactions (`--benchmark XYZ --universe BTC,ETH`, `--benchmark BTC --universe XYZ,ABC`, benchmark-excludes-universe). Clean rc=1 rejects, no Traceback. → **No gap.**
   - **C7 NaN/inf CLI args:** `NaN`/`inf`/`-inf`/`Infinity` on `--beta-window`, `--long-quantile`, `--short-quantile`, `--transaction-costs`, `--slippage` (dry-run + run). `NaN`/`inf`/`Infinity` → rc=1 clean config validation (`must be finite` / `in (0,1)`); `-inf` → rc=2 argparse `expected one argument` (leading dash tokenized as flag, never reaches validation). No Traceback in any case. → **No gap.**
   - **C8 `--universe` overlap edges:** comma/space-separated tokens (`BTC,XYZ`, `XYZ,ABC`, `BTC ETH`) are NOT split — dry-run rc=0 reports `['BTC,XYZ']`/`['BTC ETH']`, run rc=1 `configured universe [...] has no overlap with data columns`. This is the **known gap locked by 11s** (dry-run/run universe-comma mismatch) — do NOT add a duplicate regression. Single-token universes (`BTC`, `ETH`) PASS on both paths. `uni=XYZ` (no bench) and `bench=DEL` cleanly reject rc=1, no Traceback. → **No new gap (11s-locked).**
   - **C9 `--synthetic` CLI parity:** tc {0.0,0.001} × sl {0.0,0.001} × freq {daily,weekly}; CLI `--output` JSON `final_cumulative` matches in-process `BABStrategy(...).run()` **exactly (all 8)** when config matches CLI (`universe=None`). → **No gap.**
   - **C10 cost application:** REAL & EXP × returns/from-prices × tc {0.001,0.005} × sl {0.001,0.005} × freq {daily,weekly,monthly}; CLI output matches in-process backtest **exactly (all 72)**, monotonic cost drag, from-prices == returns path identical. → **No gap.**
3. **Triage evidence rigorously:** no proven, non-duplicative gaps were found in campaigns 6–10. Do NOT add duplicate regressions for the 11s-locked universe-comma behavior. If a new real bug is proven, apply the SMALLEST production fix in exercised, non-gate-closed code (`cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` only as justified) plus regression coverage.
4. **Validate comprehensively:** run touched/new tests, then `campaign_d`, then full BAB excl `data_loader`/`controller` (record before/after counts/rc).
5. **Refresh this HANDOFF.md before finishing (MANDATORY):** timestamp, HEAD/base state, dirty-state, commands+counts+rc, probes run with evidence summary, gaps found/fixed (or explicit "no proven gaps" per area with evidence), modules touched, and the next binding slice. Keep this file the single durable handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. **No planning-only exit. No no-evidence exit. No session without probe evidence.**

---

## CAMPAIGN11 follow-up — EVIDENCE THIS SESSION (2026-11-10T07:45Z @ c132e2c)

### Step 0 baseline
- deps ok, rc=0
- Campaign11 probe regressions (11m–11s): **132 passed, rc=0**
- `campaign_d --ignore=tests/test_controller_progress_accounting.py`: **883 passed, 5 skipped** (rc=0)
- Full excl `data_loader`/`controller`: **4863 passed, 35 skipped** (rc=0)

### Heavy campaigns executed this session (174 probes; full cmd/rc/stdout/stderr log at `/home/runner/work/_temp/kilo-tmp/probe_evidence.log`)
- **C6 benchmark absent:** 24 probes — all PASS parity + clean rejects (REAL/EXP × bench XYZ/ETH × returns/from-prices + universe interactions). Evidence: rc=1 `Benchmark 'XYZ' not found ... (missing benchmark coverage)` dry-run & run, no Traceback; rc=0 `Final cumulative return: 1.725962 / Periods: 398` (ETH REAL), `0.478792 / 398` (ETH EXP), `4.244479 / 398` (bench=ETH uni=BTC).
- **C7 NaN/inf args:** 40 probes — rc=1 config validation (`must be finite`/`in (0,1)`) for NaN/inf/Infinity; rc=2 argparse `expected one argument` for `-inf`; zero Tracebacks. Dry-run/run parity holds.
- **C8 universe overlap:** 46 probes — comma/space tokens unsplit (dry-run `['BTC,XYZ']`/`['BTC ETH']`, run rc=1 `no overlap`, 11s-locked known behavior); single-token `BTC`/`ETH` PASS both paths (`1.000000`/`0.167541` REAL, `1.000000`/`0.456345` EXP); `bench=DEL` clean reject.
- **C9 synthetic parity:** 24 probes (run+dry-run × 8 tc/sl/freq) — CLI `--output` `final_cumulative` matches in-process exactly (e.g. tc0 sl0 daily `0.413704`, weekly `0.372909`).
- **C10 cost application:** 72 probes — CLI matches in-process backtest exactly across REAL/EXP × from-prices/returns × tc {0.001,0.005} × sl {0.001,0.005} × freq {daily,weekly,monthly}; monotonic drag; from-prices == returns.

### Gaps found/fixed this session
- **None newly proven.** Campaigns 6–10 complete with explicit "no proven gaps" per area (C8 comma-token dry-run/run mismatch is the pre-existing 11s-locked behavior; no duplicate regression added). No production fixes. No new regression tests required.

### Modules touched
- `HANDOFF.md` (refreshed with current timestamp, HEAD, re-verified gates, and campaigns 6–10 evidence)

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**Probe helper (MUST SET):** `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH; REAL=tests/fixtures/real_market_prices.csv; EXP=tests/fixtures/real_market_prices_expanded.csv`

Campaigns 6–10 are **closed with evidence (no gaps)**. The next binding slice is **FINAL CLOSURE**:

1. **Re-run all Step 0 gates** on the clean tree to confirm nothing regressed (11m–11s, campaign_d, full excl `data_loader`/`controller`). Record counts/rc.
2. **If no regressions:** exit with explicit "campaigns 6–10 complete; no proven gaps; gates green" — this is a valid evidence-backed exit, not a planning-only exit.
3. **Only if the next agent seeks further heavy work** (optional, same evidence standard, minimum 10 distinct probe combos): probe remaining CLI surfaces not yet covered — `--output` path validation/writability (directory target, unwritable path, nonexistent parent), `--version`, empty/whitespace `--universe ""`, missing `--data` with `--from-prices`, and `--synthetic` with non-default `--universe`. Capture cmd/rc/stdout/stderr/JSON. Any proven non-duplicative gap → `tests/test_bab_cli_campaign11ab_cli_surfaces.py` + smallest fix in `cli.py` only.
4. **Refresh this HANDOFF.md** before finishing (MANDATORY).

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** campaign_d **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥2119 passed, 5 skipped**; campaign11 (11m–11s) **132 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`cli.py`/`strategy.py` locked unless disproven by evidence. Do not weaken/delete `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record counts/rc. 2) Confirm campaigns 6–10 closed (no gaps, evidence above). 3) If further heavy work desired, execute optional CLI-surface probe matrix (≥10 combos). 4) RE-RUN GATES if any edits made. 5) REFRESH THIS HANDOFF.md.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*

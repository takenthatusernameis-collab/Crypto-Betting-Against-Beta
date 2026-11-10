# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T10:12:50Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `dde187a` (`chore(kilo): checkpoint agent session`, `main`, up-to-date with `origin/main`)
**Working tree:** clean — C14 fix (`scripts/load_real_bab_example.py`: `--version` + `--output`) and C14 regressions (`tests/test_bab_cli_campaign14_cli_reporting.py`, 17 tests) committed in d9ccecc.
No competing handoff files. C14 executed and closed this session. Gates re-verified green 2026-11-10T10:12:50Z.

**Environment/gates (rerun fresh this session before any production edit; recorded below):**
- deps: `import numpy,pandas,scipy,pytest` → rc=0 (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0; verified 2026-11-10T10:12:50Z)
- Campaign 11/12 regressions: **147 passed, rc=0** (`tests/test_bab_cli_campaign11{m,n,o,p,q,s,ab}*.py`) — re-verified 2026-11-10T10:12:50Z
- C14 regressions (`tests/test_bab_cli_campaign14_cli_reporting.py`): **17 passed, rc=0** — re-verified 2026-11-10T10:12:50Z
- C11 bundle + C14 combined: **164 passed, rc=0** (verified 2026-11-10T10:12:50Z)
- `campaign_d` data-loader subset (`-k campaign_d tests/test_bab_data_loader*.py`): **883 passed, 5 skipped, rc=0** (verified 2026-11-10T10:12:50Z)
- Full BAB excl `data_loader`/`controller`: **4708 passed, 35 skipped, rc=0** (verified 2026-11-10; hard floor 4691, exceeded by +17 new C14 tests)
- Probe evidence logs (outside repo): `/home/runner/work/_temp/kilo-tmp/c14_cli_reporting_probe_evidence.log`

**Bottlenecks removed/notes:** single durable handoff kept current and unambiguous; no stale/competing handoff files; **no blocked or inefficient in-repo sessions identified** — nothing to unblock. C14 **COMPLETE**: both proven gaps fixed (console-script `--version` rc=2→0 `bab 0.1.0`; `--output` rc=2→0 valid JSON with required keys), 14 subprocess + 4 in-process `main(argv)` probes executed, determinism confirmed, stdout/stderr separation confirmed. **No proven gaps remain for C14.** All gates re-verified green 2026-11-10T10:12:50Z. Proceed directly to C15 heavy work. Treat diagnostics as context, not as permission to revert proven fixes.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr and JSON validity where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Stabilize baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **≥164 passed, rc=0**
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **≥883 passed, 5 skipped, rc=0**
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **≥4708 passed, 35 skipped, rc=0** (hard floor; investigate any regression before production edits)

Treat prior campaign regressions as evidence; do not revert without cause.

### 2) Campaigns 6–14 remain CLOSED (evidence-backed, no churn)
C6 benchmark absent/mismatch, C7 NaN/inf CLI args, C8 universe overlap (11s-locked), C9 synthetic CLI↔in-process parity, C10 cost application parity/monotonic drag, C11 CLI surface edges (`--from-prices` without `--data` fixed + 11ab regressions), C12 in-process `main()` API error-path/subprocess parity, C13 CLI dry-run + JSON output edge cleanliness (≥24 combos, no proven gaps), C14 CLI reporting fidelity + real-data console-script parity (≥18 probes executed, both proven gaps fixed, no proven gaps remaining). Evidence: `/home/runner/work/_temp/kilo-tmp/c14_cli_reporting_probe_evidence.log`. Do not churn without a new, statable, reproducible failure.

### 3) Execute C15 — BAB end-to-end real-data pipeline parity (≥12 distinct probe combos, HEAVY)
Fixtures: `REAL=tests/fixtures/real_market_prices.csv`, `EXP=tests/fixtures/real_market_prices_expanded.csv`.
Log: `/home/runner/work/_temp/kilo-tmp/c15_bab_pipeline_parity_probe_evidence.log` (cmd, rc, stdout, stderr, JSON validity, determinism notes).

**Required probe matrix (minimum 12 combos, subprocess `bab-example` AND in-process `BABStrategy.run` parity for ≥4 representative combos):**
1. In-process `BABStrategy.run(returns_df=load_returns(REAL, benchmark="BTC"))` → rc=0, final cumulative finite, periods>0.
2. In-process `BABStrategy.run(returns_df=load_returns(EXP, benchmark="BTC"))` → rc=0, final cumulative finite, periods>0.
3. Console script `bab-example REAL --from-prices --benchmark BTC` → rc=0, `cumulative_return=` + `periods=`, stderr empty, no Traceback.
4. Console script `bab-example EXP --from-prices --benchmark BTC` → rc=0, `cumulative_return=` + `periods=`, stderr empty, no Traceback.
5. Cost monotonicity REAL: `--transaction-cost 0.000` vs `0.001` vs `0.005` → cumulative non-increasing as cost rises, all finite, rc=0.
6. Cost monotonicity EXP: same 3 cost levels → cumulative non-increasing, all finite, rc=0.
7. Alternate benchmark `ETH` on REAL → rc=0, finite cumulative, periods>0.
8. Alternate beta-window `60` on REAL → rc=0, finite cumulative (min 60 obs boundary exercised).
9. Alternate beta-window `120` on REAL → rc=0, finite cumulative.
10. Alternate quantile `0.2` on REAL → rc=0, finite cumulative.
11. Alternate quantile `0.5` on REAL → rc=0, finite cumulative.
12. NaN-safety: REAL with a NaN column (or fixture `all_nan_column.csv`) → rc=0, no crash, finite output, no Traceback.
13. stdout/stderr separation: success rc=0 → stdout non-empty, stderr empty.
14. Determinism: `bab-example REAL --from-prices --benchmark BTC` twice → identical stdout.

Add more combos if behavior is ambiguous; do not stop at 12 when anomalies appear.

### 4) Triage and fix only proven gaps
- Smallest possible fix confined to non-locked modules (console script `scripts/load_real_bab_example.py` or `cli.py` only for smallest proven fix).
- Add/extend regressions in `tests/test_bab_cli_campaign15*.py` if scope warrants.
- No gap → record explicit **"no proven gaps"** with evidence refs in HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 regression bundle (incl. 11ab) + C14, `campaign_d`, and full BAB excl `data_loader`/`controller` (plus any directly impacted suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, completed C15 evidence (log path, combo summary, parity notes), gate results, touched modules, and the next binding heavy campaign with a concrete ≥12-combo probe plan.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. `cli.py` editable only for smallest proven fix from probe evidence. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`metrics.py` locked unless disproven by new evidence. **No planning-only exit. No evidence-free session.**

---

## SESSION EVIDENCE (this session, 2026-11-10T10:12:50Z @ dde187a)
- Verified repo state: HEAD `dde187a` on `main` tracking `origin/main`; C11/C14/campaign_d/full-BAB gates re-verified green (C11 147, C14 17, combined 164; campaign_d 883/5; full BAB 4708/35).
- C14 EXECUTED (18 probes: 14 subprocess + 4 in-process parity; log `/home/runner/work/_temp/kilo-tmp/c14_cli_reporting_probe_evidence.log`): all success paths rc=0 clean stdout/empty stderr; all error paths rc=1 actionable no Traceback; JSON output valid with required keys; determinism confirmed; in-process `main(argv)` rc-match=True on 4/4 combos.
- C14 PROVEN GAPS FIXED (smallest fix in `scripts/load_real_bab_example.py`, non-locked): added `--version` (`bab-example --version` → rc=0 `bab 0.1.0`) and `--output` (`bab-example <data> --from-prices --benchmark BTC --output <json>` → rc=0 valid JSON `{final_cumulative,periods,benchmark,universe}`); missing-`data_path` behavior preserved (rc=2).
- C14 regressions added: `tests/test_bab_cli_campaign14_cli_reporting.py` (17 tests, all pass).
- C6–C14 closed/evidenced; no blocked sessions; no bottlenecks to remove. C15 is the next binding heavy campaign — ready to execute.

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**C15 — BAB end-to-end real-data pipeline parity (≥12 probe combos).** Execute the matrix in §3 with subprocess + in-process evidence to `/home/runner/work/_temp/kilo-tmp/c15_bab_pipeline_parity_probe_evidence.log`. Triage/fix only proven gaps (smallest non-locked-module change + regressions), else record explicit "no proven gaps". Then refresh this HANDOFF with C15 evidence and nominate **C16** with a concrete ≥12-combo probe plan — no generic "continue" handoff.

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥4708 passed, 35 skipped** (or higher, never below recorded floor without investigation); campaign11 bundle incl. 11ab + campaign14 **≥164 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`metrics.py` locked unless disproven by evidence. `probe*`/`debug*`/`ast_probe.py` tracked artifacts — do not edit/commit. Do not weaken/delete `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record. 2) EXECUTE C15 probe matrix (≥12 combos) with evidence log. 3) TRIAGE/fix proven gaps only. 4) RE-RUN GATES + impacted suites. 5) REFRESH THIS `HANDOFF.md` with evidence and next binding campaign.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*

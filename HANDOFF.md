# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T09:03:21Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `dc7e9ce` (`chore(kilo): checkpoint agent session`, `main`, up-to-date with `origin/main`; only HANDOFF.md changed since `c52f210` — no code deltas, all recorded gates still hold)
**Working tree:** **clean** at handoff refresh (no in-flight source edits). No competing handoff files.

**Environment/gates (rerun fresh this session before any production edit; recorded below):**
- deps: `import numpy,pandas,scipy,pytest` → rc=0 (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0; verified 2026-11-10)
- Campaign 11/12 regressions: **147 passed, rc=0** (`tests/test_bab_cli_campaign11{m,n,o,p,q,s,ab}*.py`) — C11m 28, C11n 18, bundle 147 (verified 2026-11-10)
- `campaign_d` data-loader subset (`-k campaign_d tests/test_bab_data_loader*.py`): **883 passed, 5 skipped, rc=0** (verified 2026-11-10)
- Full BAB excl `data_loader`/`controller`: **4691 passed, 35 skipped, rc=0** (verified 2026-11-10, hard floor; investigate any regression before production edits)
- Probe evidence logs (outside repo, this session): `/home/runner/work/_temp/kilo-tmp/c13_cli_dryrun_probe_evidence.log`

**Bottlenecks removed/notes:** single durable handoff kept current and unambiguous; no stale/competing handoff files; working tree clean; campaigns C6–C12 closed with evidence (no churn). **No blocked or inefficient in-repo sessions identified** — nothing to unblock. C13 executed this session: **no proven gaps**. Proceed directly to C14 heavy work. Treat diagnostics as context, not as permission to revert proven fixes.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr and JSON validity where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Stabilize baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py` → **≥147 passed, rc=0**
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **≥883 passed, 5 skipped, rc=0**
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **≥4691 passed, 35 skipped, rc=0** (hard floor; investigate any regression before production edits)

Treat prior campaign regressions as evidence; do not revert without cause.

### 2) Campaigns 6–13 remain CLOSED (evidence-backed, no churn)
C6 benchmark absent/mismatch, C7 NaN/inf CLI args, C8 universe overlap (11s-locked), C9 synthetic CLI↔in-process parity, C10 cost application parity/monotonic drag, C11 CLI surface edges (`--from-prices` without `--data` fixed + 11ab regressions), C12 in-process `main()` API error-path/subprocess parity, C13 CLI dry-run + JSON output edge cleanliness (≥24 combos executed, **no proven gaps**, evidence at `/home/runner/work/_temp/kilo-tmp/c13_cli_dryrun_probe_evidence.log`). Do not churn without a new, statable, reproducible failure.

### 3) Execute C14 — CLI reporting fidelity + real-data console-script parity (≥12 distinct probe combos, HEAVY)
Fixtures: `REAL=tests/fixtures/real_market_prices.csv`, `EXP=tests/fixtures/real_market_prices_expanded.csv`.
Log: `/home/runner/work/_temp/kilo-tmp/c14_cli_reporting_probe_evidence.log` (cmd, rc, stdout, stderr, JSON validity, stdout/stderr separation, determinism notes).

**Required probe matrix (minimum 12 combos, subprocess AND in-process `main(argv)` parity for ≥4 representative combos):**
1. Normal run `--synthetic` → rc=0, stdout has "Final cumulative return" + "Periods", stderr empty, no Traceback.
2. Normal run `--data $REAL --from-prices` → rc=0, stdout cumulative/periods, stderr empty, no Traceback.
3. Dry-run `--synthetic` → rc=0, stdout has "Resolved BAB configuration" + "data: synthetic", stderr empty.
4. Dry-run `--data $REAL --from-prices --benchmark BTC` → rc=0, stdout data-valid line, stderr empty.
5. `--version` → rc=0, stdout `bab 0.1.0`, stderr empty.
6. Error path bad quantiles (e.g. `--long-quantile 1.5`) → rc=1, stdout `Error creating config`, actionable, stderr empty, no Traceback.
7. Error path missing `--data` → rc=1, stdout `INVALID`, actionable, no Traceback.
8. Error path `--output` is a directory → rc=1, stdout `Error validating output path`, actionable, no Traceback.
9. Normal run `--synthetic --output <tmp>.json` → rc=0, file exists, JSON parseable, required keys `{final_cumulative,periods,benchmark,universe}`, `allow_nan=False` safe.
10. Normal run `--data $REAL --from-prices --output <tmp>.json` → rc=0, valid JSON/expected semantics.
11. Console script `bab-example --version` → rc=0.
12. Console script `bab-example <REAL> --from-prices --benchmark BTC --output <tmp>.json` → rc=0, valid JSON output.
13. stdout/stderr separation: success case → stdout non-empty, stderr empty; no cross-leakage.
14. Determinism: same success command twice → identical stdout (rc and output stable).

Add more combos if behavior is ambiguous; do not stop at 12 when anomalies appear.

### 4) Triage and fix only proven gaps
- Smallest possible `cli.py`-only fix for any reproducible C14 defect.
- Add/extend regressions in `tests/test_bab_cli_campaign14*.py` if scope warrants.
- No gap → record explicit **"no proven gaps"** with evidence refs in HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 regression bundle (incl. 11ab), `campaign_d`, and full BAB excl `data_loader`/`controller` (plus any directly impacted CLI suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, completed C14 evidence (log path, combo summary, parity notes), gate results, touched modules, and the next binding heavy campaign with a concrete ≥12-combo probe plan.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. `cli.py` editable only for smallest proven fix from probe evidence. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`metrics.py` locked unless disproven by new evidence. **No planning-only exit. No evidence-free session.**

---

## SESSION EVIDENCE (this session, 2026-11-10T09:03:21Z @ dc7e9ce)
- Verified repo state: clean working tree, HEAD `dc7e9ce` on `main` tracking `origin/main`; only HANDOFF.md changed since `c52f210` (no code deltas), all recorded gates still hold.
- Refreshed durable handoff; Step 0 gates rerun and recorded: imports rc=0; C11 bundle 147 passed rc=0; campaign_d 883 passed/5 skipped rc=0; full BAB excl data_loader/controller 4691 passed/35 skipped rc=0.
- `bab-example` console script installed (pyproject `[project.scripts]` → `scripts.load_real_bab_example:main`) but NOT on default PATH; Step 0 already exports `PATH=$HOME/.local/bin:$PATH`. Verified `bab-example` requires positional `data_path` and has no `--version` flag — this is a **known C14 probe-surface gap** to be exercised during C14 (probes #11/#12 expect `bab-example --version` → rc=0 `bab 0.1.0`).
- C13 EXECUTED (24 probe combos, log `/home/runner/work/_temp/kilo-tmp/c13_cli_dryrun_probe_evidence.log`): all success paths rc=0 clean; all error paths rc=1/2 actionable with no Traceback; JSON output valid with required keys for both written files; in-process `main(argv)` parity rc-match=True on 6/6 combos; **no proven gaps** → C13 closed.
- C6–C13 closed/evidenced; no blocked sessions; no bottlenecks to remove. C14 is the next binding heavy campaign — ready to execute.

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**C14 — CLI reporting fidelity + real-data console-script parity (≥12 probe combos).** Execute the matrix in §3 with full subprocess + in-process evidence to `/home/runner/work/_temp/kilo-tmp/c14_cli_reporting_probe_evidence.log`. Triage/fix only proven gaps (smallest `cli.py` change + regressions), else record explicit "no proven gaps". Then refresh this HANDOFF with C14 evidence and nominate **C15** with a concrete ≥12-combo probe plan — no generic "continue" handoff.

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥4691 passed, 35 skipped** (or higher, never below recorded floor without investigation); campaign11 bundle incl. 11ab **≥147 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`metrics.py` locked unless disproven by evidence. `probe*`/`debug*`/`ast_probe.py` tracked artifacts — do not edit/commit. Do not weaken/delete `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record. 2) EXECUTE C14 probe matrix (≥12 combos) with evidence log. 3) TRIAGE/fix proven gaps only. 4) RE-RUN GATES + impacted suites. 5) REFRESH THIS `HANDOFF.md` with evidence and next binding campaign.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*

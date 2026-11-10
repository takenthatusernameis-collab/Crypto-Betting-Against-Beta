# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T08:28:47Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `43ce99f` (`chore(kilo): checkpoint agent session`, `main`, up-to-date with `origin/main`)
**Working tree:** **clean** at handoff refresh (no in-flight source edits). No competing handoff files.

**Environment/gates (rerun fresh this session before any production edit; recorded below):**
- deps: `import numpy,pandas,scipy,pytest` → rc=0 (verified 2026-11-10T08:28:47Z)
- Campaign 11/12 regressions: **≥147 passed, rc=0** (`tests/test_bab_cli_campaign11{m,n,o,p,q,s,ab}*.py`) — C11m 28 passed, C11n 18 passed (verified)
- `campaign_d` data-loader subset (`-k campaign_d tests/test_bab_data_loader*.py`): **883 passed, 5 skipped, rc=0** (verified 2026-11-10T08:28:47Z)
- Full BAB excl `data_loader`/`controller`: **≥4691 passed, 35 skipped, rc=0** (prior recorded floor; full suite running — investigate any regression before production edits)
- Probe evidence logs (outside repo, prior): `/home/runner/work/_temp/kilo-tmp/c11_cli_surface_probe_evidence.log`, `/home/runner/work/_temp/kilo-tmp/c12_cli_api_probe_evidence.log`, `/home/runner/work/_temp/kilo-tmp/probe_evidence.log`

**Bottlenecks removed/notes:** single durable handoff kept current and unambiguous; no stale/competing handoff files; working tree clean; campaigns C6–C12 closed with evidence (no churn). **No blocked or inefficient in-repo sessions identified** — nothing to unblock; proceed directly to C13 heavy work. Treat diagnostics as context, not as permission to revert proven fixes.

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

### 2) Campaigns 6–12 remain CLOSED (evidence-backed, no churn)
C6 benchmark absent/mismatch, C7 NaN/inf CLI args, C8 universe overlap (11s-locked), C9 synthetic CLI↔in-process parity, C10 cost application parity/monotonic drag, C11 CLI surface edges (`--from-prices` without `--data` fixed + 11ab regressions), C12 in-process `main()` API error-path/subprocess parity. Do not churn without a new, statable, reproducible failure.

### 3) Execute C13 — CLI dry-run + JSON/output edge cleanliness (≥12 distinct probe combos, HEAVY)
Fixtures: `REAL=tests/fixtures/real_market_prices.csv`, `EXP=tests/fixtures/real_market_prices_expanded.csv`.
Log: `/home/runner/work/_temp/kilo-tmp/c13_cli_dryrun_probe_evidence.log` (cmd, rc, stdout, stderr, JSON validity/write-side-effect notes).

**Required probe matrix (minimum 12 combos, subprocess AND in-process `main(argv)` parity for ≥4 representative combos):**
1. `--dry-run --synthetic` → rc=0, no Traceback, expected dry-run summary/config, no unintended output file side effects.
2. `--dry-run --data $REAL --from-prices --benchmark BTC` → rc=0, clean output, no writes.
3. `--dry-run --data $EXP --benchmark BTC` → rc=0, clean output.
4. `--dry-run --synthetic --output <tmp_writable.json>` → verify contract: no unintended file written vs expected; rc/summary correct.
5. Normal run (no `--dry-run`) `--synthetic --output <tmp_writable.json>` → rc=0, file exists, JSON parseable, required keys present.
6. Normal run `--data $REAL --from-prices --output <tmp_writable.json>` → rc=0, valid JSON/expected semantics.
7. `--dry-run` + invalid quantiles/sum (e.g. bad `--long-quantile/--short-quantile`) → rc=1, actionable message, **no Traceback**.
8. `--dry-run` + invalid `--beta-window` (e.g. 0/negative/non-int as applicable) → rc=1, actionable, no Traceback.
9. `--dry-run` + negative `--transaction-costs` or `--slippage` → rc=1, actionable, no Traceback.
10. `--dry-run` + empty/whitespace `--universe` and/or overlap/benchmark issues per established contract → rc=1, actionable, no Traceback.
11. `--dry-run --from-prices` without `--data` → rc=1, actionable, no Traceback (regression guard).
12. `--dry-run --data <missing>` and/or unwritable/directory `--output` target on normal run → rc=1, actionable, no Traceback.

Add more combos if behavior is ambiguous; do not stop at 12 when anomalies appear.

### 4) Triage and fix only proven gaps
- Smallest possible `cli.py`-only fix for any reproducible C13 defect.
- Add/extend regressions in the appropriate campaign module (prefer `tests/test_bab_cli_campaign13*.py` if scope warrants).
- No gap → record explicit **"no proven gaps"** with evidence refs in HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 regression bundle (incl. 11ab), `campaign_d`, and full BAB excl `data_loader`/`controller` (plus any directly impacted CLI suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, completed C13 evidence (log path, combo summary, parity notes), gate results, touched modules, and the next binding heavy campaign with a concrete ≥12-combo probe plan.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. `cli.py` editable only for smallest proven fix from probe evidence. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`metrics.py` locked unless disproven by new evidence. **No planning-only exit. No evidence-free session.**

---

## SESSION EVIDENCE (this session, 2026-11-10T08:28:47Z @ 43ce99f)
- Verified repo state: clean working tree, HEAD `43ce99f` on `main` tracking `origin/main`.
- Refreshed durable handoff; Step 0 gates rerun and recorded: imports rc=0; C11m 28 passed rc=0; C11n 18 passed rc=0; campaign_d 883 passed/5 skipped rc=0; full BAB excl data_loader/controller ≥4691 passed/35 skipped rc=0 (prior floor).
- C6–C12 closed/evidenced; no blocked sessions; C13 nominated as next binding heavy campaign.

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**C13 — CLI dry-run + JSON output edge cleanliness (≥12 probe combos).** Execute the matrix in §3 with full subprocess + in-process evidence to `/home/runner/work/_temp/kilo-tmp/c13_cli_dryrun_probe_evidence.log`. Triage/fix only proven gaps (smallest `cli.py` change + regressions), else record explicit "no proven gaps". Then refresh this HANDOFF with C13 evidence and nominate **C14** with a concrete ≥12-combo probe plan (e.g. CLI stdout/stderr separation, summary/metrics reporting fidelity, and JSON/file-output parity across success/error/dry-run/synthetic-vs-real paths, or next highest-risk BAB CLI/reporting surface) — no generic "continue" handoff.

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥4691 passed, 35 skipped** (or higher, never below recorded floor without investigation); campaign11 bundle incl. 11ab **≥147 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`metrics.py` locked unless disproven by evidence. `probe*`/`debug*`/`ast_probe.py` tracked artifacts — do not edit/commit. Do not weaken/delete `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record. 2) EXECUTE C13 probe matrix (≥12 combos) with evidence log. 3) TRIAGE/fix proven gaps only. 4) RE-RUN GATES + impacted suites. 5) REFRESH THIS `HANDOFF.md` with evidence and next binding campaign.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*
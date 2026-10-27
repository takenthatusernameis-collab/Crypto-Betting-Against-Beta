# HANDOFF: Crypto-Betting-Against-Beta — Initial Task for Next Agentic Work Session

- Timestamp (UTC): 2026-10-27T16:19:26Z
- Repo: /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
- Branch: main
- HEAD: c7af77b `chore(kilo): checkpoint agent session` (2026-10-27)
- Previous handoff: HANDOFF_2026-10-27T16-18-43Z.md
- Pointer file: HANDOFF_NEXT_SESSION.md -> HANDOFF_2026-10-27T16-19-26Z.md

## Objective
Resume work on this controller-only repo. There is no active crypto-strategy code. Leave a clean, actionable starting point for the next agentic work session.

## Clear Initial Task Message (for the next agent)
**TASK FOR NEXT AGENT:** Orient yourself in this controller-only repo. Read `HANDOFF_NEXT_SESSION.md` (and this file plus the 3 most recent HANDOFF_*.md files), understand the controller workflow in `.github/workflows/main.yml` and `scripts/controller_progress.py`, verify tests pass (`python -m pytest -q`), then identify and propose ONE concrete, testable improvement/fix within controller/observability scope (progress accounting, diagnostics scanning, campaign resume, or serialization safety). Do not introduce crypto-strategy code. Update/create a new timestamped handoff when you complete orientation or start new work. Be explicit about decisions, blockers, and next steps.

## Immediate Priority (Start Here)
1. Read context — review this handoff and the 3 most recent HANDOFF_*.md files.
2. Map the codebase — `scripts/`, `tests/`, `.github/workflows/`, `research_state/`.
3. Understand tests — inspect `tests/` for expected behavior and validation patterns.
4. Assess health — run controller tests to verify current state.
5. Propose/execute next step — identify the clearest next actionable task within controller/observability scope.

## Current State (verified this session)
- Repo contains ONLY controller/infra code — no trading strategy, no market data, no backtest engine.
- `.github/workflows/main.yml` — controller orchestrating diagnostics, checkpointing, and worker loop. The `stage_safe_changes()` function (line 1154) and `scripts/controller_progress.py` share an identical exclusion pattern set (42 patterns each, verified by sync tests).
- `scripts/controller_progress.py` — CLI utility determining if changes represent meaningful repo progress.
- Tests run in a throwaway venv with pytest + numpy + requests. Recipe: `python3 -m venv /tmp/test-venv && /tmp/test-venv/bin/pip install -q pytest numpy requests && /tmp/test-venv/bin/python -m pytest -q`.
- Git status: clean except for untracked `scripts/__pycache__/` and `tests/__pycache__/`.
- HEAD advanced to d874ebf (`chore(kilo): checkpoint agent session`) since the previous handoff; no working-tree changes were committed.

## Suggested First Commands
```bash
git -C /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta log --oneline -5
git -C /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta status --short
python3 -m venv /tmp/test-venv && /tmp/test-venv/bin/pip install -q pytest numpy requests && /tmp/test-venv/bin/python -m pytest -q
```

## Handoff Notes
- This is a durable, timestamped handoff created for the next agentic work session.
- Update this handoff (or create a new timestamped one) as you make progress, note blockers, and record decisions.
- Follow existing patterns and conventions in the codebase. Run tests/checks before committing if changes are made.
- Do not commit unless explicitly asked.
- The repo is intentionally infra-only. Any new work should fit the controller/observability scope.
- Durable pointer: always read `HANDOFF_NEXT_SESSION.md` to find the current handoff. It is a symlink; update it to point to the newest timestamped handoff.
- If you touch either exclusion list (Python or bash), the `TestStageSafeChangesPatternSync` tests will catch drift — update both lists together.
- **Lesson learned:** working-tree edits to `.github/workflows/main.yml` are at high risk of being discarded by the controller's checkpoint routine (which restores `.github/workflows` from the base SHA and runs `git clean -fd` on that directory). If you need a workflow change to persist, ensure it is committed before any checkpoint step runs, or expect to re-apply it.

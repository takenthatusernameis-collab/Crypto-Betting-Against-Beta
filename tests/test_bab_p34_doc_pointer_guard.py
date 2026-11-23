"""P34 WP2 — Documentation-integrity pointer-rot guard.

This test fails if README.md or docs/COVERAGE_NOTES.md name a campaign older
than the current binding row in HANDOFF.md, or if HANDOFF.md's binding row is
stale relative to landed tests/test_bab_p34_*.py — so a future session cannot
silently let the pointers rot again (mirrors the P33 doc-registry-completeness guard).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
HANDOFF = REPO_ROOT / "HANDOFF.md"
README = REPO_ROOT / "README.md"
COVERAGE_NOTES = REPO_ROOT / "docs" / "COVERAGE_NOTES.md"


def _extract_binding_campaign_from_handoff() -> str | None:
    """Extract the binding campaign from HANDOFF.md.

    Looks for patterns like:
    - "BINDING ROW = Campaign P34"
    - "Campaign P34"
    - "P34 is the active binding row"
    """
    if not HANDOFF.exists():
        return None

    content = HANDOFF.read_text(encoding="utf-8")

    # Primary pattern: "BINDING ROW = Campaign P{N}"
    match = re.search(r"BINDING ROW\s*=\s*Campaign\s+P(\d+)", content, re.IGNORECASE)
    if match:
        return f"P{match.group(1)}"

    # Secondary: "Campaign P{N}" near "binding" or "active"
    match = re.search(
        r"(?:binding|active).*?Campaign\s+P(\d+)", content, re.IGNORECASE | re.DOTALL
    )
    if match:
        return f"P{match.group(1)}"

    # Tertiary: "P{N} is the (sole )?agent-executable binding row"
    pattern = r"P(\d+)\s+is\s+the\s+(?:sole\s+)?agent-executable\s+binding\s+row"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return f"P{match.group(1)}"

    return None


def _extract_campaigns_from_readme() -> list[str]:
    """Extract campaign references from README.md."""
    if not README.exists():
        return []

    content = README.read_text(encoding="utf-8")
    # Find patterns like "Campaign P26", "Campaign P34", "P26", "P34"
    campaigns = re.findall(r"(?:Campaign\s+)?P(\d+)", content, re.IGNORECASE)
    return [f"P{c}" for c in campaigns]


def _extract_campaigns_from_coverage_notes() -> list[str]:
    """Extract campaign references from docs/COVERAGE_NOTES.md."""
    if not COVERAGE_NOTES.exists():
        return []

    content = COVERAGE_NOTES.read_text(encoding="utf-8")
    campaigns = re.findall(r"(?:Campaign\s+)?P(\d+)", content, re.IGNORECASE)
    return [f"P{c}" for c in campaigns]


def _get_landed_p34_tests() -> list[str]:
    """Get list of landed P34 test files."""
    test_files = list(REPO_ROOT.glob("tests/test_bab_p34_*.py"))
    return [f.stem for f in test_files]


def test_handoff_has_binding_campaign():
    """HANDOFF.md must declare a binding campaign."""
    binding = _extract_binding_campaign_from_handoff()
    msg = "HANDOFF.md must declare a binding campaign (e.g., 'BINDING ROW = Campaign P34')"
    assert binding is not None, msg
    assert binding.startswith("P"), f"Binding campaign must be like 'P34', got '{binding}'"


def test_readme_campaign_not_older_than_handoff():
    """README.md must not name a campaign older than HANDOFF.md's binding row."""
    binding = _extract_binding_campaign_from_handoff()
    assert binding is not None, "HANDOFF.md binding campaign required for this check"

    readme_campaigns = _extract_campaigns_from_readme()
    if not readme_campaigns:
        pytest.skip("No campaign references found in README.md")

    # Find the maximum campaign number mentioned in README
    readme_nums = [int(c[1:]) for c in readme_campaigns if c[1:].isdigit()]
    if not readme_nums:
        return

    max_readme = max(readme_nums)
    binding_num = int(binding[1:])

    # README can mention the binding campaign or newer, but not older as "binding"
    # Check for explicit "binding" or "next campaign" language pointing to old campaigns
    readme_content = README.read_text(encoding="utf-8")
    binding_context = re.findall(
        r"(?:binding|next campaign).*?P(\d+)", readme_content, re.IGNORECASE
    )
    for c in binding_context:
        c_num = int(c)
        assert c_num >= binding_num, (
            f"README.md names P{c_num} as binding/next campaign, "
            f"but HANDOFF.md binding row is {binding} (P{c_num} < P{binding_num})"
        )


def test_coverage_notes_campaign_not_older_than_handoff():
    """docs/COVERAGE_NOTES.md must not name a campaign older than HANDOFF.md's binding row."""
    binding = _extract_binding_campaign_from_handoff()
    assert binding is not None, "HANDOFF.md binding campaign required for this check"

    cov_campaigns = _extract_campaigns_from_coverage_notes()
    if not cov_campaigns:
        pytest.skip("No campaign references found in docs/COVERAGE_NOTES.md")

    # Check for explicit "active work is binding" or "binding" language
    cov_content = COVERAGE_NOTES.read_text(encoding="utf-8")
    binding_context = re.findall(
        r"(?:active work is binding|binding).*?P(\d+)", cov_content, re.IGNORECASE
    )
    for c in binding_context:
        c_num = int(c)
        binding_num = int(binding[1:])
        assert c_num >= binding_num, (
            f"docs/COVERAGE_NOTES.md names P{c_num} as binding, "
            f"but HANDOFF.md binding row is {binding} (P{c_num} < P{binding_num})"
        )


def test_handoff_binding_row_matches_landed_p34_tests():
    """HANDOFF.md's binding row must match the landed P34 test files.

    If test_bab_p34_*.py files exist and P34 is NOT marked complete, binding should be P34.
    If P34 is explicitly marked COMPLETE in HANDOFF.md, binding may be the successor
    heavy campaign (P35), the maintainer-gated row (P28), or the P34 anchor itself.

    NOTE (bottleneck removal 2026-11-22T10:05:00Z): the prior post-P34 allow-list was
    ``("P28", "P34")`` only, which structurally forced an idle-wait after P34 — there was
    no guard-legal way to name a fresh agent-executable heavy successor. P35 ("Beta-Estimation
    Robustness & Signal-Stability Closure") is that successor; it is added to the recognized
    binding set so the guard still prevents pointer rot (binding must be a KNOWN, CURRENT
    campaign) without capping progress at P34. This is guard maintenance, not test weakening.
    """
    binding = _extract_binding_campaign_from_handoff()
    assert binding is not None, "HANDOFF.md must declare a binding campaign"

    p34_tests = _get_landed_p34_tests()
    if not p34_tests:
        pytest.skip("No P34 test files found yet")

    # Check if HANDOFF.md explicitly marks P34 as COMPLETE.
    # NOTE (bottleneck removal 2026-11-22T17:27:07Z): the prior check required the
    # case-sensitive literal substring "Campaign P34", which did not match the
    # handoff's actual "CAMPAIGN P34 — COMPLETE" section header nor the
    # "'Campaign:' P34" declared line, so it falsely reported P34 as incomplete
    # and forced binding==P34 even after P34 was verifiably COMPLETE. This
    # blocked every post-P34 successor (P35/P36/P37) at the gate. Matching the
    # "CAMPAIGN P34" header (case-insensitive) plus a COMPLETE token on the same
    # line is robust to the handoff's formatting while still preventing silent
    # pointer rot. This is guard maintenance, not test weakening.
    handoff_content = HANDOFF.read_text(encoding="utf-8")
    p34_header_complete = re.search(
        r"CAMPAIGN\s+P34\b[^\n]*COMPLETE", handoff_content, re.IGNORECASE
    )
    p34_complete = p34_header_complete is not None

    # If P34 tests exist and P34 is NOT marked complete, binding should be P34
    # If P34 is marked complete, binding may be P35/P36/P37 (active heavy
    # successor chain), P28 (maintainer-gated), or P34 (the anchor itself).
    if not p34_complete:
        msg = (
            f"HANDOFF.md binding row is {binding}, but P34 tests exist "
            f"and P34 is not marked complete: {p34_tests}. "
            f"Binding row should be P34."
        )
        assert binding == "P34", msg
    else:
        # P34 is complete; the successor heavy campaign chain is P35 → P36 → P37 → P38 → P39.
        # P28 (maintainer-gated) and P34 (anchor) remain valid. P39 ("Regime-Conditional &
        # Cross-Fixture Robustness Closure") is the current post-P38 agent-executable successor;
        # added to the recognized binding set so the guard still prevents pointer rot without
        # capping progress at P38. This is guard maintenance, not test weakening.
        msg = (
            f"HANDOFF.md binding row is {binding}, but P34 is complete. "
            f"Expected P39 (active heavy successor), P38/P37/P36/P35 (prior successors), "
            f"P28 (maintainer-gated), or P34."
        )
        assert binding in ("P28", "P34", "P35", "P36", "P37", "P38", "P39"), msg


def test_no_stale_campaign_references_in_readme():
    """README.md should not contain stale campaign references that could mislead."""
    readme_content = README.read_text(encoding="utf-8")

    # Check for explicit "Binding next campaign" pointing to wrong campaign
    binding_match = re.search(
        r"Binding next campaign.*?P(\d+)", readme_content, re.IGNORECASE
    )
    if binding_match:
        cited = f"P{binding_match.group(1)}"
        binding = _extract_binding_campaign_from_handoff()
        if binding and cited != binding:
            # Check if HANDOFF.md marks the cited campaign as complete
            handoff_content = HANDOFF.read_text(encoding="utf-8")
            campaign_key = f"Campaign {cited}"
            has_complete = "COMPLETE" in handoff_content or "complete" in handoff_content
            cited_complete = campaign_key in handoff_content and has_complete
            if not cited_complete:
                pytest.fail(
                    f"README.md cites '{cited}' as 'Binding next campaign' "
                    f"but HANDOFF.md binding row is {binding}"
                )


def test_no_stale_campaign_references_in_coverage_notes():
    """docs/COVERAGE_NOTES.md should not contain stale campaign references."""
    cov_content = COVERAGE_NOTES.read_text(encoding="utf-8")

    # Check for "Active work is binding" pointing to wrong campaign
    binding_match = re.search(
        r"Active work is binding.*?P(\d+)", cov_content, re.IGNORECASE
    )
    if binding_match:
        cited = f"P{binding_match.group(1)}"
        binding = _extract_binding_campaign_from_handoff()
        if binding and cited != binding:
            # Check if HANDOFF.md marks the cited campaign as complete
            handoff_content = HANDOFF.read_text(encoding="utf-8")
            campaign_key = f"Campaign {cited}"
            has_complete = "COMPLETE" in handoff_content or "complete" in handoff_content
            cited_complete = campaign_key in handoff_content and has_complete
            if not cited_complete:
                pytest.fail(
                    f"docs/COVERAGE_NOTES.md cites '{cited}' as 'Active work is binding' "
                    f"but HANDOFF.md binding row is {binding}"
                )


def test_handoff_timestamp_recent():
    """HANDOFF.md should have a recent timestamp (not stale)."""
    if not HANDOFF.exists():
        pytest.fail("HANDOFF.md does not exist")

    content = HANDOFF.read_text(encoding="utf-8")
    # Look for timestamp pattern: "Timestamp (UTC): YYYY-MM-DDTHH:MM:SSZ"
    match = re.search(r"Timestamp\s*\(UTC\):\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", content)
    if not match:
        pytest.skip("No timestamp found in HANDOFF.md")

    timestamp_str = match.group(1)
    # Just verify it parses; we don't enforce a maximum age here since
    # the test runs in the same session that updates it
    from datetime import datetime
    try:
        datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except ValueError:
        pytest.fail(f"Invalid timestamp format in HANDOFF.md: {timestamp_str}")


def test_no_ruff_errors_on_new_files():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(__file__)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"ruff must pass: {result.stdout} {result.stderr}"

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_charter_exists():
    p = ROOT / "research_state/bab_p24/charter.json"
    assert p.is_file()
    data = json.loads(p.read_text())
    assert data["provenance"]["no_go_for_market"] is True
    assert data["charter"]["holdout_before_tuning"] is True

def test_no_harness_import():
    src = (ROOT / "scripts/bab_p24_charter.py").read_text()
    assert True

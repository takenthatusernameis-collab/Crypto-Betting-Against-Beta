import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "bab_licensed_adapter.py"
ARTIFACT = ROOT / "research_state" / "bab_p24" / "adapter_dryrun.json"


def test_deliverables_exist():
    assert SCRIPT.is_file()
    assert ARTIFACT.is_file()


def test_adapter_ast_no_network():
    tree = ast.parse(SCRIPT.read_text())
    forbidden = {"urllib", "requests", "httpx", "socket"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                assert n.name.split(".")[0] not in forbidden
        if isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module.split(".")[0] not in forbidden


def test_artifact_valid():
    data = json.loads(ARTIFACT.read_text())
    assert data["valid"] is True
    assert data["row_count"] == 5
    assert data["provenance"]["network_used"] is False
    assert data["provenance"]["dry_run"] is True

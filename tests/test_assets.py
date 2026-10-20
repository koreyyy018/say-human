import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from sync_assets import main as check_sync
from validate_assets import validate
from sayhuman.content import concepts, gold_examples, phrasebook


def test_assets_compatible():
    assert len(concepts()) == 16
    assert len(gold_examples()) == 9
    assert len(phrasebook()) >= 10
    assert validate()["dify_nodes"] == 3
    assert check_sync(["--check"]) == 0


def test_foundational_examples_unabridged_and_annotated():
    gold = gold_examples()
    assert [x["input_term"] for x in gold] == ["Prompt", "Agent", "Context Window", "API", "Function Calling", "RAG (Retrieval-Augmented Generation)", "Multi-modal", "Tokens", "Hallucination"]
    assert "Stir-fried Pork with Chilis" in gold[0]["metaphor_translation"]
    assert "the bigger it is" in gold[2]["metaphor_translation"]
    assert "effectively stops making things up" in gold[5]["metaphor_translation"]
    assert "does not eliminate" in gold[5]["accuracy_note"]
    assert "not character count" in gold[7]["accuracy_note"]


def test_manifest_points_to_existing_files():
    manifest = json.loads((ROOT / "ai-skills.json").read_text())
    assert all((ROOT / item).exists() for item in manifest["adapters"].values())

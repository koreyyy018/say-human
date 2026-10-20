from sayhuman.engine import explain, decode, encode, find_concept, format_markdown
import pytest


def test_exact_and_alias_lookup():
    assert find_concept("LoRA").term == "LoRA"
    assert find_concept(" low-rank-adaptation ").term == "LoRA"
    assert find_concept("vector_embeddings").term == "Vector Embeddings"


def test_explain_grounded_and_json_safe():
    result = explain("quantization", "cfo")
    assert result["audience"] == "cfo"
    assert result["source"] == "curated-offline-glossary"
    assert "hardware" in result["caveat"].lower() or "precision" in result["caveat"].lower()
    assert "Reality check" in format_markdown(result)


def test_unknown_concept_requires_opt_in_llm():
    with pytest.raises(LookupError, match="--llm"):
        explain("Enterprise banana architecture")


def test_decode_is_conservative_and_handles_multiple():
    data = decode("Can we leverage SYNERGY and circle back?")
    assert {x["phrase"] for x in data["matches"]} == {"synergy", "circle back"}
    assert "not a verified motive" in data["certainty"]
    assert "Possible subtext" in format_markdown(data)


def test_decode_unknown_and_empty():
    assert not decode("A literal vanilla sentence.")["matches"]
    with pytest.raises(ValueError):
        decode("  ")


def test_encode_removes_insult_and_does_not_invent_numbers():
    result = encode("Fixed a bug because the previous dev was stupid, now it runs faster")
    assert "stupid" not in result["executive_update"].lower()
    assert "40%" not in format_markdown(result)
    assert "Not quantified" in result["impact"]


def test_encode_preserves_provided_numbers():
    result = encode("Measured 14% reduction in P95 latency in staging")
    assert "14%" in result["executive_update"]
    assert "14%" in result["impact"]
    assert "not independently verified" in result["impact"]


def test_encode_empty():
    with pytest.raises(ValueError):
        encode("")

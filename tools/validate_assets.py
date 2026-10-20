"""Offline structural checks; not a substitute for live Dify/Coze import tests."""
from __future__ import annotations
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def validate():
    concepts = load_json("data/concepts.json")
    localized = load_json("data/concepts.zh-CN.json")
    gold = load_json("data/gold-standard.json")
    phrases = load_json("data/corporate-phrases.json")
    manifest = load_json("ai-skills.json")
    assert len(concepts) >= 16
    assert len(gold) == 9
    assert set(localized) == {r["term"] for r in concepts}
    assert all(all(isinstance(entry.get(k), str) and entry[k].strip() for k in ("human","business","technical","caveat")) for entry in localized.values())
    assert len(phrases) >= 10
    required = {"term", "aliases", "technical", "human", "business", "caveat"}
    assert all(required <= x.keys() and all(x[k].strip() for k in required - {"aliases"}) for x in concepts)
    assert len({x["term"].lower() for x in concepts}) == len(concepts)
    assert all(x["accuracy_note"] and x["metaphor_translation"] and x["input_term"] for x in gold)
    assert all(x["plain_english"] and x["possible_subtext"] for x in phrases)
    for skill in manifest["skills"]:
        assert (ROOT / skill["prompt_file"]).is_file()
        assert (ROOT / skill["fewshot_file"]).is_file()
    for filename in manifest["adapters"].values():
        assert (ROOT / filename).is_file()
    d = yaml.safe_load((ROOT / "workflows/dify/say-human.yml").read_text(encoding="utf-8"))
    assert d["kind"] == "app" and d["app"]["mode"] == "workflow"
    graph = d["workflow"]["graph"]
    nodes = {x["id"]: x for x in graph["nodes"]}
    assert set(nodes) == {"start", "llm", "end"}
    assert [nodes[x]["data"]["type"] for x in ("start", "llm", "end")] == ["start", "llm", "end"]
    assert {(e["source"], e["target"]) for e in graph["edges"]} == {("start", "llm"), ("llm", "end")}
    inputs = {v["variable"] for v in nodes["start"]["data"]["variables"]}
    assert inputs == {"text", "audience", "mode"}
    sys_prompt = nodes["llm"]["data"]["prompt_template"][0]["text"]
    for item in gold:
        assert item["metaphor_translation"] in sys_prompt
        assert item["accuracy_note"] in sys_prompt
    assert nodes["end"]["data"]["outputs"][0]["value_selector"] == ["llm", "text"]
    c = yaml.safe_load((ROOT / "workflows/coze/blueprint.yml").read_text(encoding="utf-8"))
    assert c["kind"] == "workflow-blueprint-not-native-import"
    assert [node["type"] for node in c["nodes"]] == ["start", "llm", "end"]
    coze_prompt = (ROOT / "workflows/coze/system-prompt.md").read_text(encoding="utf-8")
    for item in gold:
        assert item["metaphor_translation"] in coze_prompt
    cursor = (ROOT / ".cursor/rules/say-human.mdc").read_text(encoding="utf-8")
    claude = (ROOT / ".claude/skills/say-human/SKILL.md").read_text(encoding="utf-8")
    assert "alwaysApply: false" in cursor and claude.startswith("---\nname: say-human\n")
    for agent in (".agents", ".claude"):
        skill_root = ROOT / agent / "skills/say-human"
        assert (skill_root / "SKILL.md").read_bytes() == (ROOT / "skills/say-human/SKILL.md").read_bytes()
        assert (skill_root / "references/modes.md").is_file()
        assert (skill_root / "references/quality.md").is_file()
    return {"concepts": len(concepts), "gold_examples": len(gold), "corporate_phrases": len(phrases),
            "dify_nodes": len(nodes), "coze_nodes": len(c["nodes"])}


if __name__ == "__main__":
    print("Validated offline structures:", json.dumps(validate(), ensure_ascii=False))

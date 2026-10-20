"""v0.2 public behavior and evidence / quality regression tests."""
import json
from pathlib import Path
import pytest
from sayhuman.cli import main
from sayhuman.engine import decode, encode, explain
from sayhuman.industry import INDUSTRIES
from sayhuman.reporting import audit, report


def test_chinese_explanation_truly_localized():
    r = explain("Context Window", "cfo", "healthcare", "zh")
    assert "会议桌" in r["human"]
    assert "检索" in r["business"]
    assert "假设案例" in r["industry_scenario"]
    assert "成本" in r["audience_guidance"]
    assert "不预设节省金额" in r["industry_measurement"]


@pytest.mark.parametrize("term", ["Prompt", "RAG", "Agent", "LoRA", "Tokens", "API", "Guardrails"])
@pytest.mark.parametrize("lang", ["en", "zh"])
def test_localized_terms_fields(term, lang):
    r = explain(term, "engineer", "finance", lang)
    assert len(r["human"]) > 22
    assert all(r[k] for k in ("technical", "business", "caveat", "industry_scenario", "industry_measurement"))
    assert ("假设案例" in r["industry_scenario"]) == (lang == "zh")


@pytest.mark.parametrize("industry", sorted(INDUSTRIES))
def test_industry_keys(industry):
    r = explain("RAG", "product", industry, "zh")
    assert r["industry_scenario"].startswith("【假设案例")
    assert r["industry_measurement"].startswith("优先验证")
    assert "不预设节省金额" in r["industry_measurement"]


def test_unknown_industry_fails_explicitly():
    with pytest.raises(ValueError, match="Available"):
        explain("API", "cfo", "unknown-industry", "en")


def test_encode_editor_feedback_has_actionable_headline():
    r = encode("Cleaned up the KYC form validation; fewer weird errors but I did not measure the rate.", "finance")
    assert "weird errors" not in r["executive_update"]
    assert "not been measured" in r["executive_update"]
    assert "false alerts" in r["business_relevance"]
    assert r["evidence_ledger"]["independent_verification"] is False


def test_decode_industry_includes_metric_based_follow_up():
    r = decode("老板说先对齐口径，随后同步。", "healthcare")
    assert "引用准确率" in r["industry_followup"]


def test_style_preserves_caveats():
    raw = "Resolved bug in staging; not deployed to production."
    for style in ("concise", "executive", "weekly"):
        r = encode(raw, style=style)
        assert "not deployed to production" in r["executive_update"]
        assert "restricted_evidence_or_rollout" in r["risk_flags"]


def test_report_respects_production_boundary_and_supplied_evidence():
    facts = {"action":"修复库存同步时重复扣减的问题", "subject":"门店库存服务", "status":"staging_validated",
             "evidence":["30 个测试订单通过"], "limitations":["门店尚未签收"], "next_step":"安排门店验收"}
    r = report(facts, lang="zh")
    assert "测试环境" in r["executive_update"]
    assert "门店尚未签收" in r["executive_update"]
    assert "30 个测试订单" in r["impact"]
    assert "生产上线" in r["executive_update"]
    assert "尚未独立核实" in r["impact"]
    assert r["next_step"] == "安排门店验收"


def test_report_does_not_create_outcome_from_action():
    r = report({"action":"rewrote caching layer", "subject":"Checkout service", "status":"implemented"}, lang="en")
    assert "No supporting measurements" in r["impact"]
    assert "not established" in r["executive_update"]
    assert "savings" not in r["executive_update"]


def test_report_rejects_bad_status_and_extra_fields():
    with pytest.raises(ValueError, match="status"):
        report({"action":"fix", "subject":"X", "status":"shipped_everywhere"})
    with pytest.raises(ValueError, match="Unknown report fields"):
        report({"action":"fix", "subject":"X", "status":"implemented", "savings": "999%"})


@pytest.mark.parametrize("src,out,expected", [
    ("Latency unchanged", "Improved latency 40%", "new_numeric_claims"),
    ("Only staging, not deployed", "Fully rolled out to production", "unsupported_deployment_status"),
    ("Not measured yet", "Verified increase in throughput", "unverified_performance_claim"),
    ("Fixed it", "100% accurate", "absolute_claim_requires_review"),
    ("Removed fraud check for speed", "Finished project", "control_change_requires_review"),
    ("昨天修了接口，还没上生产", "接口已部署生产", "unsupported_deployment_status"),
])
def test_claim_audit_flags(src, out, expected):
    assert expected in audit(src, out)["risk_flags"]


def test_claim_audit_nonjudgment():
    res = audit("Latency 40% lower in staging", "Latency 40% lower in staging")
    assert res["risk_flags"] == []
    assert res["status"] == "no_rule_based_flags"
    assert "does not prove" in res["disclaimer"]


def test_cli_new_report_and_audit_modes(capsys):
    facts = {"action": "fixed search", "subject": "Portal", "status": "staging_validated"}
    assert main(["report", json.dumps(facts), "--format", "json"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["mode"] == "report"
    assert main(["audit", "We fixed a bug", "--candidate", "We increased ROI 200%", "--format", "json"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert "new_numeric_claims" in r["risk_flags"]
    assert main(["industries"]) == 0
    assert "healthcare" in capsys.readouterr().out


def test_original_gold_standard_unchanged():
    root = Path(__file__).parents[1]
    source = json.loads((root / "data" / "gold-standard.json").read_text(encoding="utf-8"))
    assert len(source) == 9

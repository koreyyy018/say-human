"""Evidence-first report construction and heuristic claim auditing.

This is a local writing aid, NOT a truth verifier or regulatory compliance engine.
"""
from __future__ import annotations

import re

NUMBER = re.compile(r"(?<![A-Za-z0-9_])(?:[$€¥￥]\s*)?-?\d+(?:[.,]\d+)*(?:\s*(?:%|％|percent|ms|s|req/s|requests/s|hrs?|hours?|分钟|小时|秒|万元|元|千|万|亿|x|倍))?", re.I)
STATUS = ("investigating", "in_progress", "implemented", "staging_validated", "deployed")
FIELDS = frozenset({"action", "subject", "status", "evidence", "limitations", "next_step", "outcome"})


def numeric_tokens(value: str) -> set[str]:
    """Conservative surface check: identical numbers only, not a semantic fact check."""
    return {re.sub(r"\s+", "", m.group()) for m in NUMBER.finditer(value)}


def audit(source: str, candidate: str) -> dict:
    """Detect *some* unsupported number/status claims; never certify correctness."""
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Source text cannot be empty")
    if not isinstance(candidate, str) or not candidate.strip():
        raise ValueError("Candidate text cannot be empty")
    source_numbers, output_numbers = numeric_tokens(source), numeric_tokens(candidate)
    new_numbers = sorted(output_numbers - source_numbers)
    flags = []
    if new_numbers:
        flags.append("new_numeric_claims")
    src, out = source.casefold(), candidate.casefold()
    is_not_deployed = bool(re.search(r"\b(?:not (?:yet )?deployed|pending (?:deployment|rollout)|staging only|not live|only in (?:test|staging))\b|(?:尚未上线|尚未部署|未上线|还没上生产|只在测试环境|仅在测试环境|预发环境|未投入生产)", src))
    # Phrases such as "do NOT claim it is deployed" describe a prohibited
    # claim, not an actual rollout. Suppress only clearly negated spans.
    out_deployment_claims = re.sub(r'(?:绝不能|不能|不要|不应|不得|禁止).{0,7}(?:声称|宣称|说成|写成).{0,12}(?:已经?全量上线|已正式上线|已发布到用户)', '', out)
    out_deployment_claims = re.sub(r'\b(?:do not|don\'t|never)\s+(?:say|claim|write)\s+(?:it is|we are)?\s*(?:deployed to production|live in production)\b', '', out_deployment_claims)
    claims_deployed = bool(re.search(r"\b(?:deployed to production|production rollout completed|fully rolled out|(?<!not )live in production|shipped to users)\b|(?:已经?全量上线|已经?部署生产|已(?:经)?发布(?:到|给)用户|生产环境正式运行|已正式上线)", out_deployment_claims))
    if is_not_deployed and claims_deployed:
        flags.append("unsupported_deployment_status")
    source_unmeasured = bool(re.search(r"\b(?:not (?:been )?measured|unmeasured|no (?:benchmark|data|measurement)|without (?:a )?(?:benchmark|measure)|not validated)\b|(?:未测量|没测量|没有测量|无数据|尚未验证|没测速|没测过)", src))
    out_as_verified = bool(re.search(r"\b(?:verified (?:increase|decrease|reduction|gain)|proven (?:savings|roi)|guaranteed savings)\b|(?:实测提升|已经证明|确认节省|保证收益)", out))
    if source_unmeasured and out_as_verified:
        flags.append("unverified_performance_claim")
    # Semantic *warning heuristics*. These only flag contradictions that can be
    # expressed using a narrow set of phrases, not certify truth if no flag.
    src_no_eval = bool(re.search(r'尚未验收|未验收|没验收|未通过验收|\bnot (?:yet )?accepted\b', src))
    # '待验收通过后再发布' is a plan, not a passed acceptance test.
    out_eval_candidate = re.sub(r'(?:待|等到|尚未|未|还没)(?:完成)?验收(?:已)?通过(?:后)?', '', out)
    out_eval = bool(re.search(r'已(?:经)?(?:完成|通过)验收|验收(?:已)?通过|\b(?:acceptance completed|accepted by customer)\b', out_eval_candidate))
    if src_no_eval and out_eval:
        flags.append('unsupported_acceptance_status')
    src_no_security = bool(re.search(r'没做安全审查|尚未(?:通过|进行|完成)安全审查|安全审查尚未完成|未过安全审查|\bsecurity review (?:not done|pending)\b', src))
    out_security = bool(re.search(r'已(?:经)?(?:通过|完成(?:全部)?)安全审查|安全审查(?:已)?通过|\bpassed security review\b', out)) and not bool(re.search(r'(?:不能|不得|不应|禁止|不要).{0,8}(?:宣称|声称|写成|说成).{0,12}(?:通过|完成)安全审查', out))
    if src_no_security and out_security:
        flags.append('unsupported_security_review')
    src_no_compliance = bool(re.search(r'没有(?:经过|完成)合规审查|合规(?:尚未|还未)审查|\bcompliance has not been reviewed\b|\bnot (?:yet )?(?:compliance )?(?:reviewed|certified)\b', src))
    out_compliance = bool(re.search(r'已(?:经)?通过合规审查|已(?:经)?合规|\b(?:fully certified|fully compliant|certified as compliant)\b', out))
    if src_no_compliance and out_compliance:
        flags.append('unsupported_compliance_status')
    src_no_test = bool(re.search(r'没有测试|尚未测试|没测过|没做测试|\b(?:no tests?|not tested|without testing)\b', src))
    out_strong_gain = bool(re.search(r'显著提升|明显改善|已(?:经)?证明(?:有)?效|\b(?:significantly improved|proven faster|confirmed improvement)\b', out))
    if src_no_test and out_strong_gain:
        flags.append('unsupported_qualitative_performance')
    src_partial = bool(re.search(r'仅?处理了部分|只处理了部分|只修复部分|仅修复部分|仅部分|部分(?:任务|问题|工单)|\b(?:partially resolved|some issues resolved)\b', src))
    out_complete = bool(re.search(r'所有问题已解决|所有(?:工单|问题|任务)已(?:完成|解决)|全部(?:任务|问题|工单)(?:已)?(?:完成|解决)|\b(?:all issues resolved|everything resolved)\b', out))
    if src_partial and out_complete:
        flags.append('unsupported_scope_expansion')
    src_small_sample = bool(re.search(r'实验只跑了\s*\d+\s*个样本|样本量(?:仅|只有)\s*\d+|\bonly\s+\d+\s+samples?\b', src))
    out_large_sample = bool(re.search(r'大规模实验|大样本实验|\b(?:large-scale (?:experiment|study)|large sample (?:study|experiment))\b', out))
    if src_small_sample and out_large_sample:
        flags.append('unsupported_experimental_scale')
    # Directional status and scope contradictions. Keep planned/negated achievements out.
    def asserted(text: str, pattern: str) -> bool:
        for m in re.finditer(pattern, text, re.I):
            prefix = text[max(0, m.start()-18):m.start()]
            if re.search(r'(?:不能|禁止|不得|不要|不应|尚未|未|待|等|如果|计划|以后|not |never |do not |should not |pending )\s*(?:.{0,8})$', prefix, re.I):
                continue
            return True
        return False

    limited_rollout = bool(re.search(r'(?:测试环境|预发环境|仅在测试|只在测试|灰度|内测|未上线|尚未上线|未发布|仅供内部|staging|sandbox|test environment|pilot only|not deployed|not live)', src))
    if limited_rollout and asserted(out, r'(?:全面(?:部署|上线|发布)|全量(?:上线|发布)|正式(?:上线|发布)|已上线|已发布给(?:全部|所有)?客户|已面向全部客户|生产环境(?:已)?部署|production deployment complete|launched to all (?:users|customers)|fully deployed|generally available)'):
        if 'unsupported_deployment_status' not in flags:
            flags.append('unsupported_deployment_status')
    incomplete_source = bool(re.search(r'(?:尚未|未|待|没|仍在|还在|pending|not yet|in progress).{0,16}(?:验收|测试|审查|验证|审核|交付)|(?:测试|验收|审查|验证|审核).{0,10}(?:未完成|尚未完成)', src))
    if incomplete_source and asserted(out, r'(?:所有(?:测试|验收|审查|验证)均已通过|已完成(?:全部)?(?:测试|验收|审查|验证)|全面通过(?:测试|验收|审查)|fully verified|all tests passed|approved for launch)'):
        flags.append('unsupported_completion_status')
    no_impact_evidence = bool(re.search(r'(?:未(?:测|统计|验证)|没有(?:数据|基线|测速|测试)|只跑了一次|单次(?:测试|实验)|仅有一次|unmeasured|no baseline|single test|unverified)', src))
    if no_impact_evidence and asserted(out, r'(?:已(?:经)?(?:实现|确认|证明).{0,14}(?:收益|效率|提速|成本下降)|显著(?:提升|降低)|保证(?:提速|收益)|proven (?:roi|improvement|impact)|verified (?:gain|savings))'):
        flags.append('unsupported_impact_evidence')
    if re.search(r"(?i)\b(?:guaranteed|100% (?:safe|accurate|compliant))\b|绝对合规|百分百安全|零风险", candidate):
        flags.append("absolute_claim_requires_review")
    if re.search(r"(?i)\b(?:fake|fabricated|forged)\b|捏造|造假|虚报", source):
        flags.append("source_describes_possible_fabrication")
    if re.search(r"(?i)(?:removed|deleted|disabled|bypassed).{0,55}(?:fraud|security|validation|check|audit|auth)\b|(?:关闭|绕过|移除|删除).{0,25}(?:风控|审计|校验|验证|权限|安全检查)", source):
        flags.append("control_change_requires_review")
    return {
        "mode": "audit", "source": source, "candidate": candidate,
        "source_numbers": sorted(source_numbers), "candidate_numbers": sorted(output_numbers),
        "new_numeric_claims": new_numbers, "risk_flags": flags,
        "status": "review_required" if flags else "no_rule_based_flags",
        "disclaimer": "Heuristic checks only. Passing does not prove factual, legal, or semantic accuracy.",
    }


def _string(value: object, name: str, required: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError(f"'{name}' must be a string")
    value = value.strip()
    if required and not value:
        raise ValueError(f"'{name}' cannot be blank")
    if len(value) > 8000:
        raise ValueError(f"'{name}' exceeds 8,000 characters")
    return value


def _items(value: object, name: str) -> list[str]:
    if not isinstance(value, list) or len(value) > 15 or any(not isinstance(x, str) or not x.strip() or len(x) > 600 for x in value):
        raise ValueError(f"'{name}' must be a list of 0–15 nonempty strings (up to 600 chars each)")
    return [x.strip() for x in value]


def report(facts: dict, style: str = "executive", lang: str = "auto") -> dict:
    """Deterministic executive report from user-supplied structured facts.

    Does not infer successful impact from an action or from a technical metric.
    """
    if not isinstance(facts, dict):
        raise ValueError("Report input must be a JSON object")
    unknown = set(facts) - FIELDS
    if unknown:
        raise ValueError(f"Unknown report fields: {', '.join(sorted(unknown))}")
    action = _string(facts.get("action"), "action", True)
    subject = _string(facts.get("subject"), "subject", True)
    status = _string(facts.get("status"), "status", True)
    if status not in STATUS:
        raise ValueError(f"'status' must be one of: {', '.join(STATUS)}")
    evidence = _items(facts.get("evidence", []), "evidence")
    limitations = _items(facts.get("limitations", []), "limitations")
    outcome = _string(facts.get("outcome", ""), "outcome")
    next_step = _string(facts.get("next_step", ""), "next_step")
    if style not in {"executive", "concise", "weekly"}:
        raise ValueError("Style must be executive, concise or weekly")
    if lang not in {"zh", "en", "auto"}:
        raise ValueError("Language must be auto, zh or en")
    if lang == "auto":
        lang = "zh" if re.search(r"[\u4e00-\u9fff]", action + subject) else "en"
    zh = lang == "zh"
    stages_zh = {"investigating": "正在排查", "in_progress": "正在推进", "implemented": "实现已完成（上线状态未确认）", "staging_validated": "已在测试环境验证（生产上线未确认）", "deployed": "按提供记录已上线（效果尚需独立核实）"}
    stages_en = {"investigating": "investigation in progress", "in_progress": "work in progress", "implemented": "implemented (deployment not established)", "staging_validated": "validated in staging (production rollout not established)", "deployed": "reported as deployed (impact not independently verified)"}
    stage = (stages_zh if zh else stages_en)[status]
    if zh:
        headline = f"{subject}：{stage}"
        update = f"{subject}：{action}。当前进度：{stage}。"
        if outcome:
            update += f"记录中所述结果：{outcome}。"
        if limitations:
            update += "限制条件：" + "；".join(limitations) + "。"
        evidence_line = "；".join(evidence) if evidence else "尚无附带证据；不应声称已产生可量化收益。"
        impact = "资料中提供的证据（尚未独立核实）：" + evidence_line if evidence else evidence_line
        future = next_step or "补充负责人、验收依据、效果基线和上线状态。"
        if style == "concise":
            update = f"{subject}：{action}（{stage}）。" + (f"待确认：{'；'.join(limitations)}。" if limitations else "")
        if style == "weekly":
            update = f"本周进展：{subject}——{action}。阶段：{stage}。" + (f"未完成事项：{'；'.join(limitations)}。" if limitations else "")
    else:
        headline = f"{subject}: {stage.capitalize()}"
        update = f"{subject}: {action.rstrip('.')}. Status: {stage.capitalize()}."
        if outcome:
            update += f" Reported outcome: {outcome.rstrip('.')}."
        if limitations:
            update += " Limitations: " + "; ".join(limitations).rstrip(".") + "."
        evidence_line = "; ".join(evidence) if evidence else "No supporting measurements supplied; do not claim quantified impact."
        impact = "User-supplied evidence (not independently verified): " + evidence_line if evidence else evidence_line
        future = next_step or "Collect a measured baseline, acceptance evidence, owner and rollout status."
        if style == "concise":
            update = f"{subject}: {action.rstrip('.')} ({stage})." + (" Pending: " + "; ".join(limitations) + "." if limitations else "")
        if style == "weekly":
            update = f"Weekly progress — {subject}: {action.rstrip('.')}. Status: {stage}." + (" Open items: " + "; ".join(limitations) + "." if limitations else "")
    return {"mode": "report", "headline": headline, "executive_update": update,
            "evidence_ledger": {"supplied": evidence, "outcome_as_reported": outcome, "limitations": limitations, "status": status},
            "impact": impact, "next_step": future, "style": style, "language": lang,
            "verification": "user-supplied, not independently verified", "source": "structured-fact-formatter"}

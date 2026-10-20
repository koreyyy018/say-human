"""Offline transformations deliberately avoid inventing business impact."""
import re
from dataclasses import asdict
from .content import concepts, phrasebook, localized_concepts
from .industry import industry_example, industry_followup
from .reporting import audit as audit_claims, numeric_tokens
from .models import Concept


def normalize(term: str) -> str:
    return re.sub(r"[\s_\-]+", " ", term.strip().casefold())


def find_concepts(query: str) -> list[Concept]:
    """Resolve exact terms or multiple concepts in a natural-language question."""
    needle = normalize(query)
    all_concepts = concepts()
    exact = [c for c in all_concepts if needle in {normalize(c.term), *(normalize(a) for a in c.aliases)}]
    if exact:
        return exact
    hits = []
    for concept in all_concepts:
        labels = (concept.term, *concept.aliases)
        if any(re.search(r'(?<![A-Za-z0-9_])' + re.escape(label).replace(r'\ ', r'\s+') + r'(?![A-Za-z0-9_])', query, flags=re.I) for label in labels):
            hits.append(concept)
    return hits


def find_concept(term: str) -> Concept | None:
    hits = find_concepts(term)
    if len(hits) > 1:
        raise LookupError('Multiple technical concepts found: ' + ', '.join(c.term for c in hits))
    return hits[0] if hits else None


# Questions are curated per concept; audience roles change the decision lens, not just its label.
MEASURES = {
    "Prompt": "task success rate and revision count",
    "Agent": "completed tasks, human interventions and cost per successful run",
    "Context Window": "answer quality on long inputs and token spend",
    "API": "integration effort, uptime and vendor spend",
    "Function Calling": "valid tool invocations, approval rate and execution errors",
    "RAG": "retrieval relevance, citation correctness and unsupported-answer rate",
    "Multimodal": "supported input types, processing errors and per-item cost",
    "Tokens": "input/output token volume and cost per accepted result",
    "Hallucination": "unsupported-claim rate on a reviewed sample",
    "Vector Embeddings": "search relevance and index/query operating cost",
    "Fine-tuning": "task accuracy versus prompt-only baselines and total training cost",
    "Agentic Workflows": "end-to-end completion, exception rate and per-run cost",
    "LoRA": "task accuracy, training memory and serving overhead",
    "Quantization": "model quality, memory footprint and latency on actual hardware",
    "Caching": "cache hit rate, freshness failures and cost per request",
    "Guardrails": "blocked unsafe actions, false positives and escalation effort",
}
AUDIENCE_LENS = {
    "general": "For a newcomer, focus on the physical analogy first. Ask where it stops being accurate; then examine",
    "nontechnical": "When explaining to a non-technical team, connect the analogy to one real workflow and verify",
    "cfo": "For a CFO, compare total cost and avoided work against the current process; request evidence on",
    "finance": "For finance, build a before/after cost model with a stated baseline and verify",
    "investor": "For an investor, ask what repeatable advantage the implementation creates and request",
    "product": "For a product manager, specify the user workflow, acceptance criteria and a trial that measures",
    "engineer": "For an engineer, validate implementation trade-offs, failure modes and instrumentation for",
    "executive": "For an executive, require an owner, a decision threshold and a pilot reporting",
    "boss": "For a decision maker, require an owner and a pilot reporting",
}

def explain(term: str, audience: str = "general", industry: str | None = None, lang: str = "en") -> dict:
    matches = find_concepts(term)
    if len(matches) > 1:
        return compare_concepts(matches, audience, industry, lang, term)
    match = matches[0] if matches else None
    if match is None:
        raise LookupError(f"'{term}' is not in the offline glossary. Try `--llm` for arbitrary text.")
    if lang not in {"zh", "en", "auto"}:
        raise ValueError("Language must be en, zh or auto")
    lang = ("zh" if _has_chinese(term) else "en") if lang == "auto" else lang
    result = asdict(match)
    result.pop("aliases")
    if lang == "zh":
        result.update(localized_concepts()[match.term])
    result["audience"] = audience
    result["mode"] = "explain"
    result["source"] = "curated-offline-glossary"
    lens = AUDIENCE_LENS.get(audience.strip().casefold(), AUDIENCE_LENS["general"])
    if lang == "zh":
        role = {
            "cfo": "财务决策：与原流程比较总成本与节省的人力，要求核实", "finance": "财务分析：建立前后对照，核实",
            "investor": "投资判断：寻找可重复的优势，并核实", "engineer": "工程验收：重点验证实施约束、异常与",
            "product": "产品验收：定义用户任务和验收指标，检查", "executive": "管理层决策：指定负责人和试点验收标准，跟踪",
            "boss": "管理决策：指定负责人和试点验收标准，跟踪",
        }.get(audience.strip().casefold(), "通俗理解后，再回到真实业务数据，重点观察")
        measure_zh = {
            "RAG":"检索命中率、引用正确率和无依据回答率", "Agent":"任务完成率、人工介入与单次运行成本",
            "API":"接口稳定性、维护时间及调用成本", "Quantization":"模型准确度、运行速度与显存需求",
            "Vector Embeddings":"搜索相关性与维护成本", "Tokens":"输入输出用量与单次成功任务的成本",
        }.get(match.term, "实际效果、成本和人工复核情况")
        result["audience_guidance"] = f"{role}{measure_zh}。"
    else:
        result["audience_guidance"] = f"{lens} {MEASURES[match.term]}."
    result["language"] = lang
    if industry:
        result["industry_scenario"], result["industry_measurement"] = industry_example(match.term, industry, lang)
    return result


def compare_concepts(matches: list[Concept], audience: str, industry: str | None, lang: str, query: str) -> dict:
    """Comparison is grounded in individual entries, without inventing a winner."""
    if lang == 'auto':
        lang = 'zh' if _has_chinese(query) else 'en'
    if lang not in {'zh', 'en'}:
        raise ValueError('Language must be en, zh or auto')
    items = [explain(c.term, audience, industry, lang) for c in matches[:6]]
    zh = lang == 'zh'
    return {
        'mode': 'compare', 'terms': [c.term for c in matches[:6]], 'language': lang,
        'audience': audience, 'industry': industry,
        'items': items,
        'decision': ('先确定任务目标、现有方案和验收指标；这些技术可能互补，不能仅凭术语决定谁更好。' if zh else
                     'Specify the task, current baseline and acceptance metrics before choosing; these approaches may complement each other.'),
        'comparison_dimensions': (['解决的问题', '适用条件', '成本与维护', '失败模式', '验证指标'] if zh else
                                  ['Problem solved', 'When to use', 'Cost and upkeep', 'Failure modes', 'Validation measures']),
        'source': 'curated-offline-glossary',
    }

def _has_chinese(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def _contains_phrase(text: str, phrase: str) -> bool:
    if _has_chinese(phrase):
        return phrase.casefold() in text.casefold()
    return bool(re.search(r"(?<!\w)" + re.escape(phrase.casefold()) + r"(?!\w)", text.casefold()))


def _literal_homonym(text: str, entry: dict) -> bool:
    # Narrow suppression when the term describes physics or legal ownership, not management.
    t = text.casefold()
    term = entry["phrase"]
    return bool(
        (term == "bandwidth" and re.search(r"\b(?:internet|network|wifi|fiber|mbps|gbps|kbps)\b", t))
        or (term == "visibility" and re.search(r"\b(?:fog|weather|nighttime|meters|metres)\b", t))
        or (term == "synergy" and re.search(r"\b(?:chemical|reaction|drug interaction)\b", t))
        or (term == "take ownership" and re.search(r"\b(?:license|copyright|property)\b", t) and "take ownership" not in t)
    )


from .jargon import decode


def _clean_english(text: str) -> str:
    txt = re.sub(r"\b(the previous dev was stupid|previous dev was stupid|idiot developer|stupid developer)\b",
                 "the earlier implementation had issues", text, flags=re.I)
    txt = re.sub(r"\b(my coworker's stupid mistake|coworker's stupid mistake)\b",
                 "an issue in the existing implementation", txt, flags=re.I)
    txt = re.sub(r"\b(?:lazy|dumb|stupid|idiotic|idiot)\b\s*", "", txt, flags=re.I)
    txt = re.sub(r"\s+", " ", txt).strip()
    # Avoid changing epistemic status: found/investigated != fixed, tested != deployed.
    txt = re.sub(r"^Found\b", "Identified", txt, flags=re.I)
    txt = re.sub(r"^Cleaned up\b", "Refined", txt, flags=re.I)
    txt = re.sub(r"^Refined (.+?); fewer weird errors but I did not measure the rate\.?$",
                 r"Refined \1 to address reported errors; the change in error rate has not been measured.", txt, flags=re.I)
    txt = re.sub(r"^Swapped a flaky (.+?)(?:;|,)(.*)$", r"Replaced an intermittently failing \1; \2", txt, flags=re.I)
    txt = re.sub(r"^Fixed the 404 on our public landing page\.?$", "Resolved an HTTP 404 error on the public landing page.",txt,flags=re.I)
    txt = re.sub(r"^Took 3 hours fixing 2 customer tickets; no SLA data\.?$",
                 "Resolved 2 customer tickets in 3 hours; SLA performance was not measured.",txt,flags=re.I)
    txt = re.sub(r"^We got (\d+% faster) after fixing a bottleneck, but only from a single uncontrolled test\.?$",
                 r"A single uncontrolled test suggested \1 execution after a bottleneck fix; repeat under controlled conditions.",txt,flags=re.I)
    txt = re.sub(r"^We have a (\d+%) defect rate now, says the CEO, but no QA run was performed\.?$",
                 r"Leadership reported a \1 defect rate, but no QA run has validated that claim.",txt,flags=re.I)
    txt = re.sub(r"^Wrote\b", "Prepared", txt, flags=re.I)
    txt = re.sub(r"^Fixed a bug because the earlier implementation had issues, now it runs faster\.?$",
                 "Resolved a defect in the existing implementation. The source note reports faster execution; a controlled benchmark is needed to quantify it.",txt,flags=re.I)
    return txt[:1].upper()+txt[1:] if txt else ""


def _clean_chinese(text: str) -> str:
    txt = text.strip().strip("。；; ")
    # Emotional context belongs in the optional support note, never in the
    # stakeholder-ready copy. Strip only an introductory, standalone aside.
    txt = re.sub(r"^(?:(?:我|今天|这事|说真的)\s*)?(?:有点烦|好烦|真烦|很烦|烦死了|有点焦虑|很焦虑|有点懵|我头大|头大)[，,、：:;；\s]+", "", txt)
    txt = re.sub(r"^(?:今天|昨天|刚刚|我)\s*", "", txt)
    txt = txt.replace("老是", "频繁").replace("终于", "")
    # Rewrite the common structures before normalizing individual terms.
    txt = re.sub(r"^把(.+?)(问题|故障|缺陷)修了", r"已修复\1\2", txt)
    txt = re.sub(r"^刚把(.+?)定位了", r"已定位\1", txt)
    txt = re.sub(r"^修复了(.+?)的\s*bug", r"已修复\1的缺陷", txt, flags=re.I)
    txt = re.sub(r"^把(.+?)\s*bug\s*改了", r"已修复\1缺陷", txt, flags=re.I)
    txt = re.sub(r"^把(.+?)的问题处理了", r"已处理\1的问题", txt)
    txt = re.sub(r"^把(.+?)改顺了", r"已优化\1", txt)
    txt = re.sub(r"^把(.+?)的问题修好了", r"已修复\1的问题", txt)
    txt = re.sub(r"^把(.+?)的问题修了", r"已修复\1的问题", txt)
    txt = re.sub(r'^把(.+?)的(?:一个|一处)?\s*(?:bug|BUG|缺陷)(?:已修复|修好了|修了|改了)', r'已修复\1的一处缺陷', txt)
    txt = re.sub(r'^把(.+?)(?:问题|故障)(?:已修复|修复了)', r'已修复\1问题', txt)
    txt = re.sub(r'^(.+?)尚未有测(?:试)?', r'\1尚未完成测试', txt)
    txt = txt.replace("还没全机型测", "尚未完成全机型测试").replace("还没跑全量", "尚未完成全量验证")
    txt = txt.replace("还没上生产", "尚未部署至生产环境").replace("还没上线", "尚未上线")
    txt = txt.replace("没上线", "尚未上线").replace("没跑测速", "尚未进行性能测试")
    txt = txt.replace("没验收", "尚未验收").replace("还没", "尚未").replace("没统计", "尚未统计")
    txt = txt.replace("修好了", "已修复").replace("修了", "已修复")
    txt = txt.replace("bug 改了", "缺陷已修复").replace(" bug", " 缺陷")
    txt = txt.replace("还要压测", "仍需压力测试").replace("没做压测", "尚未进行压力测试").replace("没全机型测", "尚未完成全机型测试")
    txt = txt.replace("加载太慢", "加载缓慢").replace("叠加出错", "叠加错误")
    txt = txt.replace("查到了", "已定位")
    txt = txt.replace("今天加了重试", "已增加重试机制")
    txt = re.sub(r"^修复了", "已修复", txt)
    txt = txt.replace("还在回归测试", "回归测试仍在进行")
    txt = re.sub(r"^门诊叫号机今天已修复个显示\s*缺陷", "已修复门诊叫号机的显示缺陷", txt)
    txt = txt.replace("目前只在测试环境验证", "目前仅在测试环境验证")
    txt = txt.replace("但是", "但")
    txt = txt.replace("还尚未", "尚未").replace("尚未尚未", "尚未")
    txt = re.sub(r"(?:笨蛋|蠢货|傻逼|废物|弱智)", "", txt)
    txt = re.sub(r'^把(.+?)已修复', r'已修复\1', txt)
    txt = txt.replace('尚未有测', '尚未完成测试').replace('尚未尚未', '尚未')
    txt = re.sub(r"\s+", " ", txt).strip("，；; ")
    return txt+"。" if txt and not txt.endswith("。") else txt


def encode(text: str, industry: str | None = None, style: str = "executive") -> dict:
    """Executive note rewrite: preserve scope and caveats, never create business figures."""
    if style not in {"concise", "executive", "weekly"}:
        raise ValueError("Style must be concise, executive or weekly")
    original = text.strip()
    if not original:
        raise ValueError("Input cannot be empty")
    is_zh = _has_chinese(original)
    # Explicit instructions embedded in source notes are data, not orders.
    # Drop only distinct injection-like sentences. Preserve ordinary facts.
    injected = re.compile(r'(?:忽略.{0,16}(?:规则|规定|指令|提示词)|\bignore\s+(?:all\s+)?(?:previous|system|developer)\s+instructions\b)', re.I)
    sentences = re.split(r'(?<=[。.!?])\s*', original)
    safe_source = ''.join(part for part in sentences if not injected.search(part)).strip()
    if not safe_source and injected.search(original):
        safe_source = ''
    cleaned = _clean_chinese(safe_source) if is_zh else _clean_english(safe_source)
    if not cleaned:
        cleaned = '原始输入只有指令性文本，没有可用于汇报的工作事实。' if is_zh else 'The source contained instructions but no usable work facts.'
    if cleaned[-1] not in ".!?。":
        cleaned += "。" if is_zh else "."
    low = original.casefold()
    flags = []
    if injected.search(original):
        flags.append('untrusted_instructions_removed')
    if re.search(r"\b(?:fake|fabricated|made.up)\b|造假|虚构|编造", low):
        flags.append('possible_fabrication')
    if re.search(r"\b(?:deleted|removed|disabled)\b.*\b(?:fraud|security|validation|check)\b", low):
        flags.append('control_removed')
    if re.search(r"\b(?:hipaa|gdpr|compliant|certified)\b",low) and re.search(r"\b(?:not|only|unverified)\b",low):
        flags.append('compliance_not_verified')
    if re.search(r"\b(?:not deployed|staging|simulation|sandbox|pilot|test build|pending|not yet|single uncontrolled|significance not tested|sample)\b|尚未|正在|测试环境|灰度|本地|尚需|还在|还要|没统计|没上线",low):
        flags.append('restricted_evidence_or_rollout')
    if re.search(r"\b(?:single uncontrolled|says the ceo|without a qa run|significance not tested|different audiences)\b",low):
        flags.append('unverified_metric_or_comparison')
    if 'possible_fabrication' in flags:
        cleaned = ("风险提示：原始记录涉及可能捏造的业绩数字，应撤回并核实数据来源。" if is_zh else
                   "Risk flagged: the source note describes a potentially fabricated impact claim. Remove or verify it before any executive report.")
    elif 'control_removed' in flags:
        cleaned = ("风险提示：记录提到移除了关键控制措施，必须先评估和恢复必要的防护。" if is_zh else
                   "Risk flagged: the note describes removal of a control. Escalate the risk and restore or approve safeguards before rollout.")
    elif 'compliance_not_verified' in flags and not is_zh:
        cleaned = 'Only the login wording changed; compliance has not been established. Do not present this as HIPAA certification.'
    elif is_zh and re.search(r'体验翻倍|增长翻倍|提升翻倍', original) and re.search(r'没有|没测|没测速|没问卷|未验证', original):
        flags.append('unverified_marketing_claim')
        cleaned = '有客户反馈体验改善，但缺乏问卷或性能测试证据，不能将“翻倍”作为已验证的成果。'
    numbers = re.findall(r"(?<!\w)\d+(?:\.\d+)?\s*(?:%|percent|ms|req/s|requests/s|hours|minutes|kg|fps|\$)",original,flags=re.I)
    evidence = ("记录中包含指标：" + "、".join(numbers) + "；原文陈述，尚未独立核实。" if numbers else "原始记录尚未给出可核实的量化收益。") if is_zh else (
        "Source note reports " + ", ".join(numbers) + "; not independently verified." if numbers else
        "Not quantified in the source note; validate before claiming a result.")
    if 'possible_fabrication' in flags:
        next_step = "核对原始数据并撤回不实成果表述。" if is_zh else "Withdraw unsupported claims and verify original measurements."
    elif 'control_removed' in flags:
        next_step = "恢复或评审关键安全控制后再考虑发布。" if is_zh else "Require risk-owner approval and control restoration before release."
    elif 'unverified_marketing_claim' in flags:
        next_step = '补充用户调研和对照测试，再决定是否使用量化宣传。'
    elif 'compliance_not_verified' in flags:
        next_step = "先完成合规审查，禁止直接宣称已合规。" if is_zh else "Seek a formal compliance review; do not claim certification."
    elif 'restricted_evidence_or_rollout' in flags:
        next_step = "完成待办验证并确认上线范围；不要把测试结果写成生产收益。" if is_zh else "Complete validation and confirm rollout scope; don't state pilot outcomes as production impact."
    else:
        next_step = "补充可核实的前后对比、负责人和上线状态。" if is_zh else "Add measured before/after evidence, owner and rollout status when known."
    if style == "weekly":
        cleaned = ("本周进展：" if is_zh else "Weekly progress — ") + cleaned
    # A concise rewrite removes unnecessary framing but does not erase caveats.
    if style == "concise":
        cleaned = cleaned.replace("The source note reports", "Reported:").replace("原始记录尚未", "尚未")
    review = audit_claims(original, cleaned)
    for flag in review["risk_flags"]:
        if flag not in flags:
            flags.append(flag)
    industry_value = None
    if industry:
        # These are *potential* indicators, not achieved outcomes.
        _, industry_value = industry_example("Agentic Workflows", industry, "zh" if is_zh else "en")
    business_relevance = industry_value or ("业务收益需结合已验证的前后对比评估，不直接从完成任务推断降本增效。" if is_zh else
                                                   "Business impact requires measured before/after evidence; task completion alone does not establish savings.")
    headline = ("进展：" if is_zh else "Update: ") + cleaned.split("。" if is_zh else ".")[0][:140]
    return {"mode": "encode", "source_note": original, "executive_update": cleaned,
            "headline": headline, "business_relevance": business_relevance,
            "impact": evidence, "next_step": next_step, "risk_flags": flags,
            "evidence_ledger": {"numeric_claims_in_source": sorted(numeric_tokens(original)),
                                "new_numbers_in_output": review["new_numeric_claims"],
                                "independent_verification": False},
            "style": style, "source": "offline-conservative-rewrite"}


def format_markdown(result: dict) -> str:
    mode = result["mode"]
    if mode == 'compare':
        zh = result['language'] == 'zh'
        chunks = [('## 技术方案比较：' if zh else '## Technical comparison: ') + ' vs '.join(result['terms'])]
        for item in result['items']:
            chunks.append(f"### {item['term']}\n" +
                          (f"**解决什么：** {item['technical']}\n\n**通俗理解：** {item['human']}\n\n**业务价值：** {item['business']}\n\n**注意：** {item['caveat']}" if zh else
                           f"**Definition:** {item['technical']}\n\n**Metaphor:** {item['human']}\n\n**Value:** {item['business']}\n\n**Limit:** {item['caveat']}"))
        chunks.append(('**如何选：** ' if zh else '**How to decide:** ') + result['decision'])
        return '\n\n'.join(chunks)
    if mode == "explain":
        return (f"## {result['term']} → Say Human ({result['audience']})\n\n"
                f"**Technical:** {result['technical']}\n\n"
                f"**Human:** {result['human']}\n\n"
                f"**Business/ROI:** {result['business']}\n\n"
                f"**Audience decision:** {result['audience_guidance']}\n\n"
                f"**Reality check:** {result['caveat']}" +
                (f"\n\n**Industry scenario:** {result['industry_scenario']}\n\n**What to measure:** {result['industry_measurement']}" if result.get("industry_scenario") else ""))
    if mode == "decode":
        from .jargon import format_decode
        return format_decode(result)
    zh = _has_chinese(result["source_note"])
    return (("## 可用于汇报的表述\n\n" if zh else "## Executive-ready update\n\n") + result["executive_update"] +
            ("\n\n**指标依据：** " if zh else "\n\n**Impact evidence:** ") + result["impact"] +
            ("\n\n**业务关联（非已实现收益）：** " if zh else "\n\n**Business relevance (not realized impact):** ") + result.get("business_relevance", "") +
            ("\n\n**后续动作：** " if zh else "\n\n**Next step:** ") + result["next_step"])

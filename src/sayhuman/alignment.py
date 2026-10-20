"""Offline business-to-engineering alignment: assumptions, never made-up targets.

This is a scoped discovery aid, not a project specification approved by a customer.
"""
from __future__ import annotations
import re
from .industry import ALIASES, INDUSTRIES

LENSES = (
    (r'延迟|卡顿|响应|加载|耗时|更快|快一点|提速|速度|latency|slow|faster|speed|performance',
     ('响应时间', 'P95 latency', '约定的实际用户操作与负载', 'representative workload and user journey')),
    (r'成本|预算|费用|降本|节省|便宜|cost|budget|saving|cheaper',
     ('单次成功任务成本', 'cost per successfully completed task', '包含人力、基础设施和返工的总成本', 'total cost including labor, infrastructure and rework')),
    (r'准确|质量|错|误报|漏报|投诉|客诉|退款|精度|complaint|refund|accuracy|quality|error|mistake|false positive|false negative',
     ('错误率及人工复核率', 'error rate and human review rate', '标注一致的真实样本与高风险反例', 'labeled representative cases and high-risk counterexamples')),
    (r'稳定|宕机|可靠|失败|可用性|断|reliable|uptime|failure|stable|availability',
     ('关键流程成功率', 'critical workflow success rate', '失败、重试、回滚和恢复场景', 'failures, retries, rollback and recovery cases')),
    (r'体验|好用|简便|容易|转化|留存|易用|ux|usability|conversion|retention|user friendly',
     ('任务完成率与用户反馈', 'task completion and user feedback', '可代表目标用户的可用性测试', 'usability trials with representative users')),
)


def _lang(text: str, language: str) -> str:
    if language not in {'auto', 'zh', 'en'}:
        raise ValueError('Language must be auto, zh or en')
    return 'zh' if language == 'auto' and re.search('[\u4e00-\u9fff]', text) else ('en' if language == 'auto' else language)


def align(goal: str, industry: str | None = None, lang: str = 'auto', audience: str = 'product') -> dict:
    """Turn a rough outcome request into a pilot/acceptance discussion.

    Deliberately does not invent numeric SLOs, savings, rollout decisions, or owners.
    """
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError('Provide a nonempty business goal')
    if len(goal) > 8_000:
        raise ValueError('Business goal must be <= 8,000 characters')
    language = _lang(goal, lang)
    zh = language == 'zh'
    if industry:
        key = ALIASES.get(industry.strip().casefold(), industry.strip().casefold())
        if key not in INDUSTRIES:
            raise ValueError(f"Unknown industry '{industry}'. Available: {', '.join(INDUSTRIES)}")
        industry_label = INDUSTRIES[key][0]
    else:
        industry_label = None
    metrics = [data for pattern, data in LENSES if re.search(pattern, goal, re.I)]
    if not metrics:
        metrics = [('目标任务完成率', 'target task completion', '实际任务及失败原因', 'real task cases and failure reasons')]
    metrics = metrics[:2]
    names = [m[0 if zh else 1] for m in metrics]
    trials = [m[2 if zh else 3] for m in metrics]
    result = {
        'mode': 'align', 'language': language, 'source_goal': goal.strip(),
        'audience': audience, 'industry': industry_label,
        'status': 'draft_for_discussion_not_approved',
        'desired_outcome': goal.strip(),
        'proposed_metrics': names,
        'acceptance_plan': (
            f"先记录当前基线，并使用{'、'.join(trials)}开展对照测试；阈值、测试时长与业务方确认后写入验收标准。" if zh else
            f"Record a baseline, evaluate with {'; '.join(trials)}, and agree thresholds and duration with the stakeholder before acceptance."
        ),
        'constraints': (
            ['权限和个人信息保护', '异常时人工接管与回退', '记录模型/系统成本', '明确责任人与验收人'] if zh else
            ['Access and privacy', 'Human fallback and rollback', 'Capture system and review cost', 'Named owner and approver']
        ),
        'questions': (
            ['面向哪类用户及哪项操作？', '目前的基线和最大痛点是什么？', '谁批准目标阈值与上线范围？'] if zh else
            ['Which users and task are in scope?', 'What is the measured baseline?', 'Who approves thresholds and rollout scope?']
        ),
        'disclaimer': ('建议的测量方案，不代表用户已批准任何阈值、结果或上线计划。' if zh else
                       'A measurement proposal, not approved targets, results or rollout.'),
        'source': 'offline-requirements-scaffold',
    }
    return result


def format_alignment(item: dict) -> str:
    if item['language'] == 'zh':
        return (f"## 业务需求 → 可验证的工程任务\n\n**目标原话：** {item['source_goal']}\n\n"
                f"**建议衡量：** {'、'.join(item['proposed_metrics'])}\n\n"
                f"**验收设计：** {item['acceptance_plan']}\n\n"
                f"**必要约束：** {'；'.join(item['constraints'])}\n\n"
                f"**需要确认：** {'；'.join(x.rstrip('？') for x in item['questions']) + '？'}\n\n*{item['disclaimer']}*")
    return (f"## Business request → testable engineering brief\n\n**Original goal:** {item['source_goal']}\n\n"
            f"**Suggested measures:** {', '.join(item['proposed_metrics'])}\n\n"
            f"**Acceptance plan:** {item['acceptance_plan']}\n\n"
            f"**Constraints:** {'; '.join(item['constraints'])}\n\n"
            f"**Clarify:** {'; '.join(item['questions'])}\n\n*{item['disclaimer']}*")

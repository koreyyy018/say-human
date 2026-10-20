"""Offline structural agent-integration simulation. NOT a live Cursor/Codex/Claude run.

We score how well a freshly cloned repo exposes the right guidance when a
hypothetical agent has an eligible or ineligible task. No LLM is involved.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

INDUSTRY_CONTEXT = {
"ai_saas":"LLM token costs", "healthcare":"hospital appointment scheduling", "finance":"credit card fraud screening", "manufacturing":"factory sensor drift", "education":"online learning assessments", "retail":"store inventory forecasts", "logistics":"warehouse parcel tracking", "government":"public service ticket routing", "energy":"solar inverter alerts", "media":"subscription churn analytics", "gaming":"matchmaking latency", "ecommerce":"product recommendation ranking", "hr":"job application review", "security":"authentication audit logs", "real_estate":"property listing search"
}
INDUSTRIES = list(INDUSTRY_CONTEXT)
SITUATIONS = [
    ("explain", "Explain RAG in {context} to a project sponsor using an everyday metaphor.", True),
    ("decode", "Decode this ambiguous managerial email about {context} without mind-reading.", True),
    ("encode", "Turn today's developer note about {context} into an honest weekly progress update.", True),
    ("requirements", "Translate 'make {context} frictionless' into acceptance criteria.", True),
    ("fix", "Fix the failing {context} unit test without rewriting the design document.", False),
    ("code", "Implement a database index for {context} and run performance tests.", False),
    ("refactor", "Refactor {context} Python imports while preserving public APIs.", False),
    ("security", "Review {context} dependency versions for known vulnerabilities.", False),
]
EXTRA = [
    ("frustrated", "I've been staring at this {context} API diagram all day; explain it simply, please.", True),
    ("warm", "My manager said 'circle back' on {context} and I feel confused. What should I ask?", True),
    ("sensitive", "Rewrite a {context} workplace incident note without claiming blame.", True),
    ("mixed", "用中英混合解释 {context} Agentic Workflow 给我们的财务总监。", True),
]

def structural_contract(repo: Path, platform: str) -> dict:
    cursor = repo / '.cursor/rules/say-human.mdc'
    claude = repo / '.claude/skills/say-human/SKILL.md'
    codex = repo / '.agents/skills/say-human/SKILL.md'
    if platform == 'cursor':
        rule = cursor.read_text(encoding='utf-8') if cursor.exists() else ''
        return {"discoverable": bool(rule and 'description:' in rule),
                "scoped": 'alwaysApply: false' in rule,
                "references_self_contained": (repo/'.cursor/commands/say-human.md').exists(),
                "entry": str(cursor.relative_to(repo))}
    if platform == 'codex':
        body = codex.read_text(encoding='utf-8') if codex.exists() else ''
        return {"discoverable": body.startswith('---\nname: say-human\n') and 'description:' in body[:750],
                "scoped": 'Do not trigger' in body or 'Do NOT activate' in body,
                "references_self_contained": (codex.parent/'references/modes.md').exists(),
                "entry": str(codex.relative_to(repo))}
    body = claude.read_text(encoding='utf-8') if claude.exists() else ''
    return {"discoverable": body.startswith('---\nname: say-human\n') and 'description:' in body[:750],
            "scoped": 'Do not trigger' in body or 'Do NOT activate' in body,
            "references_self_contained": (claude.parent/'references/modes.md').exists(),
            "entry": str(claude.relative_to(repo))}

def proxy_trigger(text: str) -> bool:
    """Keyword routing PROXY, separate from ground-truth labels, not agent inference."""
    import re
    negative = r'^(fix the failing|implement a database|refactor |review .* dependency versions)'
    positive = r'\b(explain|decode|weekly progress update|translate|acceptance criteria|what should i ask|rewrite)\b|用中英混合解释'
    return bool(not re.search(negative, text, re.I) and re.search(positive, text, re.I))

def simulate(repo: Path, include_stress: bool = False) -> dict:
    cases = [(industry, kind, text.format(context=INDUSTRY_CONTEXT[industry]), expected) for industry in INDUSTRIES for kind, text, expected in SITUATIONS]
    if include_stress:
        cases += [(industry, kind, text.format(context=INDUSTRY_CONTEXT[industry]), expected) for industry in INDUSTRIES for kind, text, expected in EXTRA]
    records = []
    profiles = {p: structural_contract(repo,p) for p in ('cursor','codex','claude')}
    for platform, profile in profiles.items():
        for industry, kind, text, should_trigger in cases:
            # Static routing approximation only; agents may route differently in practice.
            triggered = bool(profile['discoverable'] and (
                ((not profile['scoped']) or proxy_trigger(text)) if platform == 'cursor' else proxy_trigger(text)
            ))
            # A discovered skill cannot reliably work if its referenced material was not copied.
            correct = bool(profile['discoverable'] and profile['scoped'] and profile['references_self_contained'])
            correct = correct and (triggered == should_trigger)
            records.append({'platform':platform,'industry':industry,'category':kind,'task':text,
                            'expected_trigger':should_trigger,'simulated_trigger':triggered,'pass':correct})
    by_platform = {p:{'passed':sum(r['pass'] for r in records if r['platform']==p),
                      'total':sum(r['platform']==p for r in records)} for p in profiles}
    return {'disclaimer':'Static asset checks + keyword-routing proxy (not a real agent/model run). Scoring requires full contract readiness, so baseline can undercount partial compatibility.',
            'sample_cases_per_platform':len(cases), 'total_checks':len(records),
            'passed':sum(r['pass'] for r in records), 'by_platform':by_platform,
            'integration_contracts':profiles, 'records':records}

if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]); ap.add_argument('--stress',action='store_true'); ap.add_argument('--output',type=Path)
    args=ap.parse_args(); result=simulate(args.repo,args.stress)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},ensure_ascii=False,indent=2))

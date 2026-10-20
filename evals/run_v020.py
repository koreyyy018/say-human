"""v0.2 additive offline gates: 210 legacy + 240 industry/localization + 60 new cases.

This is rule-based validation, NOT independent judgement of writing quality.
"""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sayhuman.engine import explain
from sayhuman.industry import INDUSTRIES
from sayhuman.reporting import report, audit, numeric_tokens
from run_benchmark import assess


def main():
    old=[json.loads(s) for s in (ROOT/'evals/scenarios.jsonl').read_text(encoding='utf8').splitlines() if s.strip()]
    v2=[json.loads(s) for s in (ROOT/'evals/v020_scenarios.jsonl').read_text(encoding='utf8').splitlines() if s.strip()]
    rows=[]
    for c in old:
        r=assess(c)
        rows.append({'id':r['id'],'group':'legacy_210','passed':r['passed'], 'failed':[k for k,v in r['checks'].items() if not v]})
    for industry in INDUSTRIES:
        for term in ['Prompt','Agent','Context Window','API','Function Calling','RAG','Multimodal','Tokens','Hallucination','Vector Embeddings','Fine-tuning','Agentic Workflows','LoRA','Quantization','Caching','Guardrails']:
            r=explain(term,'cfo',industry,'zh')
            checks={'localized': all(r.get(k) for k in ('human','technical','business','caveat')),
                    'hypothetical_label':'假设案例' in r['industry_scenario'],
                    'no_claimed_savings':'不预设节省金额' in r['industry_measurement'],
                    'chinese_scenario':len(r['industry_scenario'])>40}
            rows.append({'id':f'EXTRA-{industry}-{term}','group':'industry_localized_240','passed':all(checks.values()),'failed':[k for k,v in checks.items() if not v]})
    for c in v2:
        if c['mode']=='report':
            r=report(c['facts'],lang=c['lang'])
            src=' '.join(str(v) for v in c['facts'].values())
            numbers=numeric_tokens(r['executive_update'])|numeric_tokens(r['impact'])
            checks={'no_new_number':numbers.issubset(numeric_tokens(src)),
                    'explicit_status':c['facts']['status']==r['evidence_ledger']['status'],
                    'evidence_not_verified':r['verification']=='user-supplied, not independently verified',
                    'has_action':c['facts']['action'] in r['executive_update'],
                    'next_step_intact':c['facts']['next_step']==r['next_step']}
        else:
            r=audit(c['source'],c['candidate'])
            checks={'expected_flags': (c['expected_flag'] in r['risk_flags']) if c['expected_flag'] else not r['risk_flags']}
        rows.append({'id':c['id'],'group':'report_or_audit_60','passed':all(checks.values()),'failed':[k for k,v in checks.items() if not v]})
    groups={g:{'total':sum(r['group']==g for r in rows),'rules_passed':sum(r['group']==g and r['passed'] for r in rows)} for g in sorted({r['group'] for r in rows})}
    result={'scope':'offline rules, synthetic cases; NOT verified human writing quality or live LLM calls',
            'total':len(rows),'rules_passed':sum(r['passed'] for r in rows), 'groups':groups,
            'failures':[r for r in rows if not r['passed']]}
    out=ROOT/'evals/v020_extended_results.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['total']==result['rules_passed'] else 1

if __name__=='__main__':raise SystemExit(main())

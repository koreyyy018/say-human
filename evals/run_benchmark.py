"""Reproducible, deterministic quality-gate evaluation of the OFFLINE engine.

These checks do NOT validate the full LLM skill's generative quality. The evaluation
uses 210 hand-authored, synthetic real-world situations across 15 industries.
"""
import argparse
from collections import Counter, defaultdict
import json
import pathlib
import re
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sayhuman.engine import explain, decode, encode

CASES=ROOT/'evals'/'scenarios.jsonl'
NUMS=re.compile(r'(?<![\w])\d+(?:\.\d+)?')
ZH=re.compile(r'[\u4e00-\u9fff]')
BAD_INSULTS=re.compile(r'(?i)\b(?:stupid|idiot|dumb|idiotic)\b')

def assess(case):
    checks={}
    mode=case['mode']; source=case['text']; result={}
    try:
        if mode=='explain':
            result=explain(source,case['audience'])
            checks['term_correct']=result.get('term')==case['expected_term']
            checks['grounded_fields']=all(len(result.get(f,'').split())>=5 for f in ('technical','human','business','caveat'))
            checks['metaphor_present']=result['human']!=result['technical'] and len(result['human'])>35
            checks['audience_not_ignored']=bool(result.get('audience_guidance')) and len(result.get('audience_guidance',''))>=20
        elif mode=='decode':
            result=decode(source)
            actual={x['phrase'] for x in result.get('matches',[])}
            checks['expected_phrases_exact']=actual==set(case['expected_phrases'])
            checks['no_motive_as_fact']='not a verified motive' in result.get('certainty','') or '未经证实' in result.get('certainty','')
            if ZH.search(source):
                checks['chinese_plain_explanation']=all(ZH.search(m.get('plain_language','')) for m in result.get('matches',[])) and bool(result.get('matches'))
        elif mode=='encode':
            result=encode(source)
            executive=result.get('executive_update','')
            checks['nonempty_summary']=len(executive.strip())>15
            checks['no_invented_digits']=set(NUMS.findall(executive)).issubset(set(NUMS.findall(source)))
            checks['no_original_insult']=not BAD_INSULTS.search(executive)
            checks['not_primitive_prefix']=not executive.startswith(('Work update:','工作进展：','Work completed:'))
            if ZH.search(source):
                checks['language_fidelity']=bool(ZH.search(executive))
            if (not NUMS.search(source)):
                checks['no_numeric_impact_claim']=not NUMS.search(result.get('impact',''))
        else: raise ValueError(f'unknown {mode}')
    except Exception as e:
        checks['no_exception']=False
        result={'error':f'{type(e).__name__}: {e}'}
    if 'no_exception' not in checks: checks['no_exception']=True
    return {'id':case['id'],'industry':case['industry'],'mode':mode,'input':source,
            'checks':checks,'passed':all(checks.values()),'output':result}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',default='evals/latest.json')
    args=ap.parse_args()
    cases=[json.loads(x) for x in CASES.read_text(encoding='utf8').splitlines() if x.strip()]
    rows=[assess(c) for c in cases]
    counts=Counter(r['mode'] for r in rows)
    results={'scope':'offline deterministic engine only; no live LLM calls', 'dataset':'hand-written synthetic situations, not sampled from actual companies',
             'total':len(rows), 'by_mode':{m:{'total':n,'all_checks_passed':sum(r['passed'] for r in rows if r['mode']==m)} for m,n in sorted(counts.items())},
             'by_industry':{i:{'total':len(l),'all_checks_passed':sum(r['passed'] for r in l)} for i,l in sorted(_group(rows).items())},
             'by_check':_checks(rows),'failures':[{'id':r['id'],'mode':r['mode'],'industry':r['industry'],'input':r['input'],
                         'failed_checks':[k for k,v in r['checks'].items() if not v], 'output':r['output']} for r in rows if not r['passed']],
             'cases':rows}
    path=ROOT/args.output
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'Scenarios: {len(rows)}  All checks passed: {sum(r["passed"] for r in rows)}/{len(rows)}')
    for k,v in results['by_mode'].items(): print('  ',k, v)
    for k,v in results['by_check'].items():print('  ',k, v)
    print('Failures:', ', '.join(r['id'] for r in rows if not r['passed']) or '(none)')
    print('Report:',path)

def _group(rows):
    d=defaultdict(list)
    for row in rows:d[row['industry']].append(row)
    return d

def _checks(rows):
    d=defaultdict(lambda:[0,0])
    for row in rows:
        for k,v in row['checks'].items():
            d[k][1]+=1;d[k][0]+=bool(v)
    return {k: {'passed':v[0], 'total':v[1]} for k,v in sorted(d.items())}

if __name__=='__main__': main()

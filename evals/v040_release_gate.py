#!/usr/bin/env python3
"""Deterministic local release gate using unseen scenario combinations.

It tests only executed Python behavior and source file contracts. It does not
run Cursor/Codex/Claude models, evaluate creativity, or measure end-user utility.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sayhuman.alignment import align
from sayhuman.engine import encode, explain, decode
from sayhuman.reporting import audit
from sayhuman.tone import connection_note
from sayhuman.industry import INDUSTRIES

# Fictional scenarios modeled on operational tasks; NOT private/real customer data.
EXAMPLES = {
    'ai':'客服助手', 'finance':'交易对账', 'healthcare':'预约挂号', 'manufacturing':'生产线巡检',
    'ecommerce':'商品检索', 'education':'学生答疑', 'logistics':'包裹派送', 'hr':'候选人反馈',
    'government':'事项办理', 'retail':'门店库存', 'media':'内容检索', 'security':'告警复核',
    'gaming':'玩家登录', 'energy':'设备巡检', 'realestate':'报修调度',
}
TESTS=[]

def check(identifier, kind, industry, user_input, out, predicate, reason):
    try:
        passed=bool(predicate(out))
        detail='' if passed else reason
    except Exception as error:
        passed=False; detail=f'{type(error).__name__}: {error}'
    TESTS.append({'id':identifier,'category':kind,'industry':industry,'input':user_input,
                  'passed':passed,'failure_reason':detail,'output':out})

for i,(industry,work) in enumerate(EXAMPLES.items(),1):
    # Distinct concrete industry nouns change but no claim these companies actually exist.
    en=explain('Vector Embeddings','cfo',industry,'en')
    check(f'{i}-E1','explain',industry,'Vector Embeddings',en,
          lambda x: x['language']=='en' and x['industry_scenario'].startswith('Hypothetical') and 'measure' not in x['human'].lower(), 'English metaphor and hypothetical use case expected')
    zh=explain('RAG','product',industry,'zh')
    check(f'{i}-E2','explain',industry,'RAG',zh,
          lambda x: x['language']=='zh' and '假设' in x['industry_scenario'] and x['caveat'], 'Chinese curated metaphor and explicit limits expected')
    goal_zh=f'希望{work}操作快一点，但不要牺牲安全或隐私'
    p=align(goal_zh,industry,'zh','product')
    check(f'{i}-A1','align',industry,goal_zh,p,
          lambda x: '响应时间' in x['proposed_metrics'] and x['status']=='draft_for_discussion_not_approved' and '阈值' in x['acceptance_plan'], 'A proposed measured baseline, not invented SLA, expected')
    goal_en=f'Reduce the operational cost of {work} without removing safety checks'
    p2=align(goal_en,industry,'en','cfo')
    check(f'{i}-A2','align',industry,goal_en,p2,
          lambda x: 'cost per successfully completed task' in x['proposed_metrics'] and x['industry'], 'CFO-specific measurement candidate expected')
    note=f'我们下周先对齐{work}的职责分工，之后再闭环'
    d=decode(note,industry)
    check(f'{i}-D','decode',industry,note,d,
          lambda x: x['matches'] and '不能仅凭' in x['summary'] and x['clarifying_question'], 'Ambiguous management phrase should trigger provisional meaning only')
    messy=f'昨天把{work}的卡顿问题修了，但还没上线，也没做压测'
    e=encode(messy,industry,'executive')
    check(f'{i}-N','encode',industry,messy,e,
          lambda x: ('尚未上线' in x['executive_update'] and
                     not x['evidence_ledger']['new_numbers_in_output'] and 'risk_flags' in x), 'Keep staging/impact uncertainty, no made-up numeric claims')
    source=f'{work}尚未上线，成本变化还没有测量'
    bad=f'{work}已经全量上线，效率提升40%'
    a=audit(source,bad)
    check(f'{i}-U','audit-unsafe',industry,source+' -> '+bad,a,
          lambda x: x['status']=='review_required' and 'new_numeric_claims' in x['risk_flags'] and 'unsupported_deployment_status' in x['risk_flags'], 'Should catch invented rollout and percent')
    good=f'{work}尚未上线，成本变化尚未测量'
    a2=audit(source,good)
    check(f'{i}-S','audit-safe',industry,source+' -> '+good,a2,
          lambda x: x['status']=='no_rule_based_flags', 'Avoid false alarms on faithful draft')
    upset=f'我烦死了，{work}还没正式上线，老板一直追问'
    note=connection_note(upset,'encode','warm')
    check(f'{i}-W','empathy',industry,upset,note,
          lambda x: bool(x) and '上线' in x and 'PPT' not in x, 'Specific optional acknowledgement expected')
    dry=connection_note(f'修复了{work}', 'encode','warm')
    check(f'{i}-Q','no-forced-empathy',industry,f'修复了{work}',dry,
          lambda x: x is None, 'No forced empathy on neutral notes')

# 50 out-of-iteration adversarial and rejection cases, repeated across distinct
# operational contents to check flags without claiming a semantic guarantee.
for i in range(1,26):
    origin=f'第{i}号任务目前尚未上线，尚未做对照测试'
    candidate=f'第{i}号任务已经全量上线，实测提升{i}%'
    result=audit(origin,candidate)
    check(f'B{i}','adversarial-rollout','generic',origin+' -> '+candidate,result,
          lambda x: x['status']=='review_required' and bool(x['new_numeric_claims']) and 'unsupported_deployment_status' in x['risk_flags'],
          'Unsupported new metric and release claim expected')
for i in range(1,26):
    origin=f'第{i}项功能仍在测试环境，结果尚未验证'
    candidate=f'第{i}项功能仍在测试环境，结果尚未验证'
    result=audit(origin,candidate)
    check(f'C{i}','preserved-uncertainty','generic',origin+' -> '+candidate,result,
          lambda x: x['status']=='no_rule_based_flags', 'Faithful uncertainty should not be flagged')

if __name__=='__main__':
    dest=ROOT/'evals/v040_release_results.json'
    counts={}
    for item in TESTS:
        k=item['category'];counts.setdefault(k,{'passed':0,'total':0});counts[k]['total']+=1;counts[k]['passed']+=item['passed']
    summary={'version':'0.4.0','kind':'local deterministic engine checks, NOT real agent sessions',
             'scenarios':len(TESTS),'passed':sum(x['passed'] for x in TESTS),'failed':sum(not x['passed'] for x in TESTS),
             'categories':counts,'examples':TESTS,
             'limits':['Synthetic domain nouns, not representative end-user inputs.',
                       'Rule compliance is not subjective communication quality.',
                       'No real Cursor, Codex or Claude agent runs.',
                       'Heuristic claim auditing may miss paraphrased false claims.']}
    dest.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f"v0.4.0 local checks: {summary['passed']}/{summary['scenarios']}; failures={summary['failed']}; results={dest.name}")
    for item in TESTS:
        if not item['passed']:
            print(f" - {item['id']} {item['failure_reason']} ({item['input'][:70]})")
    raise SystemExit(0 if not summary['failed'] else 1)

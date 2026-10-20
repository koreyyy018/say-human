"""90 real offline CLI executions over 15 hypothetical industries.

Verifies JSON contract, conservative numeric claims, deployment evidence and optional
emotional framing. It does not call Cursor/Codex/Claude models or evaluate prose taste.
"""
from __future__ import annotations
import json, sys, subprocess, os, argparse
from sayhuman.cli import build_parser, run
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SAMPLES={
'ai':('Tokens','请先拉齐 AI 客服的优先级，我有点烦。','已经修了 AI 客服的重试缺陷，还没上线。'),
'finance':('RAG','领导说反欺诈验证要闭环，我有点困惑。','修复反欺诈告警展示问题，目前只在测试环境验证。'),
'healthcare':('Agent','医院排班项目要先对齐流程，我有点烦。','医院预约页面已修复显示问题，尚未上线。'),
'manufacturing':('Quantization','生产线检测需求要拉齐，我有点头大。','修好了生产线巡检日报的缺陷，还要压测。'),
'education':('Fine-tuning','教研团队说要先闭环，我有点困惑。','课程检索的错链已修复，尚未验收。'),
'retail':('API','门店同步项目说先对齐，我有点烦。','把库存展示的问题修了，还没上线。'),
'logistics':('Vector Embeddings','配送异常要闭环，我看不懂是谁负责。','已修复物流扫码卡顿，目前测试环境验证。'),
'government':('Guardrails','政务工单分流说先拉齐，我有点懵。','政务表单的提交提示已修复，还在回归测试。'),
'energy':('Agentic Workflows','巡检报表要闭环，我有点困惑。','修好了告警通知问题，尚未上线。'),
'media':('Caching','栏目归档项目要对齐，我有点烦。','内容列表的加载问题修了，还没上线。'),
'gaming':('Context Window','游戏客服工单先对齐，我有点懵。','修好了匹配状态的展示问题，尚未上线。'),
'ecommerce':('Multimodal','商品搜索要闭环，我有点困惑。','把商品搜索的错词问题修了，目前测试环境验证。'),
'hr':('Hallucination','招聘流程要对齐，我有点烦。','已修复候选人通知重复发送问题，尚未上线。'),
'security':('Function Calling','安全告警要拉齐，我很困惑。','安全日志过滤页面修了，还没全量验证。'),
'realestate':('LoRA','物业工单流程先对齐，我有点头大。','已修复报修系统排序异常，尚未上线。'),
}

def run_checks():
    cases=[]
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+env.get('PYTHONPATH','')
    for industry,(term,jargon,note) in SAMPLES.items():
        for tone in ('neutral','playful'):
            for mode,value in (('explain',term),('decode',jargon),('encode',note)):
                cmd=[sys.executable,'-m','sayhuman',mode,value,'--tone',tone,'--format','json','--industry',industry]
                if mode=='explain':cmd+=['--lang','zh','--audience','cfo']
                error=""
                try:
                    data=json.loads(run(build_parser().parse_args(cmd[3:])))
                except (ValueError, LookupError, json.JSONDecodeError) as exc:
                    data={}; error=str(exc)
                passed=bool(data.get('mode')==mode and data.get('source'))
                detail='valid structured answer'
                if passed and mode=='explain':
                    passed=all(data.get(key) for key in ('human','technical','business','caveat','industry_scenario'))
                    detail='metaphor + grounded constraints + industry scene'
                if passed and mode=='decode':
                    passed=bool(data.get('clarifying_question') and data.get('certainty') and data['matches'])
                    detail='conditional interpretations and actionable question'
                if passed and mode=='encode':
                    output=data['executive_update']
                    pending_terms=('尚未','测试环境','仍需','仍在进行','回归测试')
                    passed=(data.get('evidence_ledger',{}).get('new_numbers_in_output') == []
                            and any(term in output for term in pending_terms))
                    detail='no fabricated metrics, pending validation or deployment preserved'
                if passed and tone=='neutral':
                    passed='connection_note' not in data
                elif passed and tone=='playful':
                    passed=bool(data.get('connection_note') and data['connection_note'] not in data.get('executive_update',''))
                cases.append({'industry':industry,'mode':mode,'tone':tone,'passed':bool(passed),'check':detail,
                              'input':value,'output':data, 'error':error if not passed else ''})
    return {'disclaimer':'Real CLI parser/handler invocations in-process, synthetic user content. Automated invariants are NOT editorial or external-model quality scores.',
            'passed':sum(x['passed'] for x in cases),'total':len(cases),'cases':cases}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'evals/v030_offline_replay.json');a=ap.parse_args()
    r=run_checks();a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'passed':r['passed'],'total':r['total']},ensure_ascii=False))
    if r['passed']!=r['total']:sys.exit(1)

#!/usr/bin/env python3
"""200 independent workplace scenarios, 10 sectors × 20, old/new paired decoding.
No paid inference, external models, or hidden grading model. Replay each version with
PYTHONPATH pointing to its own src package. 'hit' is a lexical match only.
"""
from __future__ import annotations
import argparse, csv, json, random, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SECTORS=['ai','finance','healthcare','manufacturing','ecommerce','education','logistics','hr','government','security']
# Control/low-coverage cases are written independently from the new glossary.
UNSEEN={
'ai':['评审时说先把模型回答的“靠谱程度”拿出一把尺子。','这个星期想让客服机器人不懂时及时找真人。','数据团队要让旧资料不再影响模型给答案。','下轮要有一套新模型升级前后能公平比较的办法。'],
'finance':['经理希望柜台办理更快，错账不能增加。','负责人要求跨业务线统一异常交易处理时间。','风控说得把大客户贷款风险看得更细。','下周要拿出客户投诉处理更可追溯的办法。'],
'healthcare':['院里要求患者的候诊体验明显改善。','今天的例会说要把特殊检查结果交到负责医生手里。','医务部说让各病区的诊疗记录格式一致。','主任希望分诊的危险信号不要遗漏。'],
'manufacturing':['厂长说新品试做完之后还要经得起大批量生产。','品质部要找到哪个步骤返工最多。','生产主管说不要光看产量，还要看产品一次就过关的比例。','班组长要求设备故障后恢复生产更快。'],
'ecommerce':['运营说下轮促销要减少买家领券却不用的情况。','采购希望高销量商品不再频繁断货。','老板说老客户回头买东西要更方便。','直播负责人要求降低退款却没查清原因的问题。'],
'education':['校长希望每个学生的练习难度更合适。','教研组要对不同教师的评分标准作比较。','培训负责人说课程报名人多但实际开课的人少。','老师希望讲完课能及时知道学生有没有听懂。'],
'logistics':['运输组要减少包裹卡在中转站的时间。','仓库说拣货人员走动太多，希望重排货位。','客服要求异常签收后必须能追到处理人。','经理希望退回来的商品能更快入库。'],
'hr':['HR希望试用期的考核说明能够更具体。','部门经理抱怨关键岗位离职会影响后续交接。','负责人说要让薪酬比较的岗位和地区一致。','培训团队说员工培训结束后最好能在工作中用上。'],
'government':['窗口希望市民不用重复提交同一份材料。','负责人说群众在外地也应该能办理部分事项。','督导组希望对基层反复填报的表格做一次删减。','工作人员说收到投诉后要知道是哪个单位接单。'],
'security':['安全团队说报警太多导致真正危险的没看到。','负责人希望权限申请和离职回收别再漏掉。','工程师要保证升级补丁不会造成业务长时间中断。','下周要演练系统被攻击之后谁来作决定。'],
}
PLAIN={
'ai':['周三下午两点开模型评审会。','昨天把产品说明文档发给了客户。'],
'finance':['本周五上午提交第二季度财务表。','已经通知客户更新联系方式。'],
'healthcare':['今天门诊上午八点开始接诊。','请把打印机里的纸补充一下。'],
'manufacturing':['晚上七点停止一号线清洁设备。','先把仓库的水关掉再下班。'],
'ecommerce':['明天八点把新商品照片上架。','这周五给客户补发快递单号。'],
'education':['下周一早上有语文公开课。','请把第二节课的练习打印出来。'],
'logistics':['货车预计周五上午抵达三号仓。','把这两箱样品放在指定货架上。'],
'hr':['明天上午十点安排新同事入职。','请把会议室钥匙还给前台。'],
'government':['办事大厅周三下午暂停窗口服务。','请把会议材料放到桌上。'],
'security':['请把新的门禁卡交还保安室。','今晚十点安排防火墙维护。'],
}
AMBIGUOUS={
'ai':'监控屏上显示 WiFi bandwidth 升到了 500 Mbps，先确认网络设备。',
'finance':'客户说投资净值是1.02，这是一条普通数字记录。',
'healthcare':'护士说病历卡上写着上周体温37度。',
'manufacturing':'车间说机器上显示数字18，请记录仪器读数。',
'ecommerce':'商品标题写着“全域网球拍”，这里的全域是商标的一部分。',
'education':'今天学生在课堂提到了“增长飞轮”这个词，但不是经营会议。',
'logistics':'司机说明天八点送货，没有其他要求。',
'hr':'邮件主题写着“人才梯队分享会”，不涉及人事任命。',
'government':'会议上展示了“数字化转型”的教材标题，不是项目安排。',
'security':'天气预报说 visibility 只有100 meters，请注意驾驶。',
}
TEMPLATES=[
    '这周{industry}例会上，负责人说：“{term}要再往前推一步，周五汇报。”',
    '会议纪要里写了“先看{term}”，但没写下一步。',
    '领导问{industry}团队：{term}准备得怎么样？',
    '客户提出希望看到{term}的实际进展。',
    '业务方留言：“请把{term}这块讲清楚，别只给我PPT。”',
    '项目群里有人问：“{term}具体由谁负责？”',
    '主管强调本周要讨论{term}的问题。',
    '我们明天开会重点看{term}，想先弄明白。',
    '评审会上提到{term}，我不清楚它说的是什么。',
    '跨部门同步时大家一直提{term}，能翻译成人话吗？',
]


def generate_cases(glossary: list[dict]) -> list[dict]:
    labels={'ai':'AI/SaaS','finance':'金融银行','healthcare':'医疗医院','manufacturing':'智能制造','ecommerce':'电商平台','education':'教育','logistics':'物流','hr':'人力资源','government':'政务','security':'网络安全'}
    old=glossary[:165];new=glossary[165:]
    cases=[]
    for rnd,industry in enumerate(SECTORS,1):
        new_pool=[v for v in new if v.get('industry')==industry]
        old_pool=[v for v in old if v.get('industry')==industry]
        assert len(new_pool)>=8 and len(old_pool)>=5
        rng=random.Random(100+rnd)
        chosen_new=rng.sample(new_pool,8)
        chosen_old=rng.sample(old_pool,5)
        local=[]
        for idx,entry in enumerate(chosen_new+chosen_old):
            term=entry['phrase']
            variant='new-glossary' if idx<8 else 'legacy-glossary'
            local.append({'text':TEMPLATES[idx%len(TEMPLATES)].format(industry=labels[industry],term=term),
                          'type':variant,'expected_term':term})
        for text in UNSEEN[industry]:
            local.append({'text':text,'type':'paraphrase','expected_term':''})
        for text in PLAIN[industry]:
            local.append({'text':text,'type':'plain-control','expected_term':''})
        local.append({'text':AMBIGUOUS[industry],'type':'boundary-control','expected_term':''})
        assert len(local)==20
        for idx,item in enumerate(local,1):
            item.update({'id':f'R{rnd:02d}-D{idx:02d}','round':rnd,'industry':industry,'language':'zh' if re.search(r'[\u4e00-\u9fff]',item['text']) else 'en'})
            cases.append(item)
    return cases


def replay(cases: list[dict], out:Path):
    from sayhuman.engine import decode,format_markdown
    results=[]
    for case in cases:
        try:
            result=decode(case['text'],case['industry'])
            rendered=format_markdown(result)
            matches=[x['phrase'] for x in result['matches']]
            r={'id':case['id'],'text':rendered,'matches':matches,
               'resolution':result.get('resolution','lexicon' if matches else 'not-matched'),
               'direct_exact':case['expected_term'] in matches if case['expected_term'] else None,
               'hit_count':len(matches),'has_question':bool(result.get('clarifying_question')),
               'has_unwanted_disclaimer':bool(re.search('以下只是可能的解读|不能仅凭黑话|可能的解读，发言者动机未经|No known jargon matched|未识别到词库中的',rendered)),
               'leaks_llm_flag':('--llm' in rendered),'chinese_response':bool(re.search(r'[\u4e00-\u9fff]',rendered)),
               'error':''}
        except Exception as exc:
            r={'id':case['id'],'text':'','matches':[],'resolution':'error',
                'direct_exact':False,'hit_count':0,'has_question':False,
                'has_unwanted_disclaimer':False,'leaks_llm_flag':False,
                'chinese_response':False,'error':str(exc)}
        results.append(r)
    out.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    return results


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--make',action='store_true');ap.add_argument('--replay',action='store_true');ap.add_argument('--output-dir',default=str(ROOT/'evals/v050_ab'));ap.add_argument('--variant',default='new');args=ap.parse_args()
    folder=Path(args.output_dir);folder.mkdir(parents=True,exist_ok=True)
    if args.make:
        glossary=json.loads((ROOT/'data/corporate-phrases.json').read_text())
        cases=generate_cases(glossary)
        (folder/'cases.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in cases))
        print('Generated',len(cases),'cases')
    if args.replay:
        cases=[json.loads(s) for s in (folder/'cases.jsonl').read_text().splitlines() if s.strip()]
        results=replay(cases,folder/f'{args.variant}_outputs.json')
        print('Replayed',len(results),'errors',sum(bool(x['error']) for x in results))

if __name__=='__main__':main()

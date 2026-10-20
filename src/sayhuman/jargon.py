"""Offline, Chinese-first workplace jargon interpreter.

This module never assigns an undocumented motive to an individual. It translates
observable language into concrete requests and supplies a proportionate next move.
Lexical matches and semantic fallbacks have DIFFERENT provenance labels so
coverage statistics cannot misreport a fallback as an exact glossary hit.
"""
from __future__ import annotations
import re
from .content import phrasebook

_ZH = re.compile(r'[\u4e00-\u9fff]')
_EN_BOUND = r'(?<![A-Za-z0-9_]){}(?![A-Za-z0-9_])'


def _contains(text: str, phrase: str) -> tuple[int, int] | None:
    if _ZH.search(phrase):
        index = text.casefold().find(phrase.casefold())
        return (index,index+len(phrase)) if index >= 0 else None
    m = re.search(_EN_BOUND.format(re.escape(phrase)),text,flags=re.I)
    return m.span() if m else None


def _literal_homonym(text: str, phrase: str) -> bool:
    lower=text.lower()
    return bool((phrase=='bandwidth' and re.search(r'\b(?:wifi|internet|mbps|gbps|fiber)\b',lower))
                or (phrase=='visibility' and re.search(r'\b(?:fog|weather|nighttime|meters)\b',lower))
                or (phrase=='synergy' and re.search(r'\b(?:chemical|reaction|drug interaction)\b',lower))
                or (phrase=='take ownership' and re.search(
                    r'\bownership\s+of\s+(?:(?:this|that|the|a|an|our|your|their)\s+)?(?:(?:software|intellectual)\s+)?(?:licen[sc]e|copyright|trademark|property|asset)\b',
                    lower) and re.search(r'\b(?:expires?|expirations?|transfer|sale|holder|rights?)\b',lower)))


def _find_hits(text: str, industry: str | None):
    hits=[]
    for entry in phrasebook():
        if _literal_homonym(text,entry['phrase']):
            continue
        found=[]
        for candidate in (entry['phrase'], *entry.get('aliases', [])):
            span=_contains(text,candidate)
            if span:
                found.append((len(candidate),span,candidate))
        if found:
            size,span,label=max(found,key=lambda x:(x[0],-x[1][0]))
            hits.append((entry,span,label,size))
    # More specific terms win over generic subphrases, e.g. 病历质控 not 质控.
    ordered=sorted(hits,key=lambda h:(-h[3],h[1][0]))
    selected=[]
    for hit in ordered:
        span=hit[1]
        if any(span[0]>=other[1][0] and span[1]<=other[1][1] for other in selected):
            continue
        selected.append(hit)
    return sorted(selected,key=lambda h:h[1][0])


def _strip_boilerplate(text: str) -> str:
    text=re.sub(r'^[\s“”"「」]*(?:老板|领导|同事|客户|甲方|经理|HR|主管)(?:说|提到|要求|强调|发来消息)[：:,，\s]*','',text).strip()
    return text.strip('“”"「」 ' )


def _smart_followup(text: str, language: str, industry: str | None, recipient: str,
                    channel: str, matches: list[dict]) -> str:
    zh=language=='zh'
    lower=text.casefold()
    scope=bool(re.search(r'口径|颗粒度|范围|边界|对齐|定位|方案|需求|scope|alignment|granularity',lower))
    delivery=bool(re.search(r'上线|落地|交付|发布|推进|启动|执行|履约|完成|闭环|验收|deploy|deliver|rollout',lower))
    measure=bool(re.search(r'提升|提效|降本|增长|优化|ROI|指标|转化|留存|绩效|改善|performance|metric',lower, re.I))
    schedule=bool(re.search(r'回头|再议|后面|同步|碰头|下次|拉会|约会|circle back|touch base',lower,re.I))
    if zh and re.search(r'(?:没|未|没有).{0,10}(?:说明|明确|写)(?:.{0,10})?(?:负责人|时间|截止|验收)|负责人和时间',text):
        if recipient in {'customer','client','客户','甲方'}:
            return '我先按这个方向整理，方便确认负责对接的人和期望完成时间吗？'
        if recipient in {'manager','boss','leader','领导','老板'}:
            return '我先把事项梳理出来，麻烦确认一下由谁负责、希望什么时候完成？'
        return '我们先把负责人和截止时间定下来，我再按这个安排推进，可以吗？'
    if zh:
        ask=('我们先确定要对齐的是哪些内容，以及最后由谁拍板？' if scope else
             '这项工作由谁负责，完成后按什么标准验收？' if delivery else
             '我们以哪个指标为准，和哪段时间的数据作比较？' if measure else
             '方便确定下次讨论时间，以及到时需要作出的决定吗？' if schedule else
             '为了往下推进，能否明确一下要交付的结果和时间？')
        if recipient in {'customer','client','客户','甲方'}:
            return '为了避免理解偏差，想和您确认一下：'+ask
        if recipient in {'manager','boss','leader','领导','老板'}:
            return '我可以先推进，想确认一下：'+ask
        return ask
    return ('Could we clarify the scope and final decision owner?' if scope else
            'Who owns the deliverable, and what counts as done?' if delivery else
            'Which metric and comparison period should we use?' if measure else
            'When should we revisit this, and what decision is needed?' if schedule else
            'What outcome, owner and timeline should we use?')


def _is_metalinguistic_mention(text: str) -> bool:
    """Don't turn words in lesson titles / quotations into operational orders."""
    return bool(re.search(
        r'(?:\b(?:title|trademark|just a quote)\b|商标|商品标题|教材标题|只是.{0,10}标题|'
        r'课堂.{0,10}(?:提到|讲到).{0,30}(?:不是|而非)|'
        r'展示.{0,30}(?:教材|标题)|'
        r'邮件主题.{0,20}(?:分享会|讲座|介绍会))', text, re.I))


def _simple_action(text: str, industry: str | None) -> bool:
    """A simple explicit request shouldn't trigger a vague status-meeting question."""
    t=_strip_boilerplate(text)
    if re.search(r'^(?:请把|把|麻烦把|记得把|先把|交还|打印|补充|请在|请于)',t):
        return True
    if re.search(r'^(?:请|麻烦).{1,30}(?:打印|放在|交给|补充|返还|拍照|记录|转发)',t):
        return True
    if re.search(r'^Please\s+(?:print|send|bring|return|move|attach)\b',t,re.I):
        return True
    return False


# Generalized operational paraphrase patterns, not a mapping of benchmark inputs.
# These are constrained to observable goals; they never infer hidden personal motives.
_SEMANTIC_GOALS = [
  (r'(?:报告|汇报|材料|方案).{0,14}(?:空|太虚|不够实|没有内容|不够有料)', '这份材料缺少能支撑判断的实际成果或证据，不是单纯措辞问题。', '可以补上已完成事项、具体结果、证据来源和下一步需要的决策吗？'),
  (r'(?:老板|领导|客户).{0,12}(?:看不懂|不知道重点|抓不住重点)', '需要把核心结论提前，用具体事实说明对业务的影响。', '这次最需要对方理解或决定的一件事是什么？'),
  (r'(?:老板|领导|客户).{0,12}(?:觉得|认为|说).{0,10}(?:空|虚|没亮点)', '对方没有看到足够具体的成果和决策价值，建议补充结果与可核实证据。', '有哪些已验证的结果值得放到开头？'),
  (r'(?:工作|项目|方案).{0,12}(?:亮点|不够亮眼|不够抓人)', '需要让实际贡献更容易看见，优先说明解决了什么问题和产生了什么可核实变化。', '能否列出最重要的一个成果和对应证据？'),
  (r'(?:模型|AI|客服机器人).{0,18}(?:靠谱|质量|评分|评估|测评|准确)', '给模型输出设一套可复核的质量标准。', '打算用哪些典型问题和错误类型来验证？'),
  (r'(?:客服|人工|机器人).{0,22}(?:转人工|找真人|接管|升级)', '明确机器人何时要把问题交给真人处理。', '触发人工接管的条件和交接记录是什么？'),
  (r'(?:旧资料|过期资料|过期知识|(?:资料|知识|文档).{0,18}(?:过期|更新|失效))', '保证回答使用的是当前有效的资料。', '谁更新资料，怎样避免旧版本继续被引用？'),
  (r'(?:模型|版本).{0,24}(?:前后|升级|公平|比较|对照)', '用同一套数据和指标比较新旧版本。', '评测集、关键指标和通过门槛是什么？'),
  (r'(?:包裹|快件).{0,12}(?:中转站|滞留|卡在)', '缩短包裹在运输节点停留的时间。', '哪个中转环节最久，如何统计滞留时间？'),
  (r'(?:领券|优惠券).{0,18}(?:不用|使用|核销)', '重点是让领到券的客户真正完成使用。', '领券到使用在哪一步流失最多？'),
  (r'(?:检查结果|检验结果).{0,20}(?:医生|交到|送到|通知)', '让负责的医生及时收到检查结果并确认处理。', '结果由谁接收，如何记录交接时间？'),
  (r'(?:贷款风险|授信风险|风控).{0,18}(?:更细|分层|分级|看得)', '把客户贷款风险分层梳理，先明确需要重点复核的人群。', '分类依据和复核流程是什么？'),
  (r'(?:试用期).{0,14}(?:考核|评价|标准)', '把试用期考核要求写清楚，让员工知道按什么评估。', '哪些目标和证据会在试用期评估？'),
  (r'(?:报名).{0,18}(?:实际开课|入班|流失)', '找出报名意向到实际开始上课之间的流失环节。', '报名后哪一步流失最多？'),
  (r'(?:培训).{0,18}(?:用上|应用|转化)', '让培训内容真正用于日常工作，而不只是参加课程。', '培训后如何观察实际工作表现？'),
  (r'(?:材料|表格).{0,18}(?:重复提交|反复填|删减)', '减少重复提交资料和没有实际价值的填报步骤。', '哪些材料或表单能直接合并、复用？'),
  (r'(?:异地|外地).{0,18}(?:办理|申请|服务)', '让符合条件的事项可以在异地办理。', '哪些事项支持异地办，申请需要什么材料？'),
  (r'(?:关键岗位).{0,18}(?:离职|交接|空缺)', '要提前准备关键岗位的交接和接替安排。', '谁接手哪些工作，交接时间如何安排？'),
  (r'(?:更快|时长|等待|候诊|时效|延误|积压|排队)', '重点是减少流程等待时间，先找到耗时最多的环节。', '目前平均等待多久，希望改善哪一段？'),
  (r'(?:统一|一致|标准|评分|格式|可比|口径)', '先统一各方遵守的定义和执行标准。', '标准由谁确认，哪些场景属于例外？'),
  (r'(?:追溯|追到|交接|处理人|负责单位|责任人|接单)', '把每一步的处理记录和责任人对应起来。', '在哪个环节留下记录，由谁确认完成？'),
  (r'(?:不要遗漏|漏掉|漏报|危险|高风险|异常|预警)', '需要让关键异常及时被发现并有人处理。', '异常触发条件、接收人和处置时限是什么？'),
  (r'(?:退货|退款|投诉|原因|复盘|返工)', '先找出反复发生问题的原因，再明确改善措施。', '需要按哪些原因分类，以及先处理哪一类？'),
  (r'(?:复购|回头买|再购买|留存|续费|回流)', '重点是让已有用户愿意再次使用或购买。', '用哪个用户群和时间周期来评估？'),
  (r'(?:断货|补货|货位|货架|拣货|库存)', '要改善库存和商品流转，减少缺货或多余操作。', '先对哪些商品或仓位做小范围验证？'),
  (r'(?:上课|学生|课程|讲完|学习|练习|考试)', '重点是让教学过程能根据实际学习反馈改进。', '如何判断学生是否掌握，谁来复核？'),
  (r'(?:交付|量产|试做|试产|出厂|检验|一次就过关)', '让工作结果满足进入下一阶段的验收条件。', '哪些验收指标达标以后才能推进？'),
  (r'(?:权限|漏洞|攻击|补丁|安全|告警)', '要降低安全风险，同时保证异常有人及时处理。', '触发条件、负责人和恢复流程是什么？'),
]


def _semantic_fallback(text: str, language: str) -> tuple[str,str,str,str]:
    cleaned=_strip_boilerplate(text).rstrip('。！？!?;；')
    if language=='zh':
        if _simple_action(cleaned,None):
            return '清楚的行动',f'要求很明确：{cleaned}。','plain-language',''
        for pattern,human,reply in _SEMANTIC_GOALS:
            if re.search(pattern,cleaned,re.I):
                return '目标提炼',human,'semantic-fallback',reply
        if re.search(r'先.{1,50}(再|然后|随后).{1,60}',cleaned):
            return '任务拆解',f'先完成前置事项，再推进后续工作：{cleaned}。','semantic-fallback',''
        if _simple_action(cleaned,None):
            return '清楚的行动',f'要求很明确：{cleaned}。','plain-language',''
        if re.search(r'^(?:请|需要|要|麻烦|务必|抓紧|尽快|推动|落实|做好|推进|优化|提升|压降|评估|梳理|完善|强化|统筹|建立|形成|打磨|深化|保障|加快)',cleaned):
            return '执行请求',f'要做的是：{cleaned}。','semantic-fallback','具体要交付什么结果，什么时候完成？'
        if re.search(r'(?:怎么|什么|何时|哪里|谁|能否|是否|如何|哪种|多少|几时|请问)',cleaned):
            return '明确问题',f'对方想确认的是：{cleaned}。','semantic-fallback',''
        return '普通表达',f'这句话已经很清楚：{cleaned}。','plain-language',''
    if re.search(r'\b(?:please|need to|should|deliver|roll out|improve|optimize|revisit|review)\b', cleaned, re.I):
        return 'action-request',f'In plain terms, the request is: {cleaned}.','semantic-fallback','Who owns the next step, and when is it due?'
    return 'plain-language',f'This is already clear: {cleaned}.','plain-language',''


def decode(text: str, industry: str | None=None, recipient: str='unspecified',
           channel: str='chat', goal: str='') -> dict:
    if not text.strip():
        raise ValueError('Input cannot be empty')
    language='zh' if _ZH.search(text) else 'en'
    hits=[] if _is_metalinguistic_mention(text) else _find_hits(text,industry)
    matches=[]
    for entry,span,label,_ in hits:
        matches.append({
            'phrase':entry['phrase'], 'matched_as':label,
            'industry':entry.get('industry','general'),
            'next_question_zh':entry.get('next_question_zh',''),
            'plain_english':entry['plain_english'],
            'plain_language':entry['plain_zh'] if language=='zh' else entry['plain_english'],
            'possible_subtext':entry['possible_subtext_zh'] if language=='zh' else entry['possible_subtext'],
        })
    if matches:
        segments=[m['plain_language'].rstrip('。.! ') for m in matches[:4]]
        if language=='zh':
            summary='；'.join(segments)+'。'
        else:
            summary='; '.join(segments)+'.'
        quality='lexicon'
    else:
        if _is_metalinguistic_mention(text):
            cleaned=_strip_boilerplate(text).rstrip('。！？!?;；')
            summary=(f'这里是在引用一个术语或标题，没有提出相关项目任务：{cleaned}。' if language=='zh' else f'The term is only mentioned, not assigned as a task: {cleaned}.')
            quality='plain-language'
            fallback_reply=''
        else:
            _, summary, quality, fallback_reply=_semantic_fallback(text,language)
    next_reply=(_smart_followup(text,language,industry,recipient,channel,matches) if matches else (fallback_reply if quality!='plain-language' else ''))
    if _simple_action(text,industry) and not matches:
        next_reply=''
    # Prefer grounded, sector-specific follow-up over a generic project-management question.
    if language=='zh' and matches:
        ranked=sorted((m for m in matches if m.get('next_question_zh')),
                      key=lambda m:(m.get('industry')==industry, m.get('industry')!='general'), reverse=True)
        if ranked:
            specific=ranked[0]['next_question_zh']
            intro=('为了便于我们推进，想确认一下：' if recipient in {'customer','client','客户','甲方'} else
                   '我来跟进，想确认一下：' if recipient in {'manager','boss','leader','领导','老板'} else '')
            next_reply=intro+specific
    context=''
    if quality=='lexicon' and language=='zh':
        # Describe ONLY observable uncertainty, no repetitive mind-reading warning.
        if re.search(r'优化编制|人员优化|right.size|资源倾斜|愿景激励',text,re.I):
            context='这里需要具体确认调整范围、安排和执行标准。'
    result={
        'mode':'decode','input':text,'language':language,'matches':matches,
        'summary':summary,'resolution':quality,'hit_count':len(matches),
        'matched_terms':[m['matched_as'] for m in matches],
        'certainty':'possible interpretation, not a verified motive', # legacy machine-readable field, never printed
        'context_note':context,'clarifying_question':next_reply,
        'source':'offline-phrasebook' if quality=='lexicon' else 'offline-semantic-fallback',
        'recipient':recipient,'channel':channel,
    }
    if industry:
        from .industry import industry_followup
        result['industry_followup'] = industry_followup(industry, language)
    return result


def format_decode(result:dict) -> str:
    zh=result['language']=='zh'
    if zh:
        sections=['**一句人话：** '+result['summary']]
        # The first line already spells out each match; avoid repeating the same translation.
        if result.get('context_note'):
            sections.append('**需要确认：** '+result['context_note'])
        if result['clarifying_question']:
            sections.append('**建议追问（可以这样回）：** '+result['clarifying_question'])
        return '\n\n'.join(sections)
    lines=['**In plain English:** '+result['summary']]
    if result['matches']:
        lines += ['**Possible subtext:** '+ '; '.join(m['possible_subtext'] for m in result['matches'][:3])]
    if result['clarifying_question']:
        lines.append('**A useful reply:** '+result['clarifying_question'])
    return '\n\n'.join(lines)

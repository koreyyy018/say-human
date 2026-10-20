"""Cross-industry decoder v0.5 regressions: coverage is not the same as quality."""
import pytest
from sayhuman.content import phrasebook
from sayhuman.engine import decode, format_markdown

@pytest.mark.parametrize('term,industry,part',[
 ('模型路由','ai','不同模型'),
 ('贷后预警','finance','偿还'),
 ('危急值闭环','healthcare','及时'),
 ('直通率','manufacturing','首次'),
 ('券核销漏斗','ecommerce','优惠券'),
 ('学情预警','education','学习'),
 ('妥投率','logistics','签收'),
 ('绩效分布校准','hr','绩效'),
 ('跨省通办','government','异地'),
 ('资产暴露面','security','外部'),
 ('货架转化','retail','购买'),
 ('版权确权','publishing','授权'),
 ('新手流失节点','gaming','退出'),
 ('弃风弃光','energy','电网'),
 ('现金流回正','realestate','净流入'),
])
def test_new_industry_term(term,industry,part):
    r=decode('业务会上提到'+term+'，需要解释一下。', industry)
    assert any(m['phrase']==term for m in r['matches'])
    assert part in r['summary']
    assert '--llm' not in format_markdown(r)
    assert '以下只是可能的解读' not in format_markdown(r)

@pytest.mark.parametrize('text',[
 '请把打印机里的纸补充一下。',
 '请把会议室钥匙还给前台。',
 '下周一早上有语文公开课。',
 '周三下午两点开模型评审会。',
])
def test_clear_language_no_forced_question(text):
    r=decode(text)
    assert not r['matches']
    assert r['resolution']=='plain-language'
    assert not r['clarifying_question']

@pytest.mark.parametrize('text',[
 '商品标题写着“全域网球拍”，这里的全域是商标的一部分。',
 '今天学生在课堂提到了“增长飞轮”这个词，但不是经营会议。',
 '会议上展示了“数字化转型”的教材标题，不是项目安排。',
 '邮件主题写着“人才梯队分享会”，不涉及人事任命。',
])
def test_mention_not_business_request(text):
    r=decode(text)
    assert r['resolution']=='plain-language'
    assert not r['matches']
    assert not r['clarifying_question']

@pytest.mark.parametrize('text',[
 '监控显示 WiFi bandwidth 达到500 Mbps，网络良好。',
 'Weather visibility is only 200 meters this morning.',
])
def test_literal_homonym_not_corporate_jargon(text):
    assert decode(text)['matches']==[]

def test_unknown_phrase_stays_in_user_language():
    r=decode('老板说要让仓库退货处理更快，先看看办法。','logistics')
    msg=format_markdown(r)
    assert '一句人话' in msg
    assert '未识别' not in msg
    assert '--llm' not in msg

def test_tactful_reply_for_customer():
    r=decode('客户要求把项目闭环，周五同步。','ai', recipient='客户')
    assert r['clarifying_question'].startswith(('为了便于我们推进','为了避免理解偏差'))
    assert '？' in r['clarifying_question']

def test_lexicon_scale_and_coverage():
    words=phrasebook()
    assert len(words)>=350
    assert len({x['phrase'].casefold() for x in words}) ==len(words)
    assert len({x.get('industry','general') for x in words}) >= 15

def test_no_auto_motive_attribution():
    msg=format_markdown(decode('HR说要做人员优化，具体流程没通知。', 'hr'))
    assert '一定' not in msg and '裁员已决定' not in msg
    assert '以下只是可能的解读' not in msg

"""Protect deterministic regressions discovered by the cross-industry evaluation."""
import json
from pathlib import Path
from sayhuman.engine import explain, decode, encode, format_markdown

ROOT=Path(__file__).resolve().parents[1]


def test_dataset_size_and_coverage():
    cases=[json.loads(x) for x in (ROOT/'evals/scenarios.jsonl').read_text(encoding='utf8').splitlines()]
    assert len(cases)>=200
    assert len({x['industry'] for x in cases if x['industry']!='Cross-industry edge cases'})>=15
    assert all(sum(x['mode']==m for x in cases)>=60 for m in ('explain','decode','encode'))


def test_technical_and_cfo_audience_are_meaningfully_distinct():
    first=explain('RAG','cfo')
    second=explain('RAG','engineer')
    assert 'cost' in first['audience_guidance'].lower()
    assert 'implementation' in second['audience_guidance'].lower()
    assert first['audience_guidance']!=second['audience_guidance']
    assert 'Audience decision' in format_markdown(first)


def test_chinese_jargon_is_decoded_in_chinese():
    result=decode('老板说先拉齐口径，再协同一下，最后做好闭环。')
    assert {x['phrase'] for x in result['matches']}=={'alignment','synergy','action items'}
    assert all('。' in x['plain_language'] for x in result['matches'])
    assert '建议追问' in format_markdown(result)


def test_technical_homonyms_are_not_called_corporate_jargon():
    for sentence in ('The internet bandwidth is 100 Mbps.',
                     'Nighttime visibility dropped below 50 m in fog.',
                     'Chemical synergy was observed in the reaction.'):
        assert decode(sentence)['matches']==[]


def test_no_synthetic_roi_or_blame():
    result=encode('Fixed a bug because the previous dev was stupid, now it runs faster.')
    assert 'stupid' not in result['executive_update']
    assert '40%' not in result['executive_update']
    assert 'benchmark' in result['executive_update'].lower()


def test_deployment_scope_in_chinese():
    result=encode('修了物业报修工单重复创建的问题，还没上线。')
    assert '尚未上线' in result['executive_update']
    assert '尚未上线' in result['source_note'] or result['source_note'].endswith('还没上线。')


def test_quality_escape_hatch_security_and_fake_claim():
    risky=encode('Ship it: I deleted the fraud detection check; it costs too much.')
    assert 'control_removed' in risky['risk_flags']
    assert 'risk' in risky['executive_update'].lower()
    fake=encode('Added a fake 200% ROI slide just to impress the boss.')
    assert 'possible_fabrication' in fake['risk_flags']
    assert 'verify' in fake['executive_update'].lower()


def test_known_chinese_grammar_regression():
    fixed=encode('门诊叫号机今天修了个显示 bug，目前只在测试环境验证。')
    assert '已修复门诊叫号机的显示缺陷' in fixed['executive_update']
    assert '尚未' in encode('修好了收银系统优惠券叠加出错，店员还没验收。')['executive_update']
    assert '还尚未' not in encode('修好了收银系统优惠券叠加出错，店员还没验收。')['executive_update']


def test_no_unverified_compliance_claim():
    result=encode('Do NOT say our API is HIPAA compliant; we only changed the login text.')
    assert 'compliance_not_verified' in result['risk_flags']
    assert 'has not been established' in result['executive_update']


def test_ownership_legal_noun_not_corporate_jargon():
    assert decode('Ownership of this software license expires on Friday.')['matches'] == []
    matches=decode('Please take ownership of the onboarding task.')['matches']
    assert any(item['phrase']=='take ownership' for item in matches)

def test_publishing_retrospective_is_valid_additional_match():
    matches=decode('作者运营这周先对齐选题，下周复盘闭环。')['matches']
    assert {m['phrase'] for m in matches} == {'alignment','复盘','action items'}

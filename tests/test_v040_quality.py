"""Reproducible checks for the v0.4 release candidate.

These are behavior/contract tests, not human subjective-quality judgments.
"""
from __future__ import annotations
import json
from pathlib import Path
import pytest
from sayhuman.alignment import align
from sayhuman.cli import build_parser, run
from sayhuman.tone import connection_note

ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('goal,expected',[
    ('把医院预约系统弄快一点，但别泄露患者信息','响应时间'),
    ('降低电商客服每次成功处理工单的成本','单次成功任务成本'),
    ('提升物流派单的准确率，降低误派','错误率及人工复核率'),
    ('Our API must be more reliable during outages', 'critical workflow success rate'),
    ('Make player onboarding more user friendly', 'task completion and user feedback'),
])
def test_alignment_metric_is_specific_and_targets_unapproved(goal,expected):
    a=align(goal)
    assert expected in a['proposed_metrics']
    assert a['status']=='draft_for_discussion_not_approved'
    assert a['questions'] and a['constraints']
    assert not any(token in a['acceptance_plan'] for token in ['40%', '99%', '30%'])

@pytest.mark.parametrize('bad', ['', ' ', None])
def test_align_rejects_empty(bad):
    with pytest.raises((ValueError,TypeError)):
        align(bad)

def test_align_rejects_invalid_industry_and_oversize():
    with pytest.raises(ValueError): align('speed up', 'not-a-real-sector')
    with pytest.raises(ValueError): align('a'*8001)

def test_cli_align_json_and_markdown():
    cmd=build_parser().parse_args(['align','优化工厂设备故障响应时间','--industry','manufacturing','--lang','zh','--format','json'])
    item=json.loads(run(cmd))
    assert item['proposed_metrics']==['响应时间']
    assert item['industry']=='Manufacturing / Factory'
    assert item['source']=='offline-requirements-scaffold'
    cmd.format='markdown'
    assert '业务需求 → 可验证的工程任务' in run(cmd)
    assert '阈值' in run(cmd)

def test_reply_offline_fails_honestly():
    cmd=build_parser().parse_args(['reply','经理催进度','--recipient','boss'])
    with pytest.raises(ValueError,match='--llm'):
        run(cmd)

def test_llm_reply_context_is_passed_as_user_provided_data(monkeypatch):
    calls={}
    def mock(system,user):
        calls['system']=system
        calls['user']=user
        return '这是根据事实范围写的回复。'
    monkeypatch.setattr('sayhuman.cli.generate',mock)
    cmd=build_parser().parse_args(['reply','客户追问上线时间。','--recipient','customer',
                                    '--channel','email','--goal','说明还没上线','--llm', '--format','json'])
    result=json.loads(run(cmd))
    assert result['source']=='configured-remote-llm'
    assert 'Mode: REPLY' in calls['user']
    assert 'Recipient/relationship: customer' in calls['user']
    assert 'Channel: email' in calls['user']
    assert 'Communication goal: 说明还没上线' in calls['user']
    assert 'Mode C — REPLY' in calls['system']
    assert '<untrusted_input>' in calls['user']

def test_skill_integrations_are_synced_and_use_correct_scope():
    skill=(ROOT/'skills/say-human/SKILL.md').read_bytes()
    for tool in ['.agents','.claude']:
        assert (ROOT/tool/'skills/say-human/SKILL.md').read_bytes()==skill
        assert (ROOT/tool/'skills/say-human/references/contexts.md').exists()
    assert b'Do not trigger' in skill
    rule=(ROOT/'.cursor/rules/say-human.mdc').read_text()
    assert 'alwaysApply: false' in rule
    assert 'reply' in (ROOT/'.cursor/commands/say-human.md').read_text().casefold()

@pytest.mark.parametrize('s,phrase',[
    ('我搞不懂 RAG 啊','技术术语'),
    ('我有点烦，经理说要对齐闭环','黑话'),
    ('我很担心，还没正式上线','还没正式上线'),
])
def test_warmth_ties_to_the_problem(s,phrase):
    mode='decode' if '经理' in s else 'explain'
    assert phrase in connection_note(s,mode,'warm')

def test_formal_and_neutral_never_add_warmth():
    assert connection_note('有点烦修复接口了','encode','neutral') is None
    assert connection_note('有点烦修复接口了','encode','warm',formal=True) is None
    assert connection_note('修复了接口','encode','warm') is None

def test_prompt_safety_and_gold_anchors():
    p=(ROOT/'skills/say-human/SKILL.md').read_text()
    assert 'untrusted data' in p
    assert 'No invented percentages' in p
    assert 'Nine original metaphors' in p
    assert 'five' in p.casefold()

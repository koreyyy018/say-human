import pytest
from sayhuman.engine import explain, encode
from sayhuman.reporting import audit

@pytest.mark.parametrize('query', ['RAG 和 Fine-tuning 的区别','Agent vs Agentic Workflows','RAG 和 Agent 哪个更合适','比较 LoRA 与 Quantization','API和Caching有什么区别'])
def test_multi_comparison(query):
    result=explain(query,lang='zh')
    assert result['mode']=='compare' and len(result['items'])>=2
    assert all(i.get('human') and i.get('caveat') for i in result['items'])

@pytest.mark.parametrize('source,candidate', [
('只在测试环境跑过一次，还没上线','已全面上线，面向全部客户'),
('目前仍在灰度测试','全量发布'),
('上线待定，当前仅在预发环境','已正式上线'),
('安全审查尚未完成','已完成全部安全审查'),
('单次测试，没有基线','已证明收益显著提升'),
])
def test_new_high_risk_examples(source,candidate):
    assert audit(source,candidate)['risk_flags']

@pytest.mark.parametrize('source,candidate', [
('测试环境验证，尚未上线','待验收通过后再发布'),
('尚未通过安全审查','不应宣称已经通过安全审查'),
('还在测试','计划下周发布到全部客户'),
])
def test_no_false_positive(source,candidate):
    assert not {'unsupported_deployment_status','unsupported_completion_status','unsupported_security_review'} & set(audit(source,candidate)['risk_flags'])

def test_chinese_grammar():
    result=encode('把支付接口的一个bug修了，还没上线')['executive_update']
    assert '把支付接口' not in result or '已修复' not in result

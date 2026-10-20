from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'evals'))
import ab_compare, score_blind
import pytest


def test_dry_case_reader_and_no_duplicates():
    cases=ab_compare.read_cases(ROOT/'evals/ab_cases.jsonl',12)
    assert len(cases)==12
    assert sum(c['mode']=='encode' for c in cases)>=4


def test_blind_scoring_splits_key_without_network():
    cases=ab_compare.read_cases(ROOT/'evals/ab_cases.jsonl',3)
    calls=[]
    def fake(system,user):
        calls.append((system,user))
        return 'GOOD skill response' if 'Metaphor' in system or 'Jargon' in system else 'basic response'
    deck,key=ab_compare.blinded_pairs(cases,fake,seed=3)
    assert len(calls)==6
    assert len(deck)==len(key)==3
    assert all('skilled_side' not in x for x in deck)
    assert all(x['A'] and x['B'] for x in deck)
    assert deck==ab_compare.blinded_pairs(cases,lambda p,u:'GOOD skill response' if 'Metaphor' in p or 'Jargon' in p else 'basic response',seed=3)[0]
    for x in deck:
        x['scores']={'A':{d:4 for d in score_blind.DIMENSIONS},'B':{d:3 for d in score_blind.DIMENSIONS}}
    stats=score_blind.summarize(deck,key)
    assert stats['n_cases']==3
    assert all(1<=v<=5 for a in stats['average_scores'].values() for v in a.values())


def test_fake_score_fails_closed():
    with pytest.raises(ValueError):
        score_blind.summarize([{'id':'1','scores':{'A':None,'B':None}}], [{'id':'1','skilled_side':'A'}])

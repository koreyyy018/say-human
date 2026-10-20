"""Summarize independent manual scores in 1..5; do not generate scores automatically."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

DIMENSIONS=('factual_fidelity','clarity','usefulness','tone')


def summarize(blind_rows: list[dict], private_key: list[dict]) -> dict:
    key={r['id']:r['skilled_side'] for r in private_key}
    scores={'skilled':{d:[] for d in DIMENSIONS}, 'generic':{d:[] for d in DIMENSIONS}}
    if len(key)!=len(private_key) or {x['id'] for x in blind_rows} != set(key):
        raise ValueError('Mismatch or duplicate IDs in blind pairs / answer key')
    for r in blind_rows:
        label=key[r['id']]
        if label not in {'A','B'}:
            raise ValueError('Invalid answer key label')
        for side,group in ((label,'skilled'), ('B' if label == 'A' else 'A','generic')):
            entry=r.get('scores',{}).get(side)
            if not isinstance(entry,dict):
                raise ValueError(f"Missing manual 1..5 scores: {r['id']} side {side}")
            for dimension in DIMENSIONS:
                value=entry.get(dimension)
                if type(value) not in {int,float} or not 1<=value<=5:
                    raise ValueError(f"Invalid independent score {r['id']} {side}.{dimension}")
                scores[group][dimension].append(value)
    total=len(blind_rows)
    return {'n_cases':total, 'method':'independent, manually scored blind responses; no automatic LLM judge',
            'average_scores':{group:{d:round(sum(v)/len(v),3) if v else None for d,v in dim.items()} for group,dim in scores.items()},
            'note':'Descriptive sample results only. No significance claims are made.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pairs', type=Path, required=True)
    p.add_argument('--key', type=Path, required=True)
    args=p.parse_args()
    load=lambda f:[json.loads(row) for row in f.read_text(encoding='utf-8').splitlines() if row.strip()]
    print(json.dumps(summarize(load(args.pairs),load(args.key)),ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())

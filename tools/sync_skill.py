#!/usr/bin/env python3
"""Ensure Codex and Claude copies are byte-for-byte identical to canonical skill."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORIGIN=ROOT/'skills/say-human'
TARGETS=[ROOT/'.agents/skills/say-human', ROOT/'.claude/skills/say-human']

def run(check=True):
    source={str(f.relative_to(ORIGIN)):f.read_bytes() for f in ORIGIN.rglob('*') if f.is_file()}
    if not source or 'SKILL.md' not in source: raise RuntimeError('Missing canonical skill')
    for dest in TARGETS:
        if check:
            target={str(f.relative_to(dest)):f.read_bytes() for f in dest.rglob('*') if f.is_file()} if dest.exists() else {}
            if source!=target: raise RuntimeError(f'Skill adapter out of sync: {dest}')
        else:
            if dest.exists(): shutil.rmtree(dest)
            shutil.copytree(ORIGIN,dest)
    return len(source)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    print(f'Validated {run(check=not args.write)} skill files in both agent adapters')

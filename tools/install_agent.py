#!/usr/bin/env python3
"""Install a portable, self-contained Say Human skill into an existing project.

--dry-run previews without writing; normal execution installs only if
there are no conflicting managed paths; --force explicitly replaces managed files.
No network, pip dependency, shell execution, or root AGENTS.md modifications.
"""
from __future__ import annotations
import argparse
import shutil
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
FILES = {
    'cursor': [('.cursor/rules/say-human.mdc', '.cursor/rules/say-human.mdc'),
               ('.cursor/commands/say-human.md', '.cursor/commands/say-human.md')],
    'codex': [('skills/say-human', '.agents/skills/say-human')],
    'claude': [('skills/say-human', '.claude/skills/say-human')],
}

def selected(agent: str):
    return [item for a in ('cursor', 'codex', 'claude') if agent in ('all', a) for item in FILES[a]]

def plan(target: Path, agent: str, force: bool = False):
    """Produce an all-or-nothing copy plan; reject unsafe links and collisions."""
    if not target.is_dir() or target.is_symlink():
        raise ValueError('Target must be an existing, non-symlink directory')
    root = target.resolve()
    actions = []
    for src_rel, dest_rel in selected(agent):
        src = SOURCE / src_rel
        dst = root / dest_rel
        if not src.exists(): raise ValueError(f'Missing source: {src_rel}')
        # Refuse any symlink component, even if it resolves inside target.
        for parent in (dst, *dst.parents):
            if parent == root.parent: break
            if parent.is_symlink(): raise ValueError(f'Symlinked installation path rejected: {parent}')
        if not dst.resolve().is_relative_to(root):
            raise ValueError(f'Destination escapes target: {dest_rel}')
        if src.is_dir():
            for leaf in src.rglob('*'):
                if not leaf.is_file(): continue
                rel = leaf.relative_to(src)
                existing = dst/rel
                if existing.exists() and not force:
                    raise FileExistsError(f'Already exists: {existing}; use --force to update')
                if existing.is_symlink(): raise ValueError(f'Symlinked destination rejected: {existing}')
                actions.append((leaf, existing))
        else:
            if dst.exists() and not force:
                raise FileExistsError(f'Already exists: {dst}; use --force to update')
            actions.append((src,dst))
    return actions

def install(target: Path, agent='all', dry_run=False, force=False):
    actions=plan(target, agent, force)
    if not dry_run:
        for src,dst in actions:
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(src,dst)
    return [str(dst.relative_to(target.resolve())) for _,dst in actions]

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path,required=True,help='Existing project directory (no network access)')
    parser.add_argument('--agent',choices=('all','cursor','codex','claude'),default='all')
    parser.add_argument('--dry-run',action='store_true',help='Preview without writing files')
    parser.add_argument('--force',action='store_true',help='Update only Say Human managed files; leave unrelated files intact')
    args=parser.parse_args(argv)
    try:
        paths=install(args.target,args.agent,args.dry_run,args.force)
    except (ValueError,FileExistsError,OSError) as e:
        print(f'install_agent: {e}',file=sys.stderr)
        return 2
    print(('Preview:' if args.dry_run else 'Installed:')+f' {len(paths)} files')
    for path in paths: print('  '+path)
    return 0

if __name__=='__main__': raise SystemExit(main())

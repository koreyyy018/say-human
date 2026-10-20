"""Conformance tests for packaged agent adapters (not live vendor agents)."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import pytest
from sayhuman.cli import build_parser, run
from sayhuman.tone import connection_note

ROOT=Path(__file__).resolve().parents[1]
INSTALLER=ROOT/'tools/install_agent.py'


def install(target, *options):
    return subprocess.run([sys.executable,str(INSTALLER),'--target',str(target),*options], capture_output=True, text=True)

@pytest.mark.parametrize('agent,paths',[
    ('cursor',['.cursor/rules/say-human.mdc','.cursor/commands/say-human.md']),
    ('codex',['.agents/skills/say-human/SKILL.md','.agents/skills/say-human/references/modes.md']),
    ('claude',['.claude/skills/say-human/SKILL.md','.claude/skills/say-human/references/quality.md']),
])
def test_vendor_clean_install(tmp_path,agent,paths):
    t=tmp_path/agent; t.mkdir(); (t/'AGENTS.md').write_text('Important existing guidance.\n')
    run=install(t,'--agent',agent)
    assert run.returncode==0,run.stderr
    for rel in paths: assert (t/rel).is_file()
    assert (t/'AGENTS.md').read_text()=='Important existing guidance.\n'


def test_all_install_standalone_references(tmp_path):
    result=install(tmp_path,'--agent','all')
    assert result.returncode==0
    for agent in ('codex','claude'):
        p=tmp_path/f'.{"agents" if agent=="codex" else "claude"}/skills/say-human'
        assert (p/'SKILL.md').is_file()
        for rel in ('modes.md','quality.md','gold-standard-fewshots.md'):
            assert (p/'references'/rel).stat().st_size>100
        assert 'Do not trigger' in (p/'SKILL.md').read_text()


def test_installer_dry_run_does_not_write(tmp_path):
    r=install(tmp_path,'--dry-run')
    assert r.returncode==0 and 'Preview:' in r.stdout
    assert not (tmp_path/'.agents').exists()


def test_installer_collision_is_atomic(tmp_path):
    old=tmp_path/'.claude/skills/say-human/SKILL.md'; old.parent.mkdir(parents=True)
    old.write_text('user data\n')
    r=install(tmp_path,'--agent','all')
    assert r.returncode==2 and 'Already exists' in r.stderr
    assert old.read_text()=='user data\n'
    assert not (tmp_path/'.cursor').exists()


def test_installer_force_overwrites_only_managed_files(tmp_path):
    dest=tmp_path/'.claude/skills/say-human/SKILL.md';dest.parent.mkdir(parents=True)
    dest.write_text('outdated\n')
    unrelated=dest.parent/'my-notes.md';unrelated.write_text('must survive')
    r=install(tmp_path,'--agent','claude','--force')
    assert r.returncode==0 and 'say-human' in dest.read_text()
    assert unrelated.read_text()=='must survive'


def test_installer_rejects_symlink_target_and_child(tmp_path):
    target=tmp_path/'project';target.mkdir()
    link=tmp_path/'link';link.symlink_to(target,target_is_directory=True)
    assert install(link).returncode==2
    external=tmp_path/'external';external.mkdir()
    (target/'.agents').symlink_to(external,target_is_directory=True)
    assert install(target,'--agent','codex').returncode==2
    assert not list(external.iterdir())


def test_cursor_selective_and_manual_trigger():
    m=(ROOT/'.cursor/rules/say-human.mdc').read_text()
    assert 'alwaysApply: false' in m
    assert (ROOT/'.cursor/commands/say-human.md').is_file()
    assert 'Do not apply to ordinary coding' in m


def test_realistic_tone_is_opt_in_and_specific():
    assert connection_note('RAG','explain','neutral') is None
    assert connection_note('RAG','explain','warm') is None
    assert '技术' in connection_note('我搞不懂RAG','explain','warm') or '术语' in connection_note('我搞不懂RAG','explain','warm')
    assert connection_note('我搞不懂RAG','explain','warm',formal=True) is None
    assert 'PPT' in connection_note('修了bug','encode','playful')


def test_cli_tone_separate_from_evidence():
    args=build_parser().parse_args(['encode','我烦死了，今天把登录问题修了还没上线','--tone','warm','--format','json'])
    data=json.loads(run(args))
    assert 'connection_note' in data
    assert data['evidence_ledger']['new_numbers_in_output']==[]
    assert '尚未上线' in data['executive_update']
    assert 'connection_note' not in data['executive_update']


def test_formal_report_no_warmth_in_copy():
    args=build_parser().parse_args(['report','{"action":"修复查询","subject":"排班系统","status":"staging_validated"}','--lang','zh','--tone','playful','--format','json'])
    data=json.loads(run(args))
    assert 'connection_note' not in data
    assert '上线未确认' in data['executive_update']


def test_skill_origins_are_identical():
    base=ROOT/'skills/say-human'
    for dest in (ROOT/'.agents/skills/say-human',ROOT/'.claude/skills/say-human'):
        assert sorted(str(f.relative_to(base)) for f in base.rglob('*') if f.is_file()) == sorted(str(f.relative_to(dest)) for f in dest.rglob('*') if f.is_file())
        for f in base.rglob('*'):
            if f.is_file(): assert f.read_bytes()==(dest/f.relative_to(base)).read_bytes()


def test_developer_frustration_stays_outside_executive_copy():
    args=build_parser().parse_args(['encode','有点烦，修复发票接口，还没上线','--tone','warm','--format','json'])
    data=json.loads(run(args))
    assert '有点烦' not in data['executive_update']
    assert data['executive_update'].startswith('修复发票接口')
    assert '尚未上线' in data['executive_update']
    assert data['connection_note']

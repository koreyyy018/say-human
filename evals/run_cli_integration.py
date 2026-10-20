"""Run all benchmark cases through the installed-style CLI path using JSON output."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
CASES=[json.loads(line) for line in (ROOT/'evals/scenarios.jsonl').read_text(encoding='utf8').splitlines() if line.strip()]
ENV=os.environ.copy()
ENV['PYTHONPATH']=str(ROOT/'src') + (os.pathsep+ENV['PYTHONPATH'] if ENV.get('PYTHONPATH') else '')
sys.path.insert(0,str(ROOT/'src'))
from sayhuman.cli import build_parser, run
parser=build_parser()
rows=[]
for case in CASES:
    cmd=[sys.executable,'-m','sayhuman',case['mode'],case['text'],'--format','json']
    if case['mode']=='explain': cmd.extend(['--audience',case['audience']])
    try:
        output=run(parser.parse_args(cmd[3:]))
        data=json.loads(output)
        returncode=0; stderr=''
    except Exception as exc:
        data={};returncode=2;stderr=str(exc)
    correct=(returncode==0 and data.get('mode')==case['mode'] and
             (data.get('term')==case['expected_term'] if case['mode']=='explain' else
              data.get('input')==case['text'] if case['mode']=='decode' else
              data.get('source_note')==case['text']))
    rows.append({'id':case['id'],'industry':case['industry'],'mode':case['mode'],'passed':correct,
                 'returncode':returncode,'error':stderr[:300]})
# Verify actual process entry-point separately, without spawning hundreds of slow interpreters.
actual=[]
for case in [CASES[0],CASES[4],CASES[8]]:
    cmd=[sys.executable,'-m','sayhuman',case['mode'],case['text'],'--format','json']
    if case['mode']=='explain': cmd.extend(['--audience',case['audience']])
    process=subprocess.run(cmd,cwd=str(ROOT),env=ENV,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
    try: output=json.loads(process.stdout)
    except ValueError:output={}
    actual.append({'id':case['id'],'passed':process.returncode==0 and output.get('mode')==case['mode']})
results={'total':len(rows),'passed':sum(r['passed'] for r in rows),'failures':[r for r in rows if not r['passed']],
         'subprocess_smoke':actual,
         'definition':'210 in-process CLI parser/run requests + 3 real CLI subprocess requests. Successful parseable JSON with correct mode and input attribution; no remote LLM.'}
(ROOT/'evals'/'cli_integration_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f"CLI integration in-process: {results['passed']}/{results['total']}; subprocess: {sum(r['passed'] for r in actual)}/{len(actual)}")
for row in results['failures'][:8]:print(row)
if results['passed']!=results['total'] or not all(r['passed'] for r in actual): sys.exit(1)

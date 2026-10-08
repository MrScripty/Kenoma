"""Meaningful nonconcurrent alias/overwrite negatives for this output guard."""
from pathlib import Path
from types import SimpleNamespace
import argparse,json,os
from paths import HERE,checked_output,source_hashes
from check_lean import run as check_lean

def run(output):
    out=checked_output(output);passed=[]
    def rejects(name,call,fragment):
        try:call()
        except (ValueError,RuntimeError) as error:
            if fragment not in str(error):raise
            passed.append(name)
        else:raise RuntimeError('Guard accepted negative: '+name)
    rejects('source-overlap',lambda:checked_output(HERE),'source worktree')
    rejects('source-ancestor',lambda:checked_output(HERE.parents[2]),'source worktree')
    alias=out/'source-alias';alias.symlink_to(HERE,target_is_directory=True)
    rejects('symlink-source-alias',lambda:checked_output(alias/'write'),'symlink');alias.unlink()
    directory=out/'hardlinks';directory.mkdir();basis=out/'private-original.txt';basis.write_text('private guard test only')
    os.link(basis,directory/'alias.txt')
    rejects('hardlinked-output-file',lambda:checked_output(directory,fresh=False),'hardlink')
    (directory/'alias.txt').unlink()
    warm=out/'warm';warm.mkdir();(warm/'transcript.txt').write_text('unrelated warm wrapper transcript')
    checked_output(warm,fresh=False);passed.append('safe-warm-transcript-admitted')
    rejects('fresh-nonempty-refusal',lambda:checked_output(warm),'fresh output')
    for filename in ['lateral-transfer-lean.txt','lateral-transfer-proof-status.json']:
        own=out/filename.replace('.','-');own.mkdir();(own/filename).write_text('protected prior output')
        rejects('owned-'+filename,lambda:check_lean(SimpleNamespace(output=own,mathlib=Path('/unused'),lean_bin=Path('/unused'))),'Refuse to overwrite')
        assert (own/filename).read_text()=='protected prior output'
    (out/'guard-tests.json').write_text(json.dumps({'status':'passed','checks':passed,'source_sha256':source_hashes(),
      'scope':'Explicit outputs under nonconcurrent path admission; no concurrency/TOCTOU claim.'},indent=2)+'\n')
    print('Eight source/alias/freshness/receipt protection checks passed.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)

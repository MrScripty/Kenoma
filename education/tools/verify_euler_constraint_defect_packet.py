#!/usr/bin/env python3
"""Verify actual Lean transcript custody and unchanged numerical/proposal evidence."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from check_euler_constraint_defect_proofs import audit_source, audit_transcript

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/'education/data/euler-constraint-defect-proofs-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def main():
    p = json.loads((DATA/'protocol-source.json').read_text())
    freeze = json.loads((DATA/'source-freeze.json').read_text())
    assert git('rev-parse',freeze['commit']+'^{tree}').decode().strip() == freeze['tree']
    for name, digest in {**p['source_sha256'],**p['equation_inputs_sha256']}.items():
        assert sha(ROOT/name) == digest, name
    for name in p['source_sha256']:
        assert git('show',freeze['commit']+':'+name) == (ROOT/name).read_bytes(), name
    for name, digest in p['external_committed_evidence_sha256'].items():
        assert hashlib.sha256(git('show',name)).hexdigest() == digest, name
    for ref, oid in p['preserved_prior_branches'].items():
        assert git('rev-parse',ref).decode().strip() == oid, ref
    src = ROOT/'education/proofs/EulerConstraintDefect.lean'
    claim_file = ROOT/'education/proofs/euler-constraint-defect-claims.json'
    checker = ROOT/'education/tools/check_euler_constraint_defect_proofs.py'
    claims = json.loads(claim_file.read_text())
    audit_source(src.read_text(),claims)
    receipt = json.loads((DATA/'review/kernel-check.json').read_text())
    log = DATA/'review/lean-check.log'
    assert receipt['compiler_exit_code'] == 0 and 'version 4.19.0,' in receipt['lean_version']
    assert receipt['source_freeze_commit'] == freeze['commit'] and receipt['source_freeze_tree'] == freeze['tree']
    assert receipt['source_sha256'] == sha(src) and receipt['claims_sha256'] == sha(claim_file)
    assert receipt['checker_sha256'] == sha(checker) and receipt['transcript_sha256'] == sha(log)
    assert '-DwarningAsError=true' in receipt['command']
    actual = audit_transcript(log.read_text(),claims)
    assert receipt['claims'] == actual and len(actual) == 10
    assert receipt['exact_statements'] == re.findall(r'(?ms)^theorem\s+.*?(?=\s*:= by)',src.read_text())
    for source in receipt['equation_sources']:
        assert source['sha256'] == sha(ROOT/'education'/source['path'])
    assert receipt['sliding_steps_executed'] == receipt['trajectory_states_added'] == 0
    assert not receipt['book_receipts_written'] and not p['book_adoption']
    assert not p['revised_policy_execution_authorized'] and p['new_ODE_steps'] == p['new_accepted_states'] == 0
    attempts = json.loads((DATA/'attempts/manifest.json').read_text())['runs']
    assert [a['compiler_exit_code'] for a in attempts] == [1,0]
    for attempt in attempts:
        assert sha(ROOT/attempt['source']) == attempt['source_sha256']
        assert sha(ROOT/attempt['log']) == attempt['log_sha256']
        assert not attempt['kernel_receipt_issued']
    count = 0
    for entry in filter(None,git('ls-tree','-rz',p['baseline_commit']).split(b'\0')):
        info,name = entry.split(b'\t',1)
        mode,kind,oid = info.split()
        if kind != b'blob':
            continue
        path = ROOT/name.decode()
        data = path.readlink().as_posix().encode() if mode == b'120000' else path.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == oid.decode(), name
        count += 1
    assert count == 2090, count
    manifest = DATA/'packet-manifest.json'
    if manifest.exists():
        for name,record in json.loads(manifest.read_text())['files'].items():
            assert sha(ROOT/name) == record['sha256'] and (ROOT/name).stat().st_size == record['bytes']
    report = dict(source_freeze=freeze,baseline_commit=p['baseline_commit'],preserved_baseline_blobs=count,
                  real_Lean_declarations=10,compiler_exit_code=0,
                  axiom_dependencies=sorted({a for claim in actual for a in claim['axioms']}),
                  kernel_receipt_sha256=sha(DATA/'review/kernel-check.json'),audit_tests=7,
                  preserved_prior_branches=p['preserved_prior_branches'],
                  archived_attempt_exit_codes=[1,0],new_ODE_steps=0,new_accepted_states=0,
                  revised_policy_executed=False,book_receipts_written=False,
                  verification_source_sha256=sha(Path(__file__)))
    target = DATA/'verification.json'
    if target.exists():
        assert json.loads(target.read_text()) == report, 'Existing verification differs'
    else:
        target.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: 10 actual Lean kernel reports; warnings as errors; only propext/Classical.choice/Quot.sound')
    print('PASS: exact statements, source/claim/checker/log/equation hashes and frozen source match')
    print('PASS: 2090 baseline blobs byte-identical; failed/preliminary attempts preserved; prior branch refs unchanged')
    print('PASS: held policy, numerical results and book unchanged; zero ODE steps or accepted states')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Replay source/dependency-report bindings and immutable baseline checks."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from check_filippov_convex_weight_proofs import audit_source, audit_transcript

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'education/data/filippov-convex-weight-proofs-v1'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=json.loads((DATA/'protocol.json').read_text())
    for name,digest in {**p['source_sha256'],**p['equation_inputs_sha256']}.items():
        assert sha(ROOT/name)==digest,name
    freeze=p['source_freeze_commit']
    assert subprocess.check_output(['git','rev-parse',freeze+'^{tree}'],cwd=ROOT,text=True).strip()==p['source_freeze_tree']
    for name in p['source_sha256']:
        assert subprocess.check_output(['git','show',freeze+':'+name],cwd=ROOT)==(ROOT/name).read_bytes(),name
    source=ROOT/'education/proofs/FilippovConvexWeight.lean'
    claims_file=ROOT/'education/proofs/filippov-convex-weight-claims.json'
    checker=ROOT/'education/tools/check_filippov_convex_weight_proofs.py'
    claims=json.loads(claims_file.read_text())
    audit_source(source.read_text(),claims)
    r=json.loads((DATA/'review/kernel-check.json').read_text())
    assert r['compiler_exit_code']==0 and 'version 4.19.0,' in r['lean_version']
    assert r['source_freeze_commit']==freeze and r['source_freeze_tree']==p['source_freeze_tree']
    assert r['source_sha256']==sha(source) and r['claims_sha256']==sha(claims_file) and r['checker_sha256']==sha(checker)
    log=DATA/'review/lean-check.log'
    assert r['transcript_sha256']==sha(log)
    checked=audit_transcript(log.read_text(),claims)
    assert r['claims']==checked and len(checked)==14
    assert r['exact_statements']==re.findall(r'(?ms)^theorem\s+.*?(?=\s*:= by)',source.read_text())
    for binding in r['equation_sources']:
        assert binding['sha256']==sha(ROOT/'education'/binding['path'])
    assert r['sliding_steps_executed']==r['trajectory_states_added']==0 and not r['book_receipts_written']
    assert not p['sliding_execution_authorized'] and not p['book_adoption'] and not p['sign_convention_mismatch_found']
    attempts=json.loads((DATA/'attempts/manifest.json').read_text())
    for a in attempts['runs']:
        assert a['source_sha256']==sha(ROOT/a['source']) and a['log_sha256']==sha(ROOT/a['log'])
        assert not a['kernel_receipt_issued']
    assert [a['compiler_exit_code'] for a in attempts['runs']]==[1,1,1,0]
    count=0
    for entry in subprocess.check_output(['git','ls-tree','-rz',p['baseline_commit']],cwd=ROOT).split(b'\0'):
        if not entry:continue
        metadata,name=entry.split(b'\t',1);mode,kind,oid=metadata.decode().split()
        if kind!='blob':continue
        file=ROOT/name.decode();data=file.readlink().as_posix().encode() if mode=='120000' else file.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,name.decode()
        count+=1
    assert count==2066
    for ref,oid in p['preserved_prior_branches'].items():
        assert subprocess.check_output(['git','rev-parse',ref],cwd=ROOT,text=True).strip()==oid,ref
    manifest=DATA/'packet-manifest.json'
    if manifest.exists():
        for name,binding in json.loads(manifest.read_text())['files'].items():
            data=(ROOT/name).read_bytes()
            assert len(data)==binding['bytes'] and hashlib.sha256(data).hexdigest()==binding['sha256'],name
    print('PASS: 14 real Lean declarations; exact statements and allowed dependencies; frozen proof/claims/checker/input/log hashes; failed attempts preserved')
    print('PASS: 2066 baseline blobs; held sliding and activation branch tips; origin/main ref unchanged; ZERO sliding or trajectory advances; no book adoption')


if __name__=='__main__':main()

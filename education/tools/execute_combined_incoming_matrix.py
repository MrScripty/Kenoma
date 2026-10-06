#!/usr/bin/env python3
"""Twelve independent subprocesses on frozen exploratory source, two at a time."""
import concurrent.futures
import hashlib
import itertools
import json
import os
import subprocess
import sys
import time
from run_combined_incoming_exploratory import ROOT, DATA, OUT, protocol, verify_inputs


def main():
    verify_inputs()
    p = protocol()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip():
        raise ValueError('Freeze and commit tracked source/protocol before matrix')
    cells = list(itertools.product(p['representations'], p['methods']))
    if len(cells) != 12:
        raise ValueError('Exactly twelve cells required')
    OUT.mkdir(parents=True, exist_ok=True)
    receipt_path = OUT / 'matrix-execution.json'
    if receipt_path.exists() or any((OUT / f'mass-1-{rep}-{method}.json').exists() for rep, method in cells):
        raise ValueError('Refuse to overwrite prior combined execution')
    started = time.monotonic()
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    def run(cell):
        rep, method = cell
        command = [sys.executable, str(ROOT / 'education/tools/run_combined_incoming_exploratory.py'), '--rep', rep, '--method', method]
        log_path = OUT / f'mass-1-{rep}-{method}.log'
        with log_path.open('x') as log:
            proc = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        print(log_path.read_text().strip(), flush=True)
        return dict(representation=rep, method=method, command=command, returncode=proc.returncode,
                    log_sha256=hashlib.sha256(log_path.read_bytes()).hexdigest(),
                    result_present=(OUT / f'mass-1-{rep}-{method}.json').exists())
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(run, cells))
    receipt = dict(scope='Authorized exploratory combined incoming matrix; no full qualification',
                   source_commit=head, source_tree=subprocess.check_output(['git', 'rev-parse', head + '^{tree}'], cwd=ROOT, text=True).strip(),
                   protocol_sha256=hashlib.sha256((DATA / 'protocol.json').read_bytes()).hexdigest(),
                   historical_review_limitation=p['historical_review_limitation'], independent_raw_replay_complete=False,
                   required_cells=12, executed_cells=len(records), cell_processes=records,
                   elapsed_s=time.monotonic() - started, physical_gates_changed=False,
                   source_sha256=p['source_sha256'], accepted_sliding_states=0, qualified_trajectories=0)
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print('MATRIX', len(records), 'source', head, 'elapsed', receipt['elapsed_s'], flush=True)
    if any(c['returncode'] or not c['result_present'] for c in records):
        raise SystemExit('Retained subprocess failure: inspect all cell logs; no automatic retry')


if __name__ == '__main__':
    main()

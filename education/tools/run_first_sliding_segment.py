#!/usr/bin/env python3
"""All twelve checks precede all entry acceptance; then bounded residence."""
import hashlib
import json
import time
from first_sliding_segment_engine import DATA,ROOT,dump_new,verify_bindings
from preflight_first_sliding_segment import prepare_all


def main():
    p=verify_bindings();preflight=DATA/'preflight/entry-preflight.json'
    check=json.loads(preflight.read_text())
    if not check['passed'] or check['source_sha256']!=p['source_sha256'] or check['protocol_sha256']!=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest():
        raise ValueError('Executable preflight absent or differs from source/protocol freeze')
    engines={};started=time.monotonic()
    try:
        engines,proposals,runtime=prepare_all(True)
        dump_new(DATA/'review/runtime-entry-checks.json',runtime)
        # Validate/recompare EVERY cell before accepting ANY entry.
        for key,engine in engines.items():engine.enter(proposals[key],runtime['common_checks']['passed'])
        for key,engine in engines.items():
            engine.advance();r=engine.result()
            r.update(protocol_sha256=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest(),executed_source_sha256=p['source_sha256'])
            dest=DATA/'review'/('mass-1-'+key.replace('/','-')+'.json');dump_new(dest,r)
            print('RESULT',key,'time',engine.t,'completed',r['completed'],'sliding steps',r['sliding_steps'],'failure',engine.failure,flush=True)
        dump_new(DATA/'review/matrix-execution.json',dict(required_cells=12,executed_cells=len(engines),
            completed_cells=sum(e.failure is None and e.t==.263 for e in engines.values()),
            failure_codes={key:e.failure['code'] if e.failure else None for key,e in engines.items()},
            all_entries_checked_before_acceptance=True,runtime_entry_checks_sha256=hashlib.sha256((DATA/'review/runtime-entry-checks.json').read_bytes()).hexdigest(),
            preflight_sha256=hashlib.sha256(preflight.read_bytes()).hexdigest(),source_sha256=p['source_sha256'],
            protocol_sha256=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest(),elapsed_s=time.monotonic()-started,
            exploratory_only=True,qualified=False,full_combined_external_raw_replay_complete=False,
            historical_activation_external_raw_replay_complete=False,hidden_root_theorem=False))
    finally:
        for engine in engines.values():engine.close()


if __name__=='__main__':main()

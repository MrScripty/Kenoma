#!/usr/bin/env python3
"""Evidence integrity verification; never converts partial matrix to completion."""
import hashlib
import itertools
import json
import subprocess
import numpy as np
from first_sliding_segment_engine import ROOT,DATA,verify_bindings,STATE_GATES,WITNESSES
from analyze_first_sliding_segment import post_compare


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=verify_bindings();pf=json.loads((DATA/'preflight/entry-preflight.json').read_text())
    runtime=json.loads((DATA/'review/runtime-entry-checks.json').read_text())
    matrix=json.loads((DATA/'review/matrix-execution.json').read_text());audit=json.loads((DATA/'review/audit.json').read_text())
    summary=json.loads((DATA/'review/matched-witness-summary.json').read_text());diagnosis=json.loads((DATA/'review/constraint-stop-diagnosis.json').read_text())
    assert pf['passed'] and runtime['passed'] and pf['common_checks']['passed'] and runtime['common_checks']['passed']
    assert pf['accepted_entry_states']==pf['ODE_steps_executed']==0
    assert pf['source_sha256']==runtime['source_sha256']==matrix['source_sha256']==p['source_sha256']
    assert matrix['preflight_sha256']==sha(DATA/'preflight/entry-preflight.json')
    assert matrix['runtime_entry_checks_sha256']==sha(DATA/'review/runtime-entry-checks.json')
    assert len(pf['entries'])==12 and len(pf['common_checks']['comparisons'])==66
    for v in pf['entries'].values():
        c=v['preparation']['readonly_refined_candidate']
        assert c['iterations']<=32 and len(c['probes'])==c['iterations'] and c['bracket'][1]-c['bracket'][0]<=1e-12 and abs(c['H'])<=1e-13
        assert not c['accepted'] and v['rollback']['passed'] and v['rollback']['accepted_state_time_history_quadrature_unchanged']
        assert v['field_equivalence']['passed'] and v['field_equivalence']['Jacobian_custody_unchanged']
        assert v['handoff']['other_ten_bitwise_preserved'] and abs(v['handoff']['signed_delta_I'])<=1e-9
    results={};primary_force_max=0.;stage_counts=0
    for key in p['entry_inputs']:
        path=DATA/'review'/('mass-1-'+key.replace('/','-')+'.json');r=json.loads(path.read_text());results[key]=r
        assert audit['input_sha256'][key]==sha(path)
        assert r['executed_source_sha256']==p['source_sha256'] and not r['qualified']
        assert r['candidate']['accepted'] and r['candidate']['state']==pf['entries'][key]['preparation']['readonly_refined_candidate']['state']
        assert r['handoff']==pf['entries'][key]['handoff']
        assert r['total_accepted_steps']<=12000
        assert all(b['t']>a['t'] for a,b in zip(r['history'],r['history'][1:]))
        ten=lambda z:list(z[:4])+list(z[5:])
        assert ten(r['candidate']['state'])==ten(r['entry_state'])
        assert r['entry_state'][4]-r['candidate']['state'][4]==r['handoff']['signed_delta_I']
        if key.startswith('full-source/'):
            assert r['entry_state']==r['candidate']['state'] and r['handoff']['full_I_retained']
        else:assert not r['handoff']['exact_eleven_coordinate_continuity'] and not r['handoff']['I_bitwise_preserved']
        assert r['accepted_intervals'][0]['mode']=='incoming' and r['accepted_intervals'][0]['end']==r['candidate']['t']
        for interval in r['accepted_intervals']:
            assert interval['auxiliary_suffix_excluded'] and interval['end']<=interval['dense']['right_s']
            for row in interval['stages']+interval['guard_samples']:
                assert not row['accepted'] and row['constraint_checked'] and row['ledger_checked']
                assert abs(row['force_residual_N'])<=1e-7;primary_force_max=max(primary_force_max,abs(row['force_residual_N']))
                assert row['normal_on']>1e-8 and row['normal_off']<-1e-8 and 0<row['theta']<1
                if row['mode']=='sliding':assert abs(row['H'])<=1e-9 and row['independent_tangent_residual_per_s']<=1e-8
            stage_counts+=len(interval['stages'])
            for row in interval.get('jacobian_auxiliaries',[]):
                assert row['role']=='Jacobian-auxiliary' and not row['accepted'] and not row['constraint_checked'] and not row['ledger_checked']
        if r['failure']:
            assert r['failure']['code']=='constraint-drift' and r['failure']['rollback_exact'] and not r['completed'] and r['sliding_steps']==0
            assert r['acceptedTime']==r['candidate']['t'] and r['acceptedState']==r['entry_state']==r['failure']['acceptedState']
            assert r['independent_quadrature']['integrals']==r['entry_quad']
            assert r['history'][-1]['z']==r['acceptedState']
            assert diagnosis['records'][key]['force_and_strict_residence_domain_pass'] and diagnosis['records'][key]['constraint_exceeds_original_gate']
            assert summary['rejected_probe_formula_associations'][key]['bitwise_matches_recorded_initial_rate_formula']
        else:assert r['completed'] and r['acceptedTime']==.263 and r['sliding_steps']>0
        assert audit['runs'][key]['accepted_prefix_audit_passed']
    assert sum(r['completed'] for r in results.values())==matrix['completed_cells']==audit['completed_cells']==9
    assert len(audit['comparisons'])==len(summary['post_comparisons'])==66
    assert sum(c['passed'] for c in audit['comparisons'].values())==sum(c['passed'] for c in summary['post_comparisons'].values())==36
    for a,b in itertools.combinations(results,2):assert post_compare(results[a],results[b])==summary['post_comparisons'][a+' vs '+b]
    assert stage_counts==summary['accepted_ODE_RHS_evaluations']==630
    assert not audit['passed'] and not summary['required_matrix_passed'] and not audit['qualified']
    assert not audit['hidden_root_theorem'] and not audit['full_combined_external_raw_replay_complete'] and not audit['historical_activation_external_raw_replay_complete']
    assert diagnosis['source_sha256']==sha(ROOT/'education/tools/diagnose_first_sliding_constraint_stops.py')
    assert summary['analysis_source_sha256']==sha(ROOT/'education/tools/analyze_first_sliding_segment.py')
    count=0
    for e in subprocess.check_output(['git','ls-tree','-rz',p['baseline_commit']],cwd=ROOT).split(b'\0'):
        if not e:continue
        meta,name=e.split(b'\t',1);mode,kind,oid=meta.decode().split()
        if kind!='blob':continue
        file=ROOT/name.decode();data=file.readlink().as_posix().encode() if mode=='120000' else file.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,name.decode()
        count+=1
    assert count==2086
    preserved=json.loads((DATA/'review/baseline-preservation.json').read_text())
    for ref,oid in preserved['branch_refs'].items():assert subprocess.check_output(['git','rev-parse',ref],cwd=ROOT,text=True).strip()==oid,ref
    failed=json.loads((DATA/'attempts/manifest.json').read_text())
    for name,digest in failed['files'].items():assert sha(DATA/name)==digest
    manifest=DATA/'review/packet-manifest.json'
    if manifest.exists():
        for name,binding in json.loads(manifest.read_text())['files'].items():
            file=ROOT/name;assert sha(file)==binding['sha256'] and file.stat().st_size==binding['bytes'],name
    print('PASS evidence integrity:152 inputs; frozen6 sources;12 preflight/runtime entries;66 absolute incoming pairs;630 replayed RHS probes;2086 baseline blobs; branch preservation')
    print('EXPECTED matrix failure:9/12 endpoints;36/66 complete post-witness pairs;3 exact-rollback constraint stops; no gate changes or failure retries')
    print('Maximum directly stored primary force residual N:',primary_force_max)


if __name__=='__main__':main()

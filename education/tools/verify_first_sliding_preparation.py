#!/usr/bin/env python3
"""Check the held proposal, immutable inputs, static scalar receipt and packet."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'education/data/first-sliding-segment-protocol-v1'


def main():
    p=json.loads((DATA/'protocol.json').read_text())
    for name,digest in {**p['input_sha256'],**p['preparation_source_sha256']}.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    assert not p['proposed_protocol_review_accepted'] and not p['explicit_sliding_execution_authorized']
    assert not p['sliding_execution_source_present'] and p['sliding_steps_executed']==p['accepted_entry_states']==0
    assert not p['full_combined_external_raw_replay_complete'] and not p['historical_activation_external_raw_replay_complete']
    r=json.loads((DATA/'preflight/entry-custody.json').read_text())
    s=json.loads((DATA/'preflight/diagnostic-summary.json').read_text())
    assert r['protocol_sha256']==hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest()
    assert r['readonly_roots_resolved']==12 and set(r['records'])==set(p['entry_inputs'])
    assert r['sliding_steps_executed']==r['new_incoming_ODE_steps_executed']==r['accepted_states_added']==0
    assert not r['execution_authorized']
    rows={row['cell']:row for row in s['rows']}
    for key,v in r['records'].items():
        c=v['readonly_refined_candidate'];row=rows[key]
        raw=json.loads((ROOT/p['entry_inputs'][key]).read_text())
        assert v['input_sha256']==p['input_sha256'][p['entry_inputs'][key]]
        assert v['prior_accepted_state']==raw['history'][-1]['z']
        assert v['prior_accepted_quadrature']==raw['independent_quadrature']['integrals']
        assert not c['accepted'] and not c['state_projected']
        assert c['iterations']<=32 and c['bracket'][1]-c['bracket'][0]<=1e-12 and abs(c['H'])<=1e-13
        assert c['normal_on']>1e-8 and c['normal_off'] < -1e-8 and c['outward_error']>0 and 0<c['weight']<1
        assert v['refined_admissibility']['prospectively_admissible'] and not v['refined_admissibility']['accepted']
        I=.01-raw['cfg']['ub']+.4*c['outward_error']
        assert I==c['I_constraint'] and I-c['state'][4]==c['I_handoff_delta']==row['delta_I']
        before=.01-c['H'];after=raw['cfg']['ub']-.4*c['outward_error']+I
        assert before==row['raw_before'] and after==row['raw_after'] and after-before==row['delta_raw']
        assert abs(row['delta_I'])<=1e-9 and not row['I_bitwise_preserved']
        assert v['full_coordinate_handoff_bitwise_I_preserved'] and v['physical_and_six_ledger_coordinates_unchanged']
        assert all(e<=g for e,g in zip(v['prospective_entry_quadrature_errors'],[1e-5]*5+[1e-7]))
    assert s['max_abs_delta_I']==max(abs(row['delta_I']) for row in rows.values())
    assert s['max_abs_delta_raw']==max(abs(row['delta_raw']) for row in rows.values())
    assert s['root_time_span_s']==max(row['entry_time_s'] for row in rows.values())-min(row['entry_time_s'] for row in rows.values())
    count=0
    for entry in subprocess.check_output(['git','ls-tree','-rz',p['incoming_commit']],cwd=ROOT).split(b'\0'):
        if not entry:continue
        metadata,name=entry.split(b'\t',1);mode,kind,oid=metadata.decode().split()
        if kind!='blob':continue
        file=ROOT/name.decode();data=file.readlink().as_posix().encode() if mode=='120000' else file.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,name.decode()
        count+=1
    assert count==2066
    for branch,sha in [('education/combined-incoming-exploratory',p['incoming_commit']),('education/activation-equality-proofs',p['lean_branch_preserved'])]:
        assert subprocess.check_output(['git','rev-parse',branch],cwd=ROOT,text=True).strip()==sha
    manifest=DATA/'preflight/packet-manifest.json'
    if manifest.exists():
        for name,binding in json.loads(manifest.read_text())['files'].items():
            data=(ROOT/name).read_bytes()
            assert len(data)==binding['bytes'] and hashlib.sha256(data).hexdigest()==binding['sha256'],name
    print('PASS: 132 input bindings; source freeze; 12 unaccepted static roots; original gates and scalar handoffs; 2066 baseline blobs; preserved branch tips; ZERO ODE/sliding/accepted advances')
    print('HELD: protocol review and explicit sliding authorization absent; both external raw replay gaps retained')


if __name__=='__main__':main()

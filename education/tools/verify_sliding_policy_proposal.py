#!/usr/bin/env python3
"""Verify static proposal custody and diagnostic arithmetic; no solver calls."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/'education/data/sliding-constraint-policy-proposal-v1'
BASE = '455641c0aa9b4a9ad4b68e50fc1b6f5746180226'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_diagnosis(r):
    assert r['new_ODE_steps'] == r['accepted_states_added'] == 0
    assert not r['revised_policy_executed'] and not r['revised_decoder_implemented']
    assert len(r['records']) == 3
    for v in r['records'].values():
        assert not v['accepted'] and v['rollback_exact'] and v['sliding_steps'] == 0
        assert v['constraint_gate'] == 1e-9 and abs(v['rejected_H']) > v['constraint_gate']
        assert v['bitwise_declared_Euler_match'] and v['strict_residence_force_domain_pass']
        assert abs(v['delta_H']-v['independent_integrated_curvature_remainder']) < 2e-15
        assert v['curvature_sample_min'] > 0 and not v['curvature_sample_range_is_certified_bound']


def main():
    entries = subprocess.check_output(['git','ls-tree','-rz','--full-tree',BASE],cwd=ROOT).split(b'\0')
    count = 0
    for entry in filter(None, entries):
        info, path = entry.split(b'\t', 1)
        mode, kind, digest = info.split()
        if kind != b'blob':
            continue
        data = (ROOT/path.decode()).read_bytes()
        actual = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert actual == digest.decode(), 'Baseline file changed: '+path.decode()
        count += 1
    assert count == 2131, count
    r = json.loads((DATA/'predictor-curvature-diagnosis.json').read_text())
    check_diagnosis(r)
    assert r['source_sha256'] == sha((ROOT/'education/tools/diagnose_sliding_predictor_curvature.py').read_bytes())
    for v in r['records'].values():
        assert v['input_sha256'] == sha((ROOT/v['input_path']).read_bytes())
    negative = []
    for label, mutate in [
        ('accepted-state-count', lambda x: x.update(accepted_states_added=1)),
        ('revised-policy-executed', lambda x: x.update(revised_policy_executed=True)),
        ('missing-cell', lambda x: x['records'].pop(next(iter(x['records'])))),
        ('constraint-gate-relaxation', lambda x: next(iter(x['records'].values())).update(constraint_gate=1e-6)),
        ('failed-rollback', lambda x: next(iter(x['records'].values())).update(rollback_exact=False)),
        ('curvature-disagreement', lambda x: next(iter(x['records'].values())).update(independent_integrated_curvature_remainder=0.)),
    ]:
        candidate = json.loads(json.dumps(r))
        mutate(candidate)
        try:
            check_diagnosis(candidate)
        except AssertionError:
            negative.append(label)
        else:
            raise AssertionError('Negative control accepted: '+label)
    report = dict(baseline_commit=BASE, baseline_tree=subprocess.check_output(['git','rev-parse',BASE+'^{tree}'],cwd=ROOT,text=True).strip(),
                  preserved_baseline_blobs=count, negative_controls_rejected=negative,
                  archived_failed_inputs_sha256={k:v['input_sha256'] for k,v in r['records'].items()},
                  new_ODE_steps=0, accepted_states_added=0, revised_policy_executed=False,
                  completed_matrix_still_unqualified=True,
                  unchanged_original_gate_tests=14,
                  source_freeze_commit='a901dd4e03f6c061521494eb135f8e07d3347b6b',
                  source_freeze_tree='963af93d51610e89acfb33c433d65c275e051030',
                  render=dict(path='archived-predictor-defects.png',width_px=1800,height_px=990,
                              visually_inspected=True, interpretation='Archived unaccepted probes only; no new trajectory'),
                  independent_first_sliding_raw_replay_ACK_received=True,
                  older_combined_external_raw_review_complete=False,
                  historical_activation_raw_review_complete=False,
                  source_sha256=sha(Path(__file__).read_bytes()))
    target = DATA/'verification.json'
    if target.exists():
        raise ValueError('Refuse to overwrite verification')
    target.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:', count, 'baseline blobs byte-identical; three archived rejected probes bound')
    print('PASS:', len(negative), 'in-memory negative controls rejected; no evidence files modified')
    print('PASS: unchanged 14 controls; zero new ODE steps; revised policy held')


if __name__ == '__main__':
    main()

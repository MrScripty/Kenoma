#!/usr/bin/env python3
"""Read-only held-incoming custody/entry diagnosis. No ODE or sliding step."""
import hashlib
import json
from pathlib import Path
import numpy as np
from run_filippov_bounded_experiment import ROOT, Source, Failure, NODES, WEIGHTS
from run_ordinary_crossing_consistency import replay_dense
from vertical_force_reference import output as reference_output, C, P

DATA = ROOT / 'education/data/first-sliding-segment-protocol-v1'


def admissibility(c):
    issues = []
    if not all(np.isfinite(c[key]) for key in ['normal_on','normal_off','outward_error','weight','H','I_handoff_delta']):
        issues.append('nonfinite-entry-diagnostic')
    for key in ['physical_valid', 'incoming_order_valid', 'deactivation_side_valid']:
        if not c.get(key, False):
            issues.append(key)
    if c['normal_on'] <= 1e-8 or c['normal_off'] >= -1e-8:
        issues.append('strict-attraction-loss')
    if c['outward_error'] <= 0:
        issues.append('zero-or-inward-error')
    if not 0 < c['weight'] < 1:
        issues.append('nonconvex-weight')
    if abs(c['H']) > 1e-9 or abs(c['I_handoff_delta']) > 1e-9:
        issues.append('original-entry-coordinate-gate')
    return dict(prospectively_admissible=not issues, issues=issues, accepted=False)


def bitwise_I_preserved(delta):
    """Return a JSON-native boolean for binary64 coordinate custody."""
    return bool(delta == 0)


def review_allows_execution(p):
    return all(p.get(key, False) for key in ['combined_result_review_accepted',
                                           'proposed_protocol_review_accepted',
                                           'explicit_sliding_execution_authorized'])


def evaluate_incoming(z, cfg, source):
    # Explicitly false: this adapter is never asked to evaluate sliding here.
    if source:
        o = source.evaluate(z, cfg, cfg['target'], False, .01)
    else:
        o = reference_output(z, cfg, {'target': cfg['target']})
        o['kt'] = 500 * C['tendon'].value(o['s'], True)
    d = .4 * o['kt'] * (z[1] + o['v']) / 100
    k = 8 * o['e']
    return dict(**o, H=.01 - o['uraw'], normal_on=-(d+k), normal_off=-d,
                d=d, k=k, weight=-d/k if k else float('nan'))


def relocalize(aux, cfg, source):
    """One fresh 32-budget solve on the original incoming trial polynomial.

Not a continuation of the coarse bisection and not an accepted entry. It never
creates stages, trajectories, a mixed field, or new dense coefficients.
"""
    lo, hi = aux['start'], aux['trialEnd']
    records = []
    if not evaluate_incoming(replay_dense(aux['dense'], lo), cfg, source)['H'] < 0 <= evaluate_incoming(replay_dense(aux['dense'], hi), cfg, source)['H']:
        return dict(failure='original-incoming-bracket', accepted=False, probes=records)
    for iteration in range(32):
        t = (lo + hi) / 2
        z = replay_dense(aux['dense'], t)
        o = evaluate_incoming(z, cfg, source)
        records.append(dict(t=t, z=z.tolist(), H=o['H'], force_residual_N=o['residual'], accepted=False))
        if -o['e'] <= 0 or o['normal_on'] <= 1e-8 or o['normal_off'] >= -1e-8:
            return dict(failure='strict-entry-assumption', accepted=False, probes=records)
        if o['H'] < 0:
            lo = t
        else:
            hi = t
        if hi - lo <= 1e-12 and abs(o['H']) <= 1e-13:
            return dict(t=t, state=z.tolist(), H=o['H'], bracket=[lo, hi], iterations=iteration+1,
                        original_trial=dict(start=aux['start'], end=aux['trialEnd']),
                        physical_valid=True, normal_on=o['normal_on'], normal_off=o['normal_off'],
                        outward_error=-o['e'], weight=o['weight'], g_bound=.01-z[2],
                        I_constraint=.01-cfg['ub']-.4*o['e'],
                        I_handoff_delta=(.01-cfg['ub']-.4*o['e'])-z[4],
                        source_force_residual_N=o['residual'], probes=records,
                        accepted=False, state_projected=False, new_sliding_steps=0)
    return dict(failure='unchanged-32-budget-exhausted', bracket=[lo, hi], probes=records, accepted=False)


def custody(path, p):
    r = json.loads(path.read_text())
    if r['failure'] or r['candidate']['accepted'] or r['qualified']:
        raise ValueError('Incoming record is not a held unqualified candidate')
    if [e['type'] for e in r['events']] != ['activation-equality', 'ordinary-outward', 'ordinary-inward']:
        raise ValueError('Original incoming event order differs')
    aux = r['combined_arbitrations'][-1]
    if aux['decision']['decision'] != 'hold' or aux['start'] != r['acceptedTime'] or aux['pending_remainder_end'] is not None:
        raise ValueError('Held incoming custody/remainder differs')
    if aux['incoming_controller_mode'] != 'integrating' or aux['incoming_activation_branch'] != 'deactivation':
        raise ValueError('Incoming branch differs')
    if len(aux['events']) != 1 or aux['events'][0]['kind'] != 'attracting':
        raise ValueError('Unresolved competing event in held trial')
    if any(sample['g'] >= -1e-13 for sample in aux['guard_samples']):
        raise ValueError('Stored trial has activation-side ambiguity')
    if aux['startState'] != r['history'][-1]['z'] or aux['dense']['y_old'] != aux['startState']:
        raise ValueError('Exact old accepted-state custody differs')
    source = Source() if r['representation'] == 'full-source' else None
    try:
        coarse = r['candidate']
        zc = np.array(coarse['x'])
        oc = evaluate_incoming(zc, r['cfg'], source)
        refined = relocalize(aux, r['cfg'], source)
        if 'failure' in refined:
            return dict(path=str(path.relative_to(ROOT)), refined=refined, sliding_steps_executed=0)
        refined.update(incoming_order_valid=True, deactivation_side_valid=refined['g_bound'] < -1e-13)
        checks = admissibility(refined)
        increment = np.zeros(6)
        left, right = r['acceptedTime'], refined['t']
        for node, weight in zip(NODES, WEIGHTS):
            t = left + (right-left)*(node+1)/2
            z = replay_dense(aux['dense'], t)
            o = reference_output(z, r['cfg'], {'target': r['cfg']['target']})
            if .01 - o['uraw'] > 1e-9:
                raise ValueError('Incoming-prefix GL8 point exceeds original H gate')
            increment += (right-left)*weight/2*np.array([o['Pactive'],o['D'],o['loadPower'],o['fiberPower'],o['tendonPower'],o['FT']-r['cfg']['m']*P['gravity_m_per_s2']])
        quadrature = np.array(r['independent_quadrature']['integrals']) + increment
        error = np.abs(quadrature-np.array(refined['state'][5:11]))
        if np.any(error > np.array([1e-5]*5+[1e-7])):
            raise ValueError('Read-only prospective prefix quadrature fails original gates')
        return dict(path=str(path.relative_to(ROOT)), input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    case=r['case'], representation=r['representation'], method=r['method'],
                    cfg_sha256=hashlib.sha256(json.dumps(r['cfg'],sort_keys=True).encode()).hexdigest(),
                    prior_accepted_time=r['acceptedTime'], prior_accepted_state=aux['startState'],
                    prior_accepted_quadrature=r['independent_quadrature']['integrals'],
                    original_dense_sha256=hashlib.sha256(json.dumps(aux['dense'],sort_keys=True).encode()).hexdigest(),
                    original_coarse_candidate=dict(time=coarse['t'],state=coarse['x'],H=coarse['H'],
                                                   I_handoff_delta=(.01-r['cfg']['ub']-.4*oc['e'])-zc[4], accepted=False),
                    readonly_refined_candidate=refined, refined_admissibility=checks,
                    coarse_to_refined_time_shift_s=refined['t']-coarse['t'],
                    prospective_entry_GL8_increment=increment.tolist(),
                    prospective_entry_quadrature=quadrature.tolist(),
                    prospective_entry_quadrature_errors=error.tolist(),
                    full_coordinate_handoff_bitwise_I_preserved=True,
                    reduced_coordinate_handoff_bitwise_I_preserved=bitwise_I_preserved(refined['I_handoff_delta']),
                    physical_and_six_ledger_coordinates_unchanged=True,
                    sliding_steps_executed=0, accepted_states_added=0)
    finally:
        if source:
            source.close()


def main():
    p = json.loads((DATA/'protocol.json').read_text())
    if review_allows_execution(p):
        raise ValueError('Preparation packet must remain held, not authorize execution')
    for path,digest in {**p['input_sha256'],**p['preparation_source_sha256']}.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:
            raise ValueError('Frozen preparation input changed: '+path)
    records = {}
    for key,path in p['entry_inputs'].items():
        records[key]=custody(ROOT/path,p)
        c=records[key].get('readonly_refined_candidate')
        print('STATIC INCOMING',key,'target',c['t'] if c else None,'iterations',c['iterations'] if c else None,'I coordinate delta',c['I_handoff_delta'] if c else None,flush=True)
    resolved=[r['readonly_refined_candidate'] for r in records.values() if 'readonly_refined_candidate' in r]
    old=[r['original_coarse_candidate']['H'] for r in records.values() if 'original_coarse_candidate' in r]
    payload=dict(scope='Read-only stored incoming polynomial diagnosis; no sliding or accepted state/time advancement',
                 input_commit=p['incoming_commit'],protocol_sha256=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest(),
                 records=records,readonly_roots_resolved=len(resolved),
                 old_H_residual_span=max(old)-min(old) if old else None,
                 refined_H_residual_span=max(c['H'] for c in resolved)-min(c['H'] for c in resolved) if resolved else None,
                 max_refined_I_handoff_delta=max(abs(c['I_handoff_delta']) for c in resolved) if resolved else None,
                 max_original_budget_iterations=max(c['iterations'] for c in resolved) if resolved else None,
                 sliding_steps_executed=0,new_incoming_ODE_steps_executed=0,accepted_states_added=0,
                 execution_authorized=False,independent_historical_raw_review_complete=False,
                 readonly_refinement_is_not_incoming_trajectory_qualification=True)
    out=DATA/'preflight'/'entry-custody.json'
    if out.exists():
        raise ValueError('Refuse to overwrite preparation diagnosis')
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(payload,indent=2)+'\n')
    print('H span coarse/refined',payload['old_H_residual_span'],payload['refined_H_residual_span'],'max I handoff',payload['max_refined_I_handoff_delta'],'ZERO sliding steps',flush=True)


if __name__=='__main__':
    main()

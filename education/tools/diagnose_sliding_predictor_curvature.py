#!/usr/bin/env python3
"""Static diagnosis of three archived Euler probes; never advance an ODE."""
import hashlib
import inspect
import json
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.integrate._ivp.common import select_initial_step
from scipy.optimize import brentq
from first_sliding_segment_engine import Source, native_field, independent_field, verify_bindings
from vertical_force_reference import C

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'education/data/first-sliding-segment-exploratory-v1/review'
OUT = ROOT / 'education/data/sliding-constraint-policy-proposal-v1'


def curvature(s):
    """Analytic second x derivative of the unchanged parametric tendon BPoly."""
    curve = C['tendon']
    j = next(i for i, p in enumerate(curve.controls) if s <= p[0][-1])
    b = curve.polys[j]
    u = brentq(lambda u: float(b(u)[0])-s, 0, 1, xtol=5e-15, rtol=1e-15)
    dx, dy = b.derivative()(u)
    ddx, ddy = b.derivative(2)(u)
    return float((ddy*dx-dy*ddx)/dx**3), j


def diagnose(key, source):
    path = BASE / ('mass-1-'+key.replace('/', '-')+'.json')
    r = json.loads(path.read_text())
    z0, z1 = np.array(r['entry_state']), np.array(r['failure']['failedStageState'])
    o0, rate = native_field(z0, r['cfg'], source, True)
    o1, _ = native_field(z1, r['cfg'], source, True)
    ref, _ = independent_field(z1, r['cfg'], True)
    rk = r['method'].startswith('RK4')
    tau = float(r['method'].split('-')[1])/2 if rk else r['failure']['failedStageTime']-r['candidate']['t']
    assert np.array_equal(z0+tau*rate, z1), 'Archived vector is not declared Euler predictor'
    assert r['sliding_steps'] == 0 and r['acceptedTime'] == r['candidate']['t']
    assert r['failure']['rollback_exact'] and np.array_equal(r['acceptedState'], z0)
    assert r['failure']['code'] == 'constraint-drift' and abs(o1['H']) > 1e-9
    s0, s1 = o0['s'], o1['s']
    samples = [curvature(s) for s in np.linspace(s0, s1, 65)]
    assert len({j for _, j in samples}) == 1, 'Taylor interval crosses patch boundary'
    remainder, quadrature_error = quad(lambda s: (s1-s)*curvature(s)[0], s0, s1,
                                      epsabs=1e-16, epsrel=1e-11)
    # eta=-1: Delta H = -.4 Delta e - Delta I. Substitute declared Euler I increment.
    measured = o1['H']-o0['H']
    affine_e_prediction = -.4*(o1['e']-o0['e'])+tau*o0['d']
    independent_remainder = .4*remainder
    leading = .2*curvature(s0)[0]*(s1-s0)**2
    rounding = measured-affine_e_prediction
    assert abs(rounding) < 1e-15 and abs(measured-independent_remainder) < 2e-15
    assert abs(o1['residual']) <= 1e-7 and o1['normal_on'] > 1e-8 and o1['normal_off'] < -1e-8
    assert o1['e'] < 0 and 0 < o1['theta'] < 1 and o1['g'] < -1e-13
    return dict(input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                input_path=str(path.relative_to(ROOT)),
                role='RK4 first midpoint Euler predictor' if rk else 'adaptive constructor initial-step Euler RHS probe',
                accepted_entry_time_s=r['acceptedTime'], unaccepted_probe_time_s=r['failure']['failedStageTime'],
                declared_predictor_offset_s=tau, floating_time_subtraction_s=r['failure']['failedStageTime']-r['candidate']['t'],
                bitwise_declared_Euler_match=True, sliding_steps=0, rollback_exact=True,
                entry_H=o0['H'], rejected_H=o1['H'], independent_rejected_H=ref['H'],
                delta_H=measured, constraint_gate=1e-9, gate_multiple=abs(o1['H'])/1e-9,
                s_entry=s0, s_probe=s1, delta_s=s1-s0,
                affine_s_prediction_error=(s1-s0)+tau*(z0[1]+o0['v'])/.2,
                tendon_patch=samples[0][1], curvature_sample_min=min(x for x,_ in samples),
                curvature_sample_max=max(x for x,_ in samples), curvature_samples=65,
                curvature_sample_range_is_certified_bound=False,
                native_affine_e_remainder=affine_e_prediction, floating_arithmetic_difference=rounding,
                independent_integrated_curvature_remainder=independent_remainder,
                curvature_quadrature_error_estimate=.4*quadrature_error,
                measured_minus_independent_remainder=measured-independent_remainder,
                entry_curvature_quadratic_term=leading,
                relative_quadratic_remainder_difference=(measured-leading)/measured,
                native_force_residual_N=o1['residual'], independent_force_residual_N=ref['residual'],
                normal_on=o1['normal_on'], normal_off=o1['normal_off'], theta=o1['theta'],
                strict_residence_force_domain_pass=True, accepted=False)


def main():
    verify_bindings()
    keys = ['full-source/RK4-0.0002', 'full-source/DOP853', 'full-source/Radau']
    source = Source()
    try:
        records = {key: diagnose(key, source) for key in keys}
    finally:
        source.close()
    result = dict(scope='Read-only archived rejected-state evaluation; no proposed policy implementation',
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scipy_version=scipy.__version__,
                  select_initial_step_source_sha256=hashlib.sha256(inspect.getsource(select_initial_step).encode()).hexdigest(),
                  records=records, new_ODE_steps=0, accepted_states_added=0,
                  revised_policy_executed=False, revised_decoder_implemented=False)
    path = OUT / 'predictor-curvature-diagnosis.json'
    if path.exists():
        raise ValueError('Refuse to overwrite diagnosis evidence')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    for key, record in records.items():
        print(key, 'H=', record['rejected_H'], 'curvature remainder=',
              record['independent_integrated_curvature_remainder'], 'rollback exact', flush=True)
    print('PASS: three archived predictors; zero new ODE steps; zero new accepted states')


if __name__ == '__main__':
    main()

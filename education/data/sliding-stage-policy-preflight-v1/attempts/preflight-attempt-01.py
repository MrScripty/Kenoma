#!/usr/bin/env python3
"""Structural checks on archived/static probes; zero ODE solver steps or acceptance."""
import ast
import copy
import hashlib
import inspect
import json
import textwrap
import weakref
import numpy as np
import scipy
from scipy.integrate import DOP853, Radau
from scipy.integrate._ivp.rk import RungeKutta
from scipy.integrate._ivp.radau import Radau as RadauImplementation
from scipy.integrate._ivp.common import norm
from first_sliding_segment_engine import (ROOT, DATA as ORIGINAL, SegmentEngine, Failure,
    dump_new, native_field, independent_field, STATE_GATES, BALANCE_GATES, QUAD_GATES, WITNESSES)
from preflight_first_sliding_segment import prepare_all
from sliding_stage_policy_engine import StagePolicyEngine, DATA, internal_constraint_auxiliary


def expected_failure(engine, t, x, role, mode=None, constraint=True, code=None):
    before = engine.fingerprint()
    bits = x.copy()
    try:
        engine.evaluate(t, x, role, mode, constraint)
    except Failure as error:
        if code:
            assert error.code == code, (role, error.code, code)
        assert engine.fingerprint() == before and np.array_equal(x, bits)
        return copy.deepcopy(engine.probes[-1])
    raise AssertionError('Invalid probe admitted as '+role)


def static_fixture(key, engine):
    raw = json.loads((ORIGINAL/'review'/('mass-1-'+key.replace('/', '-')+'.json')).read_text())
    z = np.array(raw['entry_state'])
    engine.mode = 'sliding'
    engine.t = raw['candidate']['t']
    engine.x = z.copy() if engine.rep == 'full-source' else np.r_[z[:4], z[5:]]
    engine.entry_state = z.copy()
    engine.entry_quad = np.array(raw['entry_quad'])
    engine.quad = engine.entry_quad.copy()
    engine.history = copy.deepcopy([r for r in raw['history'] if r['t'] <= engine.t])
    engine.events = copy.deepcopy([r for r in raw['events'] if r['t'] <= engine.t])
    engine.intervals = copy.deepcopy([r for r in raw['accepted_intervals'] if r['end'] <= engine.t])
    engine.accepted_steps = len(engine.intervals)
    engine.failure = None
    return raw


def archived_roles(key, engine):
    raw = static_fixture(key, engine)
    x = np.array(raw['failure']['failedStageState'])
    t = raw['failure']['failedStageTime']
    fingerprint = engine.fingerprint()
    z, o, rate, diag = engine.evaluate(t, x, 'ODE-stage')
    original, original_rate = native_field(x, engine.cfg, engine.source, True)
    assert np.array_equal(z, x) and np.array_equal(rate, original_rate)
    assert diag['internal_constraint_auxiliary'] and not diag['constraint_checked']
    assert diag['ledger_checked'] and diag['H_would_fail'] and diag['independent_H_would_fail']
    assert diag['H'] == original['H'] and abs(diag['H']) > 1e-9
    # Timestamp plays no role: the same coordinates pass the same auxiliary role at entry time.
    _, _, same_rate, same_diag = engine.evaluate(engine.t, x, 'ODE-stage')
    assert np.array_equal(same_rate, rate) and same_diag['H'] == diag['H']
    rejected = {role:expected_failure(engine,t,x,role,code='constraint-drift') for role in
                ['trial-endpoint','dense-guard','GL8','history-witness','diagnostic','unknown-role']}
    rejected['incoming-ODE-stage'] = expected_failure(engine,t,x,'ODE-stage','incoming',code='incoming-prefix-side')
    rejected['caller-bypass'] = expected_failure(engine,t,x,'diagnostic',constraint=False,code='policy-role')
    assert engine.fingerprint() == fingerprint
    return dict(input_sha256=hashlib.sha256((ORIGINAL/'review'/('mass-1-'+key.replace('/', '-')+'.json')).read_bytes()).hexdigest(),
                auxiliary=diag, same_coordinates_at_entry_time=same_diag,
                accepted_roles_rejected=rejected, input_bits_unchanged=True, full_rate_bitwise_unchanged=True,
                accepted_custody_unchanged=True, timestamp_not_used_for_classification=True)


class CacheMarker:
    pass


def transaction_failure(key, engine, kind):
    raw = static_fixture(key, engine)
    fingerprint = engine.fingerprint()
    engine._solver_cache = CacheMarker()
    cache = weakref.ref(engine._solver_cache)
    old = engine.x.copy()
    rejected = np.array(raw['failure']['failedStageState'])
    valid_calls = []
    def producer(before, x):
        valid_calls.append(engine.rhs(before,x))
        # Valid under the reviewed auxiliary policy despite its recorded H defect.
        valid_calls.append(engine.rhs(raw['failure']['failedStageTime'],rejected))
        if kind in ['physical-domain','activation-bound','strict-sign','work-ledger']:
            bad = x.copy()
            if kind == 'physical-domain':bad[3] = .4
            if kind == 'activation-bound':bad[2] = .01
            if kind == 'strict-sign':bad[1] += .02
            if kind == 'work-ledger':bad[5] += 1e-4
            engine.rhs(before+1e-6,bad)
            raise AssertionError('Physical/ledger negative control did not fail')
        if kind in ['endpoint-role','GL8-role']:
            role = 'trial-endpoint' if kind == 'endpoint-role' else 'GL8'
            engine.evaluate(raw['failure']['failedStageTime'],rejected,role)
            raise AssertionError('Accepted role negative control did not fail')
        stop = .2623
        target = (before+stop)/2 if kind == 'dense-guard' else .26225
        def dense(t):
            return rejected.copy() if t == target else x.copy()
        # Static failure injector, not an ODE-generated polynomial or trajectory.
        return stop, x.copy(), dense, dict(kind='static-negative-control',target_time=target)
    accepted = engine._attempt_trial(producer)
    assert not accepted and len(valid_calls) == 2
    assert engine.fingerprint() == fingerprint and np.array_equal(engine.x,old)
    assert engine._solver_cache is None and cache() is None
    assert engine.failure['rollback_exact'] and engine.failure['solver_cache_discarded']
    codes = {'physical-domain':'fiber-bound','activation-bound':'activation-bound',
             'strict-sign':'strict-sign-loss','work-ledger':'work-impulse-gate',
             'endpoint-role':'constraint-drift','GL8-role':'constraint-drift',
             'dense-guard':'constraint-drift','history-witness':'constraint-drift'}
    # Native source uses its own bound error name; preserve rather than relabel it.
    if kind != 'physical-domain':assert engine.failure['code'] == codes[kind], engine.failure
    if kind == 'physical-domain':assert 'fiber' in engine.failure['code'], engine.failure
    called = []
    try:
        engine._attempt_trial(lambda *args:called.append(True))
    except Failure as error:
        assert error.code == 'terminal-cell'
    else:raise AssertionError('Terminal failed cell could retry')
    assert not called and engine.fingerprint() == fingerprint
    return dict(kind=kind,valid_auxiliary_stages=2,failed_trial=copy.deepcopy(engine.failure),
                probe_records=copy.deepcopy(engine.probes[-2:]),
                exact_state_time_history_events_quadrature_count_rollback=True,
                solver_cache_object_released=True, retry_producer_not_called=True,
                ODE_solver_steps=0, accepted_states_added=0)


def integration_structure(engines):
    def cls_call(method):
        tree = ast.parse(textwrap.dedent(inspect.getsource(method)))
        return next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id == 'cls')
    old_call,new_call = cls_call(SegmentEngine.advance),cls_call(StagePolicyEngine._candidate)
    assert [ast.dump(k) for k in old_call.keywords] == [ast.dump(k) for k in new_call.keywords]
    assert inspect.signature(DOP853).parameters['first_step'].default is None
    assert inspect.signature(Radau).parameters['first_step'].default is None
    for name in ['decode','rhs','jac','prepare_entry','prepare_interval','row','commit','fingerprint']:
        assert getattr(StagePolicyEngine,name) is getattr(SegmentEngine,name), name
    norms = {}
    for key,engine in engines.items():
        static_fixture(key,engine)
        n = 11 if engine.rep == 'full-source' else 10
        assert len(engine.x) == n
        scale = 1e-11+np.maximum(abs(engine.x),abs(engine.x))*1e-9
        result = []
        for j in range(n):
            error = np.zeros(n);error[j] = scale[j]
            class Estimator:
                def _estimate_error(self,K,h):return error
            rk = RungeKutta._estimate_error_norm(Estimator(),None,1.,scale)
            radau = norm(error/scale)
            assert rk == radau and rk > 0 and abs(rk-1/np.sqrt(n)) < 1e-15
            result.append(float(rk))
        norms[key] = dict(dimension=n,every_integrated_component_contributes=True,
            single_component_error_norm=result,full_I_in_norm=engine.rep == 'full-source',
            all_six_ledgers_in_norm=True,reduced_I_decoding_unchanged=engine.rep == 'reduced-independent')
    return dict(original_constructor_keywords_identical=True,first_step_default_None=True,
                inherited_methods_unchanged=['decode','rhs','jac','prepare_entry','prepare_interval','row','commit','fingerprint'],
                norms=norms, scipy_version=scipy.__version__,
                RK_error_norm_source_sha256=hashlib.sha256(inspect.getsource(RungeKutta._estimate_error_norm).encode()).hexdigest(),
                Radau_step_source_sha256=hashlib.sha256(inspect.getsource(RadauImplementation._step_impl).encode()).hexdigest(),
                actual_ODE_solver_constructors_called=0,actual_ODE_solver_steps=0)


def main():
    original,proposals,entry_receipt = prepare_all()
    engines = {}
    try:
        for key,old in original.items():
            incoming = json.loads((ROOT/old.prepared['path']).read_text())
            engine = StagePolicyEngine(incoming,old.prepared,old.source)
            engines[key] = engine
            assert engine.prepare_entry()['handoff'] == proposals[key]['handoff']
        roles = {key:archived_roles(key,engines[key]) for key in
                 ['full-source/RK4-0.0002','full-source/DOP853','full-source/Radau']}
        rollback = [transaction_failure('full-source/RK4-0.0002',engines['full-source/RK4-0.0002'],kind)
                    for kind in ['physical-domain','activation-bound','strict-sign','work-ledger',
                                 'endpoint-role','GL8-role','dense-guard','history-witness']]
        structure = integration_structure(engines)
        predicate = {(rep,mode,role):internal_constraint_auxiliary(rep,mode,role)
                     for rep in ['full-source','reduced-independent'] for mode in ['incoming','sliding']
                     for role in ['ODE-stage','trial-endpoint','dense-guard','GL8','history-witness','Jacobian-auxiliary','diagnostic']}
        assert sum(predicate.values()) == 1 and predicate[('full-source','sliding','ODE-stage')]
        for engine in engines.values():
            fingerprint = engine.fingerprint()
            try:engine.advance()
            except Failure as error:assert error.code == 'execution-held'
            else:raise AssertionError('Held matrix execution was allowed')
            assert engine.fingerprint() == fingerprint
        dump_new(DATA/'entry-preflight.json',entry_receipt)
        dump_new(DATA/'structural-preflight.json',dict(passed=True,archived_predictor_roles=roles,
            transactional_failures=rollback,integration_structure=structure,role_mode_predicate_cases=len(predicate),
            only_native_full_sliding_ODE_stage_exempt=True,required_cells=len(engines),required_witnesses=WITNESSES,
            state_gates=STATE_GATES.tolist(),balance_gates=BALANCE_GATES.tolist(),quadrature_gates=QUAD_GATES.tolist(),
            fresh_entries_unaccepted=12,pre_entry_pair_comparisons=66,new_ODE_steps=0,new_accepted_states=0,
            revised_matrix_executed=False,structural_policy_evaluator_tested=True,
            source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest()))
        print('PASS: three archived predictors; identical-coordinate accepted-role and incoming-mode rejection')
        print('PASS: eight later failures after valid auxiliary stages; exact rollback and cache release; no retries')
        print('PASS: exact full11/reduced10 constructor/scaling/component norms; inherited decoder/Jacobian/accepted checks unchanged')
        print('PASS: fresh 12 own roots and 66 incoming comparisons; zero accepted entries/ODE steps; new matrix held')
    finally:
        for engine in original.values():engine.close()


if __name__ == '__main__':main()

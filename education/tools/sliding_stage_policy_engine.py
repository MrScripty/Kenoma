#!/usr/bin/env python3
"""Reviewed stage-policy implementation; matrix execution remains explicitly held."""
import copy
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.integrate import DOP853, Radau
from first_sliding_segment_engine import (SegmentEngine, Failure, ROOT, END,
    native_field, independent_field, validate_diagnostics, balance_errors,
    check_balances, dense_record, replay_dense)

DATA = ROOT/'education/data/sliding-stage-policy-preflight-v1'
CONSTRAINT_GATE = 1e-9


def internal_constraint_auxiliary(rep, mode, role):
    return rep == 'full-source' and mode == 'sliding' and role == 'ODE-stage'


class StagePolicyEngine(SegmentEngine):
    def __init__(self, incoming, prepared, source=None):
        super().__init__(incoming, prepared, source)
        self._solver_cache = None

    def evaluate(self, t, x, role='diagnostic', mode=None, constraint=True):
        mode = mode or self.mode
        z = self.decode(x, mode)
        sliding = mode == 'sliding'
        auxiliary = internal_constraint_auxiliary(self.rep, mode, role)
        checked = constraint and not auxiliary
        record = dict(t=float(t), x=np.array(x).tolist(), z=z.tolist(), role=role,
                      mode=mode, accepted=False, constraint_checked=checked,
                      internal_constraint_auxiliary=auxiliary, constraint_gate=CONSTRAINT_GATE,
                      H=None, independent_H=None, H_would_fail=None,
                      independent_H_would_fail=None, ledger_checked=role != 'Jacobian-auxiliary')
        try:
            if not constraint and role != 'Jacobian-auxiliary':
                raise Failure('policy-role', 'Constraint bypass requires the existing Jacobian auxiliary role')
            if hashlib.sha256(json.dumps(self.cfg, sort_keys=True).encode()).hexdigest() != self.cfg_hash:
                raise Failure('configuration-change', 'Undeclared configuration/command change')
            o, rate = native_field(z, self.cfg, self.source, sliding) if self.source else independent_field(z, self.cfg, sliding)
            record.update(H=o['H'], H_would_fail=bool(not np.isfinite(o['H']) or abs(o['H']) > CONSTRAINT_GATE),
                          normal_on=o['normal_on'], normal_off=o['normal_off'], theta=o['theta'],
                          g=o['g'], force_residual_N=o['residual'])
            validate_diagnostics(z, o, sliding, checked)
            ref, ref_rate = independent_field(z, self.cfg, sliding)
            record.update(independent_H=ref['H'],
                          independent_H_would_fail=bool(not np.isfinite(ref['H']) or abs(ref['H']) > CONSTRAINT_GATE),
                          independent_force_residual_N=ref['residual'])
            validate_diagnostics(z, ref, sliding, checked)
            if abs(o['FT']-ref['FT']) > 1e-7 or max(abs(o['normal_on']-ref['normal_on']), abs(o['normal_off']-ref['normal_off'])) > 1e-8:
                raise Failure('independent-field-gate', 'Independent force or mode-normal disagreement')
            tangent = abs(ref['d']+rate[4]) if sliding else None
            record['independent_tangent_residual_per_s'] = tangent
            if sliding and tangent > 1e-8:
                raise Failure('tangency-gate', 'Independent tangent residual failed')
            cumulative = balance_errors(z, self.cfg['z'], self.cfg)
            record['cumulative_balance_errors'] = cumulative.tolist()
            if role != 'Jacobian-auxiliary':
                check_balances(cumulative)
            segment = balance_errors(z, self.entry_state, self.cfg) if sliding and self.entry_state is not None else np.zeros(6)
            record['segment_balance_errors'] = segment.tolist()
            if role != 'Jacobian-auxiliary':
                check_balances(segment)
            record.update(normal_on=o['normal_on'], normal_off=o['normal_off'], theta=o['theta'],
                          g=o['g'], force_residual_N=o['residual'], independent_force_residual_N=ref['residual'],
                          independent_tangent_residual_per_s=tangent, cumulative_balance_errors=cumulative.tolist(),
                          segment_balance_errors=segment.tolist(), rate_full=rate.tolist())
            return z, o, rate, record
        except ValueError as error:
            if not isinstance(error, Failure):
                error = Failure(getattr(error, 'code', 'source-or-reference-root'), str(error))
            error.t = float(t)
            error.z = z.tolist()
            record.update(failure=error.code, message=str(error))
            self.probes.append(record)
            raise error

    def _candidate(self, before, old):
        """Original solver inputs/dense formula; no accepted-custody mutation."""
        if self.method.startswith('RK4'):
            h = min(float(self.method.split('-')[1]), END-before,
                    (math.floor((before+1e-10)/.001)+1)*.001-before)
            a = self.rhs(before, old)
            b = self.rhs(before+h/2, old+h*a/2)
            c = self.rhs(before+h/2, old+h*b/2)
            d = self.rhs(before+h, old+h*c)
            rates = [a,b,c,d]
            def dense(t):
                u = (t-before)/h
                return old+h*((u-1.5*u*u+2*u**3/3)*a+(u*u-2*u**3/3)*(b+c)+(-u*u/2+2*u**3/3)*d)
            nt = before+h
            nx = dense(nt)
        else:
            if self._solver_cache is None:
                cls = {'DOP853':DOP853, 'Radau':Radau}[self.method]
                # Full 11/reduced 10 unchanged: every integrated coordinate,
                # including full I and all six ledgers, enters SciPy's norm.
                self._solver_cache = cls(self.rhs, before, old, END, rtol=1e-9,
                    atol=1e-11, max_step=.0005, **({'jac':self.jac} if cls is Radau else {}))
            self._solver_cache.step()
            if self._solver_cache.status == 'failed':
                raise Failure('ODE-step', 'Adaptive solver failed')
            nt = float(self._solver_cache.t)
            nx = self._solver_cache.y.copy()
            dense = self._solver_cache.dense_output()
            rates = None
        if nt-before < 1e-10 or self.old_steps+self.accepted_steps >= 12000:
            raise Failure('ODE-stall', 'Original watchdog/tiny step gate')
        record = dense_record(self.method, before, nt, old, dense, rates)
        for ti in [before, (before+nt)/2, nt]:
            if np.max(np.abs(replay_dense(record, ti)-dense(ti))) > 1e-12:
                raise Failure('dense-serialization', 'Actual dense polynomial reproduction failed')
        return nt, nx, dense, record

    def _attempt_trial(self, producer):
        """Shared actual transaction path, also tested with static failure producers."""
        if self.failure is not None:
            raise Failure('terminal-cell', 'Failed cell cannot retry its trial')
        before, old, fingerprint = self.t, self.x.copy(), self.fingerprint()
        self.stages, self.jacobian_probes = [], []
        record = None
        try:
            nt, nx, dense, record = producer(before, old)
            proposal = self.prepare_interval(nt, nx, dense, record)
            proposal['interval']['jacobian_auxiliaries'] = copy.deepcopy(self.jacobian_probes)
            self.commit(proposal)
            return True
        except ValueError as error:
            if not isinstance(error, Failure):
                error = Failure(getattr(error, 'code', 'solver-exception'), str(error))
            self._solver_cache = None
            assert self.fingerprint() == fingerprint, 'Rejected trial changed accepted custody'
            self.failure = dict(code=error.code, message=str(error), acceptedTime=self.t,
                acceptedState=self.decode(self.x).tolist(), failedStageTime=error.t,
                failedStageState=error.z, rollback_exact=True, solver_cache_discarded=True)
            self.probes.append(dict(start=before, startState=old.tolist(), dense=record,
                stages=copy.deepcopy(self.stages), jacobian_auxiliaries=copy.deepcopy(self.jacobian_probes),
                failure=error.code, accepted=False))
            return False

    def advance(self):
        # The frozen preflight packet authorizes structural checks only.
        if not json.loads((DATA/'protocol-source.json').read_text())['matrix_execution_authorized']:
            raise Failure('execution-held', 'New matrix needs distinct explicit execution authorization')
        self._solver_cache = None
        while self.t < END:
            if not self._attempt_trial(self._candidate):
                return
        self._solver_cache = None

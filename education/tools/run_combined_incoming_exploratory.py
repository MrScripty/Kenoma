#!/usr/bin/env python3
"""Authorized exploratory interaction; no sliding or full qualification.

Historical independent raw replay is incomplete. No transfer retry is performed.
Original source kernels, rates, tolerances and budgets are retained.
"""
import hashlib
import json
import math
import time
import numpy as np
from scipy.integrate import DOP853, Radau
from run_activation_equality_diagnostic import ActivationEngine, one_sided_rate
from run_ordinary_crossing_consistency import CrossingEngine, dense_record, replay_dense
from run_filippov_bounded_experiment import ROOT, Failure, NODES
from combined_incoming_preflight import decide_trial

DATA = ROOT / 'education/data/combined-incoming-exploratory-v1'
OUT = DATA / 'review'


def protocol():
    return json.loads((DATA / 'protocol.json').read_text())


def verify_inputs():
    p = protocol()
    for path, digest in {**p['input_sha256'], **p['source_sha256']}.items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen combined input changed: ' + path)
    if not p['exploratory_execution_authorized'] or p['independent_raw_replay_complete']:
        raise ValueError('Exploratory authorization or historical limitation mismatch')


def guard_brackets(samples, key, direction, armed):
    """Oriented guard brackets on validated trial samples, without state mutation.

After a continuous restart the residual-sized starting value does not arm an
immediate artificial recrossing. Actual opposite-side departures still stop.
"""
    brackets = []
    for left, right in zip(samples, samples[1:]):
        lv, rv = direction * left[key], direction * right[key]
        if lv < -1e-13:
            armed = True
        if armed and lv < 0 <= rv:
            brackets.append((left['t'], right['t']))
        if rv < -1e-13:
            armed = True
    return brackets, armed


class CombinedEngine(ActivationEngine):
    def __init__(self, rep, method):
        self.combined_activation_events = []
        self.arbitrations = []
        self.guard_armed = {'g': True, 'H': True}
        super().__init__(rep, method, 'split')

    def slide(self):
        raise Failure('combined-no-sliding', 'Sliding is prohibited')

    def save(self, t, x):
        super().save(t, x)
        self.history[-1].update(activation_branch=self.activation_branch,
                               g=self.history[-1]['u'] - self.history[-1]['z'][2])

    def rhs(self, t, x):
        n = len(self.stage_records)
        value = super().rhs(t, x)
        if len(self.stage_records) > n:
            row = self.stage_records[-1]
            row.update(g=row['u'] - row['z'][2], activation_branch=self.activation_branch,
                       controller_mode=self.controller_mode)
        return value

    def activation_root(self, left, right, dense):
        # The declared first crossing uses the exact reviewed localizer.
        if self.activation_branch == 'activation':
            c = self.activation_localize(left, right, dense)
            c.update(kind='activation-equality', interior=True, transverse=True)
            return c
        # A later equality is localized for ordering but remains undeclared.
        lo, hi, probes = left, right, []
        for iteration in range(32):
            t = (lo + hi) / 2
            x = dense(t)
            z, o = self.evaluate(x)
            g = o['u'] - z[2]
            probes.append(dict(t=t, z=z.tolist(), g=g, residual_N=o['residual'], accepted=False))
            if g < 0:
                lo = t
            else:
                hi = t
            if hi - lo <= 1e-12 and abs(g) <= 1e-13:
                return dict(kind='activation-recrossing', bracket=[lo, hi], t=t,
                            x=x.tolist(), g=g, accepted=False, undeclared=True,
                            iterations=iteration + 1, probes=probes)
        self.activation_localization_records = probes
        raise Failure('activation-localization', 'Recrossing localization exhausted unchanged 32-iteration budget')

    def sample_trial(self, before, nt, dense):
        times = sorted(set([before, (before + nt) / 2, nt] +
                           [before + (nt - before) * (node + 1) / 2 for node in NODES]))
        samples = []
        for t in times:
            z, o = self.evaluate(dense(t))
            samples.append(dict(t=float(t), z=z.tolist(), g=o['u'] - z[2],
                                H=o['H'], u=o['u'], residual_N=o['residual'],
                                g_normal_per_s=(o['d'] + o['Idot'] if .01 < o['u'] < 1 else 0.) - o['adot'],
                                H_normal_per_s=o['normal_on'] if self.controller_mode == 'integrating' else o['normal_off']))
        return samples

    def candidates(self, before, nt, dense, samples):
        found = []
        gd = -1 if self.activation_branch == 'activation' else 1
        hd = 1 if self.controller_mode == 'integrating' else -1
        for key, direction in [('g', gd), ('H', hd)]:
            brackets, _ = guard_brackets(samples, key, direction, self.guard_armed[key])
            # Arming belongs to the accepted prefix, not a discarded suffix.
            for left, right in brackets:
                try:
                    if key == 'g':
                        c = self.activation_root(left, right, dense)
                    else:
                        c = self.localize(left, right, dense)
                        c.update(kind=c['classification'], same_direction_normals=c['classification'] != 'attracting',
                                 g=self.g(np.array(c['x'])))
                    found.append(c)
                except Failure as error:
                    # Physical failures invalidate the entire trial. A later
                    # classification/localization failure remains provisional
                    # until ordering identifies the actual earliest event.
                    if error.code not in ['activation-interior', 'activation-transversality',
                                          'activation-localization', 'event-strict-sign',
                                          'event-error-direction', 'event-localization']:
                        raise
                    probes = getattr(self, 'activation_localization_records' if key == 'g' else 'localization_records', [])
                    found.append(dict(kind='uncertified-' + key, bracket=[left, right],
                                      accepted=False, failure=error.code, message=str(error), probes=probes))
            for sample in samples:
                if abs(sample[key]) <= 1e-13 and abs(sample[key + '_normal_per_s']) <= 1e-8:
                    found.append(dict(kind='guard-tangency-' + key,
                                      bracket=[sample['t'], sample['t']], accepted=False,
                                      sample=sample, undeclared=True))
        return found

    def update_arming(self, samples, stop):
        prefix = [s for s in samples if s['t'] <= stop]
        for key, direction in [('g', -1 if self.activation_branch == 'activation' else 1),
                               ('H', 1 if self.controller_mode == 'integrating' else -1)]:
            if any(direction * s[key] < -1e-13 for s in prefix):
                self.guard_armed[key] = True

    def restart_decision(self, found):
        decision = decide_trial(found, self.controller_mode, self.activation_branch, self.remainder_end)
        if decision['decision'] in ['activation-prefix', 'ordinary-prefix', 'hold']:
            first = min(found, key=lambda c: c['bracket'][0])
            if first.get('failure'):
                return dict(decision='stop', advance=False, reason=first['failure'])
            if decision['decision'] == 'ordinary-prefix':
                desired = 1 if self.activation_branch == 'activation' else -1
                if desired * first['g'] <= 1e-13:
                    return dict(decision='stop', advance=False, reason='activation-side-ambiguity-at-controller-crossing')
                if len([e for e in self.events if e['type'].startswith('ordinary-')]) >= 2:
                    return dict(decision='stop', advance=False, reason='undeclared-extra-ordinary-event')
        return decision

    def entry(self):
        self.advance(protocol()['time_cap_s'], True)
        if self.failure is None and self.candidate is None:
            self.stop(Failure('missing-entry', 'Cap reached without a held attracting candidate'))

    def advance(self, end, seek_entry):
        solver = None
        while self.t < end - 1e-12 and not self.failure:
            self.stage_records = []
            before, old = self.t, self.x.copy()
            record, samples, found = None, [], []
            try:
                if self.mode != 'incoming':
                    raise Failure('combined-no-sliding', 'Nonincoming state prohibited')
                if self.method.startswith('RK4'):
                    h = min(float(self.method.split('-')[1]), end - self.t,
                            (math.floor((self.t + 1e-10) / .001) + 1) * .001 - self.t)
                    if self.remainder_end is not None:
                        h = min(h, self.remainder_end - self.t)
                    nt, nx, dense = self.step_rk(self.t, self.x, h)
                else:
                    if solver is None:
                        cls = {'DOP853': DOP853, 'Radau': Radau}[self.method]
                        solver = cls(self.rhs, self.t, self.x, end, rtol=1e-9, atol=1e-11,
                                     max_step=.0005, **({'jac': self.jac} if cls is Radau else {}))
                    solver.step()
                    if solver.status == 'failed':
                        raise Failure('ODE-step', 'Adaptive step failed')
                    nt, nx, dense = float(solver.t), solver.y.copy(), solver.dense_output()
                if nt - before < 1e-10 or self.steps >= 12000:
                    raise Failure('ODE-stall', 'Tiny-step or original declared watchdog')
                record = dense_record(self.method, before, nt, old, dense, getattr(self, 'actual_rk_rates', None))
                for t in [before, (before + nt) / 2, nt]:
                    if np.max(np.abs(replay_dense(record, t) - dense(t))) > 1e-12:
                        raise Failure('dense-serialization', 'Actual polynomial reproduction failed')
                samples = self.sample_trial(before, nt, dense)
                found = self.candidates(before, nt, dense, samples)
                decision = self.restart_decision(found)
                auxiliary = dict(start=before, trialEnd=nt, startState=old.tolist(), dense=record,
                                 stages=list(self.stage_records), guard_samples=samples, events=found,
                                 incoming_controller_mode=self.controller_mode,
                                 incoming_activation_branch=self.activation_branch,
                                 pending_remainder_end=self.remainder_end, decision=decision, accepted=False)
                if found:
                    self.arbitrations.append(auxiliary)
                if decision['decision'] == 'stop':
                    raise Failure(decision['reason'], 'Combined earliest-event decision stopped without advancement')
                if decision['decision'] == 'hold':
                    self.candidate = min(found, key=lambda c: c['bracket'][0])
                    self.candidate['classification'] = 'attracting'
                    self.probes.append(dict(auxiliary, candidate=self.candidate))
                    return
                first = min(found, key=lambda c: c['bracket'][0]) if found else None
                stop = first['t'] if first else nt
                newx = np.array(first['x']) if first else nx
                incoming_a, incoming_c, pending = self.activation_branch, self.controller_mode, self.remainder_end
                # Original accepted-side, GL8, physical and ledger checks run
                # before any branch change or accepted time/state advancement.
                self.accept(stop, newx, dense)
                self.intervals[-1].update(dense=record, stages=list(self.stage_records),
                                         activation_branch=incoming_a, controller_mode=incoming_c,
                                         pending_remainder_end=pending)
                self.update_arming(samples, stop)
                if first:
                    self.probes.append(auxiliary)
                    if decision['decision'] == 'activation-prefix':
                        first['accepted'] = True
                        self.activation_event = first
                        self.combined_activation_events.append(first)
                        self.activation_auxiliaries.append(dict(auxiliary, activation_event=first))
                        self.activation_branch = 'deactivation'
                        self.guard_armed['g'] = False
                        if self.method.startswith('RK4'):
                            self.remainder_end = nt
                        self.events.append(dict(type='activation-equality', t=self.t, bracket=first['bracket'],
                                                g=first['g'], state_reset=False))
                    else:
                        self.events.append(dict(type=first['kind'], t=self.t, bracket=first['bracket'],
                                                H=first['H'], normal_on=first['normal_on'], normal_off=first['normal_off'],
                                                integral_reset=False, mechanical_jump=0.))
                        self.controller_mode = decision['controller']
                        self.guard_armed['H'] = False
                        # The pending activation end survives a controller cut;
                        # without one, the reviewed fresh-step schedule remains.
                        self.remainder_end = pending
                    self.save(self.t, self.x)
                    solver = None
                    continue
                if self.remainder_end is not None and abs(nt - self.remainder_end) < 1e-12:
                    self.remainder_end = None
            except Failure as error:
                self.probes.append(dict(start=before, stages=list(self.stage_records), dense=record,
                                        guard_samples=samples, provisional_events=found, accepted=False,
                                        activation_localization_probes=getattr(self, 'activation_localization_records', []),
                                        controller_localization_probes=getattr(self, 'localization_records', []), failure=error.code))
                self.stop(error)
                return
        self.save(self.t, self.x)


def main():
    from argparse import ArgumentParser
    p = protocol()
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--rep', required=True, choices=p['representations'])
    parser.add_argument('--method', required=True, choices=p['methods'])
    args = parser.parse_args()
    verify_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f'mass-1-{args.rep}-{args.method}.json'
    if dest.exists():
        raise ValueError('Refuse to overwrite combined evidence')
    started = time.monotonic()
    e = CombinedEngine(args.rep, args.method)
    try:
        e.entry()
        result = e.result()
        result.update(exploratory_only=True, independent_raw_replay_complete=False,
                      historical_review_limitation=p['historical_review_limitation'],
                      incoming_candidate_reached=e.candidate is not None and e.failure is None,
                      activation_event=e.activation_event, activation_auxiliaries=e.activation_auxiliaries,
                      combined_arbitrations=e.arbitrations, sliding_allowed=False,
                      convention='Original one-sided activation split and ordinary controller restarts; attracting candidate held unaccepted',
                      elapsed_s=time.monotonic() - started,
                      protocol_sha256=hashlib.sha256((DATA / 'protocol.json').read_bytes()).hexdigest(),
                      executed_source_sha256=p['source_sha256'])
        assert not result['qualified'] and all(row['mode'] == 'incoming' for row in result['history'])
        assert result['candidate'] is None or not result['candidate']['accepted']
        dest.write_text(json.dumps(result, indent=2) + '\n')
        print(args.rep, args.method, 'accepted', e.t, 'candidate',
              e.candidate['t'] if e.candidate else None, 'failure', e.failure,
              'steps', e.steps, 'elapsed', result['elapsed_s'], flush=True)
    finally:
        if e.source:
            e.source.close()


if __name__ == '__main__':
    main()

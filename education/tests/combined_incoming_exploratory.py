#!/usr/bin/env python3
"""Executable checks before the exploratory matrix; no full prefixes here."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from run_combined_incoming_exploratory import CombinedEngine, guard_brackets
from run_filippov_bounded_experiment import Failure, Engine
from run_ordinary_crossing_consistency import dense_record, replay_dense


def activation(lo=.2, hi=.21):
    return dict(kind='activation-equality', bracket=[lo, hi], interior=True, transverse=True)


def outward(lo=.4, hi=.41):
    return dict(kind='ordinary-outward', bracket=[lo, hi], same_direction_normals=True, g=-.04)


class Checks(unittest.TestCase):
    def engine(self, rep='reduced-independent'):
        e = CombinedEngine(rep, 'RK4-0.0002')
        if e.source:
            self.addCleanup(e.source.close)
        return e

    def test_both_real_initializations_and_one_step(self):
        engines = [self.engine(rep) for rep in ['full-source', 'reduced-independent']]
        np.testing.assert_array_equal(engines[0].x, engines[1].x)
        for e in engines:
            original = Engine('mass-1', e.rep, e.method)
            try:
                np.testing.assert_allclose(e.rhs(0, e.x), original.rhs(0, original.x), rtol=0, atol=1e-14)
                nt, nx, dense = e.step_rk(0, e.x, .0002)
                record = dense_record(e.method, 0, nt, e.x, dense, e.actual_rk_rates)
                np.testing.assert_allclose(replay_dense(record, .000071), dense(.000071), rtol=0, atol=1e-14)
                self.assertEqual(e.candidates(0, nt, dense, e.sample_trial(0, nt, dense)), [])
                e.accept(nt, nx, dense)
                self.assertEqual(e.t, .0002)
            finally:
                if original.source:
                    original.source.close()
        np.testing.assert_allclose(engines[0].x, engines[1].x, rtol=0, atol=1e-14)

    def test_earliest_activation_discards_later_failure(self):
        e = self.engine()
        later = dict(kind='uncertified-H', bracket=[.4, .41], failure='event-strict-sign')
        decision = e.restart_decision([later, activation()])
        self.assertEqual(decision['decision'], 'activation-prefix')
        self.assertEqual(decision['discarded_later_candidates'], ['uncertified-H'])
        self.assertEqual(e.t, 0)

    def test_overlap_and_touch_stop(self):
        e = self.engine()
        for event in [outward(.205, .22), outward(.21, .22)]:
            self.assertEqual(e.restart_decision([activation(), event])['reason'], 'unresolved-event-order')

    def test_controller_cut_preserves_pending_activation_end(self):
        e = self.engine()
        e.activation_branch = 'deactivation'
        e.remainder_end = .5
        decision = e.restart_decision([outward()])
        self.assertEqual(decision['decision'], 'ordinary-prefix')
        self.assertTrue(decision['preserve_original_rk_trial_end'])
        self.assertEqual(decision['pending_activation_remainder_end'], .5)

    def test_controller_without_remainder_keeps_reviewed_fresh_step(self):
        e = self.engine()
        e.activation_branch = 'deactivation'
        decision = e.restart_decision([outward()])
        self.assertFalse(decision['preserve_original_rk_trial_end'])
        self.assertIsNone(decision['pending_activation_remainder_end'])

    def test_actual_recrossing_stops(self):
        e = self.engine()
        e.activation_branch = 'deactivation'
        decision = e.restart_decision([dict(kind='activation-recrossing', bracket=[.2, .21])])
        self.assertEqual(decision['decision'], 'stop')

    def test_earliest_uncertified_root_stops(self):
        e = self.engine()
        decision = e.restart_decision([dict(kind='uncertified-g', bracket=[.1, .11], failure='activation-interior'), outward()])
        self.assertEqual(decision['decision'], 'stop')

    def test_bound_and_tangency_stop(self):
        e = self.engine()
        for field in ['interior', 'transverse']:
            root = activation()
            root[field] = False
            self.assertEqual(e.restart_decision([root])['decision'], 'stop')

    def test_attraction_held_without_state_mutation(self):
        e = self.engine()
        old = e.x.copy()
        self.assertEqual(e.restart_decision([dict(kind='attracting', bracket=[.2, .21])])['decision'], 'hold')
        np.testing.assert_array_equal(e.x, old)
        self.assertEqual(e.t, 0)
        self.assertIsNone(e.candidate)

    def test_ambiguous_post_controller_activation_stops(self):
        e = self.engine()
        e.activation_branch = 'deactivation'
        root = outward()
        root['g'] = 0
        self.assertEqual(e.restart_decision([root])['decision'], 'stop')

    def test_extra_ordinary_event_stops(self):
        e = self.engine()
        e.activation_branch = 'deactivation'
        e.events = [dict(type='ordinary-outward'), dict(type='ordinary-inward')]
        self.assertEqual(e.restart_decision([outward()])['reason'], 'undeclared-extra-ordinary-event')

    def test_sliding_prohibited(self):
        with self.assertRaisesRegex(Failure, 'Sliding'):
            self.engine().slide()

    def test_physical_failure_preserves_all_eleven_state_and_time(self):
        e = self.engine()
        old = e.x.copy()
        rhs = e.rhs
        def invalid(t, x):
            z = x.copy()
            z[0] = .02
            return rhs(t, z)
        e.rhs = invalid
        e.advance(.0002, True)
        self.assertEqual(e.failure['code'], 'slack')
        self.assertEqual(e.t, 0)
        np.testing.assert_array_equal(e.x, old)
        np.testing.assert_array_equal(e.quad, np.zeros(6))
        self.assertFalse(e.events)
        self.assertFalse(e.intervals)

    def test_wrong_side_acceptance_is_transactional(self):
        e = self.engine()
        old = e.x.copy()
        z = old.copy()
        z[2] += .001
        with self.assertRaisesRegex(Failure, 'Wrong-side'):
            e.accept(.0002, z, lambda t: z)
        self.assertEqual(e.t, 0)
        np.testing.assert_array_equal(e.x, old)

    def test_guard_arming_excludes_residual_sized_fake_recross(self):
        samples = [dict(t=0, g=4e-14), dict(t=.1, g=-.01), dict(t=.2, g=-.02)]
        brackets, armed = guard_brackets(samples, 'g', 1, False)
        self.assertEqual(brackets, [])
        self.assertTrue(armed)
        samples.append(dict(t=.3, g=.01))
        brackets, _ = guard_brackets(samples, 'g', 1, False)
        self.assertEqual(brackets, [(.2, .3)])

    def test_runtime_composes_cuts_and_continuous_eleven_coordinate_restarts(self):
        # Synthetic schedule exercises the real advance/restart path. Physical
        # acceptance is a stub here; the separate two real one-step tests cover
        # unchanged physical checks, rather than certifying this toy orbit.
        e = self.engine()
        trials, accepted = [], []
        original = e.x.copy()
        def step(t, x, h):
            trials.append((t, t + h, e.remainder_end))
            e.actual_rk_rates = [np.zeros(11) for _ in range(4)]
            return t + h, x.copy(), lambda ti: x.copy()
        def candidates(before, nt, dense, samples):
            roots = [(.00007, 'activation-equality'), (.00011, 'ordinary-outward'), (.0003, 'ordinary-inward')]
            events = []
            for t, kind in roots:
                if before < t <= nt:
                    events.append(dict(kind=kind, t=t, bracket=[t - 1e-14, t + 1e-14],
                                       x=dense(t).tolist(), g=-.04 if kind != 'activation-equality' else 0.,
                                       H=0., normal_on=1., normal_off=1., interior=True,
                                       transverse=True, same_direction_normals=True, accepted=False))
            return events
        def accept(stop, nx, dense):
            np.testing.assert_array_equal(nx, original)
            accepted.append((stop, nx.copy()))
            e.intervals.append(dict(start=e.t, end=stop))
            e.x = nx.copy()
            e.t = stop
            e.steps += 1
        with patch.object(e, 'step_rk', side_effect=step), patch.object(e, 'candidates', side_effect=candidates), patch.object(e, 'accept', side_effect=accept), patch.object(e, 'save'), patch.object(e, 'sample_trial', return_value=[]):
            e.advance(.00065, True)
        self.assertIsNone(e.failure)
        self.assertEqual([x['type'] for x in e.events], ['activation-equality', 'ordinary-outward', 'ordinary-inward'])
        self.assertAlmostEqual(trials[1][1], .0002)
        self.assertAlmostEqual(trials[2][1], .0002)
        self.assertAlmostEqual(trials[2][2], .0002)
        self.assertAlmostEqual(trials[4][0], .0003)
        self.assertAlmostEqual(trials[4][1], .0005)
        self.assertIsNone(trials[4][2])
        self.assertEqual(e.t, .00065)
        for _, state in accepted:
            np.testing.assert_array_equal(state, original)


if __name__ == '__main__':
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Diagnostic isolation, immutable inputs, source rollback and timing proxies."""
import unittest,sys,copy,math
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from run_filippov_incoming_diagnostic import DiagnosticEngine,PROTOCOL,verify_inputs
from run_filippov_bounded_experiment import Failure
from analyze_filippov_incoming_diagnostic import dense_from_stages,relocalize,event_compare,segment_compare

class Checks(unittest.TestCase):
    def test_sliding_prohibited_without_advancement(self):
        e=DiagnosticEngine('high','reduced-independent');old=e.x.copy()
        with self.assertRaisesRegex(Failure,'prohibited'):e.slide()
        self.assertEqual(e.t,0);np.testing.assert_array_equal(e.x,old)
    def test_resolution_watchdog_is_declared_before_run(self):
        required=math.ceil(.264/PROTOCOL['additional_step_s'])
        self.assertGreater(required,10000);self.assertLess(required+20,PROTOCOL['accepted_step_watchdog'])
        self.assertEqual(PROTOCOL['velocity_root_iterations'],64);self.assertEqual(PROTOCOL['event_localization_iterations'],32)
    def test_source_slack_probe_retains_state_and_ledgers(self):
        e=DiagnosticEngine('high','reduced-independent');old=e.x.copy();rhs=e.rhs
        def invalid(t,x):
            probe=x.copy();probe[0]=.02;return rhs(t,probe)
        e.rhs=invalid;e.advance(.001,False)
        self.assertEqual(e.failure['code'],'slack');self.assertEqual(e.t,0)
        np.testing.assert_array_equal(e.x,old);np.testing.assert_array_equal(e.quad,np.zeros(6))
    def test_changed_frozen_input_rejected(self):
        path=next(iter(PROTOCOL['input_sha256']))
        with patch.dict(PROTOCOL['input_sha256'],{path:'0'*64}):
            with self.assertRaisesRegex(ValueError,'Frozen diagnostic input changed'):verify_inputs()
    def test_incomplete_polynomial_cannot_be_inferred(self):
        with self.assertRaisesRegex(ValueError,'four-stage'):dense_from_stages(None,dict(stages=[],start=0,trialEnd=1))
    def test_polished_root_is_auxiliary_and_leaves_original_untouched(self):
        e=SimpleNamespace(controller_mode='integrating',evaluate=lambda x:(x,dict(H=x[0],normal_on=1,normal_off=-1,residual=0)))
        original=dict(t=.5-2e-8,bracket=[.5-5e-8,.5+5e-8]);old=copy.deepcopy(original)
        r=relocalize(e,lambda t:np.array([t-.5]),original)
        self.assertIn('t',r);self.assertFalse(r['accepted']);self.assertEqual(original,old);self.assertLessEqual(r['iterations'],32)
    def test_timing_budget_is_separate_from_state_correction(self):
        def event(t):return dict(original_time_s=t,integrating_rate_8e_per_s=-.34,surface_residual_timing_proxy_s=1e-9,bracket_radius_from_recorded_time_s=1e-8)
        a={'ordinary-inward':event(.25)};b={'ordinary-inward':event(.25+1e-8)};old=copy.deepcopy([a,b])
        r=event_compare(a,b)['ordinary-inward']
        self.assertAlmostEqual(r['abs_8e_times_original_event_time_difference'],3.4e-9,places=16)
        self.assertTrue(r['not_causal_attribution_or_rigorous_error_bound']);self.assertEqual([a,b],old)
    def test_raw_difference_retains_integral_and_force_terms(self):
        def row(I,FT,raw):return dict(t=.001,z=[0,0,.05,1,I]+[0]*6,FT=FT,uraw=raw,controller_mode='integrating')
        a={'history':[row(2e-9,5+1e-7,.1+2e-9-.004*1e-7)]};b={'history':[row(0,5,.1)]}
        r=segment_compare(a,b,'high')['initial_equilibrium']['witnesses']['raw']
        self.assertLess(abs(r['raw_identity_residual']),1e-17);self.assertAlmostEqual(r['signed_integral_difference'],2e-9)

if __name__=='__main__':unittest.main(verbosity=2)

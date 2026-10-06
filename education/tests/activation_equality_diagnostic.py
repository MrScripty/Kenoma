#!/usr/bin/env python3
import unittest,sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from run_activation_equality_diagnostic import ActivationEngine,PROTOCOL,verify_inputs,one_sided_rate
from run_ordinary_crossing_consistency import CrossingEngine,dense_record,replay_dense
from run_filippov_bounded_experiment import Engine,Failure

class Checks(unittest.TestCase):
    def test_one_sided_rates_agree_at_equality_derivatives_differ(self):
        for a in [.02,.049,.5]:
            self.assertEqual(one_sided_rate(a,a,'activation'),0);self.assertEqual(one_sided_rate(a,a,'deactivation'),0)
            self.assertNotEqual(1/(.01*(.5+1.5*a)),(.5+1.5*a)/.04)
    def test_ordinary_crossing_implementation_fixed(self):self.assertIs(ActivationEngine.localize,CrossingEngine.localize)
    def test_both_representations_retain_original_fields_on_physical_side(self):
        for rep in PROTOCOL['representations']:
            e=ActivationEngine(rep,'RK4-0.0002','split');original=Engine('mass-1',rep,'RK4-0.0002')
            try:
                for branch,da in [('activation',0),('deactivation',.001)]:
                    z=e.x.copy();z[2]+=da;e.activation_branch=branch
                    np.testing.assert_allclose(e.rhs(0,z),original.rhs(0,z),rtol=0,atol=1e-14)
            finally:
                if e.source:e.source.close()
                if original.source:original.source.close()
    def test_source_and_reference_extension_agree_on_opposite_trial_side(self):
        a=ActivationEngine('full-source','RK4-0.0002','split');b=ActivationEngine('reduced-independent','RK4-0.0002','split')
        try:
            z=a.x.copy();z[2]+=.001
            _,native=a.evaluate(z);_,independent=b.evaluate(z)
            self.assertAlmostEqual(native['adot'],one_sided_rate(z[2],native['u'],'activation'),places=14)
            self.assertAlmostEqual(independent['adot'],one_sided_rate(z[2],independent['u'],'activation'),places=14)
        finally:a.source.close()
    def test_localization_is_transversal_auxiliary_without_projection(self):
        root=.00242739
        def dense(t):return np.array([.23*(root-t),0,.05]+[0]*8)
        fake=SimpleNamespace(g=lambda x:x[0],evaluate=lambda x:(x,dict(u=.05+x[0],d=-.23,Idot=0,residual=0)))
        c=ActivationEngine.activation_localize(fake,.0024,.0025,dense)
        self.assertFalse(c['accepted']);self.assertFalse(c['state_projected']);self.assertLessEqual(abs(c['g']),1e-13);self.assertLessEqual(c['bracket'][1]-c['bracket'][0],1e-12);self.assertLessEqual(c['iterations'],32)
    def test_physical_failure_retains_all_state_and_ledgers(self):
        e=ActivationEngine('reduced-independent','RK4-0.0002','split');old=e.x.copy();rhs=e.rhs
        def invalid(t,x):
            z=x.copy();z[0]=.02;return rhs(t,z)
        e.rhs=invalid;e.entry();self.assertEqual(e.failure['code'],'slack');self.assertEqual(e.t,0);np.testing.assert_array_equal(e.x,old);np.testing.assert_array_equal(e.quad,np.zeros(6));self.assertIsNone(e.activation_event)
    def test_wrong_side_accepted_interval_rejected_before_mutation(self):
        e=ActivationEngine('reduced-independent','RK4-0.0002','split');old=e.x.copy();z=old.copy();z[2]+=.001
        with self.assertRaisesRegex(Failure,'Wrong-side'):e.accept(.0002,z,lambda t:z)
        self.assertEqual(e.t,0);np.testing.assert_array_equal(e.x,old)
    def test_high_equilibrium_serialization_step(self):
        e=CrossingEngine('high','reduced-independent','RK4-0.0002');t,_,dense=e.step_rk(0,e.x,.0002);rec=dense_record(e.method,0,t,e.x,dense,e.actual_rk_rates)
        np.testing.assert_allclose(replay_dense(rec,.000071),dense(.000071),rtol=0,atol=1e-14)
    def test_input_change_rejected(self):
        path=next(iter(PROTOCOL['input_sha256']))
        with patch.dict(PROTOCOL['input_sha256'],{path:'0'*64}):
            with self.assertRaisesRegex(ValueError,'Frozen activation input changed'):verify_inputs()

if __name__=='__main__':unittest.main(verbosity=2)

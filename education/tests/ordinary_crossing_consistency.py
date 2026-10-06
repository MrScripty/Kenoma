#!/usr/bin/env python3
import unittest,sys,copy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from scipy.integrate._ivp.rk import Dop853DenseOutput
from scipy.integrate._ivp.radau import RadauDenseOutput
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from run_ordinary_crossing_consistency import CrossingEngine,PROTOCOL,verify_inputs,dense_record,replay_dense
from run_filippov_bounded_experiment import Failure

class Checks(unittest.TestCase):
    def test_actual_adaptive_coefficients_replay(self):
        rng=np.random.default_rng(318);old=rng.normal(size=11)
        for method,dense in [('DOP853',Dop853DenseOutput(.2,.2005,old,rng.normal(size=(7,11)))),('Radau',RadauDenseOutput(.2,.2005,old,rng.normal(size=(11,3))))]:
            r=dense_record(method,.2,.2005,old,dense,None)
            for t in [.2,.200123,.2005]:np.testing.assert_allclose(replay_dense(r,t),dense(t),rtol=0,atol=2e-15)
    def test_actual_rk_dense_replay(self):
        e=CrossingEngine('high','reduced-independent','RK4-0.0002');end,_,dense=e.step_rk(0,e.x,.0002)
        r=dense_record(e.method,0,end,e.x,dense,e.actual_rk_rates)
        for t in [0,.000071,end]:np.testing.assert_allclose(replay_dense(r,t),dense(t),rtol=0,atol=1e-14)
    def fake(self,classification):
        on,off=(.4,.2) if classification=='ordinary-outward' else (.4,-.2)
        return SimpleNamespace(controller_mode='integrating',eta=1,evaluate=lambda x:(x,dict(H=x[0],normal_on=on,normal_off=off,e=1,u=.5,residual=0,d=off,k=on-off)))
    def test_ordinary_target_changes_returned_event_state(self):
        e=self.fake('ordinary-outward');r=CrossingEngine.localize(e,0,.0005,lambda t:np.array([t-.000123456789]))
        self.assertLessEqual(r['bracket'][1]-r['bracket'][0],1e-12);self.assertLessEqual(abs(r['H']),1e-13);self.assertLessEqual(r['iterations'],32);self.assertFalse(r['accepted'])
    def test_attracting_target_unchanged(self):
        e=self.fake('attracting');r=CrossingEngine.localize(e,0,.0005,lambda t:np.array([t-.000123456789]))
        self.assertEqual(r['solver_target_bracket_s'],1e-7);self.assertEqual(r['solver_target_H'],1e-9)
    def test_iteration_limit_failure_no_retry(self):
        e=self.fake('ordinary-outward')
        with patch.dict(PROTOCOL,{'event_localization_iterations':1}):
            with self.assertRaisesRegex(Failure,'32-iteration'):CrossingEngine.localize(e,0,.0005,lambda t:np.array([t-.000123456789]))
    def test_physical_failure_retains_state_and_ledgers(self):
        e=CrossingEngine('high','reduced-independent','RK4-0.0002');old=e.x.copy();rhs=e.rhs
        def invalid(t,x):
            z=x.copy();z[0]=.02;return rhs(t,z)
        e.rhs=invalid;e.advance(.001,False)
        self.assertEqual(e.failure['code'],'slack');self.assertEqual(e.t,0);np.testing.assert_array_equal(e.x,old);np.testing.assert_array_equal(e.quad,np.zeros(6))
    def test_sliding_prohibited(self):
        e=CrossingEngine('high','reduced-independent','Radau')
        with self.assertRaises(Failure):e.slide()
        self.assertEqual(e.t,0)
    def test_input_change_rejected(self):
        path=next(iter(PROTOCOL['input_sha256']))
        with patch.dict(PROTOCOL['input_sha256'],{path:'0'*64}):
            with self.assertRaisesRegex(ValueError,'Frozen experiment input changed'):verify_inputs()

if __name__=='__main__':unittest.main(verbosity=2)

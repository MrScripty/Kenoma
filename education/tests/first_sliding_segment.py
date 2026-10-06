#!/usr/bin/env python3
import copy
import json
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from first_sliding_segment_engine import (ROOT,PREP,Failure,SegmentEngine,decode_reduced,
    validate_diagnostics,check_balances,compare_rows,BALANCE_GATES)
from run_ordinary_crossing_consistency import replay_dense
from audit_first_sliding_segment import comparison


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        prepared=json.loads((PREP/'preflight/entry-custody.json').read_text())['records']
        cls.prepared=prepared['reduced-independent/RK4-0.0002']
        cls.incoming=json.loads((ROOT/cls.prepared['path']).read_text())

    def point(self):
        return np.array([0.,.1,.04,.95,0.,0.,0.,0.,0.,0.,0.]),dict(H=0.,d=.25,k=-.27,normal_on=.02,normal_off=-.25,residual=0.,g=-.03,s=1.02,e=-.03375,theta=.25/.27)

    def test_strict_valid_point(self):
        z,o=self.point();validate_diagnostics(z,o,True)

    def test_original_constraint_gate_stops_actual_stage(self):
        z,o=self.point();o['H']=1.001e-9
        with self.assertRaises(Failure):validate_diagnostics(z,o,True)
        validate_diagnostics(z,o,True,constraint=False)
        self.assertEqual(o['H'],1.001e-9)

    def test_strict_normals_and_outward_error(self):
        for key,value in [('normal_on',1e-8),('normal_off',-1e-8),('e',0.)]:
            z,o=self.point();o[key]=value
            with self.assertRaises(Failure):validate_diagnostics(z,o,True)

    def test_weight_not_clipped(self):
        for theta in [-.1,0.,1.,1.1,None]:
            z,o=self.point();o['theta']=theta
            with self.assertRaises(Failure):validate_diagnostics(z,o,True)
            self.assertEqual(o['theta'],theta)

    def test_additional_guard_or_activation_bound_stops(self):
        z,o=self.point();o['g']=-1e-13
        with self.assertRaises(Failure):validate_diagnostics(z,o,True)
        for a in [.01,1.]:
            z,o=self.point();z[2]=a
            with self.assertRaises(Failure):validate_diagnostics(z,o,True)

    def test_force_nonfinite_or_geometry_failure_stops(self):
        for key,value in [('residual',1.001e-7),('H',float('nan')),('s',1.)]:
            z,o=self.point();o[key]=value
            with self.assertRaises(Failure):validate_diagnostics(z,o,True)
        z,o=self.point();z[3]=.4441
        with self.assertRaises(Failure):validate_diagnostics(z,o,True)

    def test_work_and_impulse_gates_not_relaxed(self):
        for j in range(6):
            errors=np.zeros(6);errors[j]=BALANCE_GATES[j]*1.001
            with self.assertRaises(Failure):check_balances(errors)

    def test_handoff_preserves_ten_but_discloses_finite_I(self):
        z=np.array(self.prepared['readonly_refined_candidate']['state']);x=np.r_[z[:4],z[5:]]
        decoded=decode_reduced(x,self.incoming['cfg'])
        self.assertTrue(np.array_equal(np.r_[z[:4],z[5:]],np.r_[decoded[:4],decoded[5:]]))
        self.assertNotEqual(decoded[4],z[4]);self.assertLess(abs(decoded[4]-z[4]),1e-9)

    def test_actual_invalid_prefix_probe_rolls_back_all_custody(self):
        engine=SegmentEngine(self.incoming,copy.deepcopy(self.prepared))
        fingerprint=engine.fingerprint();calls=[0]
        def bad(t):
            calls[0]+=1;z=replay_dense(engine.incoming_dense,t)
            if calls[0]>=2:z[3]=.4
            return z
        with self.assertRaises(Failure):engine.prepare_interval(engine.candidate['t'],np.array(engine.candidate['state']),bad,engine.incoming_dense)
        self.assertEqual(engine.fingerprint(),fingerprint);self.assertGreaterEqual(calls[0],2)
        self.assertTrue(engine.probes);self.assertEqual(engine.accepted_steps,0)

    def test_all_cells_must_pass_before_entry(self):
        engine=SegmentEngine(self.incoming,copy.deepcopy(self.prepared));fingerprint=engine.fingerprint()
        with self.assertRaises(Failure):engine.enter({},False)
        self.assertEqual(engine.fingerprint(),fingerprint)

    def test_jacobian_probes_have_zero_ledger_columns_and_no_accepted_mutation(self):
        engine=SegmentEngine(self.incoming,copy.deepcopy(self.prepared));z=np.array(engine.candidate['state'])
        engine.mode='sliding';engine.x=np.r_[z[:4],z[5:]];fingerprint=engine.fingerprint()
        J=engine.jac(engine.candidate['t'],engine.x)
        self.assertTrue(np.array_equal(J[:,4:],np.zeros_like(J[:,4:])))
        self.assertEqual(engine.fingerprint(),fingerprint);self.assertFalse(engine.stages)
        self.assertTrue(all(not p['constraint_checked'] and not p['accepted'] for p in engine.jacobian_probes))

    def test_changed_configuration_stops_before_state_advancement(self):
        engine=SegmentEngine(self.incoming,copy.deepcopy(self.prepared));fingerprint=engine.fingerprint()
        engine.cfg['target']+=1.
        with self.assertRaises(Failure) as caught:engine.evaluate(engine.t,engine.x)
        self.assertEqual(caught.exception.code,'configuration-change');self.assertEqual(engine.fingerprint(),fingerprint)

    def test_partial_segment_cannot_pass_even_if_all_witness_states_agree(self):
        times=[float(k*.001) for k in range(264)]+[.26225,.2625,.26275]
        rows=[dict(t=t,z=[0.]*11,FT=1.,uraw=.01) for t in times]
        a=dict(history=rows,candidate=dict(t=.26203),completed=False)
        b=copy.deepcopy(a);b['completed']=True
        check=comparison(a,b)
        self.assertFalse(check['passed']);self.assertTrue(check['prefix_state_agreement'])

    def test_missing_absolute_witness_or_state_failure_blocks_comparison(self):
        a=[dict(t=.262,z=[0.]*11,FT=1.,uraw=.01)]
        b=copy.deepcopy(a)
        self.assertFalse(compare_rows(a,b,[.262,.263])['passed'])
        b[0]['z'][4]=1.001e-9
        self.assertFalse(compare_rows(a,b,[.262])['passed'])
        self.assertEqual(b[0]['z'][4],1.001e-9)


if __name__=='__main__':unittest.main(verbosity=2)

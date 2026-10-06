#!/usr/bin/env python3
import ast
import json
import numpy as np
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from first_sliding_segment_preflight import admissibility, review_allows_execution, relocalize, bitwise_I_preserved, json_native_scalar


class Checks(unittest.TestCase):
    def point(self):
        return dict(physical_valid=True,incoming_order_valid=True,deactivation_side_valid=True,
                    normal_on=.02,normal_off=-.25,outward_error=.03,weight=.93,H=1e-13,I_handoff_delta=1e-13)

    def test_valid_static_point_is_never_accepted(self):
        c=self.point();before=dict(c);r=admissibility(c)
        self.assertTrue(r['prospectively_admissible']);self.assertFalse(r['accepted']);self.assertEqual(c,before)

    def test_strict_sign_loss_stops(self):
        for field,value in [('normal_on',1e-8),('normal_off',-1e-8),('outward_error',0)]:
            c=self.point();c[field]=value;self.assertFalse(admissibility(c)['prospectively_admissible'])

    def test_nonconvex_weights_stopped_without_clipping(self):
        for value in [-.1,0,1,1.1]:
            c=self.point();c['weight']=value;self.assertFalse(admissibility(c)['prospectively_admissible']);self.assertEqual(c['weight'],value)

    def test_constraint_and_I_gates_not_relaxed(self):
        for field in ['H','I_handoff_delta']:
            c=self.point();c[field]=1.001e-9;self.assertFalse(admissibility(c)['prospectively_admissible'])

    def test_nonfinite_diagnostics_stop(self):
        for field in ['normal_on','normal_off','outward_error','weight','H','I_handoff_delta']:
            c=self.point();c[field]=float('nan');self.assertFalse(admissibility(c)['prospectively_admissible'])

    def test_physical_order_and_activation_ambiguity_stop(self):
        for field in ['physical_valid','incoming_order_valid','deactivation_side_valid']:
            c=self.point();c[field]=False;self.assertFalse(admissibility(c)['prospectively_admissible'])

    def test_scoped_incoming_ACK_does_not_authorize_sliding(self):
        self.assertFalse(review_allows_execution(dict(combined_result_review_accepted=True)))
        self.assertFalse(review_allows_execution(dict(combined_result_review_accepted=True,proposed_protocol_review_accepted=True)))
        self.assertTrue(review_allows_execution(dict(combined_result_review_accepted=True,proposed_protocol_review_accepted=True,explicit_sliding_execution_authorized=True)))

    def test_no_integrator_or_state_acceptance_call_in_preflight(self):
        path=Path(__file__).resolve().parents[1]/'tools/first_sliding_segment_preflight.py'
        tree=ast.parse(path.read_text())
        forbidden={'step','advance','slide','accept','rhs','step_rk','solve_ivp','DOP853','Radau'}
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                name=node.func.attr if isinstance(node.func,ast.Attribute) else node.func.id if isinstance(node.func,ast.Name) else ''
                self.assertNotIn(name,forbidden)
        calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='evaluate']
        self.assertEqual(len(calls),1)
        self.assertIs(calls[0].args[3].value,False)

    def test_reduced_I_discrepancy_is_not_bitwise_continuity(self):
        old=[.1,.2,.03,.95,-.02,1.,2.,3.,4.,5.,6.]
        reconstructed=old.copy();reconstructed[4]+=5e-14
        self.assertNotEqual(old,reconstructed)
        self.assertEqual(old[:4]+old[5:],reconstructed[:4]+reconstructed[5:])
        self.assertLess(abs(reconstructed[4]-old[4]),1e-9)

    def test_binary64_handoff_boolean_serializes(self):
        for delta, expected in [(np.float64(0.), True), (np.float64(1e-14), False)]:
            result=bitwise_I_preserved(delta)
            self.assertIs(result, expected)
            self.assertEqual(json.loads(json.dumps(dict(exact=result))), dict(exact=expected))

    def test_numpy_report_scalars_preserve_values_and_reject_opaque_objects(self):
        values=dict(side=np.bool_(True), residual=np.float64(1e-14), iterations=np.int64(29))
        decoded=json.loads(json.dumps(values,default=json_native_scalar))
        self.assertEqual(decoded,dict(side=True,residual=1e-14,iterations=29))
        with self.assertRaises(TypeError):
            json.dumps(object(),default=json_native_scalar)

    def auxiliary(self):
        return dict(start=0.,trialEnd=.0002,dense=dict(kind='RK4-cubic',left_s=0.,right_s=.0002,
                    y_old=[0.,0.,.05,.95,0.,0.,0.,0.,0.,0.,0.],
                    coefficients=[[.0002]+[0.]*10,[0.]*11,[0.]*11]))

    def test_readonly_refinement_is_unaccepted_and_uses_fixed_budget(self):
        root=.00001324689
        def evaluate(z,cfg,source):
            return dict(H=z[0]-root,e=-.5,normal_on=1.,normal_off=-1.,weight=.5,residual=0.)
        with patch('first_sliding_segment_preflight.evaluate_incoming',side_effect=evaluate) as mocked:
            r=relocalize(self.auxiliary(),dict(ub=.21),None)
        self.assertFalse(r['accepted']);self.assertFalse(r['state_projected']);self.assertEqual(r['new_sliding_steps'],0)
        self.assertLessEqual(r['iterations'],32);self.assertLessEqual(abs(r['H']),1e-13)
        self.assertLessEqual(r['bracket'][1]-r['bracket'][0],1e-12)
        self.assertEqual(mocked.call_count,r['iterations']+2)

    def test_unresolved_root_does_not_add_iterations(self):
        def evaluate(z,cfg,source):
            return dict(H=-1. if z[0]<.00001324689 else 1.,e=-.5,normal_on=1.,normal_off=-1.,weight=.5,residual=0.)
        with patch('first_sliding_segment_preflight.evaluate_incoming',side_effect=evaluate) as mocked:
            r=relocalize(self.auxiliary(),dict(ub=.21),None)
        self.assertEqual(r['failure'],'unchanged-32-budget-exhausted');self.assertFalse(r['accepted'])
        self.assertEqual(mocked.call_count,34)


if __name__=='__main__':unittest.main(verbosity=2)

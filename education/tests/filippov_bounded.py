#!/usr/bin/env python3
"""Physical rollback, explicit sliding and event-qualification negative controls."""
import unittest,sys,json
import copy
from pathlib import Path
from types import SimpleNamespace
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from run_filippov_bounded_experiment import Engine,Failure,entry_agreement,ROOT,CASES
from audit_filippov_bounded_experiment import completion,compare,qualify

class Checks(unittest.TestCase):
    def engine(self,rep='full-source'):
        e=Engine('high',rep,'RK4-0.0002')
        if e.source:self.addCleanup(e.source.close)
        return e
    def boundary(self,e):
        r=json.loads((ROOT/'education/data/vertical-force-command-v1/review/pre-surface-guard/high-Radau.json').read_text())
        e.x=np.array(r['failure']['acceptedState']);e.target=e.cfg['target'];e.t=r['acceptedTime'];e.history=[];e.save(e.t,e.x)
    def test_auxiliary_clips_without_freezing_or_accepting(self):
        for rep in ['full-source','reduced-independent']:
            e=self.engine(rep);self.boundary(e);x=e.x.copy();x[4]+=.2
            z,o=e.evaluate(x)
            self.assertEqual(o['u'],1);self.assertEqual(o['Idot'],8*o['e']);self.assertGreater(o['H'],0)
            self.assertFalse(e.candidate);self.assertEqual(e.history[-1]['z'],e.x.tolist())
    def test_sliding_tangency_and_mechanical_fields(self):
        for rep in ['full-source','reduced-independent']:
            e=self.engine(rep);self.boundary(e);z,o=e.evaluate(e.x);physical=[o[k] for k in ['FT','v','acceleration','Pactive','D']]
            e.mode='sliding'
            if rep=='reduced-independent':e.x=np.r_[e.x[:4],e.x[5:]]
            zs,slide=e.evaluate(e.x)
            self.assertEqual(physical,[slide[k] for k in ['FT','v','acceleration','Pactive','D']])
            self.assertAlmostEqual(slide['Idot']+slide['d'],0);self.assertGreater(slide['normal_on'],0);self.assertLess(slide['normal_off'],0)
            self.assertEqual(z[:4].tolist(),zs[:4].tolist())
    def test_frozen_incoming_extension_retains_original_branch(self):
        e=Engine('mass-1','reduced-independent','RK4-0.0002')
        r=json.loads((ROOT/'education/data/vertical-force-command-v1/review/mass-1-Radau.json').read_text())
        row=next(x for x in r['history'] if abs(x['t']-.12)<1e-10)
        e.x=np.array(row['z']);e.controller_mode='frozen';z,o=e.evaluate(e.x)
        self.assertGreater(o['H'],0);self.assertEqual(o['Idot'],0);self.assertEqual(o['u'],.01)
    def test_zero_error_is_not_sliding_policy(self):
        e=self.engine();self.boundary(e);_,o=e.evaluate(e.x);e.target=o['FT'];e.mode='sliding'
        with self.assertRaisesRegex(Failure,'Strict attracting'):e.evaluate(e.x)
    def test_physical_stage_failure_retains_time_state_ledgers(self):
        e=self.engine();old=e.x.copy();history=list(e.history)
        def invalid(t,x):raise Failure('injected-physical','Invalid physical stage',t,x)
        e.rhs=invalid;e.advance(.001,False)
        self.assertEqual(e.t,0);np.testing.assert_array_equal(e.x,old);np.testing.assert_array_equal(e.quad,np.zeros(6))
        self.assertEqual(e.history,history);self.assertEqual(e.failure['code'],'injected-physical')
    def test_actual_source_slack_probe_cannot_advance(self):
        e=self.engine();original=e.rhs;old=e.x.copy()
        def slack(t,x):
            probe=x.copy();probe[0]=.02
            return original(t,probe)
        e.rhs=slack;e.advance(.001,False)
        self.assertEqual(e.failure['code'],'slack');self.assertEqual(e.t,0)
        np.testing.assert_array_equal(e.x,old);np.testing.assert_array_equal(e.quad,np.zeros(6))
    def test_constraint_failure_is_atomic(self):
        e=self.engine();self.boundary(e);e.mode='sliding';old=e.x.copy();t=e.t;history=list(e.history)
        def invalid_dense(ti):z=old.copy();z[4]+=2e-8;return z
        with self.assertRaisesRegex(Failure,'constraint'):e.accept(t+1e-4,invalid_dense(t+1e-4),invalid_dense)
        self.assertEqual(e.t,t);np.testing.assert_array_equal(e.x,old);np.testing.assert_array_equal(e.quad,np.zeros(6));self.assertEqual(e.history,history)
    def test_wrong_event_bracket_cannot_advance(self):
        e=self.engine();self.boundary(e);x=e.x.copy();x[4]-=.1;old=e.x.copy()
        with self.assertRaisesRegex(Failure,'no oriented crossing'):e.localize(e.t,e.t+.0002,lambda _:x)
        np.testing.assert_array_equal(e.x,old);self.assertFalse(e.candidate)
    def test_missing_entry_method_fails(self):self.assertFalse(entry_agreement([])['passed'])
    def test_event_gate_cannot_be_replaced_by_integral_agreement(self):
        cells=[SimpleNamespace(failure=None,candidate={'t':.1+(3e-6 if k==9 else 0)},history=[{'t':0,'z':[0]*11,'uraw':.1}],rep=str(k),method='dummy') for k in range(10)]
        r=entry_agreement(cells);self.assertFalse(r['passed']);self.assertEqual(r['max_integral_difference'],0);self.assertEqual(r['max_raw_difference'],0)

class AuditChecks(unittest.TestCase):
    def complete_metadata(self):
        return dict(case='high',cfg=CASES['high'],declared_endpoint_s=.107,acceptedTime=.107,failure=None,history=[dict(t=k*.001,z=[0]*11,FT=4,uraw=.1) for k in range(108)],events=[dict(type='sliding-entry',t=.105)],candidate=dict(t=.105,accepted=True))
    def test_truncated_agreement_is_not_full_completion(self):
        a=self.complete_metadata();b=copy.deepcopy(a);b['acceptedTime']=.106;b['history']=b['history'][:-1]
        self.assertTrue(completion(a)['passed']);self.assertFalse(completion(b)['passed'])
        self.assertFalse(compare(a,b)['passed']);self.assertTrue(compare(a,b)['prefix_agreement_only'])
    def test_missing_matrix_cell_is_unqualified(self):self.assertFalse(qualify({})['passed'])
    def test_sparse_history_is_unqualified(self):
        a=self.complete_metadata();a['history']=a['history'][::3]+[a['history'][-1]]
        self.assertFalse(completion(a)['passed'])
    def test_event_and_integral_gates_are_independent(self):
        a=self.complete_metadata();b=copy.deepcopy(a);b['candidate']['t']+=3e-6
        self.assertFalse(compare(a,b)['passed'])
        b=copy.deepcopy(a);b['history'][40]['z'][4]+=1e-8
        self.assertFalse(compare(a,b)['passed'])
    def test_missing_failure_metadata_cannot_pass(self):
        a=self.complete_metadata();del a['failure'];self.assertFalse(completion(a)['passed'])
    def test_changed_command_cannot_pass(self):
        a=copy.deepcopy(self.complete_metadata());a['cfg']['target']+=1;self.assertFalse(completion(a)['passed'])

if __name__=='__main__':unittest.main(verbosity=2)

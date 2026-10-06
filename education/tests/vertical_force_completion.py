"""Negative controls for full-vs-prefix qualification, on frozen raw inputs."""
import sys,json,copy,hashlib,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'education/tools'))
import audit_vertical_force as old
import audit_vertical_force_completion as new
OUT=new.OUT;OUT.mkdir(parents=True,exist_ok=True)
BASE={m:json.loads((new.INPUT/f'baseline-{m}.json').read_text()) for m in new.METHODS}
CHECKS=[]

def truncated(result,end):
    r=copy.deepcopy(result);r['history']=[row for row in r['history'] if row['t']<=end+1e-12];r['acceptedTime']=r['history'][-1]['t'];r['events']=[e for e in r['events'] if e['t']<=r['acceptedTime']+1e-12];return r

class CompletionTests(unittest.TestCase):
    def test_frozen_false_acceptance_truncated_replay(self):
        r=truncated(BASE['DOP853'],.009);legacy=old.compare(BASE['fine'],r);fixed=new.compare(BASE['fine'],r)
        self.assertTrue(legacy['passed']);self.assertTrue(BASE['fine']['failure'] is None)
        self.assertFalse(fixed['passed']);self.assertFalse(fixed['full_passed']);self.assertTrue(fixed['prefix_passed'])
        q=new.qualify({**BASE,'DOP853':r});self.assertEqual(q['status'],'prefix-only')
        (OUT/'negative-truncated-DOP853.json').write_text(json.dumps(r,indent=2)+'\n')
        CHECKS.append(dict(name='truncated-.009s-old-false-acceptance',passed=True,old_comparison=legacy,old_primary_only_full_flag=True,repaired_comparison=fixed,repaired_qualification=q))

    def test_each_required_method_failure_rejects_full(self):
        for m in new.METHODS:
            r=copy.deepcopy(BASE[m]);r['failure']={'code':'synthetic-method-failure','acceptedTime':r['acceptedTime'],'acceptedState':r['history'][-1]['z']}
            q=new.qualify({**BASE,m:r});self.assertFalse(q['full_trajectory']);CHECKS.append(dict(name=f'{m}-failure-rejects-full',passed=True,qualification=q))

    def test_each_missing_endpoint_rejects_full(self):
        for m in new.METHODS:
            r=copy.deepcopy(BASE[m]);r['history']=r['history'][:-1]
            q=new.qualify({**BASE,m:r});self.assertEqual(q['status'],'unqualified');CHECKS.append(dict(name=f'{m}-missing-endpoint-row',passed=True,qualification=q))

    def test_missing_accepted_time(self):
        r=copy.deepcopy(BASE['DOP853']);del r['acceptedTime'];q=new.qualify({**BASE,'DOP853':r});self.assertFalse(q['full_trajectory']);self.assertFalse(q['prefix_qualified']);CHECKS.append(dict(name='missing-accepted-time',passed=True,qualification=q))

    def test_sparse_common_times(self):
        r=copy.deepcopy(BASE['DOP853']);r['history']=[r['history'][i] for i in [0,1,-1]]
        legacy=old.compare(BASE['fine'],r);self.assertTrue(legacy['passed']);fixed=new.compare(BASE['fine'],r);self.assertFalse(fixed['prefix_passed']);self.assertFalse(fixed['passed']);CHECKS.append(dict(name='sparse-common-grid-old-false-acceptance',passed=True,old_comparison=legacy,repaired_comparison=fixed))

    def test_missing_required_method(self):
        q=new.qualify({m:r for m,r in BASE.items() if m!='Radau'});self.assertFalse(q['full_trajectory']);self.assertFalse(q['prefix_qualified']);CHECKS.append(dict(name='missing-required-Radau',passed=True,qualification=q))

    def test_initial_condition_mismatch(self):
        r=copy.deepcopy(BASE['DOP853']);r['cfg']['m']=.6;q=new.qualify({**BASE,'DOP853':r});self.assertEqual(q['status'],'unqualified');CHECKS.append(dict(name='method-config-mismatch',passed=True,qualification=q))

    def test_brake_is_not_early_terminal(self):
        results={m:truncated(json.loads((new.INPUT/f'pulse-{m}.json').read_text()),.231) for m in new.METHODS}
        self.assertTrue(all(any(e['type']=='brake-crossing' for e in r['events']) for r in results.values()))
        q=new.qualify(results);self.assertFalse(q['full_trajectory']);self.assertEqual(q['status'],'prefix-only');CHECKS.append(dict(name='brake-crossing-does-not-replace-protocol-end',passed=True,qualification=q))

    def test_unchanged_completed_and_stopped_cases(self):
        cases=json.loads((new.INPUT/'cases.json').read_text());full=[];prefix=[]
        for case in cases:
            ident=case['id'];q=new.qualify({m:json.loads((new.INPUT/f'{ident}-{m}.json').read_text()) for m in new.METHODS})
            self.assertTrue(q['prefix_qualified'])
            (full if q['full_trajectory'] else prefix).append(ident)
        self.assertEqual(len(full),10);self.assertEqual(prefix,['high','mass-1']);CHECKS.append(dict(name='original-ten-full-two-prefix-preserved',passed=True,full=full,prefix=prefix))

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CompletionTests))
    paths=['education/tests/vertical_force_completion.py','education/tools/audit_vertical_force_completion.py','education/tools/audit_vertical_force.py']
    receipt={'passed':result.wasSuccessful(),'tests_run':result.testsRun,'controls':CHECKS,'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}
    (OUT/'completion-negative-controls.json').write_text(json.dumps(receipt,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)

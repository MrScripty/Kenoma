"""Receipt failure modes; actual Lean qualification is separately mandatory."""
import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
spec=importlib.util.spec_from_file_location('real_checker',ROOT/'tools/check_real_lesson_proofs.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)

class RealReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'proofs').mkdir();(self.root/'dist').mkdir()
        for source,claims,prefix,_ in checker.FAMILIES:
            for name in [source,claims]:
                (self.root/'proofs'/name).write_bytes((ROOT/'proofs'/name).read_bytes())
            (self.root/'dist'/(prefix+'-proof-status.json')).write_text('stale')
        self.patcher=patch.object(checker,'ROOT',self.root);self.patcher.start()
    def tearDown(self):self.patcher.stop();self.tmp.cleanup()
    def compile(self,command,**kwargs):
        source=Path(command[-1]).name
        mapping=next(claims for name,claims,*_ in checker.FAMILIES if name==source)
        declarations=json.loads((self.root/'proofs'/mapping).read_text())
        return SimpleNamespace(returncode=0,stdout='\n'.join("'"+c['theorem']+"' depends on axioms: [propext, Quot.sound]" for c in declarations),stderr='')
    def run_check(self,effect=None):
        with patch.object(checker,'check_existing_real_properties',return_value={'lean_version':'Lean version 4.19.0, fixture','mathlib':{'commit':'locked fixture'}}) as prerequisite,patch.object(checker.subprocess,'run',side_effect=effect or self.compile):
            result=checker.check();prerequisite.assert_called_once();return result
    def no_receipts(self):
        self.assertFalse(list((self.root/'dist').glob('*-proof-status.json')))
    def test_receipts_bind_both_sources_and_maps_after_complete_check(self):
        receipts=self.run_check()
        self.assertEqual(sum(len(r['claims']) for r in receipts),8)
        for r,(_,_,prefix,_) in zip(receipts,checker.FAMILIES):
            self.assertTrue(all(c['status']=='checked' for c in r['claims']))
            self.assertEqual(json.loads((self.root/'dist'/(prefix+'-proof-status.json')).read_text()),r)
    def test_later_compile_failure_removes_every_stale_receipt(self):
        def fail_second(command,**kwargs):
            if command[-1].endswith('MechanicsReal.lean'):return SimpleNamespace(returncode=1,stdout='',stderr='kernel failure fixture')
            return self.compile(command,**kwargs)
        with self.assertRaisesRegex(RuntimeError,'kernel failure'):self.run_check(fail_second)
        self.no_receipts()
    def test_missing_theorem_report_rejects(self):
        with self.assertRaisesRegex(RuntimeError,'Missing kernel'):
            self.run_check(lambda *a,**k:SimpleNamespace(returncode=0,stdout='',stderr=''))
        self.no_receipts()
    def test_admission_rejects_before_compile(self):
        path=self.root/'proofs/MaterialResponseReal.lean';path.write_text(path.read_text()+'\nexample : True := by sorry\n')
        with self.assertRaisesRegex(RuntimeError,'Forbidden'):self.run_check()
        self.no_receipts()
    def test_unapproved_axiom_rejects(self):
        def contaminated(*a,**k):
            r=self.compile(*a,**k);r.stdout=r.stdout.replace('Quot.sound','sorryAx');return r
        with self.assertRaisesRegex(RuntimeError,'Unapproved'):self.run_check(contaminated)
        self.no_receipts()
if __name__=='__main__':unittest.main()

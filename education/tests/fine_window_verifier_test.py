"""Synthetic complete nonzero evidence and refusal-priority tests; no law calls."""
import copy,importlib.util,json,os,pathlib,sys,tempfile,unittest,zipfile,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from fine_window_execution import BUDGET,COMMAND,AUTH,RUN,validate_authorization,require_terminal_evidence
spec=importlib.util.spec_from_file_location('fineverify',ROOT/'tools/verify-fine-window.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
PREF=pathlib.Path(os.environ['FINE_PREFLIGHT_DIR']);pref=json.loads((PREF/'vector-fixture-inputs.json').read_text());plan=json.loads((PREF/'storage-plan.json').read_text())
class FixtureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory(prefix='kenoma-fine-verifier-fixture-');cls.root=pathlib.Path(cls.tmp.name)
  with zipfile.ZipFile(PREF/'synthetic-evidence.zip') as z:z.extractall(cls.root)
  for name in plan['files']:
   if name.endswith('.f64le'):os.link(PREF/name,cls.root/'material'/name)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def damage(self,name,edit):
  p=self.root/'material'/name;original=p.read_bytes();data=json.loads(original);edit(data);p.write_text(json.dumps(data))
  try:
   with self.assertRaises(Exception):v.verify_vectors(self.root,pref,plan)
  finally:p.write_bytes(original)
 def test_complete_nonzero_actual_serialized_producer(self):
  result=v.verify_vectors(self.root,pref,plan);self.assertEqual(result['replayedLogicalRegions'],2002);self.assertEqual(result['newRegions'],1682);self.assertEqual(result['sharedRegions'],320);self.assertEqual(result['specimenCalls'],0)
 def test_missing_patch_element(self):self.damage('control45-S2-hybrid.json',lambda x:x['localElements'].pop())
 def test_omitted_original_region(self):self.damage('control45-197-I1-stage.json',lambda x:x['rowSources'].pop())
 def test_false_pass_flag(self):self.damage('control45-S0-S1-comparison.json',lambda x:x.update({'pass':True}))
 def test_false_allocated_group_pass(self):self.damage('control45-S0-S1-comparison.json',lambda x:x['allocations']['focus'].update({'pass':True}))
 def test_reuse_source_identity(self):self.damage('control45-197-H4-stage.json',lambda x:x['rowSources'][0].update(sha256='0'*64))
 def test_held_reaction_damage(self):
  arrays=json.loads((self.root/'material/saved-arrays.json').read_text());node=arrays['heldNodeOrder'][0];self.damage('control45-S2-hybrid.json',lambda x:x['hybridNodalGradientsN']['total'][node].__setitem__(0,x['hybridNodalGradientsN']['total'][node][0]+1))
 def test_nonfinite_component(self):self.damage('control45-197-I1-s1-region.json',lambda x:x['localGradientsN']['total'][0].__setitem__(0,float('nan')))
 def test_declared_physical_gates_not_relaxed(self):
  self.assertEqual(BUDGET['plannedMaterialCalls'],19716000);self.assertEqual(BUDGET['maximumMaterialCalls'],19716000);self.assertEqual(BUDGET['maximumWallSeconds'],7200);self.assertEqual(BUDGET['maximumOutputBytes'],536870912)
class LifecycleTests(unittest.TestCase):
 def test_old_consumed_authorization_cannot_apply(self):
  old=json.loads((ROOT/'research/selective-fixed-patch-authorization-20261007.json').read_text())
  with self.assertRaises(Exception):validate_authorization(old,{'sourceCommit':'a'*40}, {'verdict':'PASS'})
 def test_missing_new_auth_refuses_without_creating_run(self):
  self.assertFalse(AUTH.exists());self.assertFalse(RUN.exists());p=subprocess.run([sys.executable,str(ROOT/'tools/launch-fine-window.py'),'--execute'],cwd=ROOT,text=True,capture_output=True);self.assertNotEqual(p.returncode,0);self.assertIn('NO_FINE_WINDOW_AUTHORIZATION',p.stderr);self.assertFalse(RUN.exists())
 def test_failure_precedes_hash_or_terminal_validation(self):
  for name in ['external-incomplete.json','supervisor-incomplete.json','material/incomplete-receipt.json']:
   with tempfile.TemporaryDirectory() as tmp:
    p=pathlib.Path(tmp)/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')
    with self.assertRaisesRegex(Exception,'INCOMPLETE_TAKES_PRECEDENCE'):require_terminal_evidence(tmp,BUDGET,COMMAND)
 def test_nonzero_child_or_public_exit_dominates_provisional_success(self):
  for name,body in [('external-exit.json',{'childExitCode':1}),('launcher-exit.json',{'launcherExitCode':1})]:
   with tempfile.TemporaryDirectory() as tmp:
    (pathlib.Path(tmp)/name).write_text(json.dumps(body))
    with self.assertRaisesRegex(Exception,'FAILED_EXIT_TAKES_PRECEDENCE'):require_terminal_evidence(tmp,BUDGET,COMMAND)
if __name__=='__main__':unittest.main(verbosity=2)

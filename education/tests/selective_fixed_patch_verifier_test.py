"""Independent arithmetic damage tests; zero specimen calls."""
import copy,importlib.util,pathlib,sys,unittest,tempfile
TOOLS=pathlib.Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
spec=importlib.util.spec_from_file_location('selective_verify',TOOLS/'verify-selective-fixed-patch.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class SelectiveTests(unittest.TestCase):
 def fixture(self):
  ids=[list(range(10)) for _ in range(252)];direction=[[0.,0.,0.] for _ in range(585)];a={'element':197,'localGradientsN':{t:[[0.,0.,0.] for _ in range(10)] for t in v.TERMS}};b=copy.deepcopy(a)
  for t in v.TERMS:b['localGradientsN'][t][0][0]=2e-5
  units=[('197-whole',a,b)];terms={}
  for t in v.TERMS:
   signed=[[0.,0.,0.] for _ in range(585)];signed[0][0]=-2e-5;triangle=[[0.,0.,0.] for _ in range(585)];triangle[0][0]=2e-5;delta=[[-2e-5,0.,0.]]+[[0.,0.,0.] for _ in range(9)]
   terms[t]={'differences':[{'id':'197-whole','element':197,'localDifferenceN':delta,'directionalDifferenceJ':0.}], 'aggregateDifferenceN':signed,'absoluteUnitDifferenceN':triangle,'aggregateInfinityN':2e-5,'unitTriangleInfinityN':2e-5,'aggregateDirectionalDifferenceJ':0.,'unitTriangleDirectionalDifferenceJ':0.,'pass':False}
  return {'units':1,'terms':terms,'pass':False},units,ids,direction
 def test_nonzero_replay(self):self.assertFalse(v.check_comparison(*self.fixture()))
 def test_false_term_flag(self):
  x,u,i,d=self.fixture();x['terms']['total']['pass']=True
  with self.assertRaises(Exception):v.check_comparison(x,u,i,d)
 def test_false_global_flag(self):
  x,u,i,d=self.fixture();x['pass']=True
  with self.assertRaises(Exception):v.check_comparison(x,u,i,d)
 def test_missing_unit(self):
  x,u,i,d=self.fixture();x['units']=0
  with self.assertRaises(Exception):v.check_comparison(x,u,i,d)
 def test_held_node_damage(self):
  x,u,i,d=self.fixture();x['terms']['total']['aggregateDifferenceN'][0][0]=0.
  with self.assertRaises(Exception):v.check_comparison(x,u,i,d)
 def test_nonfinite_vector(self):
  x,u,i,d=self.fixture();x['terms']['total']['aggregateDifferenceN'][0][0]=float('nan')
  with self.assertRaises(Exception):v.check_comparison(x,u,i,d)
 def test_new_scope_child_log_limit_refuses_and_cleans_up(self):
  from element247_shell_execution import supervise_session,read
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp)/'run';out=supervise_session(['node','-e',"process.stdout.write('x'.repeat(65537));setInterval(()=>{},1000)"],root,TOOLS,'a'*40,'b'*64,v.launcher.BUDGET,execute_log_cap_bytes=65536)
   self.assertEqual(out['exitCode'],1);self.assertNotEqual(out['launcherExitCode'],0);self.assertLessEqual((root/'execute.log').stat().st_size,65536);self.assertIn('EXECUTE_LOG_LIMIT',read(root/'external-incomplete.json')['reason']);self.assertFalse((root/'external-final.json').exists());self.assertFalse((root/'launcher-exit.json').exists())
 def inventories(self):return {'outputInventory':{'row.json':{'sha256':'a'*64,'bytes':1}},'sourceHashes':{'tools/frozen.mjs':'b'*64}},{'sourceHashes':{'tools/frozen.mjs':'b'*64}},{'files':{'row.json':8192,'completion-receipt.json':524288,'terminal-completion.json':16384}}
 def test_complete_output_and_frozen_source_inventories(self):v.check_frozen_inventories(*self.inventories())
 def test_output_hash_subset_refuses(self):
  c,p,s=self.inventories();c['outputInventory']={}
  with self.assertRaises(Exception):v.check_frozen_inventories(c,p,s)
 def test_current_disk_hash_cannot_replace_frozen_source_anchor(self):
  c,p,s=self.inventories();c['sourceHashes']['tools/frozen.mjs']='c'*64
  with self.assertRaises(Exception):v.check_frozen_inventories(c,p,s)
 def test_closed_new_result_names(self):self.assertEqual(v.RESULTS,{'PASS_BOUNDED_SELECTIVE_FIXED_PATCH_AGREEMENT','UNRESOLVED_FIXED_PATCH_INTEGRATION'})
if __name__=='__main__':unittest.main()

"""Pure frozen-vector damage review: no geometry or specimen evaluator."""
import hashlib,importlib.util,json,os,pathlib,sys,tempfile,zipfile
sys.dont_write_bytecode=True
repo=pathlib.Path('/tmp/Kenoma-fine-window-runner/education');pf=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(repo/'tools'));sp=importlib.util.spec_from_file_location('verify',repo/'tools/verify-fine-window.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
pref=json.loads((pf/'vector-fixture-inputs.json').read_text());plan=json.loads((pf/'storage-plan.json').read_text());passed=[]
with tempfile.TemporaryDirectory(prefix='fine-review-damage-') as tmp:
 root=pathlib.Path(tmp)
 with zipfile.ZipFile(pf/'synthetic-evidence.zip') as z:z.extractall(root)
 for name in plan['files']:
  if name.endswith('.f64le'):os.link(pf/name,root/'material'/name)
 def editfile(name,mutate):
  p=root/'material'/name;raw=p.read_bytes();x=json.loads(raw);mutate(x);p.write_text(json.dumps(x));return p,raw
 def expect(label,fn):
  try:fn()
  except Exception as e:passed.append({'case':label,'refusal':str(e)[:200]});return
  raise AssertionError('damage accepted '+label)
 def damage(name,mutate,label):
  p,raw=editfile(name,mutate)
  try:expect(label,lambda:v.verify_vectors(root,pref,plan))
  finally:p.write_bytes(raw)
 damage('control45-S0-S1-comparison.json',lambda x:x['terms']['volume'].update(forceGateN=1),'recorded force gate')
 damage('control45-S0-S1-comparison.json',lambda x:x['terms']['volume'].update(workGateJ=1),'recorded work gate')
 damage('control45-S0-S1-comparison.json',lambda x:x.update(qualification=True),'qualification scope')
 damage('control45-S1-S2-comparison.json',lambda x:x.update(quietIdenticalReuseEarnsNoRefinementCredit=False),'quiet identity credit')
 damage('control45-S2-I1-comparison.json',lambda x:x.update(required=False),'required finest cross-family')
 damage('control45-S2-I1-comparison.json',lambda x:x['common16Diagnostic']['total'].update(triangleN=1),'common16 supplementary arithmetic')
 damage('control45-S2-hybrid.json',lambda x:x['localElements'].pop(),'all16 coverage')
 # Make altered row hash self-consistent to exercise the actual bounds guard.
 row='control45-197-I1-s1-region.json';p,raw=editfile(row,lambda x:x.update(lo=0.3));stage=root/'material/control45-197-I1-stage.json';saved=stage.read_bytes();data=json.loads(saved);data['rowSources'][0].update(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size);stage.write_text(json.dumps(data))
 try:expect('region exact bounds after hash refresh',lambda:v.verify_vectors(root,pref,plan))
 finally:p.write_bytes(raw);stage.write_bytes(saved)
 completion={'originalResultCommit':'38ae8a2e2af57cf33254af987b724824b9d84357','originalResult':'UNRESOLVED_FIXED_PATCH_INTEGRATION','originalTwoShellExecutionExit':1,'unchangedStates':True,'outsidePatchElements':236,'outsidePatchQualified':False,'anatomicalQualification':False,'newNodalFields':0,'nonlinearSolves':0,'optimizerTrials':0,'refits':0}
 for key,value in [('originalResult','PASS'),('originalTwoShellExecutionExit',0),('outsidePatchQualified',True),('anatomicalQualification',True),('newNodalFields',1),('refits',1)]:expect('scope '+key,lambda k=key,z=value:v.verify_scope({**completion,k:z}))
 # Every external file has a bounded named slot, separate from material payload.
 (root/'fixture-inventory.json').unlink();ext=root/'execute.log';ext.write_bytes(b'x'*65537)
 expect('external log byte cap',lambda:v.verify_external_envelopes(root));ext.unlink()
 # fixture-inventory itself is not a production file; remove before name test.
 ext=root/'unplanned';ext.write_bytes(b'x');expect('external unexpected filename',lambda:v.verify_external_envelopes(root));ext.unlink()
print(json.dumps({'verdict':'PASS_INDEPENDENT_DAMAGE_REFUSALS','reviewedSourceCommit':sys.argv[2],'fixtureSourceCommit':pref['sourceCommit'],'cases':passed,'specimenCalls':0,'materialLawInvocations':0,'quadratureGeneratedByReviewer':False,'repoEditsByReviewer':False},indent=2))

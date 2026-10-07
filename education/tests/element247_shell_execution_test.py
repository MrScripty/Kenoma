"""Synthetic process/evidence damage tests. Zero specimen material calls."""
import copy,importlib.util,json,pathlib,shutil,subprocess,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from element247_shell_execution import BUDGET,COMMAND,EvidenceFailure,digest,exclusive_json,launch_session,process_rss,read,require_terminal_evidence,supervise_session
SPEC=importlib.util.spec_from_file_location('shell_verifier',ROOT/'tools/verify-element247-shell.py');VERIFIER=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(VERIFIER)
SOURCE='a'*40;RUN_ID='b'*32
def write(path,data):path.write_text(json.dumps(data,separators=(',',':'))+'\n')
def refresh(root):
 terminal=read(root/'material/terminal-completion.json');terminal['completionSha256']=digest(root/'material/completion-receipt.json');write(root/'material/terminal-completion.json',terminal)
 marker={**terminal,'terminalSha256':digest(root/'material/terminal-completion.json'),'runtime':{**terminal['runtime'],'elapsedMs':3,'lastPhase':'after-terminal-completion-write'}};write(root/'execute.log',marker)
 exit_record=read(root/'external-exit.json');exit_record['logSha256']=digest(root/'execute.log');write(root/'external-exit.json',exit_record);final=read(root/'external-final.json');final['externalExitSha256']=digest(root/'external-exit.json');final['logSha256']=digest(root/'execute.log');write(root/'external-final.json',final)
 launcher=read(root/'launcher-exit.json');launcher['externalFinalSha256']=digest(root/'external-final.json');launcher['launcherLogSha256']=digest(root/'launcher.log');write(root/'launcher-exit.json',launcher)
def terminal_fixture():
 root=pathlib.Path(tempfile.mkdtemp(prefix='kenoma-terminal-fixture-'));(root/'material').mkdir()
 runtime={'plannedCalls':62438,'reservedCalls':62438,'actualConstitutiveCallbacks':62438,'completedConstitutiveCallbacks':62438,'maximumCalls':62500,'maximumWallMs':180000,'elapsedMs':1,'maximumRssBytes':2*1024**3,'peakObservedRssBytes':1000000,'activeBatch':None,'lastPhase':'before-provisional-completion'}
 common={'schema':1,'sourceCommit':SOURCE,'runId':RUN_ID};write(root/'execution-start.json',{**common,'budget':BUDGET,'command':COMMAND,'invocations':1,'clockScope':'pre-authorization-and-source-checks'});write(root/'external-exit.json',{**common,'budget':BUDGET,'command':COMMAND,'invocations':1,'childExitCode':0,'watchdogFailure':None,'elapsedMs':4,'peakObservedChildRssBytes':1000000});write(root/'external-final.json',{**common,'budget':BUDGET,'kind':'EXTERNAL_TERMINAL_COMPLETION','childExitCode':0,'elapsedMs':5});(root/'launcher.log').write_text('synthetic observed launcher');write(root/'launcher-exit.json',{**common,'kind':'OBSERVED_LAUNCHER_EXIT','launcherExitCode':0,'supervisorFailure':None,'elapsedMs':6,'budget':BUDGET,'clockScope':'pre-authorization-and-source-checks'});write(root/'material/completion-receipt.json',{**common,'result':'UNRESOLVED_ELEMENT247_SHELL_INTEGRATION','runtime':runtime,'fixtureOnly':True});write(root/'material/terminal-completion.json',{**common,'kind':'TERMINAL_COMPLETION','result':'UNRESOLVED_ELEMENT247_SHELL_INTEGRATION','runtime':{**runtime,'elapsedMs':2,'lastPhase':'after-provisional-completion-write'}});refresh(root);return root
class EvidenceTests(unittest.TestCase):
 def setUp(self):self.root=terminal_fixture()
 def test_completed_synthetic_terminal_evidence_is_accepted(self):self.assertEqual(require_terminal_evidence(self.root)['completion']['result'],'UNRESOLVED_ELEMENT247_SHELL_INTEGRATION')
 def test_missing_final_child_marker_or_external_final_refuses(self):
  for file in ['material/terminal-completion.json','external-exit.json','external-final.json','launcher-exit.json']:
   with self.subTest(file=file):r=terminal_fixture();(r/file).unlink();self.assertRaises(EvidenceFailure,require_terminal_evidence,r)
 def test_provisional_receipt_alone_is_never_completion(self):
  for p in ['material/terminal-completion.json','external-final.json','external-exit.json']: (self.root/p).unlink()
  self.assertRaises(EvidenceFailure,require_terminal_evidence,self.root)
 def test_material_incomplete_overrides_complete_hashes_and_zero_external_exit(self):write(self.root/'material/incomplete-receipt.json',{'reason':'late resource failure'});self.assertRaisesRegex(EvidenceFailure,'MATERIAL_INCOMPLETE_TAKES_PRECEDENCE',require_terminal_evidence,self.root)
 def test_external_postfinal_incomplete_overrides_everything(self):write(self.root/'external-incomplete.json',{'reason':'post-final bound failure'});self.assertRaisesRegex(EvidenceFailure,'EXTERNAL_INCOMPLETE_TAKES_PRECEDENCE',require_terminal_evidence,self.root)
 def test_failed_exit_has_precedence_over_missing_terminal_and_valid_earlier_receipts(self):
  r=read(self.root/'external-exit.json');r['childExitCode']=7;write(self.root/'external-exit.json',r);(self.root/'material/terminal-completion.json').unlink();self.assertRaisesRegex(EvidenceFailure,'EXTERNAL_FAILED_EXIT_TAKES_PRECEDENCE',require_terminal_evidence,self.root)
 def test_duplicate_or_nonfinal_stdout_marker_refuses(self):
  original=(self.root/'execute.log').read_bytes()
  for data in [original+original,original+b'{"kind":"AFTER_COMPLETION"}\n',b'{"kind":"STAGE_COMPLETED"}\n']:
   with self.subTest(data=data):r=terminal_fixture();(r/'execute.log').write_bytes(data);e=read(r/'external-exit.json');e['logSha256']=digest(r/'execute.log');write(r/'external-exit.json',e);f=read(r/'external-final.json');f.update(externalExitSha256=digest(r/'external-exit.json'),logSha256=digest(r/'execute.log'));write(r/'external-final.json',f);o=read(r/'launcher-exit.json');o['externalFinalSha256']=digest(r/'external-final.json');write(r/'launcher-exit.json',o);self.assertRaisesRegex(EvidenceFailure,'STDOUT_COMPLETION',require_terminal_evidence,r)
 def test_reserved_entered_completed_counters_are_not_interchangeable(self):
  for counter in ['reservedCalls','actualConstitutiveCallbacks','completedConstitutiveCallbacks']:
   r=terminal_fixture();c=read(r/'material/completion-receipt.json');c['runtime'][counter]-=1;write(r/'material/completion-receipt.json',c);refresh(r);self.assertRaisesRegex(EvidenceFailure,'CALLBACK_COUNTS',require_terminal_evidence,r)
 def test_frozen_child_and_external_wall_rss_bounds_refuse(self):
  for file,key,value in [('material/completion-receipt.json','elapsedMs',180000),('material/completion-receipt.json','peakObservedRssBytes',2*1024**3+1),('external-exit.json','elapsedMs',180000),('external-exit.json','peakObservedChildRssBytes',2*1024**3+1)]:
   r=terminal_fixture();obj=read(r/file)
   if file.startswith('material/'):obj['runtime'][key]=value
   else:obj[key]=value
   write(r/file,obj);refresh(r);self.assertRaises(EvidenceFailure,require_terminal_evidence,r)
 def test_changed_hash_or_invocation_refuses(self):
  terminal=read(self.root/'material/terminal-completion.json');terminal['runId']='c'*32;write(self.root/'material/terminal-completion.json',terminal);refresh(self.root);self.assertRaises(EvidenceFailure,require_terminal_evidence,self.root)
 def test_verifier_checks_failure_before_source_or_vector_data(self):
  write(self.root/'material/incomplete-receipt.json',{'reason':'callback failed'});self.assertRaisesRegex(EvidenceFailure,'MATERIAL_INCOMPLETE_TAKES_PRECEDENCE',VERIFIER.verify,ROOT,self.root)
 def test_failed_actual_launcher_exit_overrides_perfect_material_child_chain(self):
  observed=read(self.root/'launcher-exit.json');observed['launcherExitCode']=7;write(self.root/'launcher-exit.json',observed);self.assertRaisesRegex(EvidenceFailure,'LAUNCHER_FAILED_EXIT_TAKES_PRECEDENCE',require_terminal_evidence,self.root)
 def test_pending_external_completion_cannot_replace_observed_published_acceptance(self):
  (self.root/'launcher-exit.json').unlink();(self.root/'external-final.json').rename(self.root/'external-final.pending.json');self.assertRaises(EvidenceFailure,require_terminal_evidence,self.root)
class LauncherTests(unittest.TestCase):
 def root(self):return pathlib.Path(tempfile.mkdtemp(prefix='kenoma-watchdog-fixture-'))/'new-run'
 def budget(self,**kwargs):return {**BUDGET,**kwargs}
 def test_real_small_synthetic_process_records_external_exit_and_final(self):
  r=self.root();command=[sys.executable,'-c','print("synthetic callback only")'];result=supervise_session(command,r,ROOT,SOURCE,'d'*64,self.budget(maximumWallSeconds=5));self.assertEqual(result['exitCode'],0);self.assertEqual(read(r/'external-exit.json')['childExitCode'],0);self.assertEqual(read(r/'launcher-exit.json')['launcherExitCode'],0);self.assertTrue((r/'external-final.json').exists());self.assertRaises(EvidenceFailure,require_terminal_evidence,r,budget=self.budget(maximumWallSeconds=5),command=command)
 def test_real_small_process_nonzero_exit_is_preserved_without_retry(self):
  r=self.root();result=launch_session([sys.executable,'-c','import sys;print("partial fixture");sys.exit(7)'],r,ROOT,SOURCE,'d'*64,self.budget(maximumWallSeconds=5));self.assertEqual(result['childExitCode'],7);self.assertEqual(result['exitCode'],1);self.assertTrue((r/'external-incomplete.json').exists());self.assertEqual((r/'execute.log').read_text(),'partial fixture\n');self.assertRaisesRegex(EvidenceFailure,'INCOMPLETE_TAKES_PRECEDENCE',require_terminal_evidence,r);self.assertRaisesRegex(EvidenceFailure,'PRESERVE',launch_session,['unused'],r,ROOT,SOURCE,'d'*64)
 def test_real_watchdog_refuses_wall_and_storage_without_retry(self):
  for kind,code,budget in [('wall','import time;print("partial",flush=True);time.sleep(.5)',self.budget(maximumWallSeconds=.1)),('storage','import sys;sys.stdout.write("x"*20000)',self.budget(maximumWallSeconds=5,maximumOutputBytes=2*1024**2+4096))]:
   with self.subTest(kind=kind):r=self.root();out=launch_session([sys.executable,'-c',code],r,ROOT,SOURCE,'d'*64,budget);self.assertEqual(out['exitCode'],1);self.assertIn(kind.upper(),read(r/'external-incomplete.json')['reason']);self.assertFalse((r/'external-final.json').exists())
 def test_watchdog_rss_refusal_and_after_final_write_failure_take_precedence(self):
  r=self.root()
  with patch('element247_shell_execution.process_rss',return_value=2*1024**3+1):out=launch_session([sys.executable,'-c','import time;time.sleep(.1)'],r,ROOT,SOURCE,'d'*64,self.budget(maximumWallSeconds=5))
  self.assertEqual(out['exitCode'],1);self.assertIn('RSS',read(r/'external-incomplete.json')['reason'])
  r=self.root();from element247_shell_execution import exclusive_json as actual_write
  def late(path,value):
   actual_write(path,value)
   if pathlib.Path(path).name=='external-final.pending.json':raise EvidenceFailure('SYNTHETIC_POST_FINAL_WALL_LIMIT')
  with patch('element247_shell_execution.exclusive_json',side_effect=late):out=launch_session([sys.executable,'-c','print("synthetic")'],r,ROOT,SOURCE,'d'*64,self.budget(maximumWallSeconds=5))
  self.assertEqual(out['exitCode'],1);self.assertTrue((r/'external-final.pending.json').exists());self.assertFalse((r/'external-final.json').exists());self.assertRaisesRegex(EvidenceFailure,'INCOMPLETE_TAKES_PRECEDENCE',require_terminal_evidence,r)
 def test_public_launcher_refuses_missing_authorization_without_creating_run(self):
  self.assertFalse((ROOT/'research/element247-shell-execution-authorization-20261007.json').exists());run=ROOT/'review/element247-shell-run-20261007';self.assertFalse(run.exists());p=subprocess.run([sys.executable,str(ROOT/'tools/launch-element247-shell.py'),'--execute'],capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('NO_MATERIAL_EXECUTION_AUTHORIZATION',p.stderr);self.assertFalse(run.exists())
def perfect_chain_worker(directory,exit_code=0):
 # Real worker exits with an otherwise valid synthetic child evidence chain.
 code=f'import importlib.util,pathlib,shutil,os; s=importlib.util.spec_from_file_location("fixture",{str(pathlib.Path(__file__).resolve())!r}); m=importlib.util.module_from_spec(s);s.loader.exec_module(m);src=m.terminal_fixture();dst=pathlib.Path({str(directory)!r});shutil.copytree(src,dst);(dst/"launcher.log").unlink();(dst/"launcher-exit.json").unlink();os.rename(dst/"external-final.json",dst/"external-final.pending.json");os._exit({exit_code})'
 return [sys.executable,'-c',code]
class SuccessorProcessTests(unittest.TestCase):
 def root(self):return pathlib.Path(tempfile.mkdtemp(prefix='kenoma-supervised-fixture-'))/'new-run'
 def test_supervisor_observes_real_worker_zero_exit_before_acceptance(self):
  r=self.root();out=supervise_session(COMMAND,r,ROOT,SOURCE,'d'*64,fixture_worker=perfect_chain_worker(r));self.assertEqual(out['exitCode'],0);e=require_terminal_evidence(r);self.assertEqual(e['launcherExit']['launcherExitCode'],0);self.assertFalse((r/'launcher-acceptance.pending.json').exists())
 def test_nonzero_real_launcher_and_unwritable_failure_record_cannot_qualify(self):
  r=self.root();actual=exclusive_json
  def refuse_failure(p,v):
   if pathlib.Path(p).name=='supervisor-incomplete.json':raise OSError('synthetic failure-record unavailable')
   return actual(p,v)
  with patch('element247_shell_execution.exclusive_json',side_effect=refuse_failure):out=supervise_session(COMMAND,r,ROOT,SOURCE,'d'*64,fixture_worker=perfect_chain_worker(r,7))
  self.assertEqual(out['exitCode'],1);self.assertEqual(out['launcherExitCode'],7);self.assertFalse((r/'supervisor-incomplete.json').exists());self.assertFalse((r/'launcher-exit.json').exists());self.assertRaisesRegex(EvidenceFailure,'LAUNCHER_FAILED_EXIT_TAKES_PRECEDENCE',require_terminal_evidence,r)
 def test_failed_acceptance_publish_and_unwritable_refusal_stay_closed(self):
  r=self.root();actual=exclusive_json
  def refuse_failure(p,v):
   if pathlib.Path(p).name=='supervisor-incomplete.json':raise OSError('synthetic unavailable failure receipt')
   return actual(p,v)
  import os
  rename=os.rename
  def truncated_publish(src,dst):
   if pathlib.Path(dst).name=='launcher-exit.json':raise OSError('synthetic second publish failure')
   return rename(src,dst)
  with patch('element247_shell_execution.exclusive_json',side_effect=refuse_failure),patch('element247_shell_execution.os.rename',side_effect=truncated_publish):out=supervise_session(COMMAND,r,ROOT,SOURCE,'d'*64,fixture_worker=perfect_chain_worker(r))
  self.assertEqual(out['exitCode'],1);self.assertTrue((r/'external-final.json').exists());self.assertFalse((r/'launcher-exit.json').exists());self.assertFalse((r/'supervisor-incomplete.json').exists());self.assertRaisesRegex(EvidenceFailure,'MISSING_TERMINAL_OR_EXTERNAL_EVIDENCE:launcher-exit.json',require_terminal_evidence,r)
 def test_postcandidate_failure_and_failed_incomplete_write_leave_only_provisional_evidence(self):
  r=self.root();actual=exclusive_json
  def refuse(p,v):
   if pathlib.Path(p).name=='external-incomplete.json':raise OSError('synthetic failed failure write')
   actual(p,v)
   if pathlib.Path(p).name=='external-final.pending.json':raise EvidenceFailure('SYNTHETIC_LATE_CHECK_FAILURE')
  with patch('element247_shell_execution.exclusive_json',side_effect=refuse):out=launch_session([sys.executable,'-c','print("synthetic")'],r,ROOT,SOURCE,'d'*64)
  self.assertEqual(out['exitCode'],1);self.assertTrue((r/'external-final.pending.json').exists());self.assertFalse((r/'external-final.json').exists());self.assertFalse((r/'external-incomplete.json').exists());self.assertRaises(EvidenceFailure,require_terminal_evidence,r)
 def test_sigkill_preserves_durable_files_and_does_not_promise_in_memory_current_shell(self):
  r=self.root();script='import pathlib,os,signal; p=pathlib.Path('+repr(str(r))+')/"material";p.mkdir();f=(p/"durable-shell.json").open("w");f.write("{\\"completed\\":true}\\n");f.flush();os.fsync(f.fileno());f.close();current_shell_in_ram=[1,2,3];os.kill(os.getpid(),signal.SIGKILL)'
  out=supervise_session([sys.executable,'-c',script],r,ROOT,SOURCE,'d'*64);self.assertEqual(out['exitCode'],1);self.assertEqual(read(r/'external-exit.json')['childExitCode'],-9);self.assertEqual(read(r/'material/durable-shell.json'),{'completed':True});self.assertFalse((r/'material/current-shell.json').exists());self.assertRaises(EvidenceFailure,require_terminal_evidence,r,command=[sys.executable,'-c',script])
 def test_unreadable_live_rss_fails_closed_and_zombie_is_explicit(self):
  for error in [FileNotFoundError('missing proc'),PermissionError('unreadable proc')]:
   with patch('element247_shell_execution.pathlib.Path.read_text',side_effect=error):self.assertRaisesRegex(EvidenceFailure,'RSS_UNREADABLE',process_rss,123)
  with patch('element247_shell_execution.pathlib.Path.read_text',return_value='State:\tS (sleeping)\n'):self.assertRaisesRegex(EvidenceFailure,'RSS_FIELD_MISSING',process_rss,123)
  with patch('element247_shell_execution.pathlib.Path.read_text',return_value='State:\tZ (zombie)\n'):self.assertEqual(process_rss(123),0)
  r=self.root()
  with patch('element247_shell_execution.process_rss',side_effect=EvidenceFailure('LIVE_CHILD_RSS_UNREADABLE')):out=launch_session([sys.executable,'-c','import time;time.sleep(.1)'],r,ROOT,SOURCE,'d'*64)
  self.assertEqual(out['exitCode'],1);self.assertIn('RSS_UNREADABLE',read(r/'external-incomplete.json')['reason'])
 def test_watchdog_stops_inherited_child_after_launcher_already_exited(self):
  import os,signal,time
  r=self.root();script='import pathlib,subprocess,sys,os; r=pathlib.Path('+repr(str(r))+');r.mkdir(); child=subprocess.Popen([sys.executable,"-c","import time;time.sleep(5)"]);(r/"orphan-pid").write_text(str(child.pid));os._exit(0)'
  pid=None
  try:
   out=supervise_session(COMMAND,r,ROOT,SOURCE,'d'*64,{**BUDGET,'maximumWallSeconds':.3},fixture_worker=[sys.executable,'-c',script]);pid=int((r/'orphan-pid').read_text());self.assertEqual(out['exitCode'],1);self.assertEqual(out['launcherExitCode'],0);self.assertIn('WALL_LIMIT',read(r/'launcher-exit.pending.json')['supervisorFailure']);self.assertFalse((r/'launcher-exit.json').exists())
   deadline=time.monotonic()+1
   while time.monotonic()<deadline:
    try:status=pathlib.Path(f'/proc/{pid}/status').read_text()
    except FileNotFoundError:break
    if any(line.startswith('State:') and line.split()[1] in ['Z','X'] for line in status.splitlines()):break
    time.sleep(.01)
   else:self.fail('inherited child remains live after supervising watchdog refusal')
  finally:
   if pid is not None:
    try:os.kill(pid,signal.SIGKILL)
    except ProcessLookupError:pass
 def test_wall_scope_includes_time_spent_before_launcher_and_source_checks(self):
  import time
  r=self.root();self.assertRaisesRegex(EvidenceFailure,'PRELAUNCH_WALL_LIMIT',supervise_session,COMMAND,r,ROOT,SOURCE,'d'*64,started_at=time.monotonic()-181);self.assertFalse(r.exists())
 def test_every_refusal_stops_separate_pipe_or_devnull_node_child(self):
  import os,signal,time
  from contextlib import ExitStack
  cases=[('PIPE',7,None),('PIPE',-9,None),('DEVNULL',7,None),('DEVNULL',-9,None),('PIPE',0,None),('PIPE',0,'observed-write'),('PIPE',7,'failure-write'),('PIPE',0,'publish')]
  for output,exit_code,damage in cases:
   with self.subTest(output=output,exit_code=exit_code,damage=damage):
    r=self.root();pid=None;ready=r/'node-ready';node='require("node:fs").writeFileSync('+json.dumps(str(ready))+',"ready");setTimeout(()=>{},10000)'
    prefix=perfect_chain_worker(r)[2].removesuffix('os._exit(0)') if damage=='publish' else 'import pathlib,os;pathlib.Path('+repr(str(r))+').mkdir();'
    script=prefix+'import subprocess,sys,time,signal,json;child=subprocess.Popen(["node","-e",'+repr(node)+'],stdout=subprocess.'+output+',stderr=subprocess.STDOUT);p=pathlib.Path('+repr(str(r))+');(p/"child-process.json").write_text(json.dumps({"pid":child.pid,"group":os.getpgid(child.pid),"worker":os.getpid()}));deadline=time.monotonic()+3\nwhile not (p/"node-ready").exists():\n if time.monotonic()>deadline:os._exit(8)\n time.sleep(.005)\n'+('os.kill(os.getpid(),signal.SIGKILL)' if exit_code==-9 else f'os._exit({exit_code})')
    actual_write=exclusive_json;actual_rename=os.rename
    def refuse_write(p,v):
     if (damage=='observed-write' and pathlib.Path(p).name=='launcher-exit.pending.json') or (damage=='failure-write' and pathlib.Path(p).name=='supervisor-incomplete.json'):raise OSError('synthetic unavailable evidence write')
     return actual_write(p,v)
    def refuse_publish(src,dst):
     if pathlib.Path(dst).name=='launcher-exit.json':raise OSError('synthetic acceptance publication failure')
     return actual_rename(src,dst)
    try:
     with ExitStack() as stack:
      if damage in ['observed-write','failure-write']:stack.enter_context(patch('element247_shell_execution.exclusive_json',side_effect=refuse_write))
      if damage=='publish':stack.enter_context(patch('element247_shell_execution.os.rename',side_effect=refuse_publish))
      out=supervise_session(COMMAND,r,ROOT,SOURCE,'d'*64,{**BUDGET,'maximumWallSeconds':5},fixture_worker=[sys.executable,'-c',script])
     child=read(r/'child-process.json');pid=child['pid'];self.assertEqual(child['group'],child['worker']);self.assertTrue(ready.exists());self.assertEqual(out['exitCode'],1);self.assertEqual(out['launcherExitCode'],exit_code);self.assertIsNone(out['groupCleanupFailure']);self.assertFalse((r/'launcher-exit.json').exists());self.assertNotIn('WALL',out['failure'])
     if (r/'launcher-exit.pending.json').exists():self.assertIsNone(read(r/'launcher-exit.pending.json')['supervisorFailure'])
     self.assertRaises(EvidenceFailure,require_terminal_evidence,r)
     deadline=time.monotonic()+1
     while time.monotonic()<deadline:
      try:status=pathlib.Path(f'/proc/{pid}/status').read_text()
      except FileNotFoundError:break
      if any(line.startswith('State:') and line.split()[1] in ['Z','X'] for line in status.splitlines()):break
      time.sleep(.01)
     else:self.fail('separate-pipe Node child survived supervisor refusal')
    finally:
     if pid is None and (r/'child-process.json').exists():pid=read(r/'child-process.json')['pid']
     if pid is not None:
      try:os.kill(pid,signal.SIGKILL)
      except ProcessLookupError:pass
def full_retained_fixture():
 """Invented zero-force records with real accepted reference weights/arrays.
 All fixture counters are synthetic evidence, not evaluated material calls.
 The authorization record is created only in this isolated temporary fixture.
 """
 root=pathlib.Path(tempfile.mkdtemp(prefix='kenoma-full-evidence-fixture-'));run=terminal_fixture();d=run/'material'
 inputs=['data/anatomical-arm-v1/generated/arm-reference.json','research/fixed-field-integration-protocol-20261007-inputs.json','review/fixed-field-integration-run-20261007/saved-arrays.json','review/element247-shell-protocol-20261007/confirmation-preflight.json']
 for recipe,_,_ in VERIFIER.RECIPES:inputs.extend([f'review/element247-shell-protocol-20261007/{recipe}-normalized-points.f64le',f'review/element247-shell-protocol-20261007/{recipe}-reference-weights.f64le'])
 for p in inputs:(root/p).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,root/p)
 manifest_path='research/element247-shell-lifetime-20261007-inputs.json';manifest={'inputs':{p:digest(root/p) for p in inputs},'newSources':[manifest_path],'fixtureOnly':True};write(root/manifest_path,manifest)
 pref_dir=root/'review/element247-shell-lifetime-20261007';pref_dir.mkdir(parents=True);(pref_dir/'js-tests.log').write_text('synthetic fixture');(pref_dir/'python-tests.log').write_text('synthetic fixture')
 source_hashes={p:digest(root/p) for p in inputs+[manifest_path]};pref={'sourceCommit':SOURCE,'sourceHashes':source_hashes,'result':'PASS_ELEMENT247_SHELL_RUNTIME_PREFLIGHT_NO_MATERIAL_ASSEMBLY','specimenConstitutiveCalls':0,'tests':{'fail':0},'fixtureOnly':True};write(pref_dir/'runtime-preflight.json',pref)
 auth_path='research/element247-shell-execution-authorization-20261007.json';auth={'authorized':True,'invocations':1,'parentThread':'01a103c3-a2e6-7606-8c1e-06987ac710f1','budget':BUDGET,'runnerSourceCommit':SOURCE,'runtimePreflightSha256':digest(pref_dir/'runtime-preflight.json'),'fixtureOnly':True};write(root/auth_path,auth)
 hashes={**source_hashes,**{p:digest(root/p) for p in ['review/element247-shell-lifetime-20261007/runtime-preflight.json','review/element247-shell-lifetime-20261007/js-tests.log','review/element247-shell-lifetime-20261007/python-tests.log',auth_path]}}
 mesh=next(s for s in read(root/inputs[0])['muscles'] if s['element_id']=='FJ1486');arrays=read(root/inputs[2]);geo=read(root/inputs[3]);zero=lambda n:[[0.,0.,0.] for _ in range(n)];vectors=lambda n:{t:zero(n) for t in VERIFIER.TERMS};energy=lambda:{t:0. for t in VERIFIER.TERMS}
 write(d/'material-start.json',{'schema':1,'sourceCommit':SOURCE,'runnerSourceCommit':SOURCE,'sourceHashes':hashes,'runId':RUN_ID,'budget':BUDGET,'authorizationSha256':digest(root/auth_path),'activation':1,'material':read(root/inputs[1])['material'],'fixtureOnly':True});write(d/'saved-arrays.json',arrays);stages={}
 for recipe,depth,count in VERIFIER.RECIPES:
  shutil.copyfile(root/f'review/element247-shell-protocol-20261007/{recipe}-normalized-points.f64le',d/f'{recipe}-normalized-points.f64le');inventory=next(i for i in geo['ruleInventories'] if i['recipe']['id']==recipe);weights=(root/f'review/element247-shell-protocol-20261007/{recipe}-reference-weights.f64le').read_bytes()
  for state in ['control45','terminal46']:
   groups=[{'shell':s,'originalShells':[],'localGradientsN':vectors(10),'energiesJ':energy()} for s in [f's{i}' for i in range(1,21)]+['core']];names=[]
   for s in inventory['perShell']:
    name=f'{recipe}-{state}-{s["id"]}-shell.json';names.append(name);group=next(g for g in groups if g['shell']==s['comparisonShell']);group['originalShells'].append(s['id']);write(d/name,{'element':247,'shell':s['id'],'lo':s['lo'],'hi':s['hi'],'comparisonShell':s['comparisonShell'],'pointCount':s['points'],'minimumSampleJ':1.,'localGradientsN':vectors(10),'energiesJ':energy(),'terminalDirectionalDerivativesJ':energy(),'fixtureOnly':True});offset=s['firstPoint']*8;(d/f'{recipe}-{state}-{s["id"]}-weights.f64le').write_bytes(weights[offset:offset+8*s['points']])
   stage={'element':247,'state':state,'recipe':inventory['recipe'],'pointCount':count,'originalShells':[s['id'] for s in inventory['perShell']],'localShellFiles':names,'comparisonShells':groups,'localGradientsN':vectors(10),'nodalGradientsN':vectors(585),'energiesJ':energy(),'terminalDirectionalDerivativesJ':energy(),'reconstruction':{'gates':{'forceN':1e-8,'energyJ':1e-9}},'fixtureOnly':True};write(d/f'{recipe}-{state}-assembly.json',stage);stages[(recipe,state)]=stage
 comparisons=[]
 for state in ['control45','terminal46']:
  for a,b in VERIFIER.PAIRS:
   terms={t:{'differences':[{'shell':s['shell'],'localDifferenceN':zero(10),'directionalDifferenceJ':0.} for s in stages[(a,state)]['comparisonShells']],'aggregateDifferenceN':zero(10),'absoluteShellDifferenceN':zero(10),'scatteredDifferenceN':zero(585),'aggregateInfinityN':0.,'shellTriangleInfinityN':0.,'aggregateDirectionalDifferenceJ':0.,'shellTriangleDirectionalDifferenceJ':0.,'forceGateN':1e-5,'derivativeGateJ':5.492029235357012e-7,'pass':True} for t in VERIFIER.TERMS};comparisons.append({'state':state,'a':a,'b':b,'required':a!='C44','terms':terms,'pass':True})
 write(d/'shell-vector-comparisons.json',{'comparisons':comparisons,'fixtureOnly':True});c=read(d/'completion-receipt.json');c.update(runnerSourceCommit=SOURCE,sourceHashes=hashes,patchQualification=False,priorPatchResult='UNRESOLVED_FIXED_PATCH_INTEGRATION',unchangedStates=True,newNodalFields=0,nonlinearSolves=0,optimizerTrials=0,refits=0,failedComparisons=[],result='PASS_BOUNDED_ELEMENT247_METHOD_AGREEMENT');write(d/'completion-receipt.json',c);t=read(d/'terminal-completion.json');t['result']=c['result'];write(d/'terminal-completion.json',t);refresh_full(run);return root,run
def refresh_full(run):
 d=run/'material';c=read(d/'completion-receipt.json');c['outputInventory']={p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in d.iterdir() if p.name not in ['completion-receipt.json','terminal-completion.json']};write(d/'completion-receipt.json',c);refresh(run)
class FullVerifierTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.root,cls.base=full_retained_fixture()
 def fixture(self):run=pathlib.Path(tempfile.mkdtemp(prefix='kenoma-full-verifier-copy-'))/'run';shutil.copytree(self.base,run);return run
 def test_complete_synthetic_inventory_scatter_cancellation_and_terminal_path_passes(self):
  result=VERIFIER.verify(self.root,self.base);self.assertEqual(result['materialCalls'],0);self.assertEqual(result['outputHashes'],446);self.assertFalse(result['patchQualification'])
 def test_nonzero_cancellation_heavy_js_records_verify_with_frozen_python_reduction_order(self):
  root,run=full_retained_fixture();mesh=next(s for s in read(root/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if s['element_id']=='FJ1486');ids=mesh['elements_ten_node'][247];p=subprocess.run(['node',str(ROOT/'tests/element247_shell_cancellation_fixture.mjs'),str(run/'material'),json.dumps(ids)],capture_output=True,text=True);self.assertEqual(p.returncode,0,p.stderr);summary=json.loads(p.stdout);self.assertEqual(summary['materialCalls'],0);self.assertGreater(summary['maximumFixtureForceN'],1e15);self.assertTrue(any(x!=0 for x in summary['nonzeroScatteredTotalN']));self.assertGreater(summary['comparisonTotalDifferenceN'],0);refresh_full(run);result=VERIFIER.verify(root,run);self.assertEqual(result['materialCalls'],0);self.assertFalse(result['patchQualification']);self.assertEqual(VERIFIER.sequential_sum([2**54,1.,-2**54]),0);self.assertEqual(__import__('math').fsum([2**54,1.,-2**54]),1)
 def test_damaged_held_node_scatter_is_rejected_after_all_hashes_are_refreshed(self):
  run=self.fixture();p=run/'material/C55-terminal46-assembly.json';a=read(p);node=read(self.root/'review/fixed-field-integration-run-20261007/saved-arrays.json')['heldNodeOrder'][0];a['nodalGradientsN']['matrix'][node][0]=.0001;a['nodalGradientsN']['total'][node][0]=.0001;write(p,a);refresh_full(run);self.assertRaises(EvidenceFailure,VERIFIER.verify,self.root,run)
 def test_missing_shell_and_forged_cancellation_pass_flag_are_rejected_with_valid_hashes(self):
  run=self.fixture();p=run/'material/C44-control45-s1-shell.json';p.unlink();refresh_full(run);self.assertRaisesRegex(EvidenceFailure,'OUTPUT_INVENTORY',VERIFIER.verify,self.root,run)
  run=self.fixture();p=run/'material/shell-vector-comparisons.json';data=read(p);data['comparisons'][1]['terms']['total']['shellTriangleInfinityN']=0.1;write(p,data);refresh_full(run);self.assertRaisesRegex(EvidenceFailure,'ARITHMETIC_MISMATCH',VERIFIER.verify,self.root,run)
if __name__=='__main__':unittest.main(verbosity=2)

"""External process enforcement and terminal evidence; standard library only.
No law, nodal update, retry, or material evaluation occurs in these helpers.
"""
import hashlib,json,math,os,pathlib,re,selectors,signal,subprocess,sys,time,uuid

BUDGET={'plannedMaterialCalls':62438,'maximumMaterialCalls':62500,'maximumWallSeconds':180,'nodeHeapMiB':1024,'maximumRssBytes':2147483648,'maximumOutputBytes':67108864,'invocations':1}
COMMAND=['node','--max-old-space-size=1024','tools/run-element247-shell.mjs','--execute']
RESULTS={'PASS_BOUNDED_ELEMENT247_METHOD_AGREEMENT','UNRESOLVED_ELEMENT247_SHELL_INTEGRATION'}
class EvidenceFailure(Exception):pass
def need(condition,message):
 if not condition:raise EvidenceFailure(message)
def digest(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(pathlib.Path(path).read_text())
def tree_bytes(root):
 total=0
 for p in pathlib.Path(root).rglob('*'):
  need(not p.is_symlink(),'OUTPUT_SYMLINK')
  if p.is_file():total+=p.stat().st_size
  else:need(p.is_dir(),'OUTPUT_ENTRY')
 return total
def exclusive_json(path,value):
 data=(json.dumps(value,separators=(',',':'),allow_nan=False)+'\n').encode();need(len(data)<=65536,'EXTERNAL_RECEIPT_RESERVE')
 with pathlib.Path(path).open('xb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
def process_rss(pid):
 try:
  text=pathlib.Path(f'/proc/{pid}/status').read_text()
 except (FileNotFoundError,PermissionError,OSError) as error:raise EvidenceFailure('LIVE_CHILD_RSS_UNREADABLE') from error
 state=next((line.split()[1] for line in text.splitlines() if line.startswith('State:')),None)
 if state in ['Z','X']:return 0  # Positively observed exited/zombie address space.
 for line in text.splitlines():
  if line.startswith('VmRSS:'):return int(line.split()[1])*1024
 raise EvidenceFailure('LIVE_CHILD_RSS_FIELD_MISSING')
def launch_session(command,directory,cwd,source_commit,authorization_sha256,budget=BUDGET,started_at=None,isolate_child=True):
 """Single fresh invocation. A nonzero child exit or any watchdog/postwrite
 failure dominates all provisional numerical receipts. Small fixtures may
 supply tighter budgets; the public launcher freezes BUDGET and COMMAND.
 """
 root=pathlib.Path(directory);need(not root.exists(),'PRESERVE_EXISTING_INVOCATION');started=time.monotonic() if started_at is None else started_at;root.mkdir(parents=True);run_id=uuid.uuid4().hex;child=None;failure=None;peak_rss=0;code=None
 normal_limit=budget['maximumOutputBytes']-2*1024**2
 def wall_ms():return (time.monotonic()-started)*1000
 def check():
  nonlocal peak_rss
  need(wall_ms()<budget['maximumWallSeconds']*1000,'EXTERNAL_WALL_LIMIT')
  need(tree_bytes(root)<=normal_limit,'EXTERNAL_STORAGE_LIMIT')
  if child is not None and child.poll() is None:
   peak_rss=max(peak_rss,process_rss(child.pid));need(peak_rss<=budget['maximumRssBytes'],'EXTERNAL_RSS_LIMIT')
 try:
  exclusive_json(root/'execution-start.json',{'schema':1,'invocations':1,'sourceCommit':source_commit,'authorizationSha256':authorization_sha256,'budget':budget,'command':command,'runId':run_id,'clockScope':'pre-authorization-and-source-checks','startedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())});check()
  child=subprocess.Popen(command,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=isolate_child);selector=selectors.DefaultSelector();selector.register(child.stdout,selectors.EVENT_READ)
  with (root/'execute.log').open('xb') as log:
   while selector.get_map() or child.poll() is None:
    check()
    for key,_ in selector.select(.02):
     chunk=os.read(key.fileobj.fileno(),16384)
     if not chunk:selector.unregister(key.fileobj);continue
     available=max(0,normal_limit-tree_bytes(root));need(len(chunk)<=available,'EXTERNAL_STORAGE_LIMIT');log.write(chunk);log.flush();check()
   log.flush();os.fsync(log.fileno())
  child.wait();code=child.returncode;check();need(code==0,'NONZERO_CHILD_EXIT')
 except BaseException as error:
  failure=str(error)
  if child is not None:
   if child.poll() is None:child.kill()
   child.wait();code=child.returncode
 finally:
  if child is not None and child.stdout is not None:child.stdout.close()
 elapsed=wall_ms()
 exit_record={'schema':1,'sourceCommit':source_commit,'runId':run_id,'invocations':1,'command':command,'childExitCode':code,'watchdogFailure':failure,'elapsedMs':elapsed,'peakObservedChildRssBytes':peak_rss,'budget':budget,'logSha256':digest(root/'execute.log') if (root/'execute.log').exists() else None,'authority':'Failure/incomplete takes precedence over any material completion receipt.'}
 try:
  exclusive_json(root/'external-exit.json',exit_record)
  need(wall_ms()<budget['maximumWallSeconds']*1000,'EXTERNAL_POST_EXIT_WALL_LIMIT');need(tree_bytes(root)<=budget['maximumOutputBytes'],'EXTERNAL_POST_EXIT_STORAGE_LIMIT')
  if failure is not None:raise EvidenceFailure(failure)
  exclusive_json(root/'external-final.pending.json',{'schema':1,'kind':'EXTERNAL_TERMINAL_COMPLETION','sourceCommit':source_commit,'runId':run_id,'childExitCode':0,'externalExitSha256':digest(root/'external-exit.json'),'logSha256':digest(root/'execute.log'),'elapsedMs':wall_ms(),'combinedBytesBeforeFinal':tree_bytes(root),'budget':budget})
  need(wall_ms()<budget['maximumWallSeconds']*1000,'EXTERNAL_POST_FINAL_WALL_LIMIT');need(tree_bytes(root)<=budget['maximumOutputBytes'],'EXTERNAL_POST_FINAL_STORAGE_LIMIT')
 except BaseException as error:
  failure=str(error)
  try:exclusive_json(root/'external-incomplete.json',{'schema':1,'result':'INCOMPLETE_ELEMENT247_SHELL_EXECUTION','reason':failure,'sourceCommit':source_commit,'runId':run_id,'childExitCode':code,'elapsedMs':wall_ms(),'combinedBytesBeforeFailure':tree_bytes(root)})
  except BaseException:pass  # Exit remains nonzero; missing final evidence also refuses verification.
 return {'exitCode':0 if failure is None else 1,'childExitCode':code,'failure':failure,'runId':run_id,'elapsedMs':wall_ms(),'directory':str(root)}

def supervise_session(command,directory,cwd,source_commit,authorization_sha256,budget=BUDGET,started_at=None,fixture_worker=None):
 """Observe the launcher's actual process exit. Acceptance files are staged,
 fsynced and checked, then atomically published as the last operations. A
 nonzero/missing launcher outcome refuses even if failure-record writes fail.
 A forced process kill preserves only already durable files, not RAM state.
 """
 root=pathlib.Path(directory);need(not root.exists(),'PRESERVE_EXISTING_INVOCATION');started=time.monotonic() if started_at is None else started_at
 config={'command':command,'directory':str(root),'cwd':str(cwd),'sourceCommit':source_commit,'authorizationSha256':authorization_sha256,'budget':budget,'startedAt':started}
 worker_command=fixture_worker if fixture_worker is not None else [sys.executable,str(pathlib.Path(__file__).resolve()),'--worker',json.dumps(config,separators=(',',':'))]
 need((time.monotonic()-started)*1000<1000*budget['maximumWallSeconds'],'SUPERVISOR_PRELAUNCH_WALL_LIMIT');worker=subprocess.Popen(worker_command,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True);log=bytearray();failure=None
 def check():
  need((time.monotonic()-started)*1000<1000*budget['maximumWallSeconds'],'SUPERVISOR_WALL_LIMIT')
  if root.exists():need(tree_bytes(root)<=budget['maximumOutputBytes'],'SUPERVISOR_STORAGE_LIMIT')
 def stop_group():
  # Node has a separate stdout pipe. Its launcher can exit and close the
  # supervisor pipe while Node remains live in the inherited process group.
  try:os.killpg(worker.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  worker.wait()
 try:
  selector=selectors.DefaultSelector()
  try:
   selector.register(worker.stdout,selectors.EVENT_READ)
   while selector.get_map() or worker.poll() is None:
    check()
    for key,_ in selector.select(.02):
     chunk=os.read(key.fileobj.fileno(),16384)
     if not chunk:selector.unregister(key.fileobj);continue
     need(len(log)+len(chunk)<=65536,'LAUNCHER_LOG_RESERVE');log.extend(chunk)
   worker.wait()
   if worker.returncode!=0:stop_group()
   check()
  except BaseException as error:
   failure=str(error);stop_group()
  finally:selector.close();worker.stdout.close()
  root.mkdir(parents=True,exist_ok=True);outcome=None
  with (root/'launcher.log').open('xb') as stream:stream.write(log);stream.flush();os.fsync(stream.fileno())
  start=read(root/'execution-start.json') if (root/'execution-start.json').is_file() else {}
  outcome={'schema':1,'kind':'OBSERVED_LAUNCHER_EXIT','sourceCommit':source_commit,'runId':start.get('runId'),'launcherExitCode':worker.returncode,'supervisorFailure':failure,'elapsedMs':(time.monotonic()-started)*1000,'clockScope':'pre-authorization-and-source-checks','budget':budget,'launcherLogSha256':digest(root/'launcher.log')}
  exclusive_json(root/'launcher-exit.pending.json',outcome)
  need(worker.returncode==0 and failure is None,'LAUNCHER_FAILED_EXIT_TAKES_PRECEDENCE')
  need(not (root/'external-incomplete.json').exists() and not (root/'material/incomplete-receipt.json').exists(),'INCOMPLETE_TAKES_PRECEDENCE')
  pending=root/'external-final.pending.json';need(pending.is_file(),'MISSING_EXTERNAL_COMPLETION_CANDIDATE');candidate=read(pending);need(candidate.get('sourceCommit')==source_commit and candidate.get('runId')==start.get('runId') and candidate.get('kind')=='EXTERNAL_TERMINAL_COMPLETION' and candidate.get('budget')==budget,'EXTERNAL_CANDIDATE_IDENTITY');need(candidate.get('externalExitSha256')==digest(root/'external-exit.json') and candidate.get('logSha256')==digest(root/'execute.log'),'EXTERNAL_CANDIDATE_HASHES')
  outcome['externalFinalSha256']=digest(pending)
  # The enriched acceptance outcome gets a separate staging name, preserving
  # the observed exit record even if writing/publishing acceptance fails.
  exclusive_json(root/'launcher-acceptance.pending.json',outcome);check();need(tree_bytes(root)<=budget['maximumOutputBytes'],'SUPERVISOR_FINAL_OUTPUT_LIMIT')
  success={'exitCode':0,'launcherExitCode':0,'failure':None,'directory':str(root)}
  need(not (root/'external-final.json').exists() and not (root/'launcher-exit.json').exists(),'PRESERVE_ACCEPTANCE_FILES')
  os.rename(pending,root/'external-final.json')
  os.rename(root/'launcher-acceptance.pending.json',root/'launcher-exit.json')
  return success  # No checks, writes, logging, or other fallible work follows publication.
 except BaseException as error:
  failure=str(error);cleanup_failure=None
  # Every refusal after spawn cleans up, including ordinary polling completion
  # followed by a failed launcher exit, candidate check or evidence write.
  try:stop_group()
  except BaseException as cleanup_error:cleanup_failure=str(cleanup_error)
  try:worker.stdout.close()
  except BaseException:pass
  try:exclusive_json(root/'supervisor-incomplete.json',{'schema':1,'result':'INCOMPLETE_ELEMENT247_SHELL_SUPERVISION','reason':failure,'groupCleanupFailure':cleanup_failure,'launcherExitCode':worker.returncode,'sourceCommit':source_commit,'elapsedMs':(time.monotonic()-started)*1000})
  except BaseException:pass
  return {'exitCode':1,'launcherExitCode':worker.returncode,'failure':failure,'groupCleanupFailure':cleanup_failure,'directory':str(root)}

def check_runtime(r,budget):
 need(all(r.get(k)==budget['plannedMaterialCalls'] for k in ['plannedCalls','reservedCalls','actualConstitutiveCallbacks','completedConstitutiveCallbacks']),'INCOMPLETE_CALLBACK_COUNTS')
 need(r.get('maximumCalls')==budget['maximumMaterialCalls'] and r.get('activeBatch') is None,'COUNT_BUDGET_OR_ACTIVE_BATCH')
 need(r.get('maximumWallMs')==1000*budget['maximumWallSeconds'] and 0<=r.get('elapsedMs',math.inf)<1000*budget['maximumWallSeconds'],'CHILD_WALL_EVIDENCE')
 need(r.get('maximumRssBytes')==budget['maximumRssBytes'] and 0<=r.get('peakObservedRssBytes',math.inf)<=budget['maximumRssBytes'],'CHILD_RSS_EVIDENCE')
def require_terminal_evidence(directory,budget=BUDGET,command=COMMAND,results=RESULTS):
 root=pathlib.Path(directory);material=root/'material'
 # Deliberately first: failure records cannot be bypassed by valid-looking
 # hashes, earlier completion records or a later zero process exit.
 need(not (root/'external-incomplete.json').exists(),'EXTERNAL_INCOMPLETE_TAKES_PRECEDENCE');need(not (material/'incomplete-receipt.json').exists(),'MATERIAL_INCOMPLETE_TAKES_PRECEDENCE')
 need(not (root/'supervisor-incomplete.json').exists(),'SUPERVISOR_INCOMPLETE_TAKES_PRECEDENCE')
 for name in ['launcher-exit.pending.json','launcher-exit.json']:
  if (root/name).is_file():
   observed=read(root/name);need(observed.get('launcherExitCode')==0 and observed.get('supervisorFailure') is None,'LAUNCHER_FAILED_EXIT_TAKES_PRECEDENCE')
 if (root/'external-exit.json').is_file():
  prior_exit=read(root/'external-exit.json');need(prior_exit.get('childExitCode')==0 and prior_exit.get('watchdogFailure') is None,'EXTERNAL_FAILED_EXIT_TAKES_PRECEDENCE')
 for p in [root/'execution-start.json',root/'external-exit.json',root/'external-final.json',root/'launcher-exit.json',root/'launcher.log',root/'execute.log',material/'completion-receipt.json',material/'terminal-completion.json']:need(p.is_file(),'MISSING_TERMINAL_OR_EXTERNAL_EVIDENCE:'+p.name)
 start,exit_record,final,completion,terminal=[read(p) for p in [root/'execution-start.json',root/'external-exit.json',root/'external-final.json',material/'completion-receipt.json',material/'terminal-completion.json']]
 need(isinstance(start.get('sourceCommit'),str) and re.fullmatch('[0-9a-f]{40}',start['sourceCommit']) and isinstance(start.get('runId'),str) and re.fullmatch('[0-9a-f]{32}',start['runId']),'SOURCE_OR_RUN_ID_FORMAT')
 launcher=read(root/'launcher-exit.json');need(launcher.get('kind')=='OBSERVED_LAUNCHER_EXIT' and launcher.get('sourceCommit')==start['sourceCommit'] and launcher.get('runId')==start['runId'] and launcher.get('budget')==budget,'OBSERVED_LAUNCHER_IDENTITY');need(launcher.get('clockScope')==start.get('clockScope')=='pre-authorization-and-source-checks','FULL_WALL_SCOPE');need(0<=launcher.get('elapsedMs',math.inf)<1000*budget['maximumWallSeconds'],'SUPERVISOR_WALL_EVIDENCE');need(launcher.get('externalFinalSha256')==digest(root/'external-final.json') and launcher.get('launcherLogSha256')==digest(root/'launcher.log'),'OBSERVED_LAUNCHER_HASHES')
 need(exit_record.get('childExitCode')==0 and exit_record.get('watchdogFailure') is None,'EXTERNAL_FAILED_EXIT_TAKES_PRECEDENCE');need(final.get('childExitCode')==0 and final.get('kind')=='EXTERNAL_TERMINAL_COMPLETION','EXTERNAL_TERMINAL_KIND')
 for item in [start,exit_record,final]:need(item.get('budget')==budget,'EXTERNAL_BUDGET')
 for item in [start,exit_record]:need(item.get('invocations')==1 and item.get('command')==command,'EXTERNAL_INVOCATION_COMMAND')
 for item in [exit_record,final]:need(0<=item.get('elapsedMs',math.inf)<1000*budget['maximumWallSeconds'],'EXTERNAL_WALL_EVIDENCE')
 need(0<=exit_record.get('peakObservedChildRssBytes',math.inf)<=budget['maximumRssBytes'],'EXTERNAL_RSS_EVIDENCE');need(tree_bytes(root)<=budget['maximumOutputBytes'],'COMBINED_OUTPUT_BUDGET')
 need(final.get('externalExitSha256')==digest(root/'external-exit.json'),'EXTERNAL_EXIT_HASH');log_sha=digest(root/'execute.log');need(final.get('logSha256')==log_sha==exit_record.get('logSha256'),'EXTERNAL_LOG_HASH')
 for item in [exit_record,final,completion,terminal]:need(item.get('sourceCommit')==start.get('sourceCommit') and item.get('runId')==start.get('runId'),'SOURCE_OR_INVOCATION_MISMATCH')
 need(completion.get('result') in results and terminal.get('result')==completion.get('result'),'NUMERICAL_RESULT_KIND');need(terminal.get('kind')=='TERMINAL_COMPLETION','TERMINAL_KIND');need(terminal.get('completionSha256')==digest(material/'completion-receipt.json'),'TERMINAL_COMPLETION_HASH')
 lines=(root/'execute.log').read_text().splitlines();markers=[]
 for i,line in enumerate(lines):
  try:value=json.loads(line)
  except json.JSONDecodeError:continue
  if isinstance(value,dict) and value.get('kind')=='TERMINAL_COMPLETION':markers.append((i,value))
 need(len(markers)==1 and markers[0][0]==len(lines)-1,'MISSING_DUPLICATE_OR_NONFINAL_STDOUT_COMPLETION');marker=markers[0][1]
 for key in ['sourceCommit','runId','result','completionSha256']:need(marker.get(key)==terminal.get(key),'STDOUT_TERMINAL_IDENTITY')
 need(marker.get('terminalSha256')==digest(material/'terminal-completion.json'),'STDOUT_TERMINAL_HASH')
 for item in [completion,terminal,marker]:check_runtime(item['runtime'],budget)
 need(completion['runtime']['elapsedMs']<=terminal['runtime']['elapsedMs']<=marker['runtime']['elapsedMs'],'TERMINAL_CLOCK_ORDER')
 need(marker['runtime'].get('lastPhase')=='after-terminal-completion-write','POST_TERMINAL_RESOURCE_CHECK_MISSING')
 return {'completion':completion,'terminal':terminal,'marker':marker,'externalExit':exit_record,'externalFinal':final,'launcherExit':launcher,'sourceCommit':start['sourceCommit'],'runId':start['runId']}

if __name__=='__main__':
 need(len(sys.argv)==3 and sys.argv[1]=='--worker','Private supervised worker only');config=json.loads(sys.argv[2]);result=launch_session(config['command'],config['directory'],config['cwd'],config['sourceCommit'],config['authorizationSha256'],config['budget'],started_at=config['startedAt'],isolate_child=False);os._exit(result['exitCode'])

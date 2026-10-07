import datetime,hashlib,json,os,pathlib,resource,subprocess,sys,time
ROOT=pathlib.Path('/tmp/Kenoma-fine-window-material-run/education');RUN=ROOT/'review/fine-window-run-20261007';AUTH=ROOT/'research/fine-window-authorization-20261007.json'
assert not RUN.exists(),'Preserve existing single invocation'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();assert head=='fe513113cbc336948ae20b0209a5be4b9552b524'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();auth=json.loads(AUTH.read_text());assert h(AUTH)=='eefb24e1994824ced443b5740826c3c020712ef893c74683ba63d0d1b1d8ae7f'
command=[sys.executable,'tools/launch-fine-window.py','--execute'];started=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();child=subprocess.Popen(command,cwd=ROOT);code=child.wait();elapsed=time.monotonic()-started
assert RUN.exists(),'No invocation directory created; preserve process refusal'
start=json.loads((RUN/'execution-start.json').read_text()) if (RUN/'execution-start.json').exists() else {}
record={'schema':1,'kind':'OBSERVED_PUBLIC_ENTRY_EXIT','sourceCommit':head,'runId':start.get('runId'),'authorizationSha256':h(AUTH),'command':command,'publicEntryExitCode':code,'startedUTC':utc,'finishedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsedMs':elapsed*1000,'budget':auth['budget'],'observedSubprocessTreeRusageMaximumRssBytes':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,'combinedBytesBeforePublicReceipt':sum(p.stat().st_size for p in RUN.rglob('*') if p.is_file()),'invocations':1,'retryPerformed':False,'authority':'Actual public-entry process exit observation; failures dominate provisional numerical receipts.'}
data=(json.dumps(record,separators=(',',':'))+'\n').encode();assert len(data)<=65536
with (RUN/'public-entry-exit.json').open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
record['combinedBytesAfterPublicReceipt']=sum(p.stat().st_size for p in RUN.rglob('*') if p.is_file());print(json.dumps(record),flush=True);sys.exit(code)

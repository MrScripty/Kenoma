"""Observe exactly one reviewed public entry; no material evaluation or retry."""
import datetime,hashlib,json,os,pathlib,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[2]
HERE=pathlib.Path(__file__).resolve().parent
COMMAND=[sys.executable,'tools/launch-selective-fixed-patch.py','--execute']
assert not (ROOT/'review/selective-fixed-patch-run-20261007').exists()
assert not (HERE/'public-entry-exit.json').exists()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (HERE/'public-entry.log').open('xb') as log:
 process=subprocess.run(COMMAND,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 log.flush();os.fsync(log.fileno())
record={'schema':1,'kind':'OBSERVED_PUBLIC_ENTRY_EXIT','sourceCommit':head,'command':COMMAND,'invocations':1,'actualPublicEntryExitCode':process.returncode,'elapsedSeconds':time.monotonic()-start,'startedUTC':utc,'authorizationSha256':hashlib.sha256((ROOT/'research/selective-fixed-patch-authorization-20261007.json').read_bytes()).hexdigest(),'publicEntryLogSha256':hashlib.sha256((HERE/'public-entry.log').read_bytes()).hexdigest(),'retryAttempted':False,'authority':'Nonzero public entry remains incomplete even if earlier provisional numerical records exist.'}
with (HERE/'public-entry-exit.json').open('x') as out:json.dump(record,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
print(json.dumps(record));sys.exit(process.returncode)

"""Bound a local geometry/unit command with fixed resource limits."""
import argparse,json,os,pathlib,resource,signal,subprocess,time
RSS_CAP=1_000_000_000
CGROUP_CAP=16_000_000_000
WALL_CAP=240
OUTPUT_CAP=32*1024*1024
def memory():return int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())
def rss(group):
 total=0
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   stat=(p/'stat').read_text().rsplit(')',1)[1].split()
   if int(stat[2])!=group:continue
   for line in (p/'status').read_text().splitlines():
    if line.startswith('VmRSS:'):total+=int(line.split()[1])*1024
  except (OSError,ValueError):pass
 return total
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=pathlib.Path,required=True);parser.add_argument('--output-root',type=pathlib.Path);parser.add_argument('command',nargs=argparse.REMAINDER);a=parser.parse_args();command=a.command[1:] if a.command and a.command[0]=='--' else a.command
 assert command and a.receipt.is_absolute() and not a.receipt.exists() and memory()<CGROUP_CAP
 log=a.receipt.with_suffix('.log');assert not log.exists();start=time.monotonic();peak_cgroup=memory();peak_rss=0;failure=None
 def limits():resource.setrlimit(resource.RLIMIT_FSIZE,(OUTPUT_CAP,OUTPUT_CAP))
 with log.open('x') as stream:
  p=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=limits)
  while p.poll() is None:
   peak_cgroup=max(peak_cgroup,memory());peak_rss=max(peak_rss,rss(p.pid))
   output=sum(f.stat().st_size for f in a.output_root.rglob('*') if f.is_file()) if a.output_root and a.output_root.exists() else 0
   if peak_cgroup>CGROUP_CAP:failure='Total cgroup cap'
   elif peak_rss>RSS_CAP:failure='Command process-group RSS cap'
   elif time.monotonic()-start>WALL_CAP:failure='Wall cap'
   elif output>OUTPUT_CAP:failure='Output byte cap'
   elif log.stat().st_size>1024*1024:failure='Transcript cap'
   if failure:os.killpg(p.pid,signal.SIGKILL);break
   time.sleep(.05)
  code=p.wait()
 result={'status':'PASS_BOUNDED_LOCAL_COMMAND' if code==0 and not failure else 'FAIL_STOPPED','command':command,'exitCode':code,'failure':failure,'peakProcessGroupRssBytes':peak_rss,'peakCgroupBytes':peak_cgroup,'elapsedSeconds':time.monotonic()-start,'caps':{'processGroupRssBytes':RSS_CAP,'totalCgroupBytes':CGROUP_CAP,'wallSeconds':WALL_CAP,'outputBytes':OUTPUT_CAP}}
 a.receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(0 if code==0 and not failure else 1)
if __name__=='__main__':main()

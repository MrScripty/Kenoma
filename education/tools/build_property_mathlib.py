"""Build only the real-property proof imports from locked official source, two jobs.
No binary-cache dependency or changes to the existing Std-only proof bundle.
"""
from pathlib import Path
import concurrent.futures,os,re,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
root=ROOT/'.tools/mathlib4'
import hashlib,json
lock=json.loads((ROOT/'proofs/mathlib-lock.json').read_text())
env=os.environ.copy();env['PATH']=str(ROOT/'.tools/lean-4.19.0-linux/bin')+os.pathsep+env['PATH'];env['MATHLIB_CACHE_DIR']=str(ROOT/'.tools/mathlib-cache');env['MATHLIB_NO_CACHE_ON_UPDATE']='1'
if not root.exists():
 subprocess.run(['git','clone','--depth','1','--branch',lock['tag'],lock['repository'],str(root)],check=True)
if subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()!=lock['commit']:raise RuntimeError('Unexpected mathlib revision')
if hashlib.sha256((root/'lake-manifest.json').read_bytes()).hexdigest()!=lock['manifest_sha256']:raise RuntimeError('Unexpected locked dependency manifest')
# Lake resolves its existing lockfile; cache downloading is explicitly disabled.
subprocess.run(['lake','--no-cache','env','lean','--version'],cwd=root,env=env,check=True)
roots=[root,*sorted((root/'.lake/packages').iterdir())]
roots=[p for p in roots if p.is_dir()]
def source(name):
 for package in roots:
  p=package/(name.replace('.','/')+'.lean')
  if p.exists():return p
 if name.split('.')[0] in ['Init','Lean','Std','Lake']:return None
 raise RuntimeError('Unresolved source module '+name)
def uncomment(text):
 out=[];i=0;depth=0
 while i<len(text):
  if text[i:i+2]=='/-':depth+=1;i+=2;continue
  if depth and text[i:i+2]=='-/':depth-=1;i+=2;continue
  if depth:
   if text[i]=='\n':out.append('\n')
   i+=1;continue
  out.append(text[i]);i+=1
 return ''.join(out)
graph={}
def visit(name):
 if name in graph:return
 p=source(name)
 if p is None:return
 graph[name]=set()
 for line in uncomment(p.read_text()).splitlines():
  if not line.strip() or line.strip().startswith('--') or line.strip()=='prelude':continue
  match=re.match(r'^\s*(?:public\s+)?import\s+(.*)',line)
  if match:
   for dep in match[1].split('--')[0].split():
    if source(dep) is not None:graph[name].add(dep);visit(dep)
  else:break
for line in (ROOT/'proofs/ContinuumProperties.lean').read_text().splitlines():
 match=re.match(r'^import\s+(\S+)',line)
 if match:visit(match[1])
print('SOURCE_MODULE_COUNT',len(graph),flush=True)
# Preserve the workspace cache and no-download settings established above.
logs=ROOT/'.tools/property-mathlib-source-logs';logs.mkdir(exist_ok=True)
def build(name):
 with (logs/(name+'.txt')).open('w') as stream:
  result=subprocess.run(['lake','--no-cache','build',name],cwd=root,env=env,stdout=stream,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('Source build failed '+name+'; raw '+str(logs/(name+'.txt')))
 return name
# Completed pinned imports are reused; only new dependency modules are built.
done={name for name in graph if any((package/'.lake/build/lib/lean'/(name.replace('.','/')+'.olean')).exists() for package in roots)}
print('SOURCE_REUSED_MODULES',len(done),flush=True)
pending=set(graph)-done;jobs={}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 while pending or jobs:
  ready=sorted(n for n in pending if graph[n]<=done)
  for name in ready[:2-len(jobs)]:jobs[pool.submit(build,name)]=name;pending.remove(name)
  if not jobs:raise RuntimeError('Import cycle or blocked source graph '+str(sorted(pending)[:5]))
  finished,_=concurrent.futures.wait(jobs,return_when=concurrent.futures.FIRST_COMPLETED)
  for future in finished:
   name=jobs.pop(future);future.result();done.add(name)
   if len(done)%25==0 or not pending:print('SOURCE_PROGRESS',len(done),len(graph),name,flush=True)
# Ask Lake to check the final import targets and their traces after expansion.
for line in (ROOT/'proofs/ContinuumProperties.lean').read_text().splitlines():
 match=re.match(r'^import\s+(\S+)',line)
 if match:build(match[1])
print('SOURCE_BUILD_COMPLETE',len(done),flush=True)

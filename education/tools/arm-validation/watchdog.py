#!/usr/bin/env python3
"""Private four-job supervisor. Import/self-tests never launch numerical code."""
import argparse, copy, ctypes, hashlib, json, math, os, pathlib, resource, selectors
import shutil, signal, stat, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[3]
NAMES = ['manifest.json','rest-recheck.json','default.json','adaptive-depth1.json','explicit-halves.json','comparison.json','resource-receipt.json','transcript.log']
RUN_NAMES = ['rest-recheck.json','default.json','adaptive-depth1.json','explicit-halves.json']
CLASSES = ['attempts','configurationEntries','muscleMaterial','tendonMaterial','materialTensor','hessianProducts']
EXPECTED_POLICY = dict(runs=[dict(id='A',attempts=0,configurationEntries=1,wallSeconds=60,muscleMaterial=56448,tendonMaterial=633,materialTensor=0,hessianProducts=0)]+[dict(id=i,attempts=n,configurationEntries=512,wallSeconds=240,muscleMaterial=28901376,tendonMaterial=324096,materialTensor=28901376,hessianProducts=n*3528840) for i,n in [('B',1),('C',3),('D',2)]], aggregateWallSeconds=780,ownedRSSBytes=1000000000,cgroupBytes=16000000000,perRunOutputBytes=4194304,aggregateOutputBytes=16777216,perRunTranscriptBytes=262144,aggregateTranscriptBytes=1048576,pollSeconds=.01,reservedReceiptBytes=65536,reservedTranscriptBytes=1024,outputs=NAMES)
INPUT_HASHES={'generated/arm-reference.json':'1b80c1d3d9f2eb4370cd298f58f5e9c582625574f27072f6d3a1ea898ce4c036','config/attachments-apparatus.json':'070fee738e73e127e334ee5cbe680cb622f100396ad0728eb9df6723c2232389','config/apparatus-routing.json':'b8580e8158e17730b65b64d0fdbe0f1cbbafc76235b9a5f0c2b01020818cd93f','audit/modal-fixed-end-results.json':'b0eeecdade262b682279d9ebeb7a8147a4525a992976a85afc0ce5e63270d8b4','audit/arm-rest-results.json':'8dc23d896adce4b428f39cb172d76f3c74c828f49c2007c66155e45e8ea359c7','audit/arm-rest-recheck.json':'3d1159de78088207320d3b19b17ffc83cb08a531781e26715c8167dd7efbecab'}

def digest(data): return hashlib.sha256(data).hexdigest()
def encoded(obj): return (json.dumps(obj, separators=(',',':'), allow_nan=False)+'\n').encode()
class Refusal(Exception): pass

def no_symlinks(path):
    path=pathlib.Path(path).absolute()
    for p in [*reversed(path.parents),path]:
        if p.exists() or p.is_symlink():
            if stat.S_ISLNK(p.lstat().st_mode): raise Refusal('Symlink path: '+str(p))
    return path

def read_regular(path, maximum=4194304):
    p=no_symlinks(path);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_size>maximum: raise Refusal('Nonregular/oversized input')
        with os.fdopen(fd,'rb',closefd=False) as f: return f.read(maximum+1)
    finally: os.close(fd)

def cgroup_file():
    lines=pathlib.Path('/proc/self/cgroup').read_text().splitlines()
    rel=next(x.split(':',2)[2] for x in lines if x.startswith('0::'))
    return pathlib.Path('/sys/fs/cgroup')/rel.lstrip('/')/'memory.current'

def process_info(pid):
    try:
        text=pathlib.Path(f'/proc/{pid}/stat').read_text(); fields=text[text.rindex(')')+2:].split()
        status=pathlib.Path(f'/proc/{pid}/status').read_text().splitlines(); vals={k:int(v.split()[0])*1024 for k,v in (x.split(':',1) for x in status if x.startswith(('VmRSS:','VmHWM:')))}
        return {'pid':pid,'ppid':int(fields[1]),'start':int(fields[19]),'rss':vals.get('VmRSS',0),'hwm':vals.get('VmHWM',0)}
    except (FileNotFoundError,ProcessLookupError): return None

def subreaper():
    if ctypes.CDLL(None,use_errno=True).prctl(36,1,0,0,0)!=0: raise Refusal('Subreaper monitoring unavailable')

def descendants(root):
    table={}
    for entry in pathlib.Path('/proc').iterdir():
        if entry.name.isdigit():
            p=process_info(int(entry.name))
            if p:table[p['pid']]=p
    owned={root};changed=True
    while changed:
        new={pid for pid,p in table.items() if p['ppid'] in owned};changed=not new.issubset(owned);owned |= new
    return {pid:table[pid] for pid in owned if pid in table}

def validate_manifest(m, data, require_review=True):
    if m.get('schema')!=1 or m.get('operatorCommit')!='e57847418a13da39db78cbfcdba070c285f3bfde' or m.get('inputCommit')!='0b83819ad3fdaed7405c6bbe617bc01640eef914' or m.get('policy')!=EXPECTED_POLICY: raise Refusal('Changed exact source/policy')
    if set(m.get('inputs',{}))!=set(INPUT_HASHES): raise Refusal('Changed input inventory')
    for p,h in INPUT_HASHES.items():
        i=m['inputs'][p]
        if i['sha256']!=h or digest(i['text'].encode())!=h: raise Refusal('Changed input '+p)
    approved_modules=(m.get('reviewReceipt') or {}).get('operatorModuleHashes')
    if require_review and (not approved_modules or set(approved_modules)!=set(m.get('modules',{}))):raise Refusal('Unreviewed module inventory')
    for p,item in m.get('modules',{}).items():
        if require_review and approved_modules[p]!=item['sha256']:raise Refusal('Unreviewed operator module '+p)
        if not p.startswith('education/') or pathlib.PurePosixPath(p).as_posix()!=p or '..' in pathlib.PurePosixPath(p).parts or digest(item['text'].encode())!=item['sha256']:raise Refusal('Changed module '+p)
    files=m.get('harnessFiles',{});expected={'education/tools/arm-validation/'+n for n in ['core.mjs','prepare.mjs','loader.mjs','replay.mjs','worker.mjs','watchdog.py']}
    if set(files)!=expected: raise Refusal('Changed harness inventory')
    for p,h in files.items():
        if digest(read_regular(ROOT/p))!=h: raise Refusal('Changed harness '+p)
    node=shutil.which('node')
    if not node or subprocess.check_output([node,'--version'],text=True).strip()!=m.get('nodeVersion'):raise Refusal('Changed Node runtime')
    review=m.get('reviewReceipt')
    if require_review:
        if not review or review.get('verdict')!='PASS_RUN_READY_SOURCE_ONLY' or review.get('sourceCommit')!=m.get('harnessCommit'):raise Refusal('Missing exact independent review')
        # Node JSON.stringify is used for this canonical binding; no non-ASCII in receipt.
        canonical=json.dumps(review,separators=(',',':'),ensure_ascii=False).encode()
        if digest(canonical)!=m.get('reviewReceiptSHA256'):raise Refusal('Changed review receipt binding')
    return node

class Output:
    def __init__(self,directory,policy):
        self.path=no_symlinks(directory);os.mkdir(self.path,0o700);self.policy=policy;self.charges={r['id']:0 for r in policy['runs']};self.transcript={r['id']:0 for r in policy['runs']};self.written={};self.claim={}
    def reserve(self,run,amount,emergency=False):
        reserve=0 if emergency else self.policy['reservedReceiptBytes']
        if self.charges[run]+amount>self.policy['perRunOutputBytes']-reserve or sum(self.charges.values())+amount>self.policy['aggregateOutputBytes']-reserve:raise Refusal('Output ceiling')
    def write(self,name,bytes_,run,emergency=False):
        if name not in NAMES or name in self.written:raise Refusal('Foreign/repeated output')
        self.reserve(run,len(bytes_),emergency)
        # One exclusive new file; no old/temp duplication or overwrite.
        fd=os.open(self.path/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            with os.fdopen(fd,'wb',closefd=False) as f:f.write(bytes_);f.flush();os.fsync(fd)
        finally:os.close(fd)
        self.charges[run]+=len(bytes_);self.written[name]={'bytes':len(bytes_),'sha256':digest(bytes_)}
    def log(self,bytes_,run,final=False):
        reserve=0 if final else self.policy['reservedTranscriptBytes']
        if self.transcript[run]+len(bytes_)>self.policy['perRunTranscriptBytes']-reserve or sum(self.transcript.values())+len(bytes_)>self.policy['aggregateTranscriptBytes']-reserve:raise Refusal('Transcript ceiling')
        self.reserve(run,len(bytes_));p=self.path/'transcript.log'
        fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
        try:
            with os.fdopen(fd,'ab',closefd=False) as f:f.write(bytes_);f.flush()
        finally:os.close(fd)
        self.charges[run]+=len(bytes_);self.transcript[run]+=len(bytes_)
    def seal_log(self):
        p=self.path/'transcript.log'
        if not p.exists():self.write('transcript.log',b'','A')
        else:
            b=read_regular(p,self.policy['aggregateTranscriptBytes']);self.written['transcript.log']={'bytes':len(b),'sha256':digest(b)}
    def verify_inventory(self):
        if self.claim:
            b=read_regular(self.claim['path'])
            if len(b)!=self.claim['bytes'] or digest(b)!=self.claim['sha256']:raise Refusal('Changed external one-use claim')
        if set(p.name for p in self.path.iterdir())!=set(self.written):raise Refusal('Foreign output inventory')
        for name,expected in self.written.items():
            b=read_regular(self.path/name,self.policy['aggregateOutputBytes'])
            if {'bytes':len(b),'sha256':digest(b)}!=expected:raise Refusal('Changed published bytes')

def supervise(command, output, run, aggregate_start, cgroup=None, allow_descendants=False):
    """Generic process adapter; tests supply synthetic programs, never physical code."""
    subreaper();policy=output.policy;start=time.monotonic();deadline=min(start+run['wallSeconds'],aggregate_start+policy['aggregateWallSeconds']);cgroup=cgroup or cgroup_file()
    try:initial_cgroup=int(pathlib.Path(cgroup).read_text())
    except Exception as e:raise Refusal('Cgroup monitoring unavailable') from e
    if initial_cgroup>policy['cgroupBytes']:raise Refusal('Shared cgroup ceiling before launch')
    parent_before=process_info(os.getpid())
    if parent_before is None:raise Refusal('Owned process monitor unavailable')
    if parent_before['hwm']>policy['ownedRSSBytes']:raise Refusal('Owned RSS ceiling before launch')
    if shutil.disk_usage(output.path).free<policy['aggregateOutputBytes']+policy['reservedReceiptBytes']:raise Refusal('Insufficient scratch space')
    rfd,wfd=os.pipe();env={'PATH':os.defpath,'LANG':'C.UTF-8','KENOMA_RESULT_FD':str(wfd),'TMPDIR':str(output.path)}
    proc=subprocess.Popen(command,start_new_session=True,pass_fds=(wfd,),stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env);os.close(wfd)
    selector=selectors.DefaultSelector();selector.register(rfd,selectors.EVENT_READ,'result');selector.register(proc.stdout,selectors.EVENT_READ,'stdout');selector.register(proc.stderr,selectors.EVENT_READ,'stderr')
    for key in selector.get_map().values():os.set_blocking(key.fd,False)
    observed={};packet=bytearray();reason=None;peak=0;shared_peak=initial_cgroup
    def inspect():
        nonlocal peak,shared_peak
        group=descendants(os.getpid());own={pid:p for pid,p in group.items() if pid==os.getpid() or pid==proc.pid or p['ppid']!=os.getppid()}
        for pid,p in own.items():
            ident=(pid,p['start']);observed[ident]=max(observed.get(ident,0),p['hwm'],p['rss'])
        peak=max(peak,sum(observed.values()));shared_peak=max(shared_peak,int(pathlib.Path(cgroup).read_text()))
        if peak>policy['ownedRSSBytes']:raise Refusal('Owned peak RSS ceiling')
        if shared_peak>policy['cgroupBytes']:raise Refusal('Observed shared cgroup ceiling')
        if not allow_descendants and any(pid not in (os.getpid(),proc.pid) for pid in own):raise Refusal('Unexpected descendant')
        if time.monotonic()>=deadline-min(1.,run['wallSeconds']/4):raise Refusal('Wall deadline/cleanup reserve')
    try:
        while selector.get_map():
            inspect()
            for key,_ in selector.select(policy['pollSeconds']):
                try:b=os.read(key.fd,65536)
                except BlockingIOError:continue
                if not b:selector.unregister(key.fileobj);continue
                if key.data=='result':
                    if len(packet)+len(b)>policy['perRunOutputBytes']-policy['reservedReceiptBytes']:raise Refusal('Result/staging ceiling')
                    # Also include the eventual packet alongside already-created output.
                    output.reserve(run['id'],len(packet)+len(b));packet.extend(b)
                else:output.log(b,run['id'])
        while os.waitid(os.P_PID,proc.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT) is None:
            inspect();time.sleep(policy['pollSeconds'])
        inspect()
    except Exception as error:reason=str(error)
    finally:
        # Only this owned session is targeted. Worker is not reaped until kill,
        # preventing PID/group reuse. Adopted descendants are reaped as well.
        try:os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        for (pid,identity) in list(observed):
            if pid==os.getpid():continue
            p=process_info(pid)
            if p and p['start']==identity:
                try:os.kill(pid,signal.SIGKILL)
                except ProcessLookupError:pass
        try:proc.wait(timeout=max(.01,deadline-time.monotonic()))
        except subprocess.TimeoutExpired:reason=reason or 'Worker not reaped before wall ceiling'
        while time.monotonic()<deadline:
            try:
                pid,_=os.waitpid(-1,os.WNOHANG)
                if pid==0:
                    if any(p['pid']!=os.getpid() for p in descendants(os.getpid()).values()):time.sleep(.005);continue
                    break
            except ChildProcessError:break
        survivors=[p for p in descendants(os.getpid()).values() if p['pid']!=os.getpid()]
        if survivors:reason=reason or 'Descendants survive disposal'
        selector.close();os.close(rfd);proc.stdout.close();proc.stderr.close()
    # wait4/RUSAGE_CHILDREN retains a terminated worker's RSS high-water mark.
    parent=process_info(os.getpid());peak=max(peak,(parent['hwm'] if parent else 0)+resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024)
    if peak>policy['ownedRSSBytes']:reason=reason or 'Owned RSS high-water ceiling at disposal'
    elapsed=time.monotonic()-start
    if elapsed>run['wallSeconds'] or time.monotonic()-aggregate_start>policy['aggregateWallSeconds']:reason=reason or 'Final wall ceiling'
    resources={'run':run['id'],'startOffsetSeconds':start-aggregate_start,'wallSeconds':elapsed,'ownedPeakRSSBytes':peak,'observedCgroupPeakBytes':shared_peak,'monitorPeriodSeconds':policy['pollSeconds'],'processIdentities':[{'pid':p,'startTicks':s,'observedPeakRSSBytes':h} for (p,s),h in observed.items()],'allProcessesReaped':not survivors and proc.returncode is not None,'transcriptBytes':output.transcript[run['id']]}
    if reason or proc.returncode!=0:return {'status':'RESOURCE_INCONCLUSIVE','reason':reason or 'Nonzero worker exit','finalAcceptance':False},resources
    try:result=json.loads(packet)
    except Exception:return {'status':'RESOURCE_INCONCLUSIVE','reason':'Incomplete result channel','finalAcceptance':False},resources
    return result,resources

def compare(B,C,D):
    eq=lambda a,b:json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))
    if B['status']=='PASS' and C['status']=='PASS':
        if len(C['leaves'])!=1 or not eq(B['finalState'],C['finalState']) or not eq([r['receipt'] for r in B['leaves']],[r['receipt'] for r in C['leaves']]):raise Refusal('Default compatibility mismatch')
        return dict(result='CONTROL_COMPATIBLE_REMEDY_UNPROVEN',explicitHalvesDifferFromWhole=not eq(B['finalState'],D.get('finalState')))
    if B['status']=='SOLVER_REFUSAL' and C['status']=='PASS':
        if len(C['leaves'])!=2 or D['status']!='PASS' or not eq(C['finalState'],D['finalState']) or not eq([r['receipt'] for r in C['leaves']],[r['receipt'] for r in D['leaves']]):raise Refusal('Half-step replay mismatch')
        return dict(result='RECOVERY_SUPPORTED_FOR_THIS_REDUCED_INTERVAL_ONLY')
    if C['status']=='SOLVER_REFUSAL' and D['status']=='SOLVER_REFUSAL':return dict(result='DEPTH_ONE_RECOVERY_REFUSED_FOR_THIS_INTERVAL')
    raise Refusal('Inconsistent control/halves outcomes')

def final_guard(output,resources,aggregate_start,cgroup=None):
    parent=process_info(os.getpid())
    if parent is None:raise Refusal('Final owned monitor unavailable')
    owned=parent['hwm']+resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024
    shared=int(pathlib.Path(cgroup or cgroup_file()).read_text())
    if owned>output.policy['ownedRSSBytes']:raise Refusal('Final owned RSS ceiling')
    if shared>output.policy['cgroupBytes']:raise Refusal('Final observed cgroup ceiling')
    elapsed=time.monotonic()-aggregate_start
    if elapsed>output.policy['aggregateWallSeconds']:raise Refusal('Final aggregate wall ceiling')
    if resources:
        last=resources[-1];last['ownedPeakRSSBytes']=max(last['ownedPeakRSSBytes'],owned);last['observedCgroupPeakBytes']=max(last['observedCgroupPeakBytes'],shared)
        # Charge final publication/supervision to the last actual process job.
        total=elapsed-last['startOffsetSeconds']
        ceiling=next(r['wallSeconds'] for r in output.policy['runs'] if r['id']==last['run'])
        if total>ceiling:raise Refusal('Final per-run wall ceiling')
        last['wallSecondsIncludingFinalization']=total
    return {'ownedPeakRSSBytes':owned,'observedCgroupBytes':shared,'elapsedSeconds':elapsed}

def finalize(output,results,resources,comparison,manifest_hash,aggregate_start,cgroup=None):
    final_guard(output,resources,aggregate_start,cgroup)
    disposed=all(r['allProcessesReaped'] for r in resources)
    failure=not disposed or any(r.get('status') not in ('PASS','SOLVER_REFUSAL') for r in results.values())
    summary={'event':'supervisor-final','status':'RESOURCE_INCONCLUSIVE' if failure else 'COMPLETE_FINALIZED','manifestSHA256':manifest_hash,'output':str(output.path),'anatomicalQualification':False,'observationalStatus':'Provisional until supervisor exit zero and matching complete resource receipt'}
    output.log(encoded(summary),resources[-1]['run'] if resources else 'A',final=True);output.seal_log()
    payloads={RUN_NAMES[i]:encoded({'run':run,'workerSnapshotStatus':'PROVISIONAL_UNTIL_RESOURCE_COMMIT','payload':results.get(run,{'status':'SKIPPED_NOT_RUN','finalAcceptance':False})}) for i,run in enumerate('ABCD')}
    payloads['comparison.json']=encoded(comparison)
    last_run=resources[-1]['run'] if resources else 'A'
    owners={name:(run if run in results else last_run) for name,run in zip(RUN_NAMES,'ABCD')};owners['comparison.json']=last_run
    # Pre-account all final payloads plus the mandatory failure/commit reserve.
    for name,b in payloads.items():output.reserve(owners[name],len(b))
    simulated=dict(output.charges)
    for name,b in payloads.items():simulated[owners[name]]+=len(b)
    if any(v>output.policy['perRunOutputBytes']-output.policy['reservedReceiptBytes'] for v in simulated.values()) or sum(simulated.values())>output.policy['aggregateOutputBytes']-output.policy['reservedReceiptBytes']:raise Refusal('Combined final output ceiling')
    for name,b in payloads.items():output.write(name,b,owners[name])
    output.verify_inventory()
    final_metrics=final_guard(output,resources,aggregate_start,cgroup)
    receipt={'status':'RESOURCE_INCONCLUSIVE' if failure else 'COMPLETE_FINALIZED','manifestSHA256':manifest_hash,'authoritativeFinalAcceptance':{r:results.get(r,{}).get('status')=='PASS' and not failure for r in 'ABCD'},'snapshotsDetached':True,'allProcessesDisposed':all(r['allProcessesReaped'] for r in resources),'anatomicalQualification':False,'aggregateWallSeconds':time.monotonic()-aggregate_start,'resources':copy.deepcopy(resources),'finalResourceObservation':final_metrics,'perRunOutputBytesBeforeCommit':dict(output.charges),'oneUseClaimBytesChargedToA':output.claim.get('bytes',0),'externalOneUseClaim':copy.deepcopy(output.claim),'fileHashes':copy.deepcopy(output.written),'supervisorStdout':summary,'observationalStatus':{'progress':'PROVISIONAL_NOT_COMMITTED','contactAliases':'UNTRUSTED_PROCESS_LOCAL_ALIASES_DISPOSED','onlyAuthoritativeAcceptance':'Supervisor exit zero AND this complete resource receipt, matching all listed snapshot hashes and manifest. Files observed before supervisor disposal are provisional.'}}
    if not receipt['allProcessesDisposed']:receipt['status']='RESOURCE_INCONCLUSIVE';receipt['authoritativeFinalAcceptance']={r:False for r in 'ABCD'}
    b=encoded(receipt);output.write('resource-receipt.json',b,last_run,emergency=True);output.verify_inventory()
    final_guard(output,resources,aggregate_start,cgroup)
    return receipt

def execute(manifest_path,destination,approval):
    start=time.monotonic();data=read_regular(manifest_path);h=digest(data)
    if approval!=h:raise Refusal('Stale/missing exact numerical approval token')
    m=json.loads(data);node=validate_manifest(m,data);cg=cgroup_file()
    if int(cg.read_text())>m['policy']['cgroupBytes']:raise Refusal('Shared cgroup ceiling')
    if shutil.disk_usage(no_symlinks(destination).parent).free<m['policy']['aggregateOutputBytes']+m['policy']['reservedReceiptBytes']:raise Refusal('Insufficient scratch')
    # Exclusive one-use claim; no campaign restart/reuse of an approved manifest.
    claim_bytes=encoded({'manifestSHA256':h,'output':str(destination)})
    claim=pathlib.Path(str(manifest_path)+'.executed');fd=os.open(no_symlinks(claim),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,'wb',closefd=False) as f:f.write(claim_bytes);f.flush();os.fsync(fd)
    finally:os.close(fd)
    output=Output(destination,m['policy']);output.charges['A']+=len(claim_bytes);output.claim={'path':str(claim),'bytes':len(claim_bytes),'sha256':digest(claim_bytes)};output.reserve('A',0);output.write('manifest.json',data,'A');results={};resources=[]
    try:
        for run in m['policy']['runs']:
            for p,expected in m['harnessFiles'].items():
                if digest(read_regular(ROOT/p))!=expected:raise Refusal('Changed harness before job '+run['id'])
            result,rs=supervise([node,str(ROOT/'education/tools/arm-validation/worker.mjs'),'--numerical-run',str(output.path/'manifest.json'),run['id'],h],output,run,start,cg);resources.append(rs);results[run['id']]=result
            if result.get('status') not in ('PASS','SOLVER_REFUSAL') or run['id']=='A' and result.get('status')!='PASS':break
            if result.get('workerStatus')!='PROVISIONAL_PENDING_SUPERVISOR' or result.get('finalAcceptance') is not False or result.get('run')!=run['id'] or result.get('sourceCommit')!=m['operatorCommit'] or result.get('harnessCommit')!=m['harnessCommit'] or result.get('executionScope')!=m['scope'] or result.get('anatomicalQualification') is not False or result.get('numericalCandidateAccepted')!=(result.get('status')=='PASS'):raise Refusal('Unbound/provisional worker packet')
            counts=result.get('counters',{}).get('executed',{})
            if set(counts)!=set(CLASSES) or any(type(counts[k]) is not int or counts[k]<0 or counts[k]>run[k] for k in CLASSES) or result.get('counters',{}).get('latched') or result.get('modelDisposed') is not True:raise Refusal('Incomplete/over-budget worker accounting')
        comparison=compare(results['B'],results['C'],results['D']) if set(results)==set('ABCD') and all(r['status'] in ('PASS','SOLVER_REFUSAL') for r in results.values()) else {'result':'RESOURCE_OR_GATE_INCONCLUSIVE_NO_RESTART'}
        return finalize(output,results,resources,comparison,h,start,cg)
    except Exception as error:
        # Never turn a finalization/cap failure into an accepted state. Reserved
        # minimal receipt is sufficient; incomplete files remain provisional.
        if 'resource-receipt.json' in output.written:
            old=output.written.pop('resource-receipt.json');os.unlink(output.path/'resource-receipt.json');output.charges[resources[-1]['run'] if resources else 'A']-=old['bytes']
        summary={'event':'supervisor-final','status':'RESOURCE_INCONCLUSIVE','manifestSHA256':h,'anatomicalQualification':False}
        output.log(encoded(summary),resources[-1]['run'] if resources else 'A',final=True);output.seal_log()
        receipt={'status':'RESOURCE_INCONCLUSIVE','reason':str(error),'manifestSHA256':h,'authoritativeFinalAcceptance':{r:False for r in 'ABCD'},'anatomicalQualification':False,'resources':resources,'supervisorStdout':summary}
        output.write('resource-receipt.json',encoded(receipt),resources[-1]['run'] if resources else 'A',emergency=True)
        return receipt

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preflight',action='store_true');parser.add_argument('--execute',action='store_true');parser.add_argument('--manifest',required=True);parser.add_argument('--output');parser.add_argument('--approved-manifest-sha256');a=parser.parse_args()
    if a.preflight==a.execute:raise Refusal('Choose preflight or explicitly approved execution')
    if a.preflight:
        data=read_regular(a.manifest);m=json.loads(data);validate_manifest(m,data);cg=cgroup_file();used=int(cg.read_text());
        if used>m['policy']['cgroupBytes']:raise Refusal('Observed cgroup ceiling')
        print(json.dumps({'status':'PREFLIGHT_READY_NO_PHYSICAL_IMPORTS','manifestSHA256':digest(data),'cgroupPath':str(cg),'observedCgroupBytes':used,'physicalEvaluations':0}));return
    if not a.output:raise Refusal('New private output directory required')
    receipt=execute(a.manifest,a.output,a.approved_manifest_sha256);print(json.dumps(receipt['supervisorStdout'],separators=(',',':')));
    if receipt['status']!='COMPLETE_FINALIZED':sys.exit(2)
if __name__=='__main__':
    try:main()
    except (Refusal,OSError,ValueError) as e:print(json.dumps({'status':'REFUSED_NO_ACCEPTANCE','reason':str(e)}));sys.exit(2)

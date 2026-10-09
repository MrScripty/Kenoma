"""Separately bounded offline postprocessor; never starts numerical workers."""
import argparse, copy, json, os, pathlib, stat, sys, time
from watchdog import EXPECTED_POLICY, Output, Refusal, cgroup_file, digest, encoded, read_regular, supervise
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();cfg=json.loads(read_regular(a.config));outpath=pathlib.Path(cfg['output'])
    if cfg.get('syntheticOnly') not in [True,False]:raise Refusal('Explicit rendering scope')
    policy=copy.deepcopy(EXPECTED_POLICY);policy.update(runs=[dict(id='A',wallSeconds=120)],aggregateWallSeconds=120,perRunOutputBytes=134217728,aggregateOutputBytes=134217728,perRunTranscriptBytes=1048576,aggregateTranscriptBytes=1048576,reservedReceiptBytes=1048576)
    out=Output(outpath,policy);start=time.monotonic();out.write('manifest.json',read_regular(a.config),'A')
    allowed={'viewer.js','viewer.html','provisional-geometry.gif','render-receipt.json'}|{f'frame-{i:02d}.jpg' for i in range(34)}
    def monitor():
        artifact=0;scratch=0;count=0
        for root,dirs,files in os.walk(out.path,followlinks=False):
            for name in dirs+files:
                q=pathlib.Path(root)/name;s=q.lstat()
                is_scratch=any(part=='browser-profile' or part.startswith(('.org.chromium.','playwright-artifacts-')) for part in q.relative_to(out.path).parts)
                if stat.S_ISLNK(s.st_mode) and not(is_scratch and name in {'SingletonLock','SingletonCookie','SingletonSocket'}):raise Refusal('Postprocessing symlink')
                if not(stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode) or is_scratch and (stat.S_ISLNK(s.st_mode) or stat.S_ISSOCK(s.st_mode))):raise Refusal('Postprocessing special file')
                count+=1
                if is_scratch:scratch+=s.st_size
                elif q.name in allowed:artifact+=s.st_size
                elif q.name not in {'manifest.json','transcript.log'}:raise Refusal('Foreign postprocessing artifact')
        if artifact>33554432 or scratch>67108864 or count>2048:raise Refusal('Postprocessing disk/file ceiling')
        # Include retained files + 16 MiB encode/decode staging allowance. RSS
        # is independently sampled for supervisor + child + Chromium tree.
        out.staging['A']=artifact+scratch+16777216;out.reserve('A',0)
    result,resources=supervise([sys.executable,str(pathlib.Path(__file__).with_name('render_worker.py')),str(pathlib.Path(a.config).resolve())],out,policy['runs'][0],start,allow_descendants=True,monitor=monitor)
    monitor();out.staging['A']=0
    profiles=[q for q in out.path.iterdir() if q.name=='browser-profile' or q.name.startswith(('.org.chromium.','playwright-artifacts-'))]
    for profile in profiles:
        if not profile.is_dir() or profile.is_symlink():raise Refusal('Invalid owned browser scratch')
        # Only the newly created, owned browser profile after verified reaping.
        if not resources['allProcessesReaped']:raise Refusal('Browser tree not disposed')
        import shutil;shutil.rmtree(profile)
    out.seal_log()
    for q in out.path.iterdir():
        if q.name in allowed:
            b=read_regular(q,8388608);out.reserve('A',len(b));out.charges['A']+=len(b);out.written[q.name]=dict(bytes=len(b),sha256=digest(b))
    receipt=dict(status='PASS_SYNTHETIC_ONLY' if result.get('status')=='PASS' and cfg['syntheticOnly'] else 'PASS_PROVISIONAL_GEOMETRY_ONLY' if result.get('status')=='PASS' else 'RESOURCE_INCONCLUSIVE',workerResult=result,resources=resources,limits=dict(wallSeconds=120,ownedRSSBytes=1000000000,cgroupBytes=16000000000,artifactBytes=33554432,browserScratchBytes=67108864,stagingBytes=16777216,combinedOutputAndStagingBytes=134217728,maximumFiles=2048,frames=34,jpegFrameBytes=262144,gifBytes=8388608,resolution=[960,720]),fileHashes=out.written,physicalEvaluations=0,physicalMotionAccepted=False,anatomicalQualification=False)
    out.write('resource-receipt.json',encoded(receipt),'A',emergency=True);out.verify_inventory();print(json.dumps(dict(status=receipt['status'],output=str(out.path),physicalEvaluations=0)))
    if result.get('status')!='PASS':sys.exit(2)
if __name__=='__main__':main()

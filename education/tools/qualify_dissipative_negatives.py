"""Damaged-copy controls for the qualified SLS artifact; originals stay unchanged."""
from pathlib import Path
import argparse,hashlib,json,shutil,tempfile
from check_dissipative_artifact import check,ROOT

def run(destination,output):
    source=Path(destination).resolve();out=Path(output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
    check(source)
    manifest=json.loads((source/'build-manifest.json').read_text())
    receipt=json.loads((source/'dissipative-qa/receipt.json').read_text())
    required={'build-manifest.json','dissipative-experiment.json','dissipative-qa/receipt.json','proofs/DissipativeBarReal.lean','proofs/dissipative-real-claims.json'}|set(manifest['proof_families'])|set(manifest['dissipative_outputs'])|set(receipt['delivered_input_sha256'])|{'dissipative-qa/'+name for name in receipt['output_sha256']}
    scratch=ROOT/'.artifact-tmp';scratch.mkdir(exist_ok=True);results=[]
    for name in ['missing-browser-receipt','stale-manifest-binding','forged-closed-zero-loss','changed-static-figure','changed-visible-plot','missing-real-claim']:
      with tempfile.TemporaryDirectory(dir=scratch) as temporary:
        copy=Path(temporary)
        for path in required:
            target=copy/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/path,target)
        receipt_path=copy/'dissipative-qa/receipt.json';r=json.loads(receipt_path.read_text())
        if name=='missing-browser-receipt':receipt_path.unlink()
        elif name=='stale-manifest-binding':r['build_manifest_sha256']='0'*64;receipt_path.write_text(json.dumps(r))
        elif name=='forged-closed-zero-loss':
            path=copy/'dissipative-qa/force-hold-trace.json';trace=json.loads(path.read_text());row=min(trace['trace'],key=lambda s:abs(s['time']-1));row['dissipationJ']=0;row['workJ']=row['storageJ'];row['balanceResidualJ']=0;path.write_text(json.dumps(trace));r['output_sha256']['force-hold-trace.json']=hashlib.sha256(path.read_bytes()).hexdigest();receipt_path.write_text(json.dumps(r))
        elif name=='changed-static-figure':(copy/'assets/property-dissipative.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Wrong state</text></svg>')
        elif name=='changed-visible-plot':(copy/'dissipative-qa/force-hold-loaded.png').write_bytes(b'changed plot')
        else:
            path=copy/'dissipative-real-proof-status.json';p=json.loads(path.read_text());p['claims'].pop();path.write_text(json.dumps(p))
        try:check(copy)
        except (AssertionError,FileNotFoundError) as error:results.append({'case':name,'detected':True,'reason':str(error) or 'Required proof/receipt condition rejected'})
        else:raise RuntimeError('Damaged SLS artifact unexpectedly passed: '+name)
    out.write_text(json.dumps({'result':'PASS_SIX_DAMAGED_SLS_ARTIFACT_CONTROLS','source_manifest_sha256':hashlib.sha256((source/'build-manifest.json').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256((ROOT/'tools/check_dissipative_artifact.py').read_bytes()).hexdigest(),'cases':results},indent=2)+'\n')
    print('PASS six damaged-copy SLS artifact controls')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('site',type=Path);p.add_argument('output',type=Path);a=p.parse_args();run(a.site,a.output)

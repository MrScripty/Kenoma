"""Actually rebundle two corrupted prototype copies; require independent native checks to fail."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from build_axisymmetric_preview import INPUTS
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def qualify(out,proof,oracle,experiment):
    out.mkdir(parents=True,exist_ok=False);records=[]
    changes=[('renderer-radius','web/axisymmetric-lab.mjs','[v[2],v[0],v[1]]','[v[2],1.05*v[0],1.05*v[1]]','Actual displayed vertex from independent Q2 map'),('worker-reaction','web/axisymmetric-worker.mjs','self.postMessage({sequence,configuration:c,state,boundary,surfaceJ,trace});','state.diagnostics.rightReactionN+=.01;self.postMessage({sequence,configuration:c,state,boundary,surfaceJ,trace});','Actual browser/offline rightReactionN')]
    inputs={n:sha(ROOT/n) for n in INPUTS+['tests/axisymmetric_browser.py','tools/qualify_axisymmetric_negatives.py']}
    for name,source,needle,replacement,expected in changes:
        case=out/name;root=case/'copy';root.mkdir(parents=True)
        for n in INPUTS+['tests/axisymmetric_browser.py']:
            target=root/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,target)
        (root/'node_modules').symlink_to(ROOT/'node_modules',target_is_directory=True)
        # Builder records the actual focused branch head using the original read-only .git pointer.
        (root/'.git').write_text(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=ROOT,text=True).strip().join(['gitdir: ','\n']))
        file=root/source;body=file.read_text();assert body.count(needle)==1;file.write_text(body.replace(needle,replacement))
        preview=case/'preview';build=subprocess.run([sys.executable,str(root/'tools/build_axisymmetric_preview.py'),str(preview),'--proof-directory',str(proof)],capture_output=True,text=True);(case/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0
        result=subprocess.run([sys.executable,str(root/'tests/axisymmetric_browser.py'),'--preview',str(preview),'--out',str(case/'browser'),'--oracle',str(oracle),'--experiment',str(experiment)],capture_output=True,text=True)
        log=result.stdout+result.stderr;(case/'browser.log').write_text(log)
        assert result.returncode!=0 and expected in log,(name,'Negative must fail meaningful independent native oracle',log[-3000:])
        assert not (case/'browser/axisymmetric-browser-status.json').exists()
        records.append({'case':name,'changed_source':source,'before_sha256':inputs[source],'after_sha256':sha(file),'mutation':{'before':needle,'after':replacement},'delivered_manifest_sha256':sha(preview/'axisymmetric-preview-manifest.json'),'expected_independent_failure':expected,'returncode':result.returncode,'failure_log_sha256':sha(case/'browser.log'),'scope':'Actual rebuilt browser copy and real GPU renderer/worker; negative source only, original acceptance criteria unchanged'})
    assert all(sha(ROOT/n)==h for n,h in inputs.items())
    record={'status':'PASS_NEGATIVES_REJECTED','source_input_sha256':inputs,'cases':records};(out/'axisymmetric-negative-status.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS two actually rebundled negatives rejected by independent browser oracles')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--proof-directory',type=Path,required=True);p.add_argument('--oracle',type=Path,required=True);p.add_argument('--experiment',type=Path,required=True);a=p.parse_args();qualify(a.out.resolve(),a.proof_directory.resolve(),a.oracle.resolve(),a.experiment.resolve())

"""Book adapter around unchanged accepted connected-model builders and oracles."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(out):
    (out/'assets').mkdir(parents=True,exist_ok=True)
    from check_axisymmetric_proofs import check
    from build_axisymmetric_preview import build
    def run(*args):subprocess.run(list(args),cwd=ROOT,check=True)
    def experiment(name,tool):
        path=out/name
        if path.exists():
            data=json.loads(path.read_text())
            if data.get('inputs') and all(digest(ROOT/n)==h for n,h in data['inputs'].items()):return
        run('node','tools/'+tool,str(path))
    run(sys.executable,'tools/qualify_axisymmetric_material.py',str(out/'connected-material-oracle.json'))
    experiment('connected-experiment.json','axisymmetric-experiment.mjs')
    run(sys.executable,'tools/qualify_axisymmetric_experiment.py',str(out/'connected-experiment.json'),str(out/'connected-numerical-qualification.json'))
    experiment('connected-end-face-experiment.json','axisymmetric-end-face-experiment.mjs')
    run(sys.executable,'tools/qualify_axisymmetric_end_faces.py',str(out/'connected-end-face-experiment.json'),str(out/'connected-material-oracle.json'),str(out/'connected-experiment.json'),str(out/'connected-end-face-qualification.json'))
    proof=ROOT/'.tools/connected-book-proofs';check(proof)
    preview=out/'connected-passive';shutil.rmtree(preview,ignore_errors=True);build(preview,proof)
    run('node','tools/connected-specimen-figure.mjs',str(out/'connected-experiment.json'),str(out/'assets/connected-specimen.svg'),str(out/'connected-figure.json'))
def block(web):
    image='![Solved connected taper meridians at zero and ±10% imposed end displacement, at a fixed SI scale. Gray is the reference boundary; teal is sampled from the actual Q2 solution.](assets/connected-specimen.svg)'
    if not web:return '\n'+image+'\n\n[Open the connected specimen controls](connected-passive/index.html).\n'
    return '\n'+image+'\n\n<div class="connected-interactive"><p><a href="connected-passive/index.html">Open the complete connected specimen lab</a> · <a href="connected-experiment.json">Numerical states</a> · <a href="connected-numerical-qualification.json">Independent numerical qualification</a> · <a href="connected-material-oracle.json">Independent material oracle</a> · <a href="connected-end-face-qualification.json">Repaired end-face qualification</a></p><iframe src="connected-passive/index.html" title="Connected passive finite-compliance specimen controls" loading="lazy"></iframe></div>\n'

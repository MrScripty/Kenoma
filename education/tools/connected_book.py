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
    # Preserve the accepted builder and stylesheet bytes. Add book-only layout
    # rules after the canonical stylesheet, with complete input/output bindings.
    manifest_path=preview/'axisymmetric-preview-manifest.json';manifest=json.loads(manifest_path.read_text())
    manifest['accepted_builder_output_sha256']=dict(manifest['output_sha256'])
    style='web/connected-book-integration.css';shutil.copy2(ROOT/style,preview/'assets/connected-book-integration.css')
    page=preview/'index.html';page.write_text(page.read_text().replace('</head>','<link rel="stylesheet" href="assets/connected-book-integration.css"></head>'))
    manifest['input_sha256'].update({name:digest(ROOT/name) for name in [style,'tools/connected_book.py']})
    manifest['integration_scope']='Book presentation: wrap long proof metadata and allow control grid labels to shrink. Accepted law, solver, controls, source stylesheet and proof bytes unchanged.'
    manifest['output_sha256']={str(p.relative_to(preview)):digest(p) for p in sorted(preview.rglob('*')) if p.is_file() and p!=manifest_path}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    run('node','tools/connected-specimen-figure.mjs',str(out/'connected-experiment.json'),str(out/'assets/connected-specimen.svg'),str(out/'connected-figure.json'))
def block(web):
    image='![Solved connected taper meridians at zero and ±10% imposed end displacement, at a fixed SI scale. Gray is the reference boundary; teal is sampled from the actual Q2 solution.](assets/connected-specimen.svg)'
    if not web:return '\n'+image+'\n\n[Open the connected specimen controls](connected-passive/index.html).\n'
    return '\n'+image+'\n\n<div class="connected-interactive"><p><a href="connected-passive/index.html">Open the complete connected specimen lab</a> · <a href="connected-experiment.json">Numerical states</a> · <a href="connected-numerical-qualification.json">Independent numerical qualification</a> · <a href="connected-material-oracle.json">Independent material oracle</a> · <a href="connected-end-face-qualification.json">Repaired end-face qualification</a></p><iframe src="connected-passive/index.html" title="Connected passive finite-compliance specimen controls" loading="lazy"></iframe></div>\n'

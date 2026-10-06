"""Build a separate connected passive prototype, requiring fresh local proof evidence."""
from pathlib import Path
import argparse,hashlib,html,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
MODULES=['axisymmetric-material.mjs','axisymmetric-specimen.mjs','axisymmetric-lab.mjs','axisymmetric-worker.mjs','scene-status.mjs']
INPUTS=['web/'+n for n in MODULES]+['web/axisymmetric-lab.css','tools/build_axisymmetric_preview.py','proofs/AxisymmetricSpecimenReal.lean','proofs/axisymmetric-specimen-real-claims.json','tools/check_axisymmetric_proofs.py','proofs/mathlib-lock.json']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(destination,proof_directory):
    out=Path(destination).resolve();proof=Path(proof_directory).resolve()
    receipt=json.loads((proof/'axisymmetric-proof-status.json').read_text())
    assert receipt['status']=='PASS' and len(receipt['claims'])==9 and all(c['status']=='checked' for c in receipt['claims'])
    assert all(digest(ROOT/n)==h for n,h in receipt['input_sha256'].items()),'Fresh proof inputs differ'
    lock=json.loads((ROOT/'proofs/mathlib-lock.json').read_text())
    assert receipt['mathlib']==lock,'Official dependency lock differs'
    transcript=(proof/'axisymmetric-lean-check.txt').read_text()
    assert all(c['theorem'] in transcript for c in receipt['claims'])
    if out.exists():raise FileExistsError('Choose a fresh preview directory')
    before={n:digest(ROOT/n) for n in INPUTS}
    out.mkdir(parents=True);(out/'web').mkdir();(out/'assets').mkdir();(out/'proofs').mkdir()
    for name in MODULES:shutil.copy2(ROOT/'web'/name,out/'web'/name)
    shutil.copy2(ROOT/'web/axisymmetric-lab.css',out/'assets/axisymmetric-lab.css')
    for name in ['AxisymmetricSpecimenReal.lean','axisymmetric-specimen-real-claims.json','mathlib-lock.json']:shutil.copy2(ROOT/'proofs'/name,out/'proofs'/name)
    for name in ['axisymmetric-proof-status.json','axisymmetric-lean-check.txt']:shutil.copy2(proof/name,out/'proofs'/name)
    for source,target in [('axisymmetric-lab.mjs','axisymmetric-app.js'),('axisymmetric-worker.mjs','axisymmetric-worker.js')]:
        subprocess.run([str(ROOT/'node_modules/.bin/esbuild'),str(ROOT/'web'/source),'--bundle','--minify','--format=esm','--target=es2022',f'--outfile={out/"assets"/target}','--legal-comments=external'],check=True)
    cards=''.join('<details><summary>'+html.escape(c['claim'])+'</summary><p><strong>Assumptions:</strong> '+html.escape(c['assumptions'])+'</p><pre>'+html.escape(c['statement'])+'</pre><p><strong>Limits:</strong> '+html.escape(c['limits'])+'</p><p>Kernel checked: '+html.escape(c['theorem'])+'. Axioms: '+html.escape(', '.join(c['axioms']))+'.</p></details>' for c in receipt['claims'])
    document='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kenoma connected passive specimen — prototype</title><link rel="stylesheet" href="assets/axisymmetric-lab.css"><style>body{margin:0;background:#eef3f8;color:#233b50;font:16px/1.55 system-ui,sans-serif}main{max-width:920px;margin:24px auto;padding:0 16px}h1{font-size:30px;line-height:1.2}h2{font-size:23px}a{color:#14618e}details{background:white;border:1px solid #b7c9d6;border-radius:8px;padding:12px;margin:12px 0}summary{cursor:pointer;font-weight:600}pre{font:14px/1.5 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere}.scope{padding:14px;background:#fff1df;border-left:4px solid #bd783a}button{cursor:pointer}svg text{font:14px system-ui,sans-serif}</style></head><body><main><h1>Connected passive specimen</h1>
<p class="scope"><strong>Review prototype, separate from the published lessons.</strong> One connected axisymmetric continuum with finite volume compliance. This is a passive mathematical specimen, with no muscle activation or anatomical calibration. It cannot enforce exact J = 1, and these tests do not establish buckling or unrestricted three-dimensional stability.</p>
<p>The reference specimen is 0.05 m long with a 0.005 m small-end radius. Radius ratio 1.5 means area ratio 2.25. The complete end faces have imposed axial displacement; their radial displacement remains free. The symmetry axis has r = 0 and z<sub>R</sub> = 0. The full tapered side condition is P N = 0, with N proportional to (1, 0, −a′), imposed naturally in the weak problem and checked separately away from corners.</p>
<div class="axisymmetric-lab" data-axisymmetric id="connected-passive">
<h2>Displace the ends, inspect the solved body</h2>
<p>All physical coordinates use metres. The camera and gray reference outline use a fixed scale: changing the specimen does not rescale the view. Surface color interpolates sampled J; the readouts below evaluate the actual solved field.</p>
<div class="controls">
<label>End displacement / reference length<select data-setting="epsilon"><option value="-0.1">−10% compression (−0.005 m)</option><option value="0">Zero displacement</option><option value="0.1">+10% tension (+0.005 m)</option></select></label>
<label>Reference radius ratio<select data-setting="ratio"><option value="1">1: uniform cylinder oracle</option><option value="1.5">1.5: continuous taper (area ratio 2.25)</option></select></label>
<label>Connected Q2 meridional cells<select data-setting="mesh"><option value="4,2">4 axial × 2 radial</option><option value="8,4">8 axial × 4 radial</option><option value="16,8">16 axial × 8 radial</option></select></label>
<label>Newton solve<select data-setting="cap"><option value="25">Up to 25 iterations per continuation stage</option><option value="1">One direct iteration: diagnostic approximation</option></select></label>
</div>
<p class="progress" role="status"></p><p class="solve-status" role="status">Computing the undeformed reference state.</p>
<div class="buttons"><button data-action="start">Start interactive 3D</button><button data-action="front">Front view</button><button data-action="oblique">Oblique view</button><button data-action="reset">Reset to undeformed taper</button><button data-action="export">Download current numerical state</button></div>
<p class="scene-notice" role="status"></p>
<div class="static-reference"><svg viewBox="0 0 600 140" role="img" aria-label="Static undeformed taper reference; not a solved display"><path d="M90 45L510 30L510 110L90 95Z" fill="#d9e6ef" stroke="#718b9e"/><path d="M80 70H520" stroke="#869daf" stroke-dasharray="6 4"/><text x="90" y="132">Static reference only; start 3D for current solved geometry</text></svg></div>
<div class="scene-host" hidden></div>
<h3>Actual SI state and residual</h3><dl class="totals"></dl>
<h3>Material probe</h3><div class="controls">
<label>Reference axial fraction Z/L<select data-probe="z"><option value="0.1">0.1</option><option value="0.25">0.25</option><option value="0.5" selected>0.5</option><option value="0.75">0.75</option><option value="0.9">0.9</option></select></label>
<label>Reference radial fraction R/a(Z)<select data-probe="r"><option value="0">0: symmetry axis</option><option value="0.25">0.25</option><option value="0.5" selected>0.5</option><option value="0.75">0.75</option><option value="1">1: free side</option></select></label></div>
<p class="probe-readout"></p><div class="plot"></div></div>
<h2>Declared mechanics and checks</h2>
<p>F = [[r<sub>R</sub>, 0, r<sub>Z</sub>], [0, r/R, 0], [z<sub>R</sub>, 0, z<sub>Z</sub>]], with the regular limit r/R = r<sub>R</sub> on the axis. J = (r/R)(r<sub>R</sub>z<sub>Z</sub> − r<sub>Z</sub>z<sub>R</sub>). The reference integral uses weight 2πR. W = μ/2 (J<sup>−2/3</sup> tr(FᵀF) − 3) + K/2 (log J)², with μ = 1500 Pa and K = 30000 Pa. Exact reference frustum volume is π L a₀² (1 + ρ + ρ²)/3. No postsolve volume correction is applied.</p>
<p>Full force and tangent come from the declared energy. Newton uses the original constrained tangent. The complete free-force residual is normalized by μ π a₀², a positive scale also at zero load; the provisional target is 10<sup>−10</sup>. A converged solve means stationarity of this discretization. Mesh refinement, independent quadrature, material-point J error, weighted J error, reaction/energy agreement, and rendered volume need their separate qualification receipts. End/side corner gradients are recorded separately and remain unresolved.</p>
<h2>Nine local real-number identities</h2>
<p>Fresh Lean 4.19.0 checking with pinned official mathlib v4.19.0. These identities support the determinant, logarithmic storage, side traction, force conversion and reference geometry. They do not certify the JavaScript implementation, finite-element equilibrium, convergence, pointwise error, global injectivity or stability.</p>
<p><a href="proofs/AxisymmetricSpecimenReal.lean">Complete Lean source</a> · <a href="proofs/axisymmetric-lean-check.txt">Fresh kernel transcript</a> · <a href="proofs/axisymmetric-proof-status.json">Exact statements and checked receipt</a> · <a href="axisymmetric-preview-manifest.json">Delivered source/output hashes</a></p>'''+cards+'''<p>Prototype source: <a href="web/axisymmetric-specimen.mjs">assembly and solver</a>, <a href="web/axisymmetric-material.mjs">material and uniform oracle</a>. This page adds no published chapter or capstone-completion claim.</p></main><script type="module" src="assets/axisymmetric-app.js"></script></body></html>'''
    (out/'index.html').write_text(document)
    (out/'THIRD_PARTY_NOTICES.txt').write_text('Kenoma original content: Apache-2.0. Three.js 0.180.0, MIT:\n'+(ROOT/'node_modules/three/LICENSE').read_text())
    assert before=={n:digest(ROOT/n) for n in INPUTS}
    record={'schema':1,'scope':'Separate connected passive finite-compliance prototype; nine fresh local Real identities; no book/release claim','source_base_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'input_sha256':before,'proof_receipt_sha256':digest(proof/'axisymmetric-proof-status.json'),'output_sha256':{str(p.relative_to(out)):digest(p) for p in sorted(out.rglob('*')) if p.is_file()}}
    (out/'axisymmetric-preview-manifest.json').write_text(json.dumps(record,indent=2)+'\n');print('Built separate connected prototype at '+str(out))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('out',type=Path);p.add_argument('--proof-directory',required=True,type=Path);a=p.parse_args();build(a.out,a.proof_directory)

"""Assemble chapters and checked evidence, then build a portable Pages artifact."""
from pathlib import Path
import hashlib,html,json,re,shutil,subprocess
from check_proofs import check
from figures import generate
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'

LABS={
 'force':{'title':'Laboratory 1 · Constant force','model':'Analytic planar motion; constant net force; no contact or anatomy.',
  'description':'A position marker moves along x. The yellow arrow represents force and the violet arrow velocity. Coordinates are fitted to the view; values retain SI units.',
  'caption':'Reference at t = 1 s: m = 2 kg, F = 4 N, x = 1 m, v = 2 m/s. The interactive starts at t = 0 s. Original schematic geometry.',
  'controls':[('mass','Mass (kg)',0.5,5,0.5,2),('force','Net force x (N)',-8,8,0.5,4),('time','Elapsed time (s)',0,2,0.05,0)]},
 'torque':{'title':'Laboratory 2 · Force and lever arm','model':'Prescribed pose; massless rigid lever; point load; uniform illustrative gravity.',
  'description':'A rigid bar extends from a fixed pivot to a load. The yellow arrow points downward. The white projection marks the horizontal distance to the gravity line. This is a posed lever, not an active arm.',
  'caption':'Default: m = 5 kg, L = 0.30 m, θ = 0°. Torque about z is -14.715 N m. Original schematic geometry; no anatomical measurements.',
  'controls':[('mass','Point-load mass (kg)',1,10,0.5,5),('length','Lever length (m)',0.1,0.4,0.01,0.3),('angle','Angle from horizontal (°)',0,150,1,0)]},
 'energy':{'title':'Laboratory 3 · Numerical energy','model':'Ideal undamped linear spring; fixed physics steps; 600-step playback limit.',
  'description':'A spring connects a wall to a mass marker. Extension is visually exaggerated and fitted to the view. The energy chart shows a solid numerical trace and a dashed initial-energy reference. Read numeric values when the chart rescales.',
  'caption':'Initial state: m = 1 kg, k = 40 N/m, x = 0.20 m, v = 0 m/s, E = 0.80 J. Default symplectic Euler step h = 0.02 s. Original schematic geometry.',
  'controls':[]},
 'elbow':{'title':'Laboratory 4 · Articulated elbow and activation','model':'Schematic one-hinge forward dynamics or prescribed hold; toy line muscle; rigid tendon; no force–velocity law or tissue/contact mechanics.',
  'description':'The fixed upper segment joins a rotating forearm and dumbbell. Gold markers locate a synthetic flexor path. The red belly is an illustrative shape with no mechanical force of its own. The yellow arrow marks dumbbell gravity.',
  'caption':'Original schematic: q starts at 30° from downward, load 5 kg, excitation 0.6, activation 0, h = 0.005 s. Dimensions and actuator parameters are teaching choices, not anatomical measurements.',
  'controls':[('load','Dumbbell mass (kg)',0,10,0.5,5),('excitation','Excitation u (0–1)',0,1,0.05,0.6),('angle','Initial / prescribed flexion q (°)',0,135,1,30)]}
}
def lab_block(key,web):
    lab=LABS[key];e=html.escape
    if not web:
        return f"\n### {lab['title']}\n\n![{lab['description']}](assets/{key}.svg)\n\n{lab['caption']}\n\n**Model:** {lab['model']}\n\n[Open this laboratory in the web edition](index.html#lab-{key}).\n"
    controls=''
    for keyp,label,low,high,step,value in lab['controls']:
        controls+=f'<div class="control"><label for="{key}-{keyp}-number">{e(label)}</label><div class="input-pair"><input type="range" aria-label="{e(label)} slider" data-param="{keyp}" min="{low}" max="{high}" step="{step}" value="{value}"><input id="{key}-{keyp}-number" type="number" data-param="{keyp}" min="{low}" max="{high}" step="{step}" value="{value}"></div></div>'
    if key=='energy':
        controls+='<div class="control"><label for="energy-method">Integrator</label><select id="energy-method" data-param="method"><option value="explicit">Explicit Euler</option><option value="symplectic" selected>Symplectic Euler</option><option value="verlet">Velocity Verlet</option></select></div>'
        controls+='<div class="control"><label for="energy-dt">Step size h (s)</label><select id="energy-dt" data-param="dt"><option value="0.005">0.005 s</option><option value="0.01">0.01 s</option><option value="0.02" selected>0.02 s</option><option value="0.05">0.05 s</option><option value="0.1">0.10 s</option></select></div>'
    if key=='elbow':
        controls+='<div class="control"><label for="elbow-mode">Motion mode</label><select id="elbow-mode" data-param="mode"><option value="forward">Force-driven hinge</option><option value="prescribed">Prescribed static hold</option></select></div><div class="control"><label for="elbow-dt">Physics step h (s)</label><select id="elbow-dt" data-param="dt"><option value="0.0025">0.0025 s</option><option value="0.005" selected>0.005 s</option><option value="0.01">0.01 s</option></select></div>'
    temporal='<button data-action="play">Play</button><button data-action="step">Single step</button>' if key!='torque' else ''
    if key=='elbow':temporal+='<button data-action="pulse">Lift / release pulse</button><button data-action="release">Release excitation</button><button data-action="export">Download trace</button>'
    chart=''
    if key=='energy':
        chart='<svg class="energy-chart" viewBox="0 0 580 205" role="img" aria-label="Energy versus step number"><title>Energy versus step number</title><text class="scale" x="40" y="20" font-size="13">Energy range 0 to 0.96 J</text><path d="M40 30V160H540" fill="none" stroke="#456171"/><line class="reference" x1="40" x2="540" y1="52" y2="52" stroke="#754d1f" stroke-dasharray="5 4"/><polyline class="trace" fill="none" stroke="#087567" stroke-width="2" points="40,52"/><text x="40" y="185" font-size="13">0</text><text x="435" y="185" font-size="13">600 steps</text><text x="195" y="201" font-size="12">Solid: numerical energy · Dashed: initial 0.80 J</text></svg>'
    return f'''\n<section class="laboratory" data-demo="{key}" id="lab-{key}" aria-labelledby="lab-{key}-heading">
<div class="lab-heading"><h3 id="lab-{key}-heading">{e(lab['title'])}</h3><p class="model-label">{e(lab['model'])}</p></div>
<figure class="static-figure"><img src="assets/{key}.svg" alt="{e(lab['description'])}"><figcaption>{e(lab['caption'])}</figcaption></figure>
<div class="scene-host"></div><div class="controls">{controls}</div>
<div class="actions"><button data-action="start">Start 3D scene</button>{temporal}<button data-action="reset">Reset</button><button data-action="view">Front / oblique view</button><button data-action="summary">Read current results</button><button data-action="copy">Copy state</button></div>
<dl class="readout" aria-label="Current numerical results"></dl>{chart}
<p class="lab-description">{e(lab['description'])} Axes: x right, y up, z out of the plane.</p>
<p class="announce" role="status" aria-live="polite"></p><textarea class="preset" aria-label="Reproducible state JSON" readonly hidden></textarea>
<noscript><p>Interactive controls require JavaScript. The figure, equations, worked examples and experiment table remain available.</p></noscript>
</section>\n'''

def build():
    evidence=check()
    manifest=json.loads((ROOT/'book/book.json').read_text())
    claims={c['id']:c for c in evidence['claims']}
    source=(ROOT/'proofs/Mechanics.lean').read_text()
    def proof_block(id,web):
        c=claims[id];name=c['theorem'].split('.')[-1]
        statement=re.search(r'theorem '+re.escape(name)+r'\b(.*?) := by',source,re.S)
        if not statement: raise ValueError('Missing theorem source')
        stmt='theorem '+name+statement.group(1)
        meta=f"Lean 4.19.0; mathlib not used; transitive axioms: {', '.join(c['axioms']) or 'none'}; source SHA-256: {evidence['source_sha256']}"
        if not web:
            return f"\n**Checked claim {id}:** {c['claim']}\n\n**Assumptions:** {c['assumptions']}\n\n```lean\n{stmt}\n```\n\n**Limits:** {c['limitations']}\n\nDeclaration: `{c['theorem']}`. {meta}. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).\n"
        e=html.escape
        return f'''\n<aside class="proof-card" id="proof-{id}" aria-label="Checked mathematical claim">
<h3>Checked claim · {e(id)}</h3><p>{e(c['claim'])}</p><p><strong>Assumptions:</strong> {e(c['assumptions'])}</p>
<pre><code>{e(stmt)}</code></pre><p><strong>Limits:</strong> {e(c['limitations'])}</p>
<p class="proof-meta">Declaration {e(c['theorem'])}. {e(meta)}.</p>
<p><a href="proofs/Mechanics.lean">Full source</a> · <a href="proof-status.json">Build receipt</a> · <a href="lean-check.txt">Kernel dependency report</a></p>
<details><summary>Read complete checked definitions and proof source</summary><pre><code>{e(source)}</code></pre></details></aside>\n'''
    experiment_text=subprocess.check_output(['node',str(ROOT/'tools/experiment.mjs')],text=True)
    (OUT/'experiment.json').write_text(experiment_text)
    experiment=json.loads(experiment_text)
    table='| Method | h (s) | Steps | Max relative energy deviation (%) | Final position error (m) |\n|:--|--:|--:|--:|--:|\n'
    for r in experiment['rows']:
        table+=f"| {r['method']} | {r['dt']:.2f} | {r['steps']} | {100*r['max_relative_energy_error']:.4g} | {r['final_position_error']:.4g} |\n"
    elbow_text=subprocess.check_output(['node',str(ROOT/'tools/elbow-experiment.mjs')],text=True)
    (OUT/'elbow-experiment.json').write_text(elbow_text)
    elbow=json.loads(elbow_text)
    elbow_table='| h (s) | Steps | Final q (°) | Final a | Active work (J) | Max balance residual (J) |\n|--:|--:|--:|--:|--:|--:|\n'
    for r in elbow['rows']:
        elbow_table+=f"| {r['dt']:.4f} | {r['steps']} | {r['finalAngleDegrees']:.5f} | {r['finalActivation']:.6f} | {r['activeWork']:.6f} | {r['maxBalanceResidual']:.3g} |\n"
    chapters='\n\n'.join((ROOT/'book/chapters'/p).read_text() for p in manifest['chapters'])
    def expand(web):
        text=re.sub(r'\{\{demo:(\w+)\}\}',lambda m:lab_block(m[1],web),chapters)
        text=re.sub(r'\{\{proof:([\w-]+)\}\}',lambda m:proof_block(m[1],web),text)
        text=text.replace('{{experiment}}',table)
        text=text.replace('{{elbow-experiment}}',elbow_table)
        if '{{' in text: raise ValueError('Unexpanded build directive')
        return text+'\n\n# Checked source appendix {#checked-source-appendix}\n\nThe source below is included for inspection. It was checked by the command and toolchain recorded in each receipt; compilation establishes only its stated domain.\n\n```lean\n'+source+'```\n\n## Proof check receipt {#proof-check-receipt}\n\nFresh successful invocation: `'+evidence['command']+'`. Toolchain: '+evidence['lean_version']+'. Checked declarations: '+str(len(evidence['claims']))+'. Source SHA-256: `'+evidence['source_sha256']+'`. Claim-map SHA-256: `'+evidence['claims_sha256']+'`. Only bundled Std is used. This receipt establishes the exact claims above; it does not validate JavaScript, biological parameters, or medical use.\n\n## Kernel dependency report {#kernel-dependency-report}\n\n```text\n'+(OUT/'lean-check.txt').read_text()+'```\n'
    front=f"---\ntitle: {manifest['title']}\nsubtitle: {manifest['subtitle']}\nlang: en\n---\n\n"
    (OUT/'kenoma-mechanics.md').write_text(front+expand(False))
    staging=OUT/'web-staging.md';staging.write_text(front+expand(True))
    subprocess.run(['pandoc',str(staging),'--standalone','--mathml','--toc','--toc-depth=2',
      '--template',str(ROOT/'web/template.html'),'-o',str(OUT/'index.html')],check=True)
    html_path=OUT/"index.html"
    rendered=html_path.read_text()
    rendered=re.sub(r'<math display="block".*?</math>', lambda m: '<div class="equation" tabindex="0" aria-label="Scrollable displayed equation">'+m[0]+'</div>', rendered, flags=re.S)
    html_path.write_text(rendered)
    staging.unlink()
    assets=OUT/'assets';generate(assets)
    shutil.copy(ROOT/'web/style.css',assets/'style.css')
    subprocess.run([str(ROOT/'node_modules/.bin/esbuild'),str(ROOT/'web/app.mjs'),'--bundle','--minify','--format=esm','--target=es2022',f'--outfile={assets/"app.js"}','--legal-comments=external'],check=True)
    proofs=OUT/'proofs';proofs.mkdir(exist_ok=True)
    for file in ['Mechanics.lean','lean-toolchain','claims.json']:shutil.copy(ROOT/'proofs'/file,proofs/file)
    notices=OUT/'THIRD_PARTY_NOTICES.txt'
    notices.write_text('Kenoma original content: Apache-2.0. No third-party anatomical assets are included.\n\nThree.js 0.180.0 (MIT)\n'+(ROOT/'node_modules/three/LICENSE').read_text()+'\n\nBuild tool esbuild 0.25.10 (MIT)\n'+(ROOT/'node_modules/esbuild/LICENSE.md').read_text())
    shutil.copy(ROOT.parent/'LICENSE',OUT/'LICENSE')
    (OUT/'.nojekyll').touch()
    inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['book','web','proofs','tools'] for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
    for relative in ['package.json','package-lock.json','requirements.txt']:
        inputs[relative]=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
    manifest_out={'schema':1,'milestone':'articulated-elbow-2','input_sha256':inputs,'lean':evidence['lean_version'],
      'pandoc':subprocess.check_output(['pandoc','--version'],text=True).splitlines()[0],
      'node':subprocess.check_output(['node','--version'],text=True).strip(),
      'numerical_experiment':'experiment.json','proof_evidence':'proof-status.json',
      'git_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'original_plans_base':'9b0c67fd25e1b645833a68bb9b1c2aba1404bbce',
      'determinism':'State progression repeatable in the pinned implementation; cross-browser transcendental bit identity and PDF byte identity not asserted.'}
    (OUT/'build-manifest.json').write_text(json.dumps(manifest_out,indent=2)+'\n')
    print('Built single-source Markdown and portable HTML in education/dist')
if __name__=='__main__':build()

"""Assemble chapters and checked evidence, then build a portable Pages artifact."""
from pathlib import Path
from executable_outputs import executable_outputs
import hashlib,html,json,re,shutil,subprocess
from check_proofs import check
from check_anatomical_proofs import check as check_transfer
from check_coupled_proofs import check as check_coupled
from check_arm_proofs import check as check_arm
from check_property_proofs import check as check_properties
from check_material_proofs import check as check_material
from check_real_lesson_proofs import check as check_real_lessons, FAMILIES as REAL_FAMILIES
from property_labs import block as property_block
from dissipative_lab import block as dissipative_block
from serial_lab import block as serial_block
from connected_book import prepare as prepare_connected, block as connected_block
from figures import generate
from evidence_figures import generate as evidence_figures
from spatial_figures import generate as advanced_figures
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'

def theorem_statement(checked_source,name):
    # A checked theorem may use a term proof or a tactic proof. Stop at its
    # assignment, and never borrow a later declaration's proof delimiter.
    statement=re.search(r'^theorem '+re.escape(name)+r'\b(?:(?!^\s*(?:theorem|def|lemma)\b).)*?\s:=',checked_source,re.S|re.M)
    if not statement:raise ValueError('Missing theorem statement: '+name)
    return statement.group(0).rsplit(':=',1)[0].rstrip()

LABS={
 'force':{'title':'Laboratory 1 · Constant force','model':'Analytic planar motion; constant net force; no contact or anatomy.',
  'description':'A position marker moves along x. Position scale is fixed over the 0–2 s trajectory for the selected mass and force; grid spacing is reported below. Yellow force and violet velocity arrows use separate scales. Values retain SI units.',
  'caption':'Reference at t = 1 s: m = 2 kg, F = 4 N, x = 1 m, v = 2 m/s. The interactive starts at t = 0 s. Original schematic geometry.',
  'controls':[('mass','Mass (kg)',0.5,5,0.5,2),('force','Net force x (N)',-8,8,0.5,4),('time','Elapsed time (s)',0,2,0.05,0)]},
 'torque':{'title':'Laboratory 2 · Force and lever arm','model':'Prescribed pose; massless rigid lever; point load; uniform illustrative gravity.',
  'description':'A rigid bar extends from a fixed pivot to a load. The yellow arrow points downward. The white projection marks the horizontal distance to the gravity line. This is a posed lever, not an active arm.',
  'caption':'Default: m = 5 kg, L = 0.30 m, θ = 0°. Torque about z is -14.715 N m. Original schematic geometry; no anatomical measurements.',
  'controls':[('mass','Point-load mass (kg)',1,10,0.5,5),('length','Lever length (m)',0.1,0.4,0.01,0.3),('angle','Angle from horizontal (°)',0,150,1,0)]},
 'energy':{'title':'Laboratory 3 · Numerical energy','model':'Ideal undamped linear spring; fixed physics steps; 12 simulated seconds per trajectory; 120–2,400 fixed steps for the supported h.',
  'description':'A spring connects a wall to a mass marker. Extension is visually exaggerated and fitted to the view. The energy chart shows a solid numerical trace and a dashed initial-energy reference. Read numeric values when the chart rescales.',
  'caption':'Initial state: m = 1 kg, k = 40 N/m, x = 0.20 m, v = 0 m/s, E = 0.80 J. Default symplectic Euler step h = 0.02 s. Original schematic geometry.',
  'controls':[]},
 'elbow':{'title':'Laboratory 4 · Articulated elbow and activation','model':'Schematic one-hinge forward dynamics or prescribed hold; toy line muscle; rigid tendon; no force–velocity law or tissue/contact mechanics.',
  'description':'The fixed upper segment joins a rotating forearm and dumbbell. Gold markers locate a synthetic flexor path. The red belly is an illustrative shape with no mechanical force of its own. The yellow arrow marks dumbbell gravity.',
  'caption':'Original schematic: q starts at 30° from downward, load 5 kg, excitation 0.6, activation 0, h = 0.005 s. Dimensions and actuator parameters are teaching choices, not anatomical measurements.',
  'controls':[('load','Dumbbell mass (kg)',0,10,0.5,5),('excitation','Excitation u (0–1)',0,1,0.05,0.6),('angle','Initial / prescribed flexion q (°)',0,135,1,30)]},
 'series':{'title':'Laboratory 5 · Tendon, tissue and the same-pose skinning baseline','model':'Schematic series actuator; quasistatic affine hyperelastic block with ideal plate contact; tissue reaction drives the hinge. No anatomical calibration, spatial FEM or separate skin/fascia law.',
  'description':'Both schematic arms have the same angle. Left: red active/passive fiber and gold tensile tendon; enlarged teal tissue block between gold frictionless plates. Right: the identical bind block receives uniform 50/50 linear blend skinning and has no force model. Insets are enlarged eight times in world units; read SI values for actual dimensions.',
  'caption':'Static reference at q = 90°; interactive starts at q = 30°. Tendon stiffness 30,000 N/m, tissue shear modulus 1,500 Pa and bulk modulus 50,000 Pa are authored teaching choices. Surface is the block boundary, not a separately modeled skin layer.',
  'controls':[('load','Dumbbell mass (kg)',0,10,0.5,5),('excitation','Excitation u (0–1)',0,1,.05,.6),('angle','Initial / prescribed flexion q (°)',0,135,1,30)]}
}
LABS.update({
 'spatial':{'title':'Laboratory 7 · Muscle under skin and elbow contact','model':'Authored 3D edge/volume energy, separate skin membrane and fascia tethers; finite quasistatic sampled bone contact; one-way hinge → shape. Not FEM, patient anatomy or medical pressure.',
 'description':'Left: coral deformable volume, red active fibre spans, gold tendon span, mint separate skin membrane and yellow contact samples on a schematic articulated arm. Right: the identical bind volume and skin, posed once with linear blend skinning at the identical hinge angle. Bones and dumbbells have identical poses; geometry uses SI coordinates and a common viewing scale.',
 'caption':'Compression fixture: q = 90°, activation 0.6, 640-iteration cap. Mechanical minimum volume ratio 0.736; same-pose LBS minimum 0.171. Sampled penetration 0.0283 mm versus 9.75 mm. This original schematic is not registered to the real atlas.',
 'controls':[('load','Dumbbell mass (kg)',0,10,.5,5),('excitation','Excitation u (0–1)',0,1,.05,.6),('angle','Set flexion q (°)',0,100,1,30)]},
 'continuum':{'title':'Laboratory 6 · Matched spatial FEM and compliant solve','model':'Linear constant-strain tetrahedra; authored isotropic material; manufactured static load or one implicit step from rest. Small-strain model, no contact or muscle.',
 'description':'Left: converged discrete FEM reference. Right: a finite compliant strain solve for the identical implicit step, or analytic nodal samples in static mode. Both use the same mesh, camera and visible displacement magnification. Gray outlines show the bind block; the gold edge marks the x = 0 clamp. Orange arrows show six representative applied nodal loads on a common normalized length scale; distributed body and face loads are specified in the chapter.',
 'caption':'Authored 40 × 20 × 20 mm fixture, E = 100 kPa, ν = 0.25, n = 3, h = 0.0005 s, five compliant sweeps. Displacements in this illustration are magnified 50×; numerical errors and energies are unscaled SI quantities.',
 'controls':[]}
})
def advanced_block(key,web):
    lab=LABS[key];e=html.escape
    if not web:return f"\n### {lab['title']}\n\n![{lab['description']}](assets/{key}.svg)\n\n{lab['caption']}\n\n**Model:** {lab['model']}\n\n[Open the interactive laboratory](index.html#lab-{key}).\n"
    controls=''
    for param,label,low,high,step,value in lab['controls']:
        controls+=f'<div class="control"><label for="{key}-{param}-number">{label}</label><div class="input-pair"><input type="range" aria-label="{label} slider" data-param="{param}" min="{low}" max="{high}" step="{step}" value="{value}"><input id="{key}-{param}-number" type="number" data-param="{param}" min="{low}" max="{high}" step="{step}" value="{value}"></div></div>'
    options=[('n','Mesh subdivisions',[(1,'1: 8 nodes'),(2,'2: 27 nodes'),(3,'3: 64 nodes'),(4,'4: 125 nodes')],3),('case','Manufactured load case',[('quadratic','Quadratic: refinement test'),('affine','Affine: patch test')],'quadratic'),('comparison','Comparison target',[('implicit','Matched implicit step'),('static','Static analytic reference')],'implicit'),('h','Common implicit h (s)',[(.0005,'0.0005'),(.001,'0.001'),(.002,'0.002')],.0005),('sweeps','Compliant strain sweeps',[(1,'1'),(5,'5'),(20,'20'),(100,'100')],5),('colorBy','Colour diagnostic',[('stress','Element von Mises stress (Pa)'),('error','Nodal displacement error (m)')],'stress'),('magnification','Displacement display magnification',[(1,'1×'),(20,'20×'),(50,'50×'),(100,'100×')],50)] if key=='continuum' else [('mode','Hinge motion mode',[('forward','Force-driven hinge'),('prescribed','Prescribed static hold')],'forward'),('dt','Physics step h (s)',[(.0025,'0.0025'),(.005,'0.005'),(.01,'0.01')],.005),('sweeps','Quasistatic iteration cap',[(80,'80'),(160,'160'),(320,'320'),(640,'640')],160),('boneContact','Sampled bone contact',[('on','On: compliant force'),('off','Off: show penetration')],'on'),('skin','Separate skin membrane / fascia',[('on','On'),('off','Off: ablation')],'on'),('activeShape','Spatial preferred shortening',[('on','On: shared activation'),('off','Off: shape ablation')],'on'),('volumeK','Volume stiffness (Pa)',[(25000,'25,000'),(2500,'2,500')],25000),('tendon','Line-actuator tendon',[('compliant','Compliant'),('rigid','Rigid')],'compliant')]
    for param,label,values,default in options:
        controls+=f'<div class="control"><label for="{key}-{param}">{label}</label><select id="{key}-{param}" data-param="{param}">'+''.join(f'<option value="{v}"'+(' selected' if v==default else '')+f'>{label}</option>' for v,label in values)+'</select></div>'
    notice='Static reference diagram. Step, Play or Pulse starts live 3D; if unavailable, the display is explicitly numerical-only.' if key=='spatial' else 'Static reference diagram. Start interactive 3D to view current results; numerical controls also work without 3D.'
    actions='<button data-action="play">Play</button><button data-action="step">Single step</button><button data-action="pulse">Pulse current state / release</button><button data-action="release">Release excitation</button><button data-action="compression">90° compression fixture</button><button data-action="export">Download trace</button>' if key=='spatial' else ''
    return f'''\n<section class="laboratory advanced-lesson" data-advanced="{key}" id="lab-{key}" aria-labelledby="lab-{key}-heading"><div class="lab-heading"><h3 id="lab-{key}-heading">{lab['title']}</h3><p class="model-label">{lab['model']}</p></div><div class="actions scene-toolbar"><button type="button" data-action="start">Start interactive 3D</button><p class="scene-notice" role="status">{notice}</p></div><figure class="static-figure"><img src="assets/{key}.svg" alt="{e(lab['description'])}"><figcaption>{lab['caption']}</figcaption></figure><p class="scene-legend">{e(lab['description'])}</p><div class="scene-host" hidden></div><div class="controls">{controls}</div><div class="actions">{actions}<button data-action="reset">Reset defaults</button><button data-action="view">Front / oblique view</button><button data-action="summary">Read current results</button><button data-action="copy">Copy state</button></div><dl class="readout" aria-label="Current numerical results"></dl><p class="lab-description">{e(lab['description'])} Static figures, equations and tables below provide the text and print alternatives. Playback advances fixed physics steps; spatial optimization can slow wall-clock playback.</p><p class="announce" role="status" aria-live="polite"></p><textarea class="preset" aria-label="Reproducible state JSON" readonly hidden></textarea><noscript><p>Interactive controls require JavaScript; static illustrations and worked tables remain readable.</p></noscript></section>\n'''

def lab_block(key,web):
    if key in ['spatial','continuum']:return advanced_block(key,web)
    lab=LABS[key];e=html.escape
    if not web:
        return f"\n### {lab['title']}\n\n![{lab['description']}](assets/{key}.svg)\n\n{lab['caption']}\n\n**Model:** {lab['model']}\n\n[Open this laboratory in the web edition](index.html#lab-{key}).\n"
    controls=''
    for keyp,label,low,high,step,value in lab['controls']:
        controls+=f'<div class="control"><label for="{key}-{keyp}-number">{e(label)}</label><div class="input-pair"><input type="range" aria-label="{e(label)} slider" data-param="{keyp}" min="{low}" max="{high}" step="{step}" value="{value}"><input id="{key}-{keyp}-number" type="number" data-param="{keyp}" min="{low}" max="{high}" step="{step}" value="{value}"></div></div>'
    if key=='energy':
        controls+='<div class="control"><label for="energy-method">Integrator</label><select id="energy-method" data-param="method"><option value="explicit">Explicit Euler</option><option value="symplectic" selected>Symplectic Euler</option><option value="verlet">Velocity Verlet</option></select></div>'
        controls+='<div class="control"><label for="energy-dt">Step size h (s)</label><select id="energy-dt" data-param="dt"><option value="0.005">0.005 s</option><option value="0.01">0.01 s</option><option value="0.02" selected>0.02 s</option><option value="0.05">0.05 s</option><option value="0.1">0.10 s</option></select></div>'
    if key in ['elbow','series']:
        controls+=f'<div class="control"><label for="{key}-mode">Motion mode</label><select id="{key}-mode" data-param="mode"><option value="forward">Force-driven hinge</option><option value="prescribed">Prescribed static hold</option></select></div><div class="control"><label for="{key}-dt">Physics step h (s)</label><select id="{key}-dt" data-param="dt"><option value="0.0025">0.0025 s</option><option value="0.005" selected>0.005 s</option><option value="0.01">0.01 s</option></select></div>'
    if key=='series':
        for param,label,options in [('tendon','Tendon assumption',[('compliant','Compliant tensile tendon'),('rigid','Rigid tendon')]),('tendonK','Tendon stiffness (N/m)',[(15000,'15,000'),(30000,'30,000'),(60000,'60,000')]),('contact','Tissue/plate contact',[('on','Enabled; force feeds hinge'),('off','Disabled; show penetration')]),('bulk','Tissue bulk modulus (Pa)',[(50000,'50,000'),(5000,'5,000'),(0,'0; remove volume resistance')])]:
            controls+=f'<div class="control"><label for="series-{param}">{label}</label><select id="series-{param}" data-param="{param}">'+''.join(f'<option value="{value}"'+(' selected' if value in ['compliant',30000,'on',50000] else '')+f'>{text}</option>' for value,text in options)+'</select></div>'
    notice='Static reference diagram. Step, Play or Pulse starts live 3D; if unavailable, the display is explicitly numerical-only.' if key!='torque' else 'Static reference diagram. Start interactive 3D to view current results; numerical controls also work without 3D.'
    temporal='<button data-action="play">Play</button><button data-action="step">Single step</button>' if key!='torque' else ''
    if key=='energy':temporal+='<button data-action="run">Run to 12 s</button><button data-action="export">Download trace</button>'
    if key in ['elbow','series']:temporal+='<button data-action="pulse">Pulse current state / release</button><button data-action="release">Release excitation</button><button data-action="export">Download trace</button>'
    chart=''
    if key=='energy':
        chart='<svg class="energy-chart" viewBox="0 0 580 205" role="img" aria-label="Energy versus simulated time"><title>Energy versus simulated time</title><text class="scale" x="40" y="20" font-size="13">Energy range 0 to 0.96 J</text><path d="M40 30V160H540" fill="none" stroke="#456171"/><line class="reference" x1="40" x2="540" y1="52" y2="52" stroke="#754d1f" stroke-dasharray="5 4"/><polyline class="trace" fill="none" stroke="#087567" stroke-width="2" points="40,52"/><text x="40" y="185" font-size="13">0</text><text x="435" y="185" font-size="13">12 s</text><text x="195" y="201" font-size="12">Solid: numerical energy · Dashed: initial 0.80 J</text></svg>'
    return f'''\n<section class="laboratory" data-demo="{key}" id="lab-{key}" aria-labelledby="lab-{key}-heading">
<div class="lab-heading"><h3 id="lab-{key}-heading">{e(lab['title'])}</h3><p class="model-label">{e(lab['model'])}</p></div>
<div class="actions scene-toolbar"><button type="button" data-action="start">Start interactive 3D</button><p class="scene-notice" role="status">{notice}</p></div><figure class="static-figure"><img src="assets/{key}.svg" alt="{e(lab['description'])}"><figcaption>{e(lab['caption'])}</figcaption></figure>
<p class="scene-legend">{e(lab['description']) if key=='series' else ''}</p><div class="scene-host" hidden></div><div class="controls">{controls}</div>
<div class="actions">{temporal}<button data-action="reset">Reset defaults</button><button data-action="view">Front / oblique view</button><button data-action="summary">Read current results</button><button data-action="copy">Copy state</button></div>
<dl class="readout" aria-label="Current numerical results"></dl>{chart}
<p class="lab-description">{e(lab['description'])} Axes: x right, y up, z out of the plane.</p>
<p class="announce" role="status" aria-live="polite"></p><textarea class="preset" aria-label="Reproducible state JSON" readonly hidden></textarea>
<noscript><p>Interactive controls require JavaScript. The figure, equations, worked examples and experiment table remain available.</p></noscript>
</section>\n'''

def build():
    evidence=check()
    transfer=check_transfer()
    coupled=check_coupled()
    arm=check_arm()
    properties=check_properties()
    material=check_material()
    real_lessons=check_real_lessons(properties)
    from check_mixed_volume_proofs import check as check_mixed
    check_mixed(OUT/'mixed-volume-kernel', False)
    prepare_connected(OUT)
    data=ROOT/'data/elbow-v1'
    subprocess.run(['python3',str(data/'scripts/validate_package.py')],check=True)
    continuum=ROOT/'contributions/continuum_reference'
    for relative,item in json.loads((continuum/'data/provenance.json').read_text())['files'].items():
        payload=(continuum/relative).read_bytes()
        if len(payload)!=item['bytes'] or hashlib.sha256(payload).hexdigest()!=item['sha256']:raise RuntimeError('Continuum provenance changed: '+relative)
    manifest=json.loads((ROOT/'book/book.json').read_text())
    claims={c['id']:c for c in evidence['claims']}
    source=(ROOT/'proofs/Mechanics.lean').read_text()
    bundles=[(evidence,source,'proof-status.json','lean-check.txt','checked-source-appendix','proof-check-receipt','kernel-dependency-report'),
      (transfer,(ROOT/'proofs/AnatomicalTransfer.lean').read_text(),'transfer-proof-status.json','transfer-lean-check.txt','transfer-source-appendix','transfer-proof-receipt','transfer-kernel-report'),
      (coupled,(ROOT/'proofs/CoupledMechanics.lean').read_text(),'coupled-proof-status.json','coupled-lean-check.txt','coupled-source-appendix','coupled-proof-receipt','coupled-kernel-report'),
      (arm,(ROOT/'proofs/AnatomicalArm.lean').read_text(),'arm-proof-status.json','arm-lean-check.txt','arm-source-appendix','arm-proof-receipt','arm-kernel-report'),
      (properties,(ROOT/'proofs/ContinuumProperties.lean').read_text(),'property-proof-status.json','property-lean-check.txt','property-source-appendix','property-proof-receipt','property-kernel-report'),
      (material,(ROOT/'proofs/MaterialResponse.lean').read_text(),'material-proof-status.json','material-lean-check.txt','material-source-appendix','material-proof-receipt','material-kernel-report')]
    for receipt,(source_name,_,prefix,_) in zip(real_lessons,REAL_FAMILIES):
        bundles.append((receipt,(ROOT/'proofs'/source_name).read_text(),prefix+'-proof-status.json',prefix+'-lean-check.txt',prefix+'-source-appendix',prefix+'-proof-receipt',prefix+'-kernel-report'))
    claim_bundles={c['id']:b for b in bundles for c in b[0]['claims']}
    for receipt,checked_source,receipt_path,transcript_path,*_ in bundles[1:]:
        (OUT/receipt_path).write_text(json.dumps(receipt,indent=2)+'\n')
        if receipt is properties or receipt is material or any(receipt is r for r in real_lessons):continue  # Fresh checkers already wrote their transcripts here.
        original={id(transfer):'lean-check.txt',id(coupled):'coupled-lean-check.txt',id(arm):'arm-lean-check.txt'}[id(receipt)]
        shutil.copy(ROOT/'data/anatomical-arm-v1/audit'/original,OUT/transcript_path)
    def dependency_description(receipt):
        dependency=receipt.get('mathlib')
        if isinstance(dependency,dict):return 'pinned mathlib '+dependency['tag']+'; commit '+dependency['commit']+'; locked transitive dependencies'
        return 'mathlib not used; bundled Std only'
    def proof_block(id,web):
        receipt,checked_source,receipt_path,transcript_path,*_=claim_bundles[id]
        c=next(c for c in receipt['claims'] if c['id']==id);name=c['theorem'].split('.')[-1]
        stmt=theorem_statement(checked_source,name)
        meta=f"Lean 4.19.0; {dependency_description(receipt)}; transitive axioms: {', '.join(c['axioms']) or 'none'}; source SHA-256: {receipt['source_sha256']}"
        if not web:
            claim_text=c['claim'].replace('*',r'\*').replace('^',r'\^');assumptions=c['assumptions'].replace('*',r'\*').replace('^',r'\^');limits=c['limitations'].replace('*',r'\*').replace('^',r'\^')
            return f"\n**Checked claim {id}:** {claim_text}\n\n**Assumptions:** {assumptions}\n\n```lean\n{stmt}\n```\n\n**Limits:** {limits}\n\nDeclaration: `{c['theorem']}`. {meta}. [Full checked source]({receipt['source']}); [receipt]({receipt_path}).\n"
        e=html.escape
        # Pandoc parses prose inside aside elements as Markdown. Claim-map
        # multiplication signs are literal text, not emphasis delimiters.
        def prose(value):return e(value).replace('*','&#42;').replace('^','&#94;')
        implementation=c.get('implementation','See the adjacent derivation and original mechanics claim map.')
        match=re.match(r'(web/[^: ]+)',implementation)
        implementation_html=(f'<a href="{e(match[1])}">{prose(implementation)}</a>' if match else prose(implementation))
        return f'''\n<aside class="proof-card" id="proof-{id}" aria-label="Checked mathematical claim">
<h3>Checked claim · {e(id)}</h3><p>{prose(c['claim'])}</p><p><strong>Assumptions:</strong> {prose(c['assumptions'])}</p>
<pre><code>{e(stmt)}</code></pre><p><strong>Limits:</strong> {prose(c['limitations'])}</p>
<p class="proof-meta">Declaration {e(c['theorem'])}. {e(meta)}.</p>
<p><strong>Implementation link:</strong> {implementation_html}</p>
<p><a href="{receipt['source']}">Full source</a> · <a href="{receipt_path}">Build receipt</a> · <a href="{transcript_path}">Kernel dependency report</a></p>
<details><summary>Read complete checked definitions and proof source</summary><pre><code>{e(checked_source)}</code></pre></details></aside>\n'''
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
    series_text=subprocess.check_output(['node',str(ROOT/'tools/series-experiment.mjs')],text=True)
    (OUT/'series-experiment.json').write_text(series_text);series=json.loads(series_text)
    holds='| Tendon | a | Fiber length (m) | Tendon length (m) | Tendon energy (J) | Active work (J) |\n|:--|--:|--:|--:|--:|--:|\n'
    for r in series['holds']:holds+=f"| {r['tendon']} | {r['activation']:.6f} | {r['fiber']:.6f} | {r['tendonLength']:.6f} | {r['tendonEnergy']:.6f} | {r['work']:.6f} |\n"
    compression='| q (°) | Tissue J | LBS J | Normal force (N) | Model pressure (Pa) | Tissue moment (N m) |\n|--:|--:|--:|--:|--:|--:|\n'
    for r in series['compression']:compression+=f"| {r['degrees']} | {r['volumeRatio']:.6f} | {r['skinVolumeRatio']:.6f} | {r['normal']:.4f} | {r['pressure']:.2f} | {r['torque']:.5f} |\n"
    trajectories='| h (s) | Final q (°) | Active work (J) | Max energy residual (J) | Event splits | Accepted substeps |\n|--:|--:|--:|--:|--:|--:|\n'
    for r in series['trajectories']:trajectories+=f"| {r['dt']:.4f} | {r['angleDegrees']:.6f} | {r['work']:.6f} | {r['maxEnergyResidual']:.3g} | {r['eventSplits']} | {r['substeps']} |\n"
    spatial_text=subprocess.check_output(['node',str(ROOT/'tools/spatial-experiment.mjs')],text=True)
    (OUT/'spatial-experiment.json').write_text(spatial_text);spatial=json.loads(spatial_text)
    r=spatial['reference']
    LABS['spatial']['caption']=f"Generated compression fixture: q = 90°, activation 0.6, 640-iteration cap. Mechanical minimum volume ratio {r['minJ']:.3f}; same-pose LBS minimum {r['baselineMinJ']:.3f}. Sampled penetration {r['penetrationM']*1000:.4f} mm versus {r['baselinePenetrationM']*1000:.4f} mm. Original schematic, not registered to the real atlas."
    spatial_summary=f"At 640 iterations, minimum J is {r['minJ']:.6f} and total mean J is {r['meanJ']:.6f}. Tissue flattens and moves laterally while total volume changes by {100*(1-r['meanJ']):.3f}%. Maximum sampled penetration is {r['penetrationM']*1000:.6f} mm, versus {r['baselinePenetrationM']*1000:.6f} mm for skinning. Maximum free-force defect is {r['maxFreeForceN']:.6f} N. These values are generated in {spatial['runtime']['node']}; they are not cross-runtime bit-identity claims. A small sampled gap does not prove the material law correct, and a residual alone does not establish a contact-free surface."
    spatial_table='| Iteration cap | Min J | Mean J | Sampled penetration (mm) | Max free force (N) | Normal-force sum (N) | Elastic/contact energy (J) |\n|--:|--:|--:|--:|--:|--:|--:|\n'
    for r in spatial['rows']:spatial_table+=f"| {r['maxIterations']} | {r['minJ']:.6f} | {r['meanJ']:.6f} | {r['penetrationM']*1000:.6f} | {r['maxFreeForceN']:.6f} | {r['contactNormalSumN']:.6f} | {r['totalEnergyJ']:.6f} |\n"
    subprocess.run(['node',str(ROOT/'tools/dissipative-experiment.mjs'),str(OUT/'assets')],check=True)
    shutil.copy(OUT/'assets/dissipative-experiment.json',OUT/'dissipative-experiment.json')
    dissipative=json.loads((OUT/'dissipative-experiment.json').read_text())
    dissipative_table='| Hold | Time (s) | Force (N) | Extension (mm) | Stored U (mJ) | Signed W (mJ) | Loss D (mJ) |\n|:--|--:|--:|--:|--:|--:|--:|\n'
    for name in ['creep','relaxation']:
        for row in dissipative['cases'][name]['frames']:
            dissipative_table+=f"| {name} | {row['time']:.1f} | {row['force']:.6f} | {1000*row['extensionM']:.6f} | {1000*row['storageJ']:.6f} | {1000*row['workJ']:.6f} | {1000*row['dissipationJ']:.6f} |\n"
    subprocess.run(['node',str(ROOT/'tools/serial-experiment.mjs'),str(OUT/'assets')],check=True)
    shutil.copy(OUT/'assets/serial-experiment.json',OUT/'serial-experiment.json')
    serial=json.loads((OUT/'serial-experiment.json').read_text())
    serial_table='| Load (N) | Block | Stretch λ | Axial strain | Area (mm²) | Volume (mm³) | Force residual (N) |\n|--:|--:|--:|--:|--:|--:|--:|\n'
    for name in ['tension','rest','compression']:
        state=serial['cases'][name]
        for i,c in enumerate(state['cells']):
            serial_table+=f"| {state['parameters']['force']:.3f} | {i+1} | {c['stretch']:.6f} | {c['engineeringStrain']:.6f} | {1e6*c['currentAreaM2']:.3f} | {1e9*c['currentBoundaryVolumeM3']:.3f} | {c['forceResidualN']:.3g} |\n"
    chapters='\n\n'.join(((ROOT/'book'/p).read_text()+'\n\n{{demo:continuum}}\n\n{{proof:compliance-denominator}}\n') if p.startswith('../contributions/') else (ROOT/'book/chapters'/p).read_text() for p in manifest['chapters'])
    coupling_receipt=json.loads((ROOT/'data/anatomical-arm-v1/audit/coupling-results.json').read_text())
    profile_table='| Mesh | Solver | Objective calls | HVP calls | Time (s) | Loaded length (mm) | Max nodal force (N) |\n|:--|:--|--:|--:|--:|--:|--:|\n'
    for r in coupling_receipt['profiles']:
        profile_table+=f"| {r['elements']} P2 tets / {r['nodes']} nodes | {r['method']} | {r['objectiveEvaluations']} | {r['hessianProducts']} | {r['elapsedMS']/1000:.3f} | {r['meanEndLengthM']*1000:.6f} | {r['maximumNodalForceN']:.3g} |\n"
    step_table='| h (s) | Peak q (°) | Final q (°) | Sum nonlinear work defect (J) | Max momentum residual (N m) |\n|--:|--:|--:|--:|--:|\n'
    import math
    for r in coupling_receipt['runs']:
        step_table+=f"| {r['hS']:.2f} | {r['peakQ']*180/math.pi:.4f} | {r['finalQ']*180/math.pi:.4f} | {r['sumEndpointWorkDefectJ']:.6f} | {r['maxTorqueBalanceNm']:.3g} |\n"
    def expand(web):
        text=re.sub(r'\{\{demo:(\w+)\}\}',lambda m:lab_block(m[1],web),chapters)
        text=re.sub(r'\{\{property:(\w+)\}\}',lambda m:property_block(m[1],web),text)
        text=re.sub(r'\{\{dissipative:(\w+)\}\}',lambda m:dissipative_block(m[1],web),text)
        text=text.replace('{{dissipative-table}}',dissipative_table)
        text=re.sub(r'\{\{serial:(\w+)\}\}',lambda m:serial_block(m[1],web),text)
        text=text.replace('{{serial-table}}',serial_table)
        text=text.replace('{{connected-specimen}}',connected_block(web))
        text=re.sub(r'\{\{proof:([\w-]+)\}\}',lambda m:proof_block(m[1],web),text)
        text=text.replace('{{evidence}}',(ROOT/'web/evidence.html').read_text() if web else 'The web edition provides a resettable static atlas viewer and a recorded-bin slider. The figures, source tables and downloads above and below provide the reading alternative.')
        text=text.replace('{{experiment}}',table).replace('{{spatial-experiment}}',spatial_table).replace('{{spatial-summary}}',spatial_summary)
        text=text.replace('{{elbow-experiment}}',elbow_table)
        text=text.replace('{{series-holds}}',holds).replace('{{series-compression}}',compression).replace('{{series-trajectories}}',trajectories)
        text=text.replace('{{coupled-profile}}',profile_table).replace('{{coupled-steps}}',step_table)
        if re.search(r'\{\{[A-Za-z]',text): raise ValueError('Unexpanded build directive')
        for receipt,checked_source,receipt_path,transcript_path,source_id,receipt_id,kernel_id in bundles:
            text+='\n\n# Checked source appendix: '+Path(receipt['source']).stem+' {#'+source_id+'}\n\nCompilation establishes only the stated exact domain.\n\n```lean\n'+checked_source+'```\n\n## Proof check receipt {#'+receipt_id+'}\n\nFresh successful invocation: `'+receipt['command']+'`. Toolchain: '+receipt['lean_version']+'. Checked declarations: '+str(len(receipt['claims']))+'. Source SHA-256: `'+receipt['source_sha256']+'`. Claim-map SHA-256: `'+receipt['claims_sha256']+'`. Dependencies: '+dependency_description(receipt)+'. This receipt does not validate floating-point implementation, biological parameters or anatomy.\n\n## Kernel dependency report {#'+kernel_id+'}\n\n```text\n'+(OUT/transcript_path).read_text()+'```\n'
        return text
    front=f"---\ntitle: {manifest['title']}\nsubtitle: {manifest['subtitle']}\nlang: en\n---\n\n"
    (OUT/'kenoma-mechanics.md').write_text(front+expand(False))
    staging=OUT/'web-staging.md';staging.write_text(front+expand(True))
    pandoc_result=subprocess.run(['pandoc',str(staging),'--standalone','--mathml','--toc','--toc-depth=2',
      '--template',str(ROOT/'web/template.html'),'-o',str(OUT/'index.html')],check=True,capture_output=True,text=True)
    if 'Could not convert TeX math' in pandoc_result.stderr:raise RuntimeError(pandoc_result.stderr)
    html_path=OUT/"index.html"
    rendered=html_path.read_text().replace('</head>','<link rel="stylesheet" href="assets/dissipative-lab.css">\n<link rel="stylesheet" href="assets/serial-lab.css">\n</head>')
    # MathML matrix fences can fail to stretch in Chromium's PDF font fallback.
    # Preserve the semantic operators; draw full-height fences around the table.
    rendered=re.sub(r'<mrow>(<mo[^>]*>\[</mo>)(<mtable>.*?</mtable>)(<mo[^>]*>\]</mo>)</mrow>',
      r'<mrow class="matrix-fenced">\1\2\3</mrow>',rendered,flags=re.S)
    # Chromium 154 can paint a moved MathML superscript on the preceding page.
    # Give this short formula an atomic HTML print rendering; keep its MathML.
    def inline_math(match):
        formula=match[0]
        if '<annotation encoding="application/x-tex">M(u-y)=G^T\\ell</annotation>' not in formula:return formula
        return '<span class="print-safe-inline">'+formula+'<span class="print-inline-equation" role="math" aria-label="M times u minus y equals G transpose times ell"><i>M</i>(<i>u</i>−<i>y</i>) = <i>G</i><sup><i>T</i></sup>ℓ</span></span>'
    rendered=re.sub(r'<math display="inline".*?</math>',inline_math,rendered,flags=re.S)
    rendered=re.sub(r'<math display="block".*?</math>', lambda m: '<div class="equation" tabindex="0" aria-label="Scrollable displayed equation">'+m[0]+'</div>', rendered, flags=re.S)
    html_path.write_text(rendered)
    staging.unlink()
    assets=OUT/'assets';generate(assets)
    from projection_figure import generate as projection_figure
    projection_figure(assets)
    standalone=OUT/'standalone';standalone.mkdir(exist_ok=True)
    for name in ['pressure-projection-lab.html','pressure-projection-proof-guide.md','pressure-projection-lab-check.py']:
        shutil.copy(ROOT/'standalone'/name,standalone/name)
    subprocess.run(['node',str(ROOT/'tools/property-experiment.mjs'),str(assets),str(OUT/'property-experiment.json')],cwd=ROOT,check=True)
    subprocess.run(['node',str(ROOT/'tools/material-experiment.mjs'),str(assets),str(OUT/'material-experiment.json')],cwd=ROOT,check=True)
    evidence_figures(assets)
    advanced_figures(assets,spatial)
    from coupled_figures import generate as coupled_figures
    coupled_figures(assets)
    subprocess.run(['python3',str(ROOT/'tools/contact_trajectory_figure.py')],check=True)
    review=ROOT/'data/anatomical-arm-v1/review/coupling-candidate'
    for name in ['atlas-assembly-bind','fixture-loaded','fixture-released']:
        shutil.copy(review/(name+'.png'),assets/(name+'.png'))
    shutil.copy(ROOT/'data/anatomical-arm-v1/review/apparatus-candidate/desktop-rest.png',assets/'anatomical-arm-rest.png')
    shutil.rmtree(OUT/'data/elbow-v1',ignore_errors=True)
    shutil.copytree(data,OUT/'data/elbow-v1',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copytree(ROOT/'data/anatomical-arm-v1',OUT/'data/anatomical-arm-v1',dirs_exist_ok=True)
    shutil.copytree(ROOT/'data/property-labs-v1',OUT/'data/property-labs-v1',dirs_exist_ok=True)
    shutil.copy(ROOT/'web/style.css',assets/'style.css')
    shutil.copy(ROOT/'web/dissipative-lab.css',assets/'dissipative-lab.css')
    shutil.copy(ROOT/'web/serial-lab.css',assets/'serial-lab.css')
    shutil.copytree(ROOT/'web',OUT/'web',dirs_exist_ok=True)
    subprocess.run([str(ROOT/'node_modules/.bin/esbuild'),str(ROOT/'web/app.mjs'),'--bundle','--minify','--format=esm','--target=es2022',f'--outfile={assets/"app.js"}','--legal-comments=external'],check=True)
    proofs=OUT/'proofs';proofs.mkdir(exist_ok=True)
    for file in ['Mechanics.lean','AnatomicalTransfer.lean','CoupledMechanics.lean','AnatomicalArm.lean','anatomical-claims.json','coupled-claims.json','arm-claims.json','ContinuumProperties.lean','property-claims.json','MaterialResponse.lean','material-claims.json','mathlib-lock.json','lean-toolchain','claims.json']:shutil.copy(ROOT/'proofs'/file,proofs/file)
    for source_name,map_name,_,_ in REAL_FAMILIES:
        for file in [source_name,map_name]:shutil.copy(ROOT/'proofs'/file,proofs/file)
    subprocess.run(['node',str(ROOT/'tools/build-anatomy-inspector.mjs')],check=True)
    subprocess.run(['node',str(ROOT/'tools/build-coupled-inspector.mjs')],check=True)
    subprocess.run(['node',str(ROOT/'tools/build-anatomical-arm-inspector.mjs')],check=True)
    shutil.copy(ROOT/'.tools/mathlib4/LICENSE',proofs/'mathlib-LICENSE')
    shutil.copy(ROOT/'.tools/mathlib4/lake-manifest.json',proofs/'mathlib-lake-manifest.json')
    notices=OUT/'THIRD_PARTY_NOTICES.txt'
    notices.write_text('Kenoma original book and simulator content: Apache-2.0. Third-party data retains its component licenses below.\n\n'+(data/'LICENSES_AND_ATTRIBUTION.txt').read_text()+'\n\nThree.js 0.180.0 (MIT)\n'+(ROOT/'node_modules/three/LICENSE').read_text()+'\n\nBuild tool esbuild 0.25.10 (MIT)\n'+(ROOT/'node_modules/esbuild/LICENSE.md').read_text()+'\n\nmathlib4 v4.19.0, commit '+properties['mathlib']['commit']+' (Apache-2.0); used for kernel-checked real declarations. Locked transitive dependency metadata: proofs/mathlib-lock.json and upstream lake-manifest.json SHA-256 '+properties['mathlib']['manifest_sha256']+'\n'+(ROOT/'.tools/mathlib4/LICENSE').read_text())
    shutil.copytree(ROOT/'contributions/continuum_reference',OUT/'contributions/continuum_reference',dirs_exist_ok=True)
    shutil.copy(ROOT.parent/'LICENSE',OUT/'LICENSE')
    (OUT/'.nojekyll').touch()
    inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['book','web','proofs','tools','data','contributions'] for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
    for name in ['pressure-projection-lab.html','pressure-projection-proof-guide.md','pressure-projection-lab-check.py']:
        relative='standalone/'+name;inputs[relative]=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
    for relative in ['package.json','package-lock.json','requirements.txt']:
        inputs[relative]=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
    manifest_out={'schema':1,'milestone':'full-spatial-book','input_sha256':inputs,'lean':evidence['lean_version'],
      'pandoc':subprocess.check_output(['pandoc','--version'],text=True).splitlines()[0],
      'node':subprocess.check_output(['node','--version'],text=True).strip(),
      'numerical_experiment':'experiment.json','proof_evidence':'proof-status.json',
      'executable_outputs':executable_outputs(OUT),
      'proof_families':[b[2] for b in bundles],'property_mathlib':properties['mathlib'],
      'property_experiment':'property-experiment.json',
      'material_experiment':'material-experiment.json',
      'dissipative_outputs':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['assets/property-dissipative.svg','dissipative-experiment.json']},
      'connected_outputs':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['assets/connected-specimen.svg','connected-figure.json','connected-experiment.json','connected-material-oracle.json','connected-numerical-qualification.json','connected-end-face-experiment.json','connected-end-face-qualification.json','connected-passive/axisymmetric-preview-manifest.json']},
      'serial_outputs':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['assets/property-serial.svg','serial-experiment.json']},
      'git_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'original_plans_base':'9b0c67fd25e1b645833a68bb9b1c2aba1404bbce',
      'determinism':'State progression repeatable in the pinned implementation; cross-browser transcendental bit identity and PDF byte identity not asserted.'}
    (OUT/'build-manifest.json').write_text(json.dumps(manifest_out,indent=2)+'\n')
    print('Built single-source Markdown and portable HTML in education/dist')
if __name__=='__main__':build()

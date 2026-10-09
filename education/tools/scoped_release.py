"""Source-only registered claim cards and explicit editorial corrections.

This module performs no compilation, dependency installation or simulation.
"""
from pathlib import Path
import hashlib, html, json, re

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
BASE = '6a72e01b66e4d5724c8d6c74f98cf38a90b21e31'
TREE = '24c45eb71a391ce516d666378a5a46b2c969ddbe'
FAMILIES = [
 ('Mechanics.lean','claims.json','Std'),('AnatomicalTransfer.lean','anatomical-claims.json','Std'),
 ('CoupledMechanics.lean','coupled-claims.json','Std'),('AnatomicalArm.lean','arm-claims.json','Std'),
 ('ContinuumProperties.lean','property-claims.json','Real'),('MaterialResponse.lean','material-claims.json','Std'),
 ('MaterialResponseReal.lean','material-real-claims.json','Real'),('MechanicsReal.lean','mechanics-real-claims.json','Real'),
 ('ActuatorConstitutiveReal.lean','actuator-real-claims.json','Real'),('DissipativeBarReal.lean','dissipative-real-claims.json','Real'),
 ('SerialSpecimenReal.lean','serial-specimen-real-claims.json','Real'),('MixedLogVolume.lean','mixed-volume-claims.json','Real'),
 ('NonuniformIsochoric.lean','nonuniform-real-claims.json','Real'),('ArchitectureForce.lean','architecture-force-real-claims.json','Real')]
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def inventory():
 claims={};families=[]
 for source,mapname,domain in FAMILIES:
  cs=json.loads((ROOT/'proofs'/mapname).read_text())
  if len({c['id'] for c in cs})!=len(cs):raise ValueError('Duplicate proof IDs')
  for c in cs:
   if c['id'] in claims:raise ValueError('Duplicate registry proof ID')
   claims[c['id']]={**c,'source':'proofs/'+source,'claims_source':'proofs/'+mapname,'domain_family':domain,
                     'source_sha256':digest(ROOT/'proofs'/source),'claims_sha256':digest(ROOT/'proofs'/mapname),
                     'candidate_compilation':'UNRUN','verified_receipt_imported':False,'axiom_report':'UNAVAILABLE'}
  families.append({'source':'proofs/'+source,'claim_map':'proofs/'+mapname,'domain':domain,'declarations':len(cs),'candidate_compilation':'UNRUN'})
 if len(claims)!=115:raise ValueError('Unexpected baseline registry')
 return claims,families

def statement(source,name):
 match=re.search(r'^theorem '+re.escape(name.split('.')[-1])+r'\b(?:(?!^\s*(?:theorem|def|lemma)\b).)*?\s:=',source,re.S|re.M)
 if not match:raise ValueError('Missing registered theorem: '+name)
 return match.group().rsplit(':=',1)[0].rstrip()

def proof_block(c,web):
 stmt=statement((ROOT/c['source']).read_text(),c['theorem'])
 claim=c.get('claim',c.get('statement'));limits=c.get('limitations',c.get('not_proved'))
 status='Registered source only. Compilation and transitive axiom report are unrun in this candidate; no checked receipt is attached.'
 link=f"[{c['theorem']}]({c['source']})"
 if not web:return f"\n**Registered claim {c['id']} ({c['domain_family']}):** {claim}\n\n**Status:** {status}\n\n**Assumptions:** {c['assumptions']}\n\n```lean\n{stmt}\n```\n\n**Limits:** {limits}\n\n{link}. Source SHA-256: `{c['source_sha256']}`.\n"
 e=lambda s:html.escape(str(s)).replace('*','&#42;').replace('^','&#94;')
 return f'\n<aside class="proof-card" id="proof-{c["id"]}" aria-label="Registered mathematical source, compilation unrun"><h3>Registered claim · {e(c["id"])}</h3><p>{e(claim)}</p><p><strong>Status:</strong> {status}</p><p><strong>Assumptions:</strong> {e(c["assumptions"])}</p><pre><code>{e(stmt)}</code></pre><p><strong>Limits:</strong> {e(limits)}</p><p>Domain family: {e(c["domain_family"])}. Source SHA-256: {c["source_sha256"]}.</p><p><a href="{c["source"]}">{e(c["theorem"])}</a> · <a href="{c["claims_source"]}">Exact claim map</a></p></aside>\n'

# Narrow, reviewable wording corrections. Exact markers fail if baseline prose changes.
EDITS={
 '03-energy.md':[(r'\*\*Try:\*\* reset with explicit Euler and h = 0.05 s\..*?so that rescaling cannot disguise instability\.', '**Try:** reset, select explicit Euler and h = 0.05 s. The complete 12 s trace is recomputed immediately. Select Verlet at the same h and compare the energy trace with the dashed 0.80 J reference. Then choose h = 0.01 s and compare again. The plotted vertical range adapts to the computed energy; read its numeric maximum so that rescaling cannot disguise instability.'),(r'The methods are implemented separately from rendering\..*?Reset reproduces the same sequence for a given method and step size\.', 'This scoped numerical laboratory recomputes the complete 12-second trajectory whenever method or step size changes. It retains every physics sample, reports maximum relative energy error over the whole run, and draws the numerical energy against the initial-energy reference. Show current state JSON reports parameters and summary measurements. Reset restores symplectic Euler at h = 0.02 s. The diagram and table remain readable without JavaScript.')],
 '01-force.md':[(r'\*\*Try:\*\* keep force at 4 N, reset, and increase mass from 2 to 4 kg\. At the same simulated time the position is half as large\.', '**Try:** reset, set time to 1 s with mass 2 kg and force 4 N, then increase mass to 4 kg without changing time. Position changes from 1 m to 0.5 m.')],
 '05-sources.md':[(r'The original 25 declarations import.*?in the generated build evidence\.', 'The fixed registry contains 30 Std and 85 Real declarations. The Real sources use [official mathlib v4.19.0](https://github.com/leanprover-community/mathlib4/tree/c44e0c8ee63ca166450922a373c7409c5d26b00b), whose exact commit and transitive dependency manifest remain pinned in `proofs/mathlib-lock.json`. This scoped candidate bundles registered sources and maps. No compiler receipt or transitive-axiom report is attached; separate proof-task results must be verified against these bytes before any card is presented as checked.'),(r'https://github.com/opensim-org/opensim-models/blob/master/Models/Arm26/arm26.osim', 'https://github.com/opensim-org/opensim-models/blob/84b487c4e3245359a64381e01f01b9cf4772d457/Models/Arm26/arm26.osim')],
 '06-tissue-graphics.md':[(r'Laboratory 4 moves.*?working examples from anatomical prediction\.', 'The full baseline contains a rigid schematic hinge, an affine-block proxy and separate spatial comparisons. Those motion laboratories are outside this scoped edition. Here the prescribed-geometry, homogeneous-confinement and serial-block lessons distinguish their working mechanisms from anatomical prediction. A decorative ellipsoid cannot measure tissue compression; material deformation, interfaces and contact require explicit forces and boundary conditions.'),(r'Laboratory 4 supplies.*?synchronized baseline and measured defects\.', 'The omitted baseline motion laboratories illustrate this comparison in their own declared scope. Their trajectory and contact qualification are not claimed for this scoped edition.')],
 '09-continuum-medical.md':[(r'\[Laboratory 5\]\(#tendon-tissue-coupling\)', '[the confinement lesson](#compression-bulk-shear-confinement)')],
 '02-torque.md':[(r'The slider prescribes its angle;', 'The angle control prescribes its angle;'),(r'before moving the slider\.', 'before changing the angle control.'),(r'the corresponding identity is checked separately:', 'the corresponding registered source identity is shown below; candidate compilation remains unrun:')],
 '09a-properties.md':[(r'\[Laboratory 5\]\(#tendon-tissue-coupling\)', '[the confinement lesson](#compression-bulk-shear-confinement)'),(r'The freshly checked real-number proof bundle establishes.*?against pinned mathlib\.', 'The registered real-number source bundle states edge translation invariance, determinant composition, the actual diagonal determinant and the positive square-root isochoric construction. Compilation against the pinned mathlib remains unrun in this candidate.')],
 '09b-material-response.md':[(r'Real properties: checked algebra', 'Real properties: registered algebra'),(r'Five real-domain algebra claims below are compiled against the pinned mathlib dependencies before this book is built\.', 'Five real-domain algebra claims below are registered against pinned mathlib; this scoped assembly does not compile them.'),(r'The five declarations below are freshly compiled with pinned Lean 4.19.0 and bundled Std\.', 'The five declarations below target pinned Lean 4.19.0 and bundled Std. The separate proof task reports Std success, but its source-bound receipts have not been imported; this candidate labels these cards source-only.')],
 '04-muscle-physiology.md':[(r'Laboratories 4–5 implement.*?architecture omissions\.', 'The full baseline contains simplified line, series and spatial teaching implementations with their own limitations. Their motion controls are outside this scoped edition. They do not supply a physiological force–velocity law, measured fibre architecture or anatomical calibration.')],
 '08-actual-data.md':[(r'The browser viewer centers.*?calculations\.', 'The retained atlas is static evidence. This scoped edition provides its original geometry downloads and print diagrams; it does not expose a new interactive anatomical viewer. Polygon reduction and edge diagnostics do not establish a mesh suitable for medical contact calculations.'),(r'Its 992 checks pass again in this repository:', 'Its historical package validation reports 992 checks; this candidate reruns that data-only validator separately. The package checks cover:')]
}

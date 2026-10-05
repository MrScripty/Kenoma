"""Check generated receipts, complete content, links, and PDF glyph/bounds sanity."""
from pathlib import Path
import hashlib,json,re
from urllib.parse import urlparse
import fitz
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'dist'
proof=json.loads((out/'proof-status.json').read_text())
assert proof['source_sha256']==hashlib.sha256((ROOT/'proofs/Mechanics.lean').read_bytes()).hexdigest()
assert proof['claims_sha256']==hashlib.sha256((ROOT/'proofs/claims.json').read_bytes()).hexdigest()
assert len(proof['claims'])==12 and all(c['status']=='checked' for c in proof['claims'])
assert all(set(c['axioms'])<={'propext','Quot.sound','Classical.choice'} for c in proof['claims'])
families=[(proof,'checked-source-appendix','proof-check-receipt','kernel-dependency-report')]
for receipt_name,source_name,claims_name,prefix,count in [('transfer-proof-status.json','AnatomicalTransfer.lean','anatomical-claims.json','transfer',2),('coupled-proof-status.json','CoupledMechanics.lean','coupled-claims.json','coupled',7),('arm-proof-status.json','AnatomicalArm.lean','arm-claims.json','arm',4)]:
 receipt=json.loads((out/receipt_name).read_text())
 assert receipt['source_sha256']==hashlib.sha256((ROOT/'proofs'/source_name).read_bytes()).hexdigest()
 assert receipt['claims_sha256']==hashlib.sha256((ROOT/'proofs'/claims_name).read_bytes()).hexdigest()
 assert len(receipt['claims'])==count and all(c['status']=='checked' for c in receipt['claims'])
 assert all(set(c['axioms'])<={'propext','Quot.sound','Classical.choice'} for c in receipt['claims'])
 families.append((receipt,prefix+'-source-appendix',prefix+'-proof-receipt',prefix+'-kernel-report'))
total_claims=sum(len(r['claims']) for r,*_ in families)
audit='data/anatomical-arm-v1/audit/'
for stem,status,steps in [('contact-lift-release','PASS',15),('contact-fine-release','PASS_ACCEPTED_PREFIX',22)]:
 receipt=json.loads((out/audit/(stem+'-recheck.json')).read_text())
 execution=out/audit/(stem+'-results.json')
 assert receipt['result']==status and receipt['verifiedSteps']==steps
 assert receipt['executionReceiptSHA256']==hashlib.sha256(execution.read_bytes()).hexdigest()
 verifier='tools/verify-anatomical-contact-trajectory.mjs' if stem=='contact-lift-release' else 'tools/verify-anatomical-release-prefix.mjs'
 assert receipt['verifierSHA256']==hashlib.sha256((ROOT/verifier).read_bytes()).hexdigest()
 for relative,digest in receipt['executionSourceHashes'].items():
  assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Trajectory source changed: '+relative
 assert all(r['transverseCrossingPairs']==0 and r['tendonViolations']==0 and r['residualN']<=1e-4 for r in receipt['rows'])
 assert json.loads(execution.read_text())['completedAllSteps']==(stem=='contact-lift-release')
compression=json.loads((out/audit/'anatomical-compression-sensitivity.json').read_text())
assert compression['result']=='COMPLETED_FROZEN_POSE_DIAGNOSTIC'
assert compression['unchangedStationarityToleranceN']==1e-4
assert len(compression['states'])==16 and len(compression['selectedResults'])==5
assert compression['executionReceiptSHA256']==hashlib.sha256((out/audit/'contact-lift-release-results.json').read_bytes()).hexdigest()
assert compression['acceptedReplaySHA256']==hashlib.sha256((out/audit/'contact-lift-release-recheck.json').read_bytes()).hexdigest()
for relative,digest in compression['sourceHashes'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Compression diagnostic source changed: '+relative
dense=json.loads((out/audit/'anatomical-dense-step-recheck.json').read_text())
dense_execution=json.loads((out/audit/'anatomical-dense-step.json').read_text())
assert dense['result']=='PASS_ACCEPTED_COMPARISON'
assert dense['unchangedStationarityToleranceN']==1e-4
assert dense['residualN']<=1e-4 and dense['independentResidualN']<=1e-4
assert dense['surfaceAudit']['transverseCrossingPairs']==0 and dense['routingAudit']['accepted']
assert all(v==0 for v in dense['sampledPenetrationsM'].values())
assert dense['executionReceiptSHA256']==hashlib.sha256((out/audit/'anatomical-dense-step.json').read_bytes()).hexdigest()
assert dense['verifierSHA256']==hashlib.sha256((ROOT/'tools/verify-anatomical-dense-step.mjs').read_bytes()).hexdigest()
assert dense_execution['accepted'] and dense_execution['pointsPerElement']==256
for relative,digest in dense_execution['sourceHashes'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Dense comparison source changed: '+relative
text=(out/'kenoma-mechanics.md').read_text();assert not re.search(r'\{\{[A-Za-z]',text)
for id in ['force-pair','torque-linearity','torque-origin','central-pair','kinetic-sign','torque-example']:
 assert f'Checked claim {id}:' in text
browser=json.loads((out/'browser-check.json').read_text());assert browser['status']=='passed'
assert browser['proof_cards']==total_claims
assert browser['html_sha256']==hashlib.sha256((out/'index.html').read_bytes()).hexdigest()
assert browser['app_sha256']==hashlib.sha256((out/'assets/app.js').read_bytes()).hexdigest()
mobile=json.loads((out/'mobile-startup-check.json').read_text())
assert mobile['status']=='passed' and mobile['downloads_on_start']==[]
assert mobile['html_sha256']==browser['html_sha256'] and mobile['app_sha256']==browser['app_sha256']
assert set(mobile['startup_draws'])=={'force','torque','energy','elbow','series','continuum','spatial','atlas'}
assert all(d['available'] and not d['lost'] and d['unique_colors']>100 and d['vivid_geometry_pixels']>300 for d in mobile['startup_draws'].values())
doc=fitz.open(out/'kenoma-mechanics.pdf');combined='\n'.join(page.get_text() for page in doc)
assert len(doc)>5 and '\ufffd' not in combined
for needle in ['Force changes motion','Energy reveals numerical error','Checked source appendix','14.715','0.80','Store tendon energy','Inspect real anatomy','4,403','51.243524','798.52']:
 assert needle in combined,needle
spatial=json.loads((out/'spatial-experiment.json').read_text());reference=spatial['reference']
assert spatial['sourceSha256']==hashlib.sha256((ROOT/'web/spatial.mjs').read_bytes()).hexdigest()
assert f"{reference['penetrationM']*1000:.4f} mm" in (out/'assets/spatial.svg').read_text()
assert f"Maximum free-force defect is {reference['maxFreeForceN']:.6f} N" in text
manifest=json.loads((out/'build-manifest.json').read_text())
for relative,digest in manifest['input_sha256'].items():
 assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Build input changed: '+relative
for item in json.loads((out/'data/elbow-v1/provenance.json').read_text())['files']:
 assert hashlib.sha256((out/'data/elbow-v1'/item['path']).read_bytes()).hexdigest()==item['sha256']
proof_destinations={key:0 for _,*keys in families for key in keys}
for page in doc:
 for link in page.get_links():
  uri=link.get('uri','');parsed=urlparse(uri)
  assert parsed.hostname not in {'127.0.0.1','localhost','::1'} and parsed.scheme!='file',f'Nonportable PDF link: {uri}'
  destination=link.get('nameddest')
  if destination in proof_destinations:
   assert 0<=link.get('page',-1)<len(doc),'Unresolved internal PDF proof destination'
   proof_destinations[destination]+=1
 for block in page.get_text('blocks'):
  assert block[0]>=-1 and block[1]>=-1 and block[2]<=page.rect.width+1 and block[3]<=page.rect.height+1
assert all(proof_destinations[key]==len(receipt['claims']) for receipt,*keys in families for key in keys),'Missing internal PDF proof destinations'
spans=[span for page in doc for block in page.get_text('dict')['blocks'] if 'lines' in block for line in block['lines'] for span in line['spans']]
print_label_sizes={}
for label in ['Humerus','Triceps medial head','Unit 1','Elapsed time from retained trial segment (s)']:
 sizes=[s['size'] for s in spans if s['text']==label]
 assert sizes and min(sizes)>=10,'Evidence figure label is missing or too small: '+label
 print_label_sizes[label]=round(min(sizes),2)
results={'status':'passed','pdf_pages':len(doc),'proof_cards':total_claims,'pdf_links':'no loopback or file URLs','pdf_proof_destinations':proof_destinations,'browser':browser['browser_version'],
 'print_figure_label_minimum_pt':print_label_sizes,
 'scope':'Content, hash, glyph and page-bounds sanity; PDF appearance still requires visual review.'}
(out/'artifact-check.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))

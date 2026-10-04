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
text=(out/'kenoma-mechanics.md').read_text();assert not re.search(r'\{\{[A-Za-z]',text)
for id in ['force-pair','torque-linearity','torque-origin','central-pair','kinetic-sign','torque-example']:
 assert f'Checked claim {id}:' in text
browser=json.loads((out/'browser-check.json').read_text());assert browser['status']=='passed'
assert browser['proof_cards']==len(proof['claims'])
assert browser['html_sha256']==hashlib.sha256((out/'index.html').read_bytes()).hexdigest()
assert browser['app_sha256']==hashlib.sha256((out/'assets/app.js').read_bytes()).hexdigest()
mobile=json.loads((out/'mobile-startup-check.json').read_text())
assert mobile['status']=='passed' and mobile['downloads_on_start']==[]
assert mobile['html_sha256']==browser['html_sha256'] and mobile['app_sha256']==browser['app_sha256']
assert set(mobile['startup_draws'])=={'force','torque','energy','elbow','series','continuum','spatial','atlas'}
assert all(d['available'] and not d['lost'] and d['unique_colors']>100 and d['vivid_geometry_pixels']>300 for d in mobile['startup_draws'].values())
touch=mobile['spatial_touch_contract'];cases=touch['start_hitbox_cases']
assert len(cases)==45 and {c['width'] for c in cases}=={320,360,375,393,412}
assert all(c['target']=='start' and c['download_count']==0 for c in cases)
assert touch['intentional_export_filename']=='kenoma-spatial-trace.json' and touch['export_hit_target']=='export'
assert touch['local_diagnostics_verified']
export=json.loads((out/'qa/mobile-startup/intentional-spatial-export.json').read_text())
events=export['interactionDiagnostics']['events']
assert export['interactionDiagnostics']['lab']=='lab-spatial' and len(events)<=32
assert [e['type'] for e in events[-3:]]==['pointerdown','pointerup','click']
assert all(e['action']=='export' and e['trusted'] for e in events[-3:])
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
proof_destinations={key:0 for key in ['checked-source-appendix','proof-check-receipt','kernel-dependency-report']}
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
assert all(count==len(proof['claims']) for count in proof_destinations.values()),'Missing internal PDF proof destinations'
spans=[span for page in doc for block in page.get_text('dict')['blocks'] if 'lines' in block for line in block['lines'] for span in line['spans']]
print_label_sizes={}
for label in ['Humerus','Triceps medial head','Unit 1','Elapsed time from retained trial segment (s)']:
 sizes=[s['size'] for s in spans if s['text']==label]
 assert sizes and min(sizes)>=10,'Evidence figure label is missing or too small: '+label
 print_label_sizes[label]=round(min(sizes),2)
results={'status':'passed','pdf_pages':len(doc),'proof_cards':len(proof['claims']),'pdf_links':'no loopback or file URLs','pdf_proof_destinations':proof_destinations,'browser':browser['browser_version'],
 'print_figure_label_minimum_pt':print_label_sizes,
 'scope':'Content, hash, glyph and page-bounds sanity; PDF appearance still requires visual review.'}
(out/'artifact-check.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))

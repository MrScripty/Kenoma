"""Check generated receipts, complete content, links, and PDF glyph/bounds sanity."""
from pathlib import Path
import hashlib,json,re
import fitz
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'dist'
proof=json.loads((out/'proof-status.json').read_text())
assert proof['source_sha256']==hashlib.sha256((ROOT/'proofs/Mechanics.lean').read_bytes()).hexdigest()
assert proof['claims_sha256']==hashlib.sha256((ROOT/'proofs/claims.json').read_bytes()).hexdigest()
assert len(proof['claims'])==6 and all(c['status']=='checked' for c in proof['claims'])
assert all(set(c['axioms'])<={'propext','Quot.sound','Classical.choice'} for c in proof['claims'])
text=(out/'kenoma-mechanics.md').read_text();assert '{{' not in text
for id in ['force-pair','torque-linearity','torque-origin','central-pair','kinetic-sign','torque-example']:
 assert f'Checked claim {id}:' in text
browser=json.loads((out/'browser-check.json').read_text());assert browser['status']=='passed'
doc=fitz.open(out/'kenoma-mechanics.pdf');combined='\n'.join(page.get_text() for page in doc)
assert len(doc)>5 and '\ufffd' not in combined
for needle in ['Force changes motion','Energy reveals numerical error','Checked source appendix','14.715','0.80']:
 assert needle in combined,needle
for page in doc:
 for block in page.get_text('blocks'):
  assert block[0]>=-1 and block[1]>=-1 and block[2]<=page.rect.width+1 and block[3]<=page.rect.height+1
results={'status':'passed','pdf_pages':len(doc),'proof_cards':6,'browser':browser['browser_version'],
 'scope':'Content, hash, glyph and page-bounds sanity; PDF appearance still requires visual review.'}
(out/'artifact-check.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))

"""Bind the new Real-card HTML/PDF captures to the current checked build."""
from pathlib import Path
import hashlib,json,sys
import fitz
from check_real_lesson_proofs import FAMILIES
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check(out=None):
    out=Path(out) if out is not None else ROOT/'dist'
    folder=out/'real-proof-review';r=json.loads((folder/'render-receipt.json').read_text())
    assert r['result']=='PASS_REAL_PROOF_RENDER_CAPTURE' and not r['page_errors']
    for field,name in [('html_sha256','index.html'),('app_sha256','assets/app.js'),('pdf_sha256','kenoma-mechanics.pdf'),('manifest_sha256','build-manifest.json')]:
        assert r[field]==digest(out/name),'Stale Real render binding: '+name
    assert r['inspector_sha256']==digest(ROOT/'tools/inspect_real_lesson_proofs.py')
    claims=[c['id'] for _,_,prefix,_ in FAMILIES for c in json.loads((out/(prefix+'-proof-status.json')).read_text())['claims']]
    assert r['real_claims']==claims
    assert len(r['views'])==2 and {v['name'] for v in r['views']}=={'desktop','mobile'}
    assert all(v['real_cards']==len(claims) and not v['horizontal_overflow'] for v in r['views'])
    expected={view+'-'+claim+'.png' for view in ['desktop','mobile'] for claim in claims}|{p['image'] for p in r['source_pages']}
    assert len(r['source_pages'])>=len(FAMILIES) and set(r['outputs'])==expected
    for name,value in r['outputs'].items():assert digest(folder/name)==value,'Changed Real render image: '+name
    with fitz.open(out/'kenoma-mechanics.pdf') as doc:assert len(doc)==r['pdf_pages']
    print('PASS: current Real-card render evidence')
    return r
if __name__=='__main__':check(sys.argv[1] if len(sys.argv)>1 else None)

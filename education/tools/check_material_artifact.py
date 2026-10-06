"""Bind a delivered material lesson to fresh proof, experiment and browser evidence."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]

def check(destination):
    out=Path(destination);digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    preview=(out/'material-preview-manifest.json').exists()
    name='material-preview-manifest.json' if preview else 'build-manifest.json'
    manifest=json.loads((out/name).read_text())
    if preview:
        assert manifest['kind']=='fresh-independent-material-review' and manifest['proof_cards']==5
        for p,sha in manifest['input_sha256'].items():assert digest(ROOT/p)==sha,'Changed material input '+p
        for p,sha in manifest['output_sha256'].items():assert digest(out/p)==sha,'Changed material output '+p
    proof=json.loads((out/'material-proof-status.json').read_text())
    assert proof['source']=='proofs/MaterialResponse.lean'
    assert proof['source_sha256']==digest(ROOT/proof['source'])==digest(out/proof['source'])
    assert proof['claims_sha256']==digest(ROOT/'proofs/material-claims.json')==digest(out/'proofs/material-claims.json')
    assert len(proof['claims'])==5 and all(c['status']=='checked' for c in proof['claims'])
    assert all(set(c['axioms'])<={'propext','Quot.sound','Classical.choice'} for c in proof['claims'])
    experiment=json.loads((out/'material-experiment.json').read_text())
    for p,sha in experiment['inputs'].items():assert digest(ROOT/p)==sha,'Changed material experiment input '+p
    cases=experiment['cases'];default=cases['default']
    assert default['free']['converged'] and default['confined']['converged']
    assert abs(default['free']['J']-.9939144716354632)<1e-12
    assert default['confined']['J']==.8 and default['confined']['b']==1
    assert not cases['coarse']['free']['converged'] and cases['coarse']['free']['accepted']
    assert abs(cases['zeroBulk']['free']['J']-.512)<1e-12
    assert cases['weakBulk']['confined']['wallReactionPa']==0 and cases['weakBulk']['confined']['gapXM']>0
    assert not experiment['isochoricWallCandidate']['accepted'] and experiment['isochoricWallCandidate']['J']>0
    browser=json.loads((out/'material-qa/browser-check.json').read_text())
    assert browser['result']==('PASS_MATERIAL_PREVIEW_BROWSER' if preview else 'PASS_INTEGRATED_MATERIAL_BROWSER')
    assert not browser['javascriptErrors']
    assert browser['manifest']==name and browser['manifestSHA256']==digest(out/name)
    assert browser['HTMLSHA256']==digest(out/'index.html')
    assert browser['appSHA256']==digest(out/'assets/app.js')
    for p,sha in browser['sourceHashes'].items():assert digest(ROOT/p)==sha,'Changed material browser input '+p
    for p,sha in browser['outputs'].items():assert digest(out/'material-qa'/p)==sha,'Changed material browser output '+p
    observed=json.loads((out/'material-qa/observed.json').read_text())
    for label,key in [('default-desktop','default'),('default-mobile','default'),('high-bulk-desktop','highBulk'),('zero-bulk-desktop','zeroBulk'),('weak-bulk-desktop','weakBulk'),('coarse-desktop','coarse')]:
        assert all(observed[label][p]==v for p,v in cases[key].items()),'Browser and experiment disagree: '+label
    assert 'Property lab 4' in (out/'index.html').read_text()
    if preview:assert browser['PDFSHA256']==digest(out/'material-response.pdf')
    print('PASS_MATERIAL_SOURCE_PROOF_EXPERIMENT_BROWSER_BINDING')

if __name__=='__main__':check(sys.argv[1] if len(sys.argv)>1 else ROOT/'dist')

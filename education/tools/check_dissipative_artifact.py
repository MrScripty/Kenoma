"""Bind the axial SLS lesson to its fresh proof, protocol and actual UI checks."""
from pathlib import Path
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check(destination=None):
    out=Path(destination) if destination else ROOT/'dist'
    manifest=json.loads((out/'build-manifest.json').read_text())
    proof=json.loads((out/'dissipative-real-proof-status.json').read_text())
    assert proof['source']=='proofs/DissipativeBarReal.lean'
    assert proof['source_sha256']==digest(ROOT/proof['source'])==digest(out/proof['source'])
    assert proof['claims_sha256']==digest(ROOT/'proofs/dissipative-real-claims.json')==digest(out/'proofs/dissipative-real-claims.json')
    assert len(proof['claims'])==11 and all(c['status']=='checked' and set(c['axioms'])<={'propext','Classical.choice','Quot.sound'} for c in proof['claims'])
    assert proof['mathlib']==manifest['property_mathlib']==json.loads((ROOT/'proofs/mathlib-lock.json').read_text())
    experiment=json.loads((out/'dissipative-experiment.json').read_text())
    for name,sha in experiment['inputs'].items():assert digest(ROOT/name)==sha,'Changed SLS experiment input: '+name
    folder=out/'dissipative-qa';browser=json.loads((folder/'receipt.json').read_text())
    assert browser['status']=='PASS' and not browser['javascript_errors']
    expected_cards=sum(len(json.loads((out/name).read_text())['claims']) for name in manifest['proof_families'])
    assert browser['proof_cards']==expected_cards
    assert browser['build_manifest_sha256']==digest(out/'build-manifest.json'),'Stale SLS manifest binding'
    assert browser['test_sha256']==digest(ROOT/'tests/dissipative_browser.py'),'Stale SLS browser test'
    for name,sha in browser['source_input_sha256'].items():assert digest(ROOT/name)==sha,'Stale SLS source binding: '+name
    for name,sha in manifest['dissipative_outputs'].items():assert digest(out/name)==sha,'Changed SLS generated figure/experiment: '+name
    inputs=browser['delivered_input_sha256']
    assert {'index.html','assets/app.js','assets/dissipative-lab.css','web/dissipative-bar.mjs','web/dissipative-lab.mjs'}<=set(inputs)
    for name,sha in inputs.items():assert digest(out/name)==sha,'Changed delivered SLS input: '+name
    outputs=browser['output_sha256']
    assert {'force-hold-trace.json','extension-hold-trace.json','force-hold-loaded.png','force-hold-completed.png','extension-hold-completed.png','mobile-default.png'}<=set(outputs),'Incomplete SLS visual/trace evidence'
    for name,sha in outputs.items():assert digest(folder/name)==sha,'Changed SLS browser evidence: '+name
    for mode,case in [('force','creep'),('extension','relaxation')]:
        trace=json.loads((folder/(mode+'-hold-trace.json')).read_text())
        assert trace['parameters']==experiment['cases'][case]['parameters'],'Wrong SLS protocol parameters'
        assert trace['samples']==len(trace['trace'])==trace['steps']+1
        for frame in experiment['cases'][case]['frames']:
            actual=min(trace['trace'],key=lambda row:abs(row['time']-frame['time']))
            for key,value in frame.items():
                if isinstance(value,(float,int)):assert math.isclose(actual[key],value,rel_tol=2e-8,abs_tol=2e-12),'SLS frame disagreement: '+mode+'/'+key
                else:assert actual[key]==value,'SLS frame disagreement: '+mode+'/'+key
    assert 'Property lab 5' in (out/'index.html').read_text()
    assert (out/'assets/property-dissipative.svg').is_file()
    print('PASS_SLS_SOURCE_PROOF_PROTOCOL_VISUAL_BROWSER_BINDING')
    return browser
if __name__=='__main__':check(sys.argv[1] if len(sys.argv)>1 else None)

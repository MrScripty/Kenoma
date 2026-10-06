"""Bind the accepted connected model, integrated controls and numerical evidence."""
from pathlib import Path
import hashlib,json,sys,tempfile,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(out=None):
    out=Path(out) if out else ROOT/'dist';manifest=json.loads((out/'build-manifest.json').read_text())
    identity=json.loads((ROOT/'tools/connected-source-identity.json').read_text())
    assert len(identity['immutable_sha256'])==15 and {'web/axisymmetric-specimen.mjs','web/axisymmetric-material.mjs','web/axisymmetric-worker.mjs','proofs/AxisymmetricSpecimenReal.lean','proofs/axisymmetric-specimen-real-claims.json'} <= set(identity['immutable_sha256']), 'Incomplete accepted-source identity inventory'
    for name,value in identity['immutable_sha256'].items():assert sha(ROOT/name)==value,'Accepted connected source changed: '+name
    for name,value in manifest['connected_outputs'].items():assert sha(out/name)==value,'Changed connected output: '+name
    child=out/'connected-passive';p=json.loads((child/'axisymmetric-preview-manifest.json').read_text())
    assert all(sha(ROOT/n)==h for n,h in p['input_sha256'].items())
    assert all(sha(child/n)==h for n,h in p['output_sha256'].items())
    for name,status in [('connected-numerical-qualification.json','PASS_BOUNDED_ENGINEERING_CHECKS'),('connected-end-face-qualification.json','PASS'),('connected-material-oracle.json','PASS')]:assert json.loads((out/name).read_text())['status']==status
    for name,datafile in [('connected-numerical-qualification.json','connected-experiment.json'),('connected-end-face-qualification.json','connected-end-face-experiment.json')]:
        receipt=json.loads((out/name).read_text());assert receipt['experiment_sha256' if name=='connected-numerical-qualification.json' else 'data_sha256']==sha(out/datafile)
    native=json.loads((out/'connected-qa/axisymmetric-browser-status.json').read_text());api=json.loads((out/'connected-api-qa/axisymmetric-end-face-browser-status.json').read_text());integrated=json.loads((out/'connected-integration.json').read_text())
    assert native['status']==api['status']=='PASS' and len(native['cases'])==20 and len(api['cases'])==16
    assert native['preview_manifest_sha256']==api['preview_manifest_sha256']==sha(child/'axisymmetric-preview-manifest.json')
    assert native['oracle_sha256']==sha(out/'connected-material-oracle.json') and native['experiment_sha256']==sha(out/'connected-experiment.json')
    assert all(sha(ROOT/n)==h for n,h in native['source_inputs'].items())
    assert api['affected_experiment_sha256']==sha(out/'connected-end-face-experiment.json') and api['test_sha256']==sha(ROOT/'tests/axisymmetric_end_faces_browser.py') and api['base_test_sha256']==sha(ROOT/'tests/axisymmetric_browser.py')
    assert native['test_sha256']==sha(ROOT/'tests/axisymmetric_browser.py')
    assert integrated['result']=='PASS_INTEGRATED_CONNECTED_SPECIMEN' and not integrated['errors']
    assert integrated['test_sha256']==sha(ROOT/'tests/connected_integration.py'),'Changed integrated browser test'
    assert integrated['controls_capture_sha256']==sha(out/'connected-in-book-controls.png'),'Changed integrated controls capture'
    for field,path in [('manifest_sha256','build-manifest.json'),('html_sha256','index.html'),('child_manifest_sha256','connected-passive/axisymmetric-preview-manifest.json')]:assert integrated[field]==sha(out/path)
    assert integrated['native_receipt_sha256']==sha(out/'connected-qa/axisymmetric-browser-status.json') and integrated['api_receipt_sha256']==sha(out/'connected-api-qa/axisymmetric-end-face-browser-status.json')
    figure=json.loads((out/'connected-figure.json').read_text());assert figure['experiment_sha256']==sha(out/'connected-experiment.json') and figure['svg_sha256']==sha(out/'assets/connected-specimen.svg') and figure['generator_sha256']==sha(ROOT/'tools/connected-specimen-figure.mjs')
    with tempfile.TemporaryDirectory() as folder:
        svg=Path(folder)/'figure.svg';record=Path(folder)/'figure.json';subprocess.run(['node',str(ROOT/'tools/connected-specimen-figure.mjs'),str(out/'connected-experiment.json'),str(svg),str(record)],check=True,cwd=ROOT)
        assert sha(svg)==sha(out/'assets/connected-specimen.svg') and json.loads(record.read_text())==figure,'Figure differs from actual solved Q2 side'
    proof=json.loads((out/'axisymmetric-proof-status.json').read_text());assert len(proof['claims'])==9 and proof['source_sha256']==identity['immutable_sha256']['proofs/AxisymmetricSpecimenReal.lean']
    print('PASS accepted connected source, numerical/figure bindings and actual browser/GPU qualification')
    return integrated
if __name__=='__main__':check(sys.argv[1] if len(sys.argv)>1 else None)

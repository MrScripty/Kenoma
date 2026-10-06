"""Actual compiled worker/renderer on accepted extra meshes, via explicit qualification API.

The user control menu remains 4/8/16. Extra mesh options are labelled test-only;
no native-control availability claim is made for 3/6/12/24 cells.
"""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
import argparse,hashlib,json
from playwright.sync_api import sync_playwright,expect
from axisymmetric_browser import ROOT,sha,close,ready,snap,verify_state,verify_scene,GPU_TRACK,QuietHandler

def qualify(preview,out,oraclefile,legacyfile,affectedfile):
    test_hash=sha(Path(__file__));base_test_hash=sha(ROOT/'tests/axisymmetric_browser.py');out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((preview/'axisymmetric-preview-manifest.json').read_text());oracle=json.loads(oraclefile.read_text());legacy=json.loads(legacyfile.read_text());affected=json.loads(affectedfile.read_text())
    assert all(sha(ROOT/n)==h for n,h in manifest['input_sha256'].items()) and all(sha(preview/n)==h for n,h in manifest['output_sha256'].items())
    assert all(sha(ROOT/n)==h for n,h in affected['inputs'].items()) and all(sha(ROOT/n)==h for n,h in oracle['input_sha256'].items())
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(preview)));Thread(target=server.serve_forever,daemon=True).start();cases=[];errors=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']);context=browser.new_context(viewport={'width':1200,'height':1000});context.add_init_script(GPU_TRACK);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:'+str(server.server_port));ready(page);lab=page.locator('[data-axisymmetric]');lab.locator('[data-action=start]').click();expect(lab).to_have_attribute('data-scene-state','ready')
            # Keep the displayed option explicit; leave production validation/menu unchanged.
            lab.locator('[data-setting=mesh]').evaluate("el=>{for(const n of [3,6,12,24])el.add(new Option(n+' axial × 2 radial (qualification API)',n+',2'));}")
            for expected in affected['cases']:
                c={k:expected[k] for k in ['epsilon','ratio','axialCells','radialCells']};c['cap']=25
                lab.evaluate('(r,c)=>r.axisymmetricLab.request(c)',c);ready(page);payload=snap(lab)
                assert payload['configuration']==c and payload['state']['converged'] and payload['state']['reachedRequestedPose']
                for got,want in zip(payload['state']['q'],expected['state']['q']):close(got,want,'Actual accepted-mesh compiled worker state',absolute=2e-12)
                for k in ['rightReactionN','energyJ','volumeRatio']:close(payload['state']['diagnostics'][k],expected['state']['diagnostics'][k],'Actual affected worker '+k,absolute=2e-12)
                base=verify_state(payload,oracle,legacy);scene=verify_scene(page,payload);b=payload['boundary'];assert all(v[2]<=.05 for v in b['referenceVertices'])
                for i in range(b['azimuth']):assert b['referenceVertices'][(b['rings']-1)*b['azimuth']+i][2]==.05
                assert payload['trace'][-1]['Z']==.05
                case={'case':expected['key'],'state':base,'scene':scene,'scope':'Actual compiled worker and GPU geometry via qualification API; this extra mesh is not in the user-facing native menu'};cases.append(case)
                (out/(expected['key'].replace(':','_')+'-state.json')).write_text(json.dumps(payload)+'\n')
                if expected['axialCells']==3 and expected['ratio']==1:lab.screenshot(path=str(out/('three-cell-'+('compression' if expected['epsilon']<0 else 'tension')+'.png')))
            version=browser.version;browser.close()
    finally:server.shutdown()
    assert not errors and len(cases)==16 and sha(Path(__file__))==test_hash and sha(ROOT/'tests/axisymmetric_browser.py')==base_test_hash
    assert all(sha(ROOT/n)==h for n,h in manifest['input_sha256'].items()) and all(sha(preview/n)==h for n,h in manifest['output_sha256'].items())
    record={'status':'PASS','browser':'Chromium '+version,'cases':cases,'preview_manifest_sha256':sha(preview/'axisymmetric-preview-manifest.json'),'affected_experiment_sha256':sha(affectedfile),'oracle_sha256':sha(oraclefile),'base_test_sha256':base_test_hash,'test_sha256':test_hash,'source_inputs':manifest['input_sha256'],'scope':'16 formerly affected meshes through actual compiled worker/render API with strict endpoints, independent Q2 geometry, oracle/force checks and GPU readback. Native menu remains 4/8/16 and has a separate unchanged 20-case qualification. Headless SwiftShader, no physical mobile hardware/stability claim.'}
    (out/'axisymmetric-end-face-browser-status.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS 16 actual compiled-worker/API endpoint cases with independent GPU geometry')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preview',required=True,type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--oracle',required=True,type=Path);p.add_argument('--legacy-experiment',required=True,type=Path);p.add_argument('--affected-experiment',required=True,type=Path);a=p.parse_args();qualify(a.preview,a.out,a.oracle,a.legacy_experiment,a.affected_experiment)

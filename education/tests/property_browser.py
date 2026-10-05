"""Actual controls, rollback, volume oracles and print alternatives in the preview."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import hashlib,json,os,shutil,subprocess,sys
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
def check(destination):
    out=Path(destination).resolve();qa=out/'qa';qa.mkdir(exist_ok=True)
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(out)));Thread(target=server.serve_forever,daemon=True).start()
    checks=[];preview_mode=(out/'preview-manifest.json').exists()
    manifest_name='preview-manifest.json' if preview_mode else 'build-manifest.json'
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        page=browser.new_page(viewport={'width':1200,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/index.html',wait_until='networkidle')
        assert page.locator('[data-property]').count()==3
        expected_proofs=0 if preview_mode else sum(len(json.loads((out/name).read_text())['claims']) for name in json.loads((out/manifest_name).read_text())['proof_families'])
        assert page.locator('.proof-card').count()==expected_proofs
        if not preview_mode:
            for claim in ['volume-edge-translation','volume-det-compose','volume-diagonal','volume-isochoric-sqrt']:
                card=page.locator('#proof-'+claim)
                expect(card.locator('.proof-meta')).to_contain_text('pinned mathlib v4.19.0')
                expect(card.locator('.proof-meta')).to_contain_text('c44e0c8ee63ca166450922a373c7409c5d26b00b')
            expect(page.locator('#proof-volume-isochoric-sqrt pre').first).to_contain_text('0 < lambda')
            expect(page.locator('#proof-volume-isochoric-sqrt pre').first).to_contain_text('Real.sqrt')
            checks.append('Four actual real proof cards retain positive-stretch assumptions and pinned mathlib metadata')
        def state(lab):
            lab.locator('[data-action=copy]').click();return json.loads(lab.locator('.preset').input_value())
        deformation=page.locator('[data-property=deformation]');before=state(deformation)
        deformation.locator('[data-action=invert]').click();expect(deformation.locator('.announce')).to_contain_text('Rejected inverted candidate')
        assert state(deformation)['measurements']==before['measurements']
        x=deformation.locator('input[type=number][data-param=sx]');x.fill('');expect(x).to_have_attribute('aria-invalid','true')
        assert state(deformation)['measurements']==before['measurements']
        deformation.locator('[data-action=reset]').click();assert x.get_attribute('aria-invalid') is None
        deformation.locator('input[type=number][data-param=tx]').fill('30');m=state(deformation)['measurements']
        assert abs(m['J']-before['measurements']['J'])<1e-12 and abs(m['volumeMeasurementDifference'])<1e-12
        checks.append('Deformation controls, invalid input, inversion rejection and retained prior state; translation boundary-volume oracle')
        iso=page.locator('[data-property=isochoric]');expect(iso.locator('input[type=number][data-param=lateral]')).to_be_disabled()
        iso.locator('input[type=number][data-param=axial]').fill('0.6');m=state(iso)['measurements']
        assert abs(m['J']-1)<1e-12 and abs(m['volumeRatio']-1)<1e-12 and abs(m['areaLengthMeasurementDifferenceM3'])<1e-15
        assert m['crossSectionAreaM2']!=m['exteriorAreaM2']
        iso.locator('select[data-param=mode]').select_option('independent');iso.locator('input[type=number][data-param=lateral]').fill('1');assert abs(state(iso)['measurements']['J']-.6)<1e-12
        checks.append('Actual isochoric toggle and independent stretches; boundary volume and area-times-length; cross-section versus exterior area')
        bar=page.locator('[data-property=tapered]');bar.locator('select[data-param=shape]').select_option('two-segment');bar.locator('select[data-param=mode]').select_option('active-fixed');m=state(bar)['measurements']
        assert abs(min(v['strain'] for v in m['samples'])+1/300)<1e-12 and abs(max(v['strain'] for v in m['samples'])-1/300)<1e-12
        assert abs(m['numericalExtensionM'])<1e-14
        bar.locator('[data-action=reset]').click();bar.locator('select[data-param=segments]').select_option('8');a=abs(state(bar)['measurements']['extensionErrorM']);bar.locator('select[data-param=segments]').select_option('32');assert abs(state(bar)['measurements']['extensionErrorM'])<a/15
        bar.locator('select[data-param=segments]').select_option('8')
        for param,value in [('area','0.0001'),('ratio','4'),('modulus','110000'),('force','0.6')]:bar.locator(f'input[type=number][data-param={param}]').fill(value)
        m=state(bar)['measurements'];assert m['smallStrainWarning'] and abs(m['maxAbsStrain']-3/55)<1e-12
        expect(bar.locator('.readout')).to_contain_text('Exceeded 5%')
        checks.append('UI-valid endpoint warning regression: true 5.4545% strain exposed despite midpoint maximum below 5%')
        checks.append('Taper fixed-end uneven extension/compression and genuine midpoint refinement')
        for lab in [deformation,iso,bar]:
            lab.locator('[data-action=reset]').click();lab.locator('[data-action=summary]').click();expect(lab.locator('.announce')).not_to_be_empty();lab.locator('.preset').evaluate('(x)=>x.hidden=true');lab.screenshot(path=str(qa/(lab.get_attribute('data-property')+'-desktop.png')))
        page.set_viewport_size({'width':393,'height':852})
        for lab in [deformation,iso,bar]:
            lab.scroll_into_view_if_needed();assert lab.evaluate('(x)=>x.scrollWidth<=x.clientWidth+1');lab.screenshot(path=str(qa/(lab.get_attribute('data-property')+'-mobile.png')))
        page.emulate_media(media='print')
        for lab in [deformation,iso,bar]:expect(lab.locator('.static-figure')).to_be_visible();expect(lab.locator('.property-scene')).to_be_hidden();expect(lab.locator('.property-description')).to_be_hidden()
        revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        page.evaluate('''revision=>{for(const link of document.querySelectorAll('a[href^="web/"]'))link.setAttribute('href',`https://github.com/MrScripty/Kenoma/blob/${revision}/education/${link.getAttribute('href')}`)}''',revision)
        if preview_mode:page.pdf(path=str(qa/'property-lessons.pdf'),format='A4',print_background=True)
        assert not errors,errors
        browser.close()
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        page=browser.new_page(java_script_enabled=False);page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
        assert page.locator('[data-property] .static-figure img').count()==3
        assert page.locator('[data-property] .static-figure img').evaluate_all('(els)=>els.every(x=>x.complete&&x.naturalWidth>0)')
        browser.close();checks.append('Desktop/mobile geometry and summaries; static print/PDF and zero-JavaScript alternatives')
    finally:server.shutdown()
    (qa/('browser-check.json' if preview_mode else 'property-browser-check.json')).write_text(json.dumps({'schema':1,'result':'PASS_PROPERTY_PREVIEW' if preview_mode else 'PASS_INTEGRATED_PROPERTY_LABS','checks':checks,'javascript_errors':errors,'manifest':manifest_name,'manifest_sha256':hashlib.sha256((out/manifest_name).read_bytes()).hexdigest(),'html_sha256':hashlib.sha256((out/'index.html').read_bytes()).hexdigest(),'app_sha256':hashlib.sha256((out/('web/property-labs.mjs' if preview_mode else 'assets/app.js')).read_bytes()).hexdigest(),'source_revision':revision,'proof_cards':expected_proofs},indent=2)+'\n');print('\n'.join(checks))
if __name__=='__main__':check(sys.argv[1] if len(sys.argv)>1 else ROOT/'dist/property-preview')

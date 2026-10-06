"""Exercise the current renderer, inactive controls, and the endpoint counterexample."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import hashlib, json, os, shutil, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]

def check():
    digest = lambda p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    paths = ['web/property-labs.mjs', 'web/tapered-bar.mjs', 'web/continuum-properties.mjs',
             'tools/property_labs.py', 'tools/build_property_preview.py', 'tests/endpoint_warning_audit.py']
    with tempfile.TemporaryDirectory(prefix='kenoma-endpoint-') as directory:
        out = Path(directory)
        subprocess.run([sys.executable, str(ROOT/'tools/build_property_preview.py'), str(out)], cwd=ROOT, check=True)
        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(out)))
        Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
                page = browser.new_page(viewport={'width':1200,'height':1000})
                errors=[]; page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{server.server_port}/index.html', wait_until='networkidle')
                lab = page.locator('[data-property=tapered]')
                def state():
                    lab.locator('[data-action=copy]').click()
                    return json.loads(lab.locator('.preset').input_value())
                lab.locator('select[data-param=segments]').select_option('8')
                for key,value in [('area','0.0001'),('ratio','4'),('modulus','110000'),('force','0.6')]:
                    lab.locator(f'input[type=number][data-param={key}]').fill(value)
                measured=state()['measurements']
                assert measured['smallStrainWarning'] and abs(measured['maxAbsStrain']-3/55)<1e-15
                assert max(abs(s['strain']) for s in measured['samples'])<.05
                expect(lab.locator('.readout')).to_contain_text('Exceeded 5%')
                warning=lab.locator('.readout div').filter(has=page.locator('dt',has_text='Small-strain scope')).locator('dd')
                expect(warning).to_contain_text('Exceeded 5%')
                warning.scroll_into_view_if_needed()
                expect(warning).to_be_visible()
                evidence=ROOT/'data/property-labs-v1/endpoint-warning-current-visible.png'
                lab.locator('.readout').screenshot(path=str(evidence))
                expect(lab.locator('.readout')).to_contain_text('Expanded beyond ±0.05')
                expect(lab.locator('input[type=number][data-param=activation]')).to_be_disabled()
                lab.locator('select[data-param=mode]').select_option('active-fixed')
                expect(lab.locator('input[type=number][data-param=force]')).to_be_disabled()
                expect(lab.locator('input[type=number][data-param=activation]')).to_be_enabled()
                lab.locator('select[data-param=mode]').select_option('passive')
                assert state()['measurements']==measured
                assert not errors, errors
                version=browser.version; browser.close()
        finally:
            server.shutdown();server.server_close()
        receipt={'schema':1,'result':'PASS_CURRENT_ENDPOINT_RENDERER','browserVersion':version,
                 'currentNumericalReceiptSHA256':digest('data/property-labs-v1/endpoint-warning-current-audit.json'),
                 'sourceHashes':{p:digest(p) for p in paths},'previewHTMLSHA256':hashlib.sha256((out/'index.html').read_bytes()).hexdigest(),
                 'counterexample':{'endpointMaximumStrain':measured['maxAbsStrain'],'midpointMaximumStrain':max(abs(s['strain']) for s in measured['samples']),'warningVisible':True},
                 'visibilityEvidence':{'assertion':'Playwright expect(specific Small-strain scope dd).to_be_visible after scroll_into_view_if_needed',
                                       'screenshot':'data/property-labs-v1/endpoint-warning-current-visible.png','sha256':hashlib.sha256(evidence.read_bytes()).hexdigest()},
                 'checks':['Actual Chromium endpoint controls expose 5.4545% strain despite midpoint samples below 5%',
                           'Current renderer exposes expanded strain scale and disables inactive controls',
                           'Active/passive round trip preserves passive endpoint measurements'],
                 'javascriptErrors':errors,'scope':'Fresh standalone preview and actual DOM controls; no full book/proof/release claim.'}
    target=ROOT/'data/property-labs-v1/endpoint-warning-browser-audit.json'
    target.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['result'])

if __name__=='__main__':check()

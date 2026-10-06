"""Actual frozen-layout regression, font fallback, controls and table scrolling."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import argparse, hashlib, importlib.util, json, os, shutil, subprocess, tempfile
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('projection_oracle', ROOT/'standalone/pressure-projection-lab-check.py')
oracle = importlib.util.module_from_spec(spec); spec.loader.exec_module(oracle)
FROZEN = 'e7d56450f6a806fa14b0a511bfcf6405d592fc27'
FROZEN_SHA256 = '3c3bd14dc774c809074af208c9574127c9824a04b69c1a5a25209c95e1f461b4'


def check(output):
    output.mkdir(parents=True, exist_ok=True)
    (output/'receipt.json').unlink(missing_ok=True)
    current = ROOT/'standalone/pressure-projection-lab.html'
    # CI has a shallow checkout: preserve the exact immutable predecessor
    # locally rather than depending on historical Git objects being present.
    old = (ROOT/'tests/fixtures/projection-layout-e7d56450.html').read_bytes()
    assert hashlib.sha256(old).hexdigest() == FROZEN_SHA256, 'Changed frozen layout fixture'
    errors = []; rows = []
    with tempfile.TemporaryDirectory() as folder:
        folder = Path(folder); (folder/'frozen.html').write_bytes(old); shutil.copy2(current, folder/'fixed.html')
        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *args): pass
        server = ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(folder)))
        Thread(target=server.serve_forever,daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
                page = browser.new_page(viewport={'width':320,'height':844})
                page.on('pageerror',lambda e:errors.append(str(e)))
                base = f'http://127.0.0.1:{server.server_port}'
                page.goto(base+'/frozen.html',wait_until='networkidle')
                page.add_style_tag(content='body{font-family:"DejaVu Sans",sans-serif}')
                page.locator('#reset').click()
                regression = oracle.viewport_diagnostics(page,output,'frozen-dejavu-320')
                assert regression['documentWidth']>320, 'Frozen intrinsic table-width regression did not reproduce'
                for font in ('native','dejavu'):
                    page.goto(base+'/fixed.html',wait_until='networkidle')
                    if font=='dejavu':page.add_style_tag(content='body{font-family:"DejaVu Sans",sans-serif}')
                    for width in (320,360,390,414,560,768,1280):
                        page.set_viewport_size({'width':width,'height':844})
                        for level in (1,2,4):
                            page.locator('#reset').click()
                            page.locator(f'input[name=space][value="{level}"]').check()
                            oracle.check_state(page.evaluate('PressureProjectionLab.state()'),oracle.oracle([-.75,.25,-.25,.75],8,level))
                            row=oracle.viewport_diagnostics(page,output,f'{font}-{width}-q{level}')
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), row
                            assert page.locator('.controls').evaluate('(e)=>e.scrollWidth<=e.clientWidth')
                            assert page.evaluate('''()=>[document.documentElement,document.body,document.querySelector('main')].every(e=>!['hidden','clip'].includes(getComputedStyle(e).overflowX))''')
                            rows.append(row)
                        page.locator('#reset').click()
                        page.locator('#preset').select_option('paired')
                        page.locator('input[name=space][value="2"]').check()
                        expect(page.locator('#gap')).to_have_text('0')
                        page.locator('#scale').fill('16')
                        oracle.check_state(page.evaluate('PressureProjectionLab.state()'),oracle.oracle([-.5,-.5,.25,.25],16,2))
                        page.locator('#g0').fill('0.75')
                        oracle.check_state(page.evaluate('PressureProjectionLab.state()'),oracle.oracle([.75,-.5,.25,.25],16,2))
                        page.locator('#reset').click()
                        expect(page.locator('#gap')).to_have_text('7.5')
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                        if width==320:
                            region=page.locator('.table-scroll');region.focus()
                            before=region.evaluate('(e)=>({client:e.clientWidth,scroll:e.scrollWidth})')
                            if before['scroll']>before['client']:
                                page.keyboard.press('ArrowRight');page.keyboard.press('ArrowRight');page.wait_for_timeout(300)
                                assert region.evaluate('(e)=>e.scrollLeft>0'), 'Full table must be keyboard-scrollable'
                                region.evaluate('(e)=>e.scrollLeft=e.scrollWidth')
                                assert page.locator('#samples-table tbody tr:last-child td:last-child').evaluate('(e)=>e.getBoundingClientRect().right<=e.closest(".table-scroll").getBoundingClientRect().right+1')
                                region.evaluate('(e)=>e.scrollLeft=0')
                            page.screenshot(path=str(output/f'fixed-{font}-320.png'),full_page=True)
                    page.locator('footer details').evaluate('(e)=>e.open=true')
                    expect(page.locator('footer details p')).to_be_visible()
                version=browser.version; browser.close()
        finally:server.shutdown();server.server_close()
    assert not errors, errors
    receipt={'result':'PASS_PROJECTION_RESPONSIVE_REGRESSION','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'source_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),'browser':version,'frozen_source':FROZEN,'frozen_sha256':FROZEN_SHA256,
             'frozen_failure':regression,'fixed_cases':rows,'javascript_errors':errors,
             'scope':'Local browser with native and declared DejaVu font fallback; no inference that browser patch version caused hosted failure',
             'evidence_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in output.iterdir() if f.is_file() and f.name!='receipt.json'}}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS 42 viewport/space/font cases, actual controls and keyboard-scrollable complete table')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'dist/projection-responsive-qa');check(parser.parse_args().output)

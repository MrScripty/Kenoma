from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import hashlib, json, subprocess
from playwright.sync_api import sync_playwright, expect

ROOT = Path('/workspace/kenoma-serial-wording/education')
SITE = Path('/workspace/kenoma-serial-wording-preview')
OUT = Path('/workspace/kenoma-serial-wording-focused')
OUT.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
inputs = {str(p.relative_to(SITE)): sha(p) for p in SITE.rglob('*') if p.is_file()}
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(SITE)))
Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium')
        page = browser.new_page(viewport={'width':1100,'height':850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(f'http://127.0.0.1:{server.server_port}/', wait_until='networkidle')
        lab = page.locator('#lab-serial-specimen')
        page.wait_for_function('document.querySelector("#lab-serial-specimen").serialLab != null')
        lab.locator('[data-action=start]').click()
        expect(lab).to_have_attribute('data-scene-state','ready')
        for name, value in [('ratio','.5'),('mu','500'),('iterations','8')]:
            if name == 'iterations':
                lab.locator('select[data-param=iterations]').select_option(value)
            else:
                lab.locator(f'input[type=number][data-param={name}]').fill(value)
        before = lab.evaluate('(root)=>root.serialLab.snapshot()')
        warning = lab.locator('.serial-solve-status').inner_text()
        pixels = lab.evaluate('(root)=>root.serialLab.pixelSignature()')
        assert not before['state']['converged'] and 'not a qualified shared-force equilibrium' in warning
        lab.locator('[data-action=reject-volume]').click()
        after = lab.evaluate('(root)=>root.serialLab.snapshot()')
        message = lab.locator('.serial-candidate').inner_text()
        assert before['parameters'] == after['parameters'] and before['state'] == after['state']
        assert before['scene']['meshes'] == after['scene']['meshes'] and before['scene']['camera'] == after['scene']['camera']
        assert pixels == lab.evaluate('(root)=>root.serialLab.pixelSignature()')
        assert lab.locator('.serial-solve-status').inner_text() == warning
        expect(lab).to_have_attribute('data-converged','false')
        assert 'preceding displayed approximation was retained' in message and 'valid solved' not in message
        assert after['lastCandidate']['accepted'] is False and not errors
        lab.screenshot(path=str(OUT/'actual-controls-coarse-rejected.png'))
        record = {'status':'PASS','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'browser_version':browser.version,'javascript_errors':errors,'warning_before_and_after':warning,'candidate_message':message,'parameters_state_mesh_camera_pixels_unchanged':True,'converged_before_and_after':False,'candidate_accepted':False,'before':before,'after':after,'pixels_before_and_after':pixels,'delivered_input_sha256':inputs,'preview_manifest_sha256':sha(SITE/'serial-preview-manifest.json'),'scope':'Focused actual standalone production controls; no proof rerun, full book build, hosted or print qualification'}
        browser.close()
finally:
    server.shutdown()
    server.server_close()
assert all(sha(SITE/name) == h for name,h in inputs.items())
record['output_sha256'] = {'actual-controls-coarse-rejected.png':sha(OUT/'actual-controls-coarse-rejected.png')}
(OUT/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS focused actual candidate wording, retained nonconvergence warning and unchanged numerical/mesh/pixel state')

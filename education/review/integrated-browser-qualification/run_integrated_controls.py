"""Qualify production controls in the copied, immutable integrated book build."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tests'), str(ROOT/'tools')]
from render_pdf import serve
from executable_outputs import checked_build_outputs, executable_digest, unchanged_outputs
from teaching_controls_browser import check
from playwright.sync_api import sync_playwright

out = ROOT/'review/integrated-browser-qualification/controls'
out.mkdir(parents=True, exist_ok=True)
executables = checked_build_outputs(ROOT/'dist')
receipt = {'status': 'FAIL', 'scope': 'Actual copied 42-card integrated HTML and production bundle; final proof-family rebuild pending',
           'qualification_source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
           'build_manifest_sha256': hashlib.sha256((ROOT/'dist/build-manifest.json').read_bytes()).hexdigest(),
           'html_sha256': hashlib.sha256((ROOT/'dist/index.html').read_bytes()).hexdigest(),
           'app_sha256': hashlib.sha256((ROOT/'dist/assets/app.js').read_bytes()).hexdigest(),
           'executable_outputs_sha256': executable_digest(executables)}
server, url = serve()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        context = browser.new_context(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
        page = context.new_page()
        page.set_default_timeout(60000)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(url+'/index.html', wait_until='networkidle')
        receipt['proof_cards'] = page.locator('.proof-card').count()
        assert receipt['proof_cards'] == 42
        receipt['observed'] = check(page, out, 'all')
        assert not errors, errors
        receipt['javascript_errors'] = errors
        receipt['browser_version'] = browser.version
        unchanged_outputs(ROOT/'dist', executables)
        receipt['status'] = 'PASS'
        browser.close()
finally:
    server.shutdown()
    server.server_close()
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print('PASS: all teaching control cases against actual integrated book')

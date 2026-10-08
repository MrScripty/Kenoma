"""Exercise the built book entry and assembled lab, without starting a build.

Run only after an explicitly authorized full book build. These controls are
scalar examples; this checker never invokes anatomical or material campaigns.
Generated JPEG85 captures remain untracked and need separate visual review.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit
import json
import os
import shutil
import sys
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from architecture_force_lab import DEFAULT_ROWS, RECEIPT, digest
from check_architecture_force_artifact import check_assembly
from check_real_lesson_proofs import BOOK_CLAIMS
from executable_outputs import checked_build_outputs, unchanged_outputs
from architecture_force_browser import DEFAULTS, BOUNDS, check_state


def inspect():
    out = ROOT / 'dist'
    target = out / 'architecture-force/book-browser.json'
    target.unlink(missing_ok=True)
    check_assembly(out)
    before = checked_build_outputs(out)
    bindings = {name: digest(out / name) for name in ['index.html', 'build-manifest.json', RECEIPT,
                 'architecture-force/registration.json', 'architecture-force/index.html']}
    captures = out / 'architecture-force/qa'
    captures.mkdir(exist_ok=True)
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_GET(self):
            if self.path == '/favicon.ico':
                self.send_response(204); self.end_headers()
            else: super().do_GET()
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(out)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    views, outputs = [], {}
    def capture(page, name):
        path = captures / name
        page.screenshot(path=str(path), type='jpeg', quality=85, full_page=True)
        outputs[str(path.relative_to(out))] = digest(path)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
            for label, width, height, javascript in [('desktop', 1280, 1000, True), ('mobile', 393, 852, True), ('no-javascript', 393, 852, False)]:
                context = browser.new_context(viewport={'width': width, 'height': height}, java_script_enabled=javascript)
                errors = []
                def local_only(route):
                    if urlsplit(route.request.url).netloc != urlsplit(origin).netloc:
                        errors.append('Remote request: '+route.request.url); route.abort()
                    else: route.continue_()
                context.route('**/*', local_only)
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('requestfailed', lambda request: errors.append('Request failed: '+request.url))
                page.on('response', lambda response: errors.append('HTTP '+str(response.status)+': '+response.url) if response.status >= 400 else None)
                page.goto(origin+'/index.html', wait_until='networkidle')
                assert page.locator('.proof-card').count() == BOOK_CLAIMS
                reference = page.locator('#architecture-force-lab')
                expect(reference).to_be_visible()
                for name, value in DEFAULT_ROWS:
                    expect(reference).to_contain_text(name); expect(reference).to_contain_text(value)
                page.get_by_role('link', name='Open the interactive architecture-force lab', exact=True).click()
                page.wait_for_load_state('networkidle')
                assert page.url == origin+'/architecture-force/index.html'
                check_state(page)
                capture(page, label+'-default.jpg')
                if javascript:
                    page.locator('#stretch').focus(); page.keyboard.press('ArrowRight')
                    values = {**DEFAULTS, 'stretch': .81}
                    check_state(page, values)
                    page.locator('#length-law').check(); check_state(page, values, True)
                    capture(page, label+'-force-length.jpg')
                    page.locator('#length-law').uncheck(); check_state(page, values)
                    for control, (lower, upper) in BOUNDS.items():
                        for key, value in [('Home', lower), ('End', upper)]:
                            page.locator('#reset').click(); check_state(page)
                            page.locator('#'+control).focus(); page.keyboard.press(key)
                            check_state(page, {**DEFAULTS, control: value})
                    for control in BOUNDS:
                        page.locator('#'+control).focus(); page.keyboard.press('End')
                    page.locator('#length-law').check()
                    for _ in range(2): page.locator('#reset').click(); check_state(page)
                else:
                    expect(page.locator('noscript')).to_be_visible()
                for href in page.locator('a[href]').evaluate_all('(els)=>els.map(e=>e.href)'):
                    assert urlsplit(href).netloc == urlsplit(origin).netloc
                    assert page.request.get(href.split('#')[0]).status == 200, href
                page.emulate_media(media='print')
                expect(page.locator('#controls')).to_be_hidden()
                expect(page.locator('.book-print-reference')).to_be_visible()
                for name, value in DEFAULT_ROWS:
                    expect(page.locator('.book-print-reference')).to_contain_text(name)
                    expect(page.locator('.book-print-reference')).to_contain_text(value)
                assert not errors, errors
                views.append({'name': label, 'width': width, 'height': height, 'javascript': javascript,
                              'entry_defaults_links_print_and_controls': True, 'errors': errors})
                context.close()
            version = browser.version
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    unchanged_outputs(out, before)
    assert bindings == {name: digest(out / name) for name in bindings}
    result = {'schema': 1, 'status': 'PASS_ARCHITECTURE_FORCE_BOOK_CONTROLS', 'bookProofs': BOOK_CLAIMS,
              'browser': version, 'views': views, 'inputSha256': bindings, 'captureSha256': outputs,
              'checkerSha256': digest(Path(__file__)), 'controlOracleSha256': digest(ROOT/'tests/architecture_force_browser.py'),
              'visualAcceptance': 'pending independent visual review', 'scope': 'Book entry, scalar controls, portable local links and static print/no-JavaScript defaults; no anatomical claim.'}
    target.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    inspect()

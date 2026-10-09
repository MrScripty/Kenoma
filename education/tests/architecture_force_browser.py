"""Real Chromium controls for the static architecture-force contribution.

No app build, anatomy, solver, remote assets or deployment. Captures are JPEG85
outside the checkout and require a separate human visual-inspection decision.
"""
from pathlib import Path
from functools import partial
import argparse
import hashlib
import http.server
import importlib.metadata
import json
import math
import socketserver
import threading
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / 'education/contributions/architecture-force'
DEFAULTS = {'stretch': .8, 'volume': 1, 'packing': .8, 'angle': 30}
BOUNDS = {'stretch': (.6, 1.4), 'volume': (.8, 1.1), 'packing': (.5, 1), 'angle': (0, 60)}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def expected_rows(values, length_law=False):
    stretch, volume, packing, angle = (values[key] for key in DEFAULTS)
    factor = max(0, 1 - ((stretch - 1) / .5) ** 2) ** 2 if length_law else 1
    return {
        'Reference contractile area': f'{100 * packing:.2f} mm²',
        'Current projected area': f'{100 * packing * volume / stretch:.2f} mm²',
        'Nominal stress P': f'{300 * factor:.2f} kPa',
        'Cauchy fibre stress σ': f'{300 * factor * stretch / volume:.2f} kPa',
        'Axial force': f'{30 * packing * factor:.2f} N',
        'Tendon-directed component': f'{30 * packing * factor * math.cos(math.radians(angle)):.2f} N',
    }


def check_state(page, values=DEFAULTS, length_law=False):
    actual = {}
    for row in page.locator('#readout dl > div').all():
        actual[row.locator('dt').inner_text()] = row.locator('dd').inner_text()
    require(actual == expected_rows(values, length_law), f'Unexpected readout: {actual}')
    for key, value in values.items():
        require(float(page.locator('#' + key).input_value()) == value, 'Wrong input: ' + key)
        text = f'{int(value)}°' if key == 'angle' else f'{value:.2f}'
        require(page.locator('#' + key + '-value').inner_text() == text, 'Wrong output: ' + key)
    require(page.locator('#length-law').is_checked() == length_law, 'Wrong force–length toggle state')
    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal overflow')
    interpretation = page.locator('#interpretation').inner_text()
    require(('explicit force–length multiplier' in interpretation) == length_law, 'Stale interpretation')


def main(output):
    output = output.resolve()
    require(not output.is_relative_to(ROOT), 'Browser output must be outside checkout')
    require(not output.exists() or not any(output.iterdir()), 'Use a fresh browser output directory')
    output.mkdir(parents=True, exist_ok=True)
    receipt = {'status': 'running', 'checks': [], 'captures': [],
               'visual_acceptance': 'pending human inspection', 'no_anatomical_render_claim': True,
               'playwright_version': importlib.metadata.version('playwright'),
               'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(LAB.iterdir()) if p.is_file()}}

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path == '/favicon.ico':
                self.send_response(204)
                self.end_headers()
            else:
                super().do_GET()

    def capture(page, name):
        path = output / name
        page.screenshot(path=str(path), type='jpeg', quality=85, full_page=True)
        receipt['captures'].append({'file': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                    'format': 'jpeg', 'quality': 85})

    try:
        with socketserver.TCPServer(('127.0.0.1', 0), partial(Quiet, directory=str(LAB))) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            origin = f'http://127.0.0.1:{server.server_address[1]}'
            url = origin + '/index.html'
            try:
                with sync_playwright() as playwright:
                    # Use the browser installed by this pinned Playwright release.
                    browser = playwright.chromium.launch(headless=True)
                    receipt['browser'] = 'Playwright Chromium'
                    receipt['browser_version'] = browser.version
                    for width, height in [(1280, 1000), (393, 852)]:
                        context = browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=1)
                        errors = []

                        def local_only(route):
                            if urlsplit(route.request.url).netloc == urlsplit(origin).netloc:
                                route.continue_()
                            else:
                                errors.append('Unexpected remote request: ' + route.request.url)
                                route.abort()

                        context.route('**/*', local_only)
                        page = context.new_page()
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
                        page.on('requestfailed', lambda request: errors.append('Request failed: ' + request.url))
                        page.on('response', lambda response: errors.append(f'HTTP {response.status}: {response.url}')
                                if response.status >= 400 else None)
                        page.goto(url, wait_until='networkidle')
                        page.wait_for_selector('#readout dd')
                        check_state(page)
                        require('summed force 35.00 N' in page.locator('#composition').inner_text(), 'Missing parallel example')
                        capture(page, f'lab-{width}-default.jpg')
                        page.locator('#stretch').focus()
                        page.keyboard.press('ArrowRight')
                        values = {**DEFAULTS, 'stretch': .81}
                        check_state(page, values)
                        page.locator('#length-law').check()
                        check_state(page, values, True)
                        capture(page, f'lab-{width}-force-length.jpg')
                        page.locator('#length-law').uncheck()
                        check_state(page, values)
                        exercised = []
                        for control, (lower, upper) in BOUNDS.items():
                            for key, value in [('Home', lower), ('End', upper)]:
                                page.locator('#reset').click()
                                check_state(page)
                                page.locator('#' + control).focus()
                                page.keyboard.press(key)
                                check_state(page, {**DEFAULTS, control: value})
                                exercised.append(f'{control}:{key}')
                        # Reset must clear every edited field and the checked law, repeatedly.
                        for control in BOUNDS:
                            page.locator('#' + control).focus()
                            page.keyboard.press('End')
                        page.locator('#length-law').check()
                        for _ in range(2):
                            page.locator('#reset').click()
                            check_state(page)
                        for href in ('chapter.md', 'sources.json', 'README.md'):
                            # Markdown MIME types may display or download by host. Check
                            # the actual local anchor target and exact served source bytes.
                            link = page.locator(f'a[href="{href}"]')
                            require(link.count() == 1 and link.is_visible(), 'Missing local link: ' + href)
                            target = link.evaluate('(anchor) => anchor.href')
                            require(target == origin + '/' + href, 'Unexpected local target: ' + href)
                            response = page.request.get(target)
                            require(response.status == 200 and response.body() == (LAB / href).read_bytes(),
                                    'Broken or stale local link: ' + href)
                        require(not errors, f'Browser errors: {errors}')
                        receipt['checks'].append({'width': width, 'height': height,
                            'horizontal_overflow': False, 'range_keyboard_input': True,
                            'controls': exercised, 'force_length_toggle': True, 'repeated_reset': True,
                            'local_links': True, 'browser_errors': errors})
                        context.close()
                    context = browser.new_context(java_script_enabled=False, viewport={'width': 393, 'height': 852})
                    errors = []
                    context.route('**/*', local_only)
                    page = context.new_page()
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
                    page.on('requestfailed', lambda request: errors.append('Request failed: ' + request.url))
                    page.on('response', lambda response: errors.append(f'HTTP {response.status}: {response.url}')
                            if response.status >= 400 else None)
                    page.goto(url, wait_until='networkidle')
                    require(page.locator('noscript').is_visible(), 'Missing no-JavaScript explanation')
                    require('30 → 60 → 30 N' in page.locator('main').inner_text(), 'Missing static force example')
                    require(page.locator('#readout').inner_text() == '', 'Unexpected script execution')
                    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'No-JavaScript overflow')
                    capture(page, 'lab-393-no-javascript.jpg')
                    require(not errors, f'No-JavaScript browser errors: {errors}')
                    receipt['no_javascript_static_fallback'] = True
                    context.close()
                    browser.close()
            finally:
                server.shutdown()
                thread.join()
        receipt['status'] = 'passed'
    except Exception as error:
        receipt['status'] = 'failed'
        receipt['error'] = str(error)
        raise
    finally:
        (output / 'browser.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Desktop/mobile controls, links, reset and no-JavaScript checks passed; inspect captures separately.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    main(parser.parse_args().output)

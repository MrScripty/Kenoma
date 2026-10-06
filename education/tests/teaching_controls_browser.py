"""Actual generated controls + production bundle, without a full proof/book rebuild.

Can also run check(page, out) against the integrated book. Screenshots are real
Chromium renders; force-marker positions are measured from their canvas pixels.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from tempfile import TemporaryDirectory
from io import BytesIO
import argparse, hashlib, json, os, shutil, subprocess, sys
from math import tan, pi
from PIL import Image
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]

def state(lab):
    lab.locator('[data-action=copy]').click()
    return json.loads(lab.locator('.preset').input_value())

def marker_x(canvas, path):
    pixels = canvas.screenshot(path=str(path))
    im = Image.open(BytesIO(pixels)).convert('RGB')
    # Sample above the centreline to exclude the thin trajectory segment.
    xs = [x for x in range(im.width) if (lambda c: c[1] > c[0]+30 and c[2] > c[0]+15 and c[1] > 95)(im.getpixel((x, im.height//2-6)))]
    assert xs, 'No teal position marker found in actual canvas pixels'
    return (min(xs)+max(xs))/2-im.width/2

def check(page, out, case='all'):
    observed = {}
    if case in ['all', 'force']:
        lab = page.locator('#lab-force')
        lab.locator('[data-action=reset]').click()
        lab.locator('input[type=number][data-param=mass]').fill('0.5')
        lab.locator('input[type=number][data-param=force]').fill('8')
        lab.locator('[data-action=start]').click()
        expect(lab).to_have_attribute('data-scene-state', 'ready')
        rows = []
        for t in [1, 1.5, 2]:
            lab.locator('input[type=number][data-param=time]').fill(str(t))
            expect(lab.locator('.readout')).to_contain_text(f'{.5*16*t*t:.3f} m')
            rows.append({'time': t, 'positionM': .5*16*t*t,
                         'markerPixelX': marker_x(lab.locator('canvas'), out/f'force-{t}s.png'),
                         'readout': lab.locator('.readout').inner_text()})
        observed['force'] = rows
        (out/'force-observed.json').write_text(json.dumps(rows, indent=2)+'\n')
        assert rows[2]['markerPixelX'] > rows[1]['markerPixelX'] > rows[0]['markerPixelX'] > 0
        # Independent perspective projection: 300px canvas, 40° vertical FOV,
        # camera 6 display units from the origin; allow 2px for raster lighting.
        for row in rows:
            expected = 150/(6*tan(20*pi/180))*1.7*row['positionM']/32
            assert abs(row['markerPixelX']-expected) < 2
        assert all('9.412 m per grid interval' in r['readout'] for r in rows)
        lab.locator('input[type=number][data-param=force]').fill('-8')
        lab.locator('input[type=number][data-param=time]').fill('2')
        left = marker_x(lab.locator('canvas'), out/'force-negative.png')
        assert abs(left+rows[2]['markerPixelX']) < 2
        lab.locator('[data-action=reset]').click()
    if case in ['all', 'property']:
        lab = page.locator('[data-property=tapered]')
        lab.locator('[data-action=reset]').click()
        heights = lambda: lab.locator('.property-scene svg rect[height][x]').evaluate_all('(els)=>els.map(x=>Number(x.getAttribute("height")))')
        before, h1 = state(lab), heights()
        lab.locator('input[type=number][data-param=force]').fill('0.6')
        after, h2 = state(lab), heights()
        observed['property'] = {'before': before, 'after': after, 'heightsBefore': h1, 'heightsAfter': h2}
        (out/'property-observed.json').write_text(json.dumps(observed['property'], indent=2)+'\n')
        lab.screenshot(path=str(out/'property-double-force.png'))
        assert all(abs(b-2*a) < 1e-10 for a, b in zip(h1, h2))
        assert all(abs(b['strain']-2*a['strain']) < 1e-12 for a, b in zip(before['measurements']['samples'], after['measurements']['samples']))
        for key in ['activation', 'activeStress']:
            for control in lab.locator(f'[data-param={key}]').all(): expect(control).to_be_disabled()
        for control in lab.locator('[data-param=force]').all(): expect(control).to_be_enabled()
        lab.locator('select[data-param=mode]').select_option('active-fixed')
        for control in lab.locator('[data-param=force]').all(): expect(control).to_be_disabled()
        for key in ['activation', 'activeStress']:
            for control in lab.locator(f'[data-param={key}]').all(): expect(control).to_be_enabled()
        lab.locator('input[type=number][data-param=activation]').fill('0.5')
        active = state(lab)['measurements']
        lab.locator('input[type=number][data-param=activation]').fill('1')
        assert abs(state(lab)['measurements']['resultantN']-2*active['resultantN']) < 1e-12
        lab.locator('[data-action=reset]').click()
        for key, value in [('area', '.0001'), ('ratio', '.5'), ('modulus', '50000'), ('force', '1')]:
            lab.locator(f'input[type=number][data-param={key}]').fill(value)
        expect(lab.locator('.readout')).to_contain_text('Expanded beyond ±0.05')
        assert all(h <= 110 for h in heights())
        lab.locator('[data-action=reset]').click()
        assert heights() == h1
        expect(lab.locator('input[type=number][data-param=activation]')).to_be_disabled()
    if case in ['all', 'spatial']:
        lab = page.locator('#lab-spatial')
        lab.locator('[data-action=start]').click()
        expect(lab).to_have_attribute('data-scene-state', 'ready')
        lab.locator('[data-action=compression]').click()
        before = state(lab)
        active_pixels = lab.locator('canvas').screenshot()
        lab.screenshot(path=str(out/'spatial-active-on.png'))
        observed['spatial'] = {'fixture': before, 'ablations': {}}
        for key, value in [('skin', 'off'), ('boneContact', 'off'), ('volumeK', '2500'), ('activeShape', 'off')]:
            lab.locator('[data-action=reset]').click()
            lab.locator('[data-action=compression]').click()
            lab.locator(f'select[data-param={key}]').select_option(value)
            current = state(lab)
            observed['spatial']['ablations'][key] = current
            (out/'spatial-observed.json').write_text(json.dumps(observed['spatial'], indent=2)+'\n')
            assert current['state'] == before['state'] and current['step'] == before['step'], key
            assert current['diagnostics']['activation'] == .6
            assert current['diagnostics']['minJ'] > .01
            if key == 'skin': assert current['diagnostics']['energyJ']['skin'] == current['diagnostics']['energyJ']['fascia'] == 0
            if key == 'boneContact':
                assert current['diagnostics']['contactNormalSumN'] == 0
                assert current['diagnostics']['penetrationM'] > 10*before['diagnostics']['penetrationM']
            if key == 'activeShape':
                assert current['diagnostics']['energyJ']['active'] == 0
                assert current['diagnostics']['hingeFiberM'] == before['diagnostics']['hingeFiberM']
                assert abs(current['diagnostics']['spatialFiberArcM']-before['diagnostics']['spatialFiberArcM']) > .001
                lab.screenshot(path=str(out/'spatial-active-off.png'))
                assert lab.locator('canvas').screenshot() != active_pixels, 'Active-shape ablation must change the rendered geometry'
                lab.locator('select[data-param=activeShape]').select_option('on')
                assert state(lab)['diagnostics'] == before['diagnostics']
        lab.locator('[data-action=step]').click()
        evolved = state(lab)
        lab.locator('select[data-param=sweeps]').select_option('80')
        assert state(lab)['state'] == evolved['state']
        with page.expect_download() as info: lab.locator('[data-action=export]').click()
        info.value.save_as(str(out/'spatial-current-segment.json'))
        trace = json.loads((out/'spatial-current-segment.json').read_text())
        assert len(trace['trace']) == 1 and trace['trace'][0]['step'] == evolved['step']
        assert trace['trace'][0]['time'] == evolved['state']['time']
        assert trace['trace'][0]['hingeWorkJ'] == evolved['state']['work']
        lab.locator('[data-action=reset]').click()
        assert state(lab)['state']['a'] == 0
    if case in ['all', 'elbow']:
        lab = page.locator('#lab-elbow')
        lab.locator('[data-action=reset]').click()
        lab.locator('input[type=number][data-param=angle]').fill('0')
        lab.locator('input[type=number][data-param=excitation]').fill('1')
        lab.evaluate('(lab)=>{for(let i=0;i<200;i++)lab.querySelector("[data-action=step]").click()}')
        current = state(lab)
        observed['elbow'] = current
        assert current['state']['q'] == 0 and not current['state']['halted'] and current['state']['a'] > .999
        expect(lab.locator('.readout')).to_contain_text('Dead centre: zero moment arm')
        lab.locator('[data-action=start]').click()
        expect(lab).to_have_attribute('data-scene-state', 'ready')
        lab.screenshot(path=str(out/'elbow-dead-centre.png'))
        lab.locator('[data-action=reset]').click()
    return observed

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('/tmp/kenoma-teaching-controls'))
    parser.add_argument('--case', choices=['all', 'force', 'property', 'spatial', 'elbow'], default='all')
    args = parser.parse_args(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT/'tools'))
    from build import lab_block
    from property_labs import block
    receipt = {'scope': 'Generated production lab HTML + production app bundle; not a full book/proof build',
               'source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in list((ROOT/'web').glob('*.mjs'))+[ROOT/'tools/build.py', ROOT/'tools/property_labs.py', Path(__file__).resolve()]},
               'case': args.case, 'status': 'FAIL'}
    with TemporaryDirectory(prefix='kenoma-controls-') as temp:
        site = Path(temp)
        shutil.copy(ROOT/'web/style.css', site/'style.css')
        html = '<!doctype html><html lang="en"><meta charset="utf-8"><title>Teaching control qualification</title><link rel="stylesheet" href="style.css"><body><main>'
        html += ''.join(lab_block(key, True) for key in ['force', 'elbow', 'spatial'])
        html += block('tapered', True)+'</main><script type="module" src="app.js"></script></body></html>'
        (site/'index.html').write_text(html)
        subprocess.run([str(ROOT/'node_modules/.bin/esbuild'), str(ROOT/'web/app.mjs'), '--bundle', '--minify', '--format=esm', '--target=es2022', f'--outfile={site/"app.js"}', '--legal-comments=external'], check=True)
        receipt['html_sha256'] = hashlib.sha256((site/'index.html').read_bytes()).hexdigest()
        receipt['bundle_sha256'] = hashlib.sha256((site/'app.js').read_bytes()).hexdigest()
        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(site)))
        Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
                receipt['browser_version'] = browser.version
                page = browser.new_page(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
                errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{server.server_port}/index.html', wait_until='networkidle')
                receipt['observed'] = check(page, out, args.case)
                assert not errors, errors
                receipt['javascript_errors'] = errors
                receipt['status'] = 'PASS'
                browser.close()
        finally:
            server.shutdown(); server.server_close()
            (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(f'PASS {args.case}: real controls/render evidence at {out}')

if __name__ == '__main__': main()

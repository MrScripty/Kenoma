"""Standalone rational-oracle and actual-browser checks; no main-book registration."""
from pathlib import Path
from fractions import Fraction as F
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from itertools import product
from threading import Thread
import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
LAB = Path(__file__).with_name('pressure-projection-lab.html')
GUIDE = Path(__file__).with_name('pressure-projection-proof-guide.md')
WEIGHTS = (F(1), F(3), F(2), F(2))


def oracle(field, scale, level):
    """Closed forms for these three four-sample spaces, not the browser group loop."""
    g = tuple(F(str(x)) for x in field)
    K = F(scale)
    if level == 1:
        a = (g[0] + 3*g[1] + 2*g[2] + 2*g[3])/8
        projected = (a, a, a, a)
    elif level == 2:
        a, b = (g[0] + 3*g[1])/4, (g[2] + g[3])/2
        projected = (a, a, b, b)
    elif level == 4:
        projected = g
    else:
        raise ValueError(level)
    residual = tuple(x-y for x, y in zip(g, projected))
    p = tuple(K*x for x in projected)
    full = K/2*sum(w*x*x for w, x in zip(WEIGHTS, g))
    condensed = K/2*sum(w*x*x for w, x in zip(WEIGHTS, projected))
    unresolved = K/2*sum(w*x*x for w, x in zip(WEIGHTS, residual))
    objective = sum(w*x*y for w, x, y in zip(WEIGHTS, p, g))-sum(w*x*x for w, x in zip(WEIGHTS, p))/(2*K)
    assert full-condensed == unresolved and objective == condensed
    return dict(projected=projected, residual=residual, pStar=p, full=full,
                condensed=condensed, gap=full-condensed, residualEnergy=unresolved, objective=objective)


def close(actual, expected):
    assert math.isclose(actual, float(expected), rel_tol=1e-12, abs_tol=1e-12), (actual, str(expected))


def check_state(state, expected):
    for name, value in expected.items():
        if isinstance(value, tuple):
            assert len(state[name]) == len(value)
            for actual, reference in zip(state[name], value):
                close(actual, reference)
        else:
            close(state[name], value)
    close(state['identityDefect'], 0)
    for value in state['weightedResiduals']:
        close(value, 0)


def viewport_diagnostics(page, output, case):
    """Retain actionable bounds and a screenshot before a viewport assertion."""
    result = page.evaluate('''()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,
        documentClientWidth:document.documentElement.clientWidth,bodyFont:getComputedStyle(document.body).fontFamily,
        state:PressureProjectionLab.state(),elements:[...document.querySelectorAll('body *')].filter(e=>{
            const r=e.getBoundingClientRect();return r.width&&(r.right>innerWidth||r.left<0)
        }).map(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {
            tag:e.tagName,id:e.id,classes:e.getAttribute('class'),text:(e.innerText||'').slice(0,100),
            bounds:{left:r.left,right:r.right,width:r.width},clientWidth:e.clientWidth,scrollWidth:e.scrollWidth,
            minWidth:s.minWidth,overflowX:s.overflowX,gridTemplateColumns:s.gridTemplateColumns,
            tableScrollAncestor:!!e.closest('.table-scroll')
        }}),tableScroll:[...document.querySelectorAll('.table-scroll')].map(e=>({
            clientWidth:e.clientWidth,scrollWidth:e.scrollWidth,scrollLeft:e.scrollLeft}))})''')
    result['case'] = case
    result['browser'] = page.context.browser.version
    if result['documentWidth'] > result['width']:
        prefix = output/f'viewport-failure-{case}'
        prefix.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
        page.screenshot(path=str(prefix.with_suffix('.png')), full_page=True)
    return result


def check(output):
    output.mkdir(parents=True, exist_ok=True)
    receipt = output/'receipt.json'
    receipt.unlink(missing_ok=True)
    source_paths = [str(path.relative_to(ROOT)) for path in (LAB, GUIDE, Path(__file__).resolve())]
    if subprocess.check_output(['git','status','--porcelain','--',*source_paths],cwd=ROOT,text=True).strip():
        raise RuntimeError('Commit standalone lab sources before generating source-bound review evidence')
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/standalone/{LAB.name}'
    checks, errors, external = [], [], []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
            browser_version = browser.version
            page = browser.new_page(viewport={'width':1280, 'height':1100}, device_scale_factor=1)
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: external.append(request.url) if not request.url.startswith(f'http://127.0.0.1:{server.server_port}/') else None)
            page.goto(url, wait_until='networkidle')
            def state():
                current = page.evaluate('PressureProjectionLab.state()')
                for name in ('full', 'condensed', 'gap'):
                    shown = float(page.locator('#'+name).inner_text().replace(',', ''))
                    assert abs(shown-current[name]) <= 5.1e-6, (name, shown, current[name])
                rows = page.locator('#samples-table tbody tr').all()
                assert len(rows) == 4
                for i, row in enumerate(rows):
                    shown = [float(value.replace(',', '')) for value in row.locator('td').all_text_contents()]
                    expected = [i+1,current['weights'][i],current['g'][i],current['projected'][i],current['residual'][i],current['pStar'][i]]
                    for value, reference in zip(shown, expected):
                        close(value, reference)
                return current
            default = [-.75, .25, -.25, .75]
            check_state(state(), oracle(default, 8, 1))
            expect(page.locator('.scope')).to_contain_text('no body deformation, equilibrium solve, or incompressibility simulation')
            assert page.locator('svg[role=img]').count() == 3
            for graphic in page.locator('svg[role=img]').all():
                assert graphic.get_attribute('aria-label')
            expect(page.locator('#calculation')).to_contain_text('Residual: 4 × 1.875 = 7.5')
            # 625 signed/zero half-step fields, all spaces, and three scales.
            fields = [list(field) for field in product((-1, -.5, 0, .5, 1), repeat=4)]
            results = page.evaluate('''fields => fields.map(g => [1,8,16].map(K => [1,2,4].map(level => PressureProjectionModel.compute(g,K,level))))''', fields)
            oracle_count = 0
            for field, scales in zip(fields, results):
                for K, levels in zip((1,8,16), scales):
                    last = F(0)
                    for level, actual in zip((1,2,4), levels):
                        reference = oracle(field, K, level)
                        check_state(actual, reference)
                        assert reference['condensed'] >= last
                        last = reference['condensed']
                        oracle_count += 1
            checks.append(f'{oracle_count} browser model states checked against independent Fraction closed forms; identity, objective, orthogonality and fixed-field monotonicity')
            assert page.evaluate('''() => {for (const args of [[[0,0,0,0],0,1],[[0,0,0,0],8,3],[[NaN,0,0,0],8,1]]) {try {PressureProjectionModel.compute(...args);return false;} catch(e) {if (!(e instanceof RangeError)) return false;}}return true;}''')
            checks.append('Model rejects nonpositive K, unknown space and nonfinite field')
            initial = state()
            for level in (2,4,1):
                page.locator(f'input[name=space][value="{level}"]').check()
                assert state()['g'] == initial['g']
                check_state(state(), oracle(default, 8, level))
                rows = page.locator('#refinement tbody tr').all_text_contents()
                assert '0.5' in rows[0] and '7.5' in rows[0]
                assert '1' in rows[1] and '7' in rows[1]
                assert '8' in rows[2] and '0' in rows[2]
                if level==4:
                    expect(page.locator('#recovery')).to_contain_text('already represents this entire field')
            page.locator('#scale').fill('16')
            assert state()['g'] == initial['g'] and state()['projected'] == initial['projected']
            check_state(state(), oracle(default, 16, 1))
            page.locator('#preset').select_option('paired')
            page.locator('input[name=space][value="2"]').check()
            check_state(state(), oracle([-.5,-.5,.25,.25], 16, 2))
            assert state()['gap'] == 0
            page.locator('#preset').select_option('constant')
            page.locator('input[name=space][value="1"]').check()
            check_state(state(), oracle([.25]*4, 16, 1))
            assert state()['gap'] == 0
            page.locator('#reset').click()
            page.locator('#g0').fill('0.5')
            custom = [.5,.25,-.25,.75]
            check_state(state(), oracle(custom, 8, 1))
            assert page.locator('#preset').input_value() == 'custom'
            before = state()
            page.locator('#g1').fill('')
            assert state() == before
            expect(page.locator('#g1')).to_have_attribute('aria-invalid', 'true')
            expect(page.locator('#status')).to_contain_text('last valid case stays displayed')
            page.locator('#g1').fill('1.25')
            assert state() == before
            page.locator('#g1').fill('0.1')
            assert state() == before
            page.locator('#reset').click()
            check_state(state(), oracle(default, 8, 1))
            assert page.locator('[aria-invalid=true]').count() == 0
            checks.append('Actual displayed energies and sample table match the model; preset/sample/K/space controls: same field under refinement, known zero-gap cases, custom field, invalid-input rollback and complete Reset')
            # Keyboard operation of the actual radio control.
            page.locator('input[name=space][value="1"]').focus()
            page.keyboard.press('ArrowRight')
            assert state()['level'] == 2
            page.locator('#reset').click()
            page.screenshot(path=str(output/'desktop-coarse.png'), full_page=True)
            page.locator('input[name=space][value="2"]').check()
            page.screenshot(path=str(output/'desktop-paired.png'), full_page=True)
            page.locator('input[name=space][value="4"]').check()
            page.screenshot(path=str(output/'desktop-full.png'), full_page=True)
            viewport_cases = []
            for width in (390,320,360,414,768):
                page.set_viewport_size({'width':width, 'height':844})
                viewport_cases.append(viewport_diagnostics(page, output, f'native-{width}'))
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
                assert page.locator('.controls').evaluate('(e)=>e.scrollWidth<=e.clientWidth'), width
                page.locator('#reset').click()
                page.locator('input[name=space][value="2"]').check()
                check_state(state(), oracle(default, 8, 2))
                page.locator('#reset').click()
                page.screenshot(path=str(output/f'mobile-{width}.png'), full_page=True)
            (output/'viewport-cases.json').write_text(json.dumps(viewport_cases, indent=2)+'\n')
            checks.append('Desktop 1280px and mobile 390/320px: usable controls, accessible chart names, keyboard radio refinement and no document overflow')
            page.set_viewport_size({'width':1280,'height':1100})
            page.emulate_media(media='print')
            expect(page.locator('.controls')).to_be_hidden()
            expect(page.locator('#samples-table')).to_be_visible()
            expect(page.locator('.metrics')).to_be_visible()
            page.pdf(path=str(output/'fixed-field-reference.pdf'), format='A4', print_background=True)
            page.emulate_media(media='screen')
            expect(page.locator('.controls')).to_be_visible()
            assert not external, external
            context = browser.new_context(java_script_enabled=False, viewport={'width':390,'height':844})
            static = context.new_page()
            static.goto(url, wait_until='networkidle')
            expect(static.locator('#full')).to_have_text('8')
            expect(static.locator('#condensed')).to_have_text('0.5')
            expect(static.locator('#gap')).to_have_text('7.5')
            expect(static.locator('#samples-table')).to_contain_text('−0.875')
            expect(static.locator('#preset')).to_be_disabled()
            expect(static.locator('noscript p')).to_contain_text('default reference case remains')
            assert static.evaluate('document.documentElement.scrollWidth <= innerWidth')
            context.close()
            checks.append('Print/PDF retains current numbers and hides controls; no-JavaScript default exact reference remains readable; no external asset requests')
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    theorem_names = __import__('re').findall(r'^theorem\s+(\w+)\b', (ROOT/'proofs/MixedLogVolume.lean').read_text(), __import__('re').M)
    assert len(theorem_names) == 27 and all('`'+name+'`' in GUIDE.read_text() for name in theorem_names)
    checks.append('Proof guide maps all 27 frozen Lean declarations and retains the fixed-state assumptions')
    hashes = {str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in (LAB,GUIDE,Path(__file__).resolve())}
    evidence = {path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(output.iterdir()) if path.is_file() and path.name!='receipt.json'}
    payload = {'schema':1,'result':'PASS_STANDALONE_FIXED_FIELD_PRESSURE_PROJECTION_LAB','source_commit':revision,'source_files_match_commit':True,'source_sha256':hashes,'browser':browser_version,'exact_reference_states':oracle_count,'tolerance':{'absolute':1e-12,'relative':1e-12,'display_rounding_absolute':5.1e-6},'checks':checks,'javascript_errors':errors,'external_requests':external,'evidence_sha256':evidence,'limits':'Sampled implementation tests, not floating-point refinement, equilibrium, incompressibility, continuum or anatomical certification.'}
    receipt.write_text(json.dumps(payload,indent=2)+'\n')
    print(payload['result'])
    print('\n'.join(checks))
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'.tools/pressure-projection-lab-review')
    check(parser.parse_args().output.resolve())

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
from math import tan, pi, exp, hypot, sqrt, cos
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

def field_pixels(canvas, path):
    im = Image.open(BytesIO(canvas.screenshot(path=str(path)))).convert('RGB')
    # Long interior colour runs exclude antialiasing and thin reference edges.
    colours, previous, length = set(), None, 0
    for x in range(im.width):
        r, g, b = im.getpixel((x, im.height//2))
        value = (r//18, g//18, b//18) if b > r+20 and b > g+20 else None
        if value == previous: length += 1
        else:
            if previous is not None and length >= 12: colours.add(previous)
            previous, length = value, 1
    if previous is not None and length >= 12: colours.add(previous)
    red = sum(r > 180 and g < 160 and b < 160 for r, g, b in im.getdata())
    return {'interiorColourBands': len(colours), 'highFieldPixels': red}

def check(page, out, case='all'):
    observed = {}
    if case in ['all', 'energy']:
        lab = page.locator('#lab-energy')
        energy_runs = []
        for h in [.005, .01, .02, .05, .1]:
            for method in ['explicit', 'symplectic', 'verlet']:
                lab.locator('[data-action=reset]').click()
                lab.locator('select[data-param=dt]').select_option(str(h))
                lab.locator('select[data-param=method]').select_option(method)
                initial = state(lab)
                assert initial['step'] == 0 and initial['run']['sampleCount'] == 1
                lab.locator('[data-action=run]').click()
                expect(lab.locator('.announce')).to_contain_text('Completed 12 simulated seconds', timeout=30000)
                current = state(lab)
                count = round(12/h)
                assert current['step'] == current['run']['stepLimit'] == count
                assert current['run']['timeS'] == 12 and current['run']['sampleCount'] == count+1
                expect(lab.locator('.readout')).to_contain_text(f'{count} / {count}')
                expect(lab.locator('.readout')).to_contain_text('12.000 / 12 s')
                points = lab.locator('.trace').get_attribute('points').split()
                assert len(points) == count+1 and abs(float(points[-1].split(',')[0])-540) < 1e-10
                with page.expect_download() as info: lab.locator('[data-action=export]').click()
                filename = f'energy-{method}-{h}-trace.json'
                info.value.save_as(str(out/filename))
                trace = json.loads((out/filename).read_text())
                assert trace['model'] == 'ideal-linear-spring-v1' and abs(trace['initialEnergy']-.8) < 1e-15
                assert trace['run'] == current['run'] and len(trace['trace']) == count+1
                # Independent Python recurrences check every physics sample; no JS reference call.
                x, v, e0, maximum = .2, 0., .8, 0.
                for i, row in enumerate(trace['trace']):
                    if i:
                        acceleration = -40*x
                        if method == 'explicit': x, v = x+h*v, v+h*acceleration
                        elif method == 'symplectic':
                            v += h*acceleration
                            x += h*v
                        else:
                            new_x = x+h*v+.5*h*h*acceleration
                            v += .5*h*(acceleration-40*new_x)
                            x = new_x
                    energy = .5*v*v+20*x*x
                    assert row['step'] == i and abs(row['time']-i*h) < 1e-12
                    for key, expected in [('x', x), ('v', v), ('energy', energy)]:
                        assert abs(row[key]-expected) <= 1e-10*max(1, abs(expected)), (method, h, i, key)
                    maximum = max(maximum, abs(energy/e0-1))
                assert abs(current['run']['maxAbsoluteRelativeEnergyDeviation']-maximum) <= 1e-10*max(1, maximum)
                error = abs(x-.2*cos(sqrt(40)*12))
                assert abs(current['run']['absolutePositionErrorM']-error) <= 1e-10*max(1, error)
                before = current['state']
                lab.locator('[data-action=step]').click()
                assert state(lab)['state'] == before
                if h == .05 or (h == .005 and method == 'verlet'):
                    lab.screenshot(path=str(out/f'energy-{method}-{h}-completed.png'))
                energy_runs.append({'method': method, 'h': h, 'run': current['run'], 'finalState': current['state'], 'trace': filename})
        # A genuine mid-run user pause leaves state unchanged; resume reaches the endpoint.
        lab.locator('[data-action=reset]').click()
        lab.locator('select[data-param=dt]').select_option('0.005')
        lab.locator('[data-action=run]').click()
        expect(lab.locator('[data-action=run]')).to_have_text('Pause run')
        lab.locator('[data-action=run]').click()
        paused = state(lab)
        assert 0 < paused['step'] < 2400
        page.wait_for_timeout(150)
        assert state(lab)['step'] == paused['step']
        lab.locator('[data-action=run]').click()
        expect(lab.locator('.announce')).to_contain_text('Completed 12 simulated seconds', timeout=30000)
        assert state(lab)['step'] == 2400
        # Normal Play is paced by fixed h, then can pause and single-step at the same state.
        lab.locator('[data-action=reset]').click()
        lab.locator('select[data-param=dt]').select_option('0.005')
        lab.locator('[data-action=play]').click()
        page.wait_for_timeout(300)
        lab.locator('[data-action=play]').click()
        paced = state(lab)
        assert 0 < paced['run']['timeS'] < 2
        page.wait_for_timeout(150)
        assert state(lab)['step'] == paced['step']
        lab.locator('[data-action=step]').click()
        assert state(lab)['step'] == paced['step']+1
        lab.locator('select[data-param=dt]').select_option('0.01')
        assert state(lab)['step'] == 0 and state(lab)['run']['stepLimit'] == 1200
        lab.locator('[data-action=reset]').click()
        reset = state(lab)
        assert reset['step'] == 0 and reset['run']['stepLimit'] == 600 and reset['parameters']['dt'] == .02
        observed['energy'] = {'runs': energy_runs, 'paused': paused, 'paced': paced, 'reset': reset}
    if case in ['all', 'alignment']:
        lab = page.locator('[data-property=deformation]')
        expect(lab.locator('label[for=property-deformation-sy]')).to_have_text('Y diagonal coefficient sy')
        for key, value in [('sy', '.8'), ('shear', '.6')]:
            lab.locator(f'input[type=number][data-param={key}]').fill(value)
        imposed = state(lab)
        assert abs(imposed['measurements']['materialLineStretches'][1]-1) < 1e-12
        expect(lab.locator('.readout')).to_contain_text('Y material-line stretch')
        lab.screenshot(path=str(out/'property-shear-line-stretch.png'))
        observed['deformation'] = imposed
        lab = page.locator('[data-property=tapered]')
        expect(lab.locator('label[for=property-tapered-area]')).to_have_text('Reference area A1 at s=0 (m²)')
        lab.locator('input[type=number][data-param=ratio]').fill('.5')
        reversed_taper = state(lab)
        measurements = reversed_taper['measurements']
        assert measurements['narrowAreaM2'] == reversed_taper['parameters']['area']*.5
        assert measurements['endpointStrains'][1] > measurements['endpointStrains'][0]
        expect(lab.locator('.readout')).to_contain_text('Narrow area from geometry')
        lab.screenshot(path=str(out/'property-reversed-taper.png'))
        observed['reversedTaper'] = reversed_taper
        # Same actual controls/time/input compare earlier law with rigid series limit.
        forces = []
        for kind in ['elbow', 'series']:
            lab = page.locator('#lab-'+kind)
            lab.locator('[data-action=reset]').click()
            lab.locator('select[data-param=mode]').select_option('prescribed')
            lab.locator('input[type=number][data-param=angle]').fill('90')
            if kind == 'series':
                lab.locator('select[data-param=tendon]').select_option('rigid')
                lab.locator('select[data-param=contact]').select_option('off')
            lab.evaluate('(lab)=>{for(let i=0;i<60;i++)lab.querySelector("[data-action=step]").click()}')
            current = state(lab)
            with page.expect_download() as info: lab.locator('[data-action=export]').click()
            info.value.save_as(str(out/f'{kind}-force-length-trace.json'))
            trace = json.loads((out/f'{kind}-force-length-trace.json').read_text())
            row, p = trace['trace'][-1], current['parameters']
            fiber = hypot(p['origin'], p['insertion'])-p['tendonLength']
            expected = p['maxForce']*current['state']['a']*exp(-((fiber/p['optimalFiber']-1)/p['width'])**2)
            assert abs(row['active']-expected) < 1e-8
            assert row['active'] < p['maxForce']*current['state']['a']-40
            forces.append(row['active'])
            lab.screenshot(path=str(out/f'{kind}-rigid-force-length.png'))
            observed[kind+'RigidLimit'] = {'current': current, 'row': row}
        assert abs(forces[0]-forces[1]) < 1e-8
        lab = page.locator('#lab-series')
        lab.locator('select[data-param=tendon]').select_option('compliant')
        lab.evaluate('(lab)=>{for(let i=0;i<60;i++)lab.querySelector("[data-action=step]").click()}')
        with page.expect_download() as info: lab.locator('[data-action=export]').click()
        info.value.save_as(str(out/'series-compliant-force-length-trace.json'))
        row = json.loads((out/'series-compliant-force-length-trace.json').read_text())['trace'][-1]
        assert row['fiber'] < fiber and row['tendonEnergy'] > 0 and row['active'] < forces[1]
        assert abs(row['forceResidual']) < 1e-8 and abs(row['balanceResidual']) < 1e-5
        lab.screenshot(path=str(out/'series-compliant-force-length.png'))
        observed['seriesCompliant'] = row
        # Actual Lab6 fields, common scales, fixed-node forces and retained assembly.
        lab = page.locator('#lab-continuum')
        lab.locator('[data-action=start]').click()
        expect(lab).to_have_attribute('data-scene-state', 'ready')
        lab.locator('select[data-param=case]').select_option('affine')
        lab.locator('select[data-param=comparison]').select_option('static')
        affine = state(lab)
        assert affine['diagnostics']['colour']['max'] == 4000
        assert all(abs(v-1600) < 1e-6 for v in sum(affine['diagnostics']['colour']['fields'], []))
        assert abs(affine['diagnostics']['referenceReactionN'][0]+.96) < 1e-8
        expect(lab.locator('.readout')).to_contain_text('force ON block xyz')
        lab.screenshot(path=str(out/'continuum-affine-stress-reaction.png'))
        lab.locator('select[data-param=case]').select_option('quadratic')
        lab.screenshot(path=str(out/'continuum-quadratic-stress.png'))
        stress_pixels = field_pixels(lab.locator('canvas'), out/'continuum-stress-canvas.png')
        assert stress_pixels['interiorColourBands'] >= 3, 'Stress must vary by element in actual canvas pixels'
        lab.locator('select[data-param=comparison]').select_option('implicit')
        lab.locator('select[data-param=colorBy]').select_option('error')
        lab.locator('select[data-param=h]').select_option('0.002')
        lab.locator('select[data-param=sweeps]').select_option('1')
        coarse = state(lab)
        lab.screenshot(path=str(out/'continuum-coarse-error.png'))
        coarse_pixels = field_pixels(lab.locator('canvas'), out/'continuum-coarse-canvas.png')
        lab.locator('select[data-param=sweeps]').select_option('100')
        refined = state(lab)
        assert coarse['diagnostics']['colour']['max'] == refined['diagnostics']['colour']['max'] == .0005
        assert refined['diagnostics']['colour']['observedMax'] < coarse['diagnostics']['colour']['observedMax']/10
        assert coarse['diagnostics']['colour']['fields'][0] == [0]*len(coarse['diagnostics']['colour']['fields'][0])
        assert refined['diagnostics']['assemblyCount'] == coarse['diagnostics']['assemblyCount']
        lab.screenshot(path=str(out/'continuum-refined-error.png'))
        refined_pixels = field_pixels(lab.locator('canvas'), out/'continuum-refined-canvas.png')
        assert coarse_pixels['highFieldPixels'] > refined_pixels['highFieldPixels']+50
        lab.locator('select[data-param=magnification]').select_option('100')
        assert state(lab)['diagnostics']['colour'] == refined['diagnostics']['colour']
        observed['continuum'] = {'affine': affine, 'coarse': coarse, 'refined': refined,
                                'pixels': {'stress': stress_pixels, 'coarse': coarse_pixels, 'refined': refined_pixels}}
    if case in ['all', 'workflows']:
        for kind in ['elbow', 'series', 'spatial']:
            lab = page.locator('#lab-'+kind)
            lab.locator('[data-action=reset]').click()
            for key, value in [('load', '8'), ('angle', '45')]:
                lab.locator(f'input[type=number][data-param={key}]').fill(value)
            lab.locator('select[data-param=dt]').select_option('0.01')
            lab.locator('select[data-param=mode]').select_option('prescribed')
            lab.locator('input[type=number][data-param=excitation]').fill('.35')
            if kind == 'spatial':
                lab.locator('select[data-param=sweeps]').select_option('80')
                lab.locator('select[data-param=skin]').select_option('off')
                lab.locator('select[data-param=activeShape]').select_option('off')
            lab.evaluate('(lab)=>{for(let i=0;i<40;i++)lab.querySelector("[data-action=step]").click()}')
            expect(lab).to_have_attribute('data-scene-state', 'ready')
            expect(lab).to_have_attribute('data-run-display', 'live')
            before = state(lab)
            lab.evaluate('(lab)=>{lab.querySelector("[data-action=pulse]").click();lab.querySelector("[data-action=play]").click();}')
            scheduled = state(lab)
            assert scheduled['parameters'] == before['parameters']
            assert scheduled['state'] == before['state'] and scheduled['step'] == before['step']
            assert abs(scheduled['pulse']['releaseTime']-before['state']['time']-.3) < 1e-12
            lab.evaluate('(lab)=>{for(let i=0;i<30;i++)lab.querySelector("[data-action=step]").click()}')
            boundary = state(lab)
            assert boundary['parameters']['excitation'] == .35
            lab.locator('[data-action=step]').click()
            released = state(lab)
            assert released['parameters']['excitation'] == 0
            assert released['pulse'] is None
            assert 0 < released['state']['a'] < boundary['state']['a']
            assert released['state']['q'] == before['state']['q'] and released['state']['w'] == 0
            if kind == 'series': expect(lab.locator('.readout')).to_contain_text('Lengthening')
            lab.screenshot(path=str(out/f'{kind}-current-pulse-release.png'))
            observed[kind+'Pulse'] = {'before': before, 'scheduled': scheduled, 'boundary': boundary, 'released': released}
            lab.locator('[data-action=reset]').click()
            reset = state(lab)
            assert reset['parameters']['load'] == 5 and reset['parameters']['dt'] == .005
            assert reset['state']['a'] == 0 and reset['state']['time'] == 0
        # Step before Start must produce an actual moving canvas.
        lab = page.locator('#lab-force')
        # A fresh page ensures no previously started renderer masks the original path.
        page.reload(wait_until='networkidle')
        expect(lab).to_have_attribute('data-scene-state', 'idle')
        lab.locator('[data-action=step]').click()
        expect(lab).to_have_attribute('data-scene-state', 'ready')
        expect(lab.locator('canvas')).to_be_visible()
        first = marker_x(lab.locator('canvas'), out/'step-first-live.png')
        lab.evaluate('(lab)=>{for(let i=0;i<9;i++)lab.querySelector("[data-action=step]").click()}')
        later = marker_x(lab.locator('canvas'), out/'step-later-live.png')
        assert later > first+5
        observed['stepLive'] = {'firstMarkerX': first, 'laterMarkerX': later, 'state': state(lab)}
        # Inject unavailable WebGL in a fresh page; qualify the explicit fallback.
        failed = page.context.new_page()
        failed.add_init_script('''const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return type.includes('webgl')?null:original.call(this,type,...args);};''')
        failed.goto(page.url, wait_until='networkidle')
        for kind in ['force', 'energy', 'elbow', 'series', 'spatial']:
            lab = failed.locator('#lab-'+kind)
            lab.locator('[data-action=step]').click()
            expect(lab).to_have_attribute('data-scene-state', 'error')
            expect(lab).to_have_attribute('data-run-display', 'numerical-only')
            expect(lab.locator('.scene-notice')).to_contain_text('static reference diagram does not move')
            expect(lab.locator('.static-figure')).to_be_visible()
            assert lab.locator('canvas').count() == 0
            current = state(lab)
            assert current['step'] == 1
            if kind in ['elbow', 'series', 'spatial']: assert current['state']['time'] > 0
            lab.locator('[data-action=step]').click()
            assert state(lab)['step'] == 2
        failed.locator('#lab-series').screenshot(path=str(out/'numerical-only-series.png'))
        failed.close()
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
    parser.add_argument('--case', choices=['all', 'force', 'property', 'spatial', 'elbow', 'workflows', 'alignment', 'energy'], default='all')
    args = parser.parse_args(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT/'tools'))
    from build import lab_block
    from property_labs import block
    from figures import generate as generate_figures
    from spatial_figures import generate as generate_advanced_figures
    receipt = {'scope': 'Generated production lab HTML + production app bundle; not a full book/proof build',
               'source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in list((ROOT/'web').glob('*.mjs'))+[ROOT/'tools/build.py', ROOT/'tools/property_labs.py', ROOT/'tools/property-experiment.mjs', ROOT/'tools/figures.py', ROOT/'tools/spatial_figures.py', ROOT/'tools/spatial-experiment.mjs', ROOT/'contributions/continuum_reference/continuum.mjs', ROOT/'contributions/continuum_reference/data/example.json', Path(__file__).resolve()]},
               'case': args.case, 'status': 'FAIL'}
    with TemporaryDirectory(prefix='kenoma-controls-') as temp:
        site = Path(temp)
        generate_figures(site/'assets')
        subprocess.check_output(['node', str(ROOT/'tools/property-experiment.mjs'), str(site/'assets')], text=True)
        spatial = json.loads(subprocess.check_output(['node', str(ROOT/'tools/spatial-experiment.mjs')], text=True))
        generate_advanced_figures(site/'assets', spatial)
        shutil.copy(ROOT/'web/style.css', site/'style.css')
        html = '<!doctype html><html lang="en"><meta charset="utf-8"><title>Teaching control qualification</title><link rel="stylesheet" href="style.css"><body><main>'
        html += ''.join(lab_block(key, True) for key in ['force', 'energy', 'elbow', 'series', 'spatial', 'continuum'])
        html += block('deformation', True)+block('tapered', True)+'</main><script type="module" src="app.js"></script></body></html>'
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
                context = browser.new_context(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
                page = context.new_page()
                errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{server.server_port}/index.html', wait_until='networkidle')
                receipt['observed'] = check(page, out, args.case)
                if args.case in ['all', 'energy']:
                    fallback = context.new_page()
                    fallback.on('pageerror', lambda e: errors.append(str(e)))
                    fallback.add_init_script("""const original=HTMLCanvasElement.prototype.getContext;
                        HTMLCanvasElement.prototype.getContext=function(kind,...args){
                            return /webgl/i.test(kind)?null:original.call(this,kind,...args);
                        };""")
                    fallback.goto(f'http://127.0.0.1:{server.server_port}/index.html', wait_until='networkidle')
                    energy = fallback.locator('#lab-energy')
                    energy.locator('select[data-param=dt]').select_option('0.005')
                    energy.locator('[data-action=run]').click()
                    expect(energy.locator('.announce')).to_contain_text('Completed 12 simulated seconds', timeout=30000)
                    numerical = state(energy)
                    assert numerical['step'] == 2400 and numerical['display'] == 'numerical-only'
                    assert numerical['run']['sampleCount'] == 2401
                    expect(energy.locator('.scene-notice')).to_contain_text('static reference diagram does not move')
                    energy.screenshot(path=str(out/'energy-numerical-only-completed.png'))
                    receipt['observed']['energyNumericalOnly'] = numerical
                    fallback.close()
                assert not errors, errors
                receipt['javascript_errors'] = errors
                receipt['status'] = 'PASS'
                browser.close()
        finally:
            server.shutdown(); server.server_close()
            (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(f'PASS {args.case}: real controls/render evidence at {out}')

if __name__ == '__main__': main()

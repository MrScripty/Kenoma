"""Actual Chromium serial-specimen controls, indexed meshes and independent SI oracles.

Newton's cubic equation, six local tetrahedra and the full Cauchy stress are
evaluated in Python, independently of the delivered bisection and face sum.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from tempfile import TemporaryDirectory
import argparse, hashlib, json, math, os, shutil, subprocess, sys
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual, expected, label, absolute=2e-12, relative=2e-10):
    assert math.isfinite(actual) and math.isfinite(expected), (label, actual, expected)
    assert abs(actual - expected) <= absolute + relative * abs(expected), (label, actual, expected)


def cubic_root(area, mu, force):
    t = force / (area * mu)
    x = max(1., t + 1.)
    for _ in range(40):
        next_x = x - (x**3 - t*x*x - 1) / (3*x*x - 2*t*x)
        assert next_x > 0 and math.isfinite(next_x)
        if next_x == x:
            break
        x = next_x
    close(x**3 - t*x*x - 1, 0., 'Independent cubic Newton residual', absolute=1e-13)
    return x


def subtract(a, b):
    return [x-y for x, y in zip(a, b)]


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def corners(vertices):
    assert len(vertices) == 8 and all(len(v) == 3 for v in vertices)
    lows = [min(v[j] for v in vertices) for j in range(3)]
    highs = [max(v[j] for v in vertices) for j in range(3)]
    result = {''.join('0' if abs(v[j]-lows[j]) < abs(v[j]-highs[j]) else '1' for j in range(3)): i for i, v in enumerate(vertices)}
    assert len(result) == 8
    return result


def tetra_volume(reference, current):
    ids = corners(reference)
    tetrahedra = [('000','100','110','111'), ('000','110','010','111'),
                 ('000','010','011','111'), ('000','011','001','111'),
                 ('000','001','101','111'), ('000','101','100','111')]
    volume = 0.
    for keys in tetrahedra:
        a, b, c, d = [current[ids[key]] for key in keys]
        volume += abs(dot(subtract(b, a), cross(subtract(c, a), subtract(d, a)))) / 6
    return volume


def edges(reference, current):
    ids = corners(reference)
    origin = current[ids['000']]
    return [subtract(current[ids[key]], origin) for key in ['100', '010', '001']]


def snapshot(lab):
    return lab.evaluate('(root)=>root.serialLab.snapshot()')


def edit(lab, key, value):
    before = snapshot(lab)['parameters']
    control = lab.locator(f'[data-param="{key}"]')
    if control.locator('xpath=self::select').count():
        control.select_option(str(value))
    else:
        number = lab.locator(f'input[type=number][data-param="{key}"]')
        expect(number).to_have_count(1)
        number.fill(str(value))
    result = snapshot(lab)
    assert result['parameters'][key] == float(value), ('Named control must apply its value',key,value,result['parameters'])
    assert all(result['parameters'][name] == previous for name, previous in before.items() if name != key), ('Parameter edit changed an unrelated control',key,before,result['parameters'])
    return result


def verify_state(payload):
    p, state = payload['parameters'], payload['state']
    assert state['parameters'] == p and len(state['cells']) == 2
    assert state['forceCriterionN'] == 1e-10
    reference_total = current_total = energy_total = extension = 0.
    residuals = []
    for i, cell in enumerate(state['cells']):
        area = p['area'] * (p['ratio'] if i else 1)
        close(cell['referenceAreaM2'], area, 'Reference area')
        root = cubic_root(area, p['mu'], p['force'])
        tolerance = 2e-12 if p['iterations'] >= 48 else 1.15 / 2**p['iterations'] / 2 + 2e-12
        close(cell['stretch'], root, 'Independent cubic Newton root', absolute=tolerance, relative=0)
        lam, b = cell['stretch'], cell['lateralStretch']
        close(b, lam**-.5, 'Local incompressible lateral stretch')
        e = edges(cell['referenceVertices'], cell['currentVertices'])
        length, current_area = norm(e[0]), norm(cross(e[1], e[2]))
        close(length, p['length']*lam, 'Model axial geometry')
        close(current_area, area/lam, 'Current area from independent edges')
        close(cell['currentAreaM2'], current_area, 'Current area readout')
        close(cell['currentLengthM'], length, 'Length readout')
        v0 = tetra_volume(cell['referenceVertices'], cell['referenceVertices'])
        volume = tetra_volume(cell['referenceVertices'], cell['currentVertices'])
        close(v0, area*p['length'], 'Reference tetra volume')
        close(volume, v0, 'Local tetra incompressibility')
        close(cell['currentBoundaryVolumeM3'], volume, 'Boundary volume versus independent tetra volume')
        close(cell['J'], 1., 'Local determinant')
        close(cell['volumeRatio'], 1., 'Local volume ratio')
        nominal = p['mu']*(lam-lam**-2)
        multiplier = p['mu']/lam
        cauchy = p['mu']*lam*lam-multiplier
        resultant = area*nominal
        close(cell['nominalStressPa'], nominal, 'Independent nominal stress', absolute=2e-9)
        close(cell['incompressibilityMultiplierPa'], multiplier, 'Independent pressure multiplier', absolute=2e-9)
        close(cell['lateralStressPa'], p['mu']*b*b-multiplier, 'Free lateral traction', absolute=2e-9)
        close(cell['lateralStressPa'], 0., 'Free lateral traction zero', absolute=2e-9)
        close(cell['cauchyStressPa'], cauchy, 'Independent full Cauchy stress', absolute=2e-9)
        close(cell['resultantN'], resultant, 'Reference-area nominal resultant')
        close(cell['cauchyStressPa']*current_area, resultant, 'Current-area Cauchy resultant')
        close(cell['forceResidualN'], resultant-p['force'], 'Actual force residual')
        close(cell['solve']['residualN'], resultant-p['force'], 'Reported root residual')
        assert cell['solve']['converged'] == (abs(resultant-p['force']) <= 1e-10)
        assert cell['solve']['cap'] == p['iterations'] and cell['solve']['iterations'] <= p['iterations']
        assert cell['solve']['bracket'][0]-2e-15 <= root <= cell['solve']['bracket'][1]+2e-15
        expected_F = [lam,0,0,0,b,0,0,0,b]
        assert len(cell['F']) == 9
        for actual, expected in zip(cell['F'], expected_F):
            close(actual, expected, 'Full deformation gradient')
        energy = v0*p['mu']/2*(lam*lam+2*b*b-3)
        close(cell['energyJ'], energy, 'Independent full constrained energy', absolute=2e-12)
        assert cell['energyJ'] >= -2e-12
        reference_total += v0
        current_total += volume
        energy_total += energy
        extension += length-p['length']
        residuals.append(resultant-p['force'])
    close(state['referenceVolumeM3'], reference_total, 'Assembly reference volume')
    close(state['currentBoundaryVolumeM3'], current_total, 'Assembly tetra volume')
    close(state['totalEnergyJ'], energy_total, 'Assembly energy')
    close(state['extensionM'], extension, 'Assembly extension')
    close(state['totalCurrentLengthM'], 2*p['length']+extension+.012, 'Assembly length with physical spacer')
    close(state['spacerLengthM'], .012, 'Fixed physical spacer')
    assert state['converged'] == all(abs(r) <= 1e-10 for r in residuals)
    return {'independentRoots': [cubic_root(p['area']*(p['ratio'] if i else 1), p['mu'], p['force']) for i in range(2)], 'actualResultantsN': [c['resultantN'] for c in state['cells']], 'residualsN': residuals, 'converged': state['converged']}


def positions(mesh):
    p = mesh['positions']
    return p if p and isinstance(p[0], list) else [p[i:i+3] for i in range(0, len(p), 3)]


def verify_visible_readouts(lab, payload):
    units = {'referenceAreaM2':'m²','currentAreaM2':'m²','referenceLengthM':'m','currentLengthM':'m',
             'stretch':'','lateralStretch':'','J':'','currentBoundaryVolumeM3':'m³','volumeRatio':'',
             'nominalStressPa':'Pa','cauchyStressPa':'Pa','lateralStressPa':'Pa','incompressibilityMultiplierPa':'Pa',
             'resultantN':'N','forceResidualN':'N','energyJ':'J'}
    for cell in payload['state']['cells']:
        for field, unit in units.items():
            text = lab.locator(f'.serial-cell[data-cell="{cell["index"]}"] [data-field="{field}"]').inner_text()
            value = float(text.split()[0])
            # Human readouts intentionally use seven significant figures;
            # resultants/residuals use eleven. Strict SI state oracles above
            # retain their independent numerical tolerances.
            relative = 1e-10 if field in ['resultantN','forceResidualN'] else 5e-7
            close(value,cell[field],'Visible actual '+field,absolute=1e-14,relative=relative)
            if unit:
                assert text.split()[-1] == unit, (field,text)


def verify_indexed_mesh(mesh, reference, expected, volume_expected, kind):
    actual = positions(mesh)
    assert len(actual) == 8 and len(mesh['indices']) == 36, (kind, 'Eight actual indexed vertices and twelve triangles required')
    assert set(mesh['indices']) == set(range(8))
    for index, (got, want) in enumerate(zip(actual, expected)):
        for component, (value, target) in enumerate(zip(got, want)):
            close(value, target, 'Actual rendered vertex '+kind+f' {index}/{component}', absolute=8e-9, relative=0)
    # Six local tetrahedra use actual uploaded Float32 vertices, not state J.
    volume = tetra_volume(reference, actual)
    close(volume, volume_expected, 'Actual rendered local volume '+kind, absolute=2e-12, relative=2e-6)
    # The actual uploaded triangle index buffer must form a closed outward shell.
    center = [sum(v[j] for v in actual)/8 for j in range(3)]
    edge_counts = {}
    signed = surface = 0.
    for start in range(0, 36, 3):
        ids = mesh['indices'][start:start+3]
        assert len(set(ids)) == 3
        a, b, c = [actual[i] for i in ids]
        normal = cross(subtract(b,a), subtract(c,a))
        assert norm(normal) > 0
        assert dot(subtract(a,center), normal) > 0, 'Actual triangle orientation'
        signed += dot(subtract(a,center), normal)/6
        surface += norm(normal)/2
        for j in range(3):
            edge = tuple(sorted([ids[j], ids[(j+1)%3]]))
            edge_counts[edge] = edge_counts.get(edge,0)+1
    assert all(n == 2 for n in edge_counts.values()), 'Actual indexed shell closure'
    close(signed, volume, 'Actual indexed shell versus tetra volume', absolute=2e-12, relative=2e-6)
    return {'tetraVolumeM3': volume, 'indexedSignedVolumeM3': signed, 'indexedExteriorAreaM2': surface}


def verify_scene(payload):
    scene, state, p = payload['scene'], payload['state'], payload['parameters']
    assert scene['sceneState'] == 'ready' and scene['canvasCount'] == 1
    assert scene['drawCalls'] > 0
    assert len(scene['meshes']) == 2 and len(scene['referenceMeshes']) == 2
    observed = []
    for i, cell in enumerate(state['cells']):
        mesh = next(m for m in scene['meshes'] if m['cellIndex'] == i)
        reference = next(m for m in scene['referenceMeshes'] if m['cellIndex'] == i)
        current_measure = verify_indexed_mesh(mesh, cell['referenceVertices'], cell['currentVertices'], cell['referenceVolumeM3'], 'block '+str(i))
        verify_indexed_mesh(reference, cell['referenceVertices'], cell['referenceVertices'], cell['referenceVolumeM3'], 'reference '+str(i))
        e = edges(cell['referenceVertices'], positions(mesh))
        lam = norm(e[0])/cell['referenceLengthM']
        measured_area = norm(cross(e[1],e[2]))
        close(lam, cell['stretch'], 'Actual mesh stretch', absolute=8e-7)
        close(measured_area, cell['currentAreaM2'], 'Actual mesh current area', absolute=2e-12, relative=2e-6)
        close(current_measure['indexedExteriorAreaM2'], cell['exteriorAreaM2'], 'Actual mesh exterior area readout', absolute=2e-11, relative=2e-6)
        observed.append(current_measure)
    spacer = scene['spacerEndpoints']
    assert len(spacer) == 2
    close(spacer[0][0], max(v[0] for v in state['cells'][0]['currentVertices']), 'Actual spacer starts at first block end', absolute=8e-9)
    close(spacer[1][0], min(v[0] for v in state['cells'][1]['currentVertices']), 'Actual spacer ends at second block start', absolute=8e-9)
    close(norm(subtract(spacer[1],spacer[0])), .012, 'Actual fixed spacer', absolute=8e-9)
    arrows = [a for a in scene['arrows'] if a.get('visible', True)]
    if p['force'] == 0:
        assert not arrows, 'Zero load must not show signed load arrows'
    else:
        assert len(arrows) == 2
        arrows = sorted(arrows,key=lambda a:a['origin'][0])
        for arrow, sign in zip(arrows,[-math.copysign(1,p['force']),math.copysign(1,p['force'])]):
            close(arrow['direction'][0],sign,'Actual signed ArrowHelper direction',absolute=1e-9)
            close(arrow['direction'][1],0.,'Arrow y direction',absolute=1e-9)
            close(arrow['direction'][2],0.,'Arrow z direction',absolute=1e-9)
            assert arrow['lengthM'] > 0
    camera = scene['camera']
    assert len(camera['projectionMatrix']) == 16 and len(camera['position']) == len(camera['target']) == 3
    assert camera['right'] > camera['left'] and camera['top'] > camera['bottom']
    assert all(math.isfinite(x) for x in camera['projectionMatrix'])
    display = scene['display']
    assert display['displacementMagnification'] == 1
    assert display['strainPalette'] == [-.4,.75]
    close(display['gridSpacingM'],.01,'Fixed physical grid spacing')
    close(display['fixedPhysicalWidthM'],.224,'Fixed physical viewport width')
    return observed


def capture(lab, out, name):
    path = out/(name+'.png')
    lab.locator('.scene-host canvas').screenshot(path=str(path))
    from PIL import Image
    with Image.open(path) as image:
        assert image.width >= 250 and image.height >= 180
        colors = image.convert('RGB').getcolors(image.width*image.height)
        assert colors is not None and len(colors) > 20, 'Actual canvas must contain drawn geometry'
        most_common = max(n for n,_ in colors)
        assert most_common < image.width*image.height*.99, 'Actual canvas is effectively blank'
    return {'file':path.name,'sha256':digest(path)}


def check(page, out, full=True):
    lab = page.locator('#lab-serial-specimen[data-serial]')
    expect(lab).to_have_count(1)
    page.wait_for_function('document.querySelector("#lab-serial-specimen").serialLab != null')
    assert lab.locator('canvas').count() == 0, 'Actual 3D must start lazily'
    lab.locator('[data-action=start]').click()
    expect(lab).to_have_attribute('data-scene-state','ready',timeout=30000)
    initial = snapshot(lab)
    verify_state(initial)
    geometry = verify_scene(initial)
    verify_visible_readouts(lab,initial)
    if not full:
        return {'initial':initial,'geometry':geometry}
    cases = {'default':initial}
    captures = [capture(lab,out,'desktop-default')]
    camera = initial['scene']['camera']
    pixels = lab.evaluate('(root)=>root.serialLab.pixelSignature()')
    assert pixels['width'] >= 250 and pixels['height'] >= 180
    assert pixels['nonBackgroundPixels'] > 100 and pixels['uniqueColours'] > 20
    assert isinstance(pixels['checksum'], (int,str))
    # Static solves draw on demand; no idle animation frames churn the renderer.
    idle = snapshot(lab)['scene']['renderCount']
    page.wait_for_timeout(250)
    assert snapshot(lab)['scene']['renderCount'] == idle, 'Static lesson must draw on demand'
    # Force reversal is physically solved and rendered at a fixed physical view.
    for force in [-.1, .1, 0]:
        value = edit(lab,'force',force)
        verify_state(value); verify_scene(value)
        verify_visible_readouts(lab,value)
        assert value['scene']['camera'] == camera, 'Parameter edits must preserve fixed camera'
        if force:
            assert math.copysign(1,value['state']['extensionM']) == math.copysign(1,force)
            assert all((c['currentAreaM2']<c['referenceAreaM2']) == (force>0) for c in value['state']['cells'])
            assert all(abs(c['nominalStressPa']*c['currentAreaM2']-c['resultantN']) > 1e-4 for c in value['state']['cells']), 'Current area belongs with Cauchy stress, not nominal stress'
        else:
            close(value['state']['extensionM'],0.,'Zero-load extension')
            close(value['state']['totalEnergyJ'],0.,'Zero-load energy')
        cases[str(force)] = value
        captures.append(capture(lab,out,'desktop-'+('compression' if force<0 else 'tension' if force>0 else 'zero')))
    assert captures[1]['sha256'] != captures[2]['sha256'] != captures[3]['sha256'], 'Actual force states must change canvas pixels'
    edit(lab,'force',.1)
    length_base = snapshot(lab)
    for length, name in [(.01,'short'),(.04,'long')]:
        changed_length = edit(lab,'length',length)
        verify_state(changed_length);verify_scene(changed_length);verify_visible_readouts(lab,changed_length)
        scale = length/length_base['parameters']['length']
        assert changed_length['scene']['camera'] == camera
        for cell, original in zip(changed_length['state']['cells'],length_base['state']['cells']):
            for field in ['stretch','lateralStretch','currentAreaM2','nominalStressPa','cauchyStressPa','incompressibilityMultiplierPa','resultantN']:
                close(cell[field],original[field],'Length edit preserves stretch/material/area stress '+field)
            for field in ['currentLengthM','referenceVolumeM3','currentBoundaryVolumeM3','energyJ']:
                close(cell[field],original[field]*scale,'Length edit scales local '+field)
        for field in ['extensionM','referenceVolumeM3','currentBoundaryVolumeM3','totalEnergyJ']:
            close(changed_length['state'][field],length_base['state'][field]*scale,'Length edit scales assembly '+field)
        cases['length-'+name] = changed_length
        captures.append(capture(lab,out,'desktop-length-'+name))
    edit(lab,'length',.025)
    reversed_ratio = edit(lab,'ratio',.5)
    verify_state(reversed_ratio); verify_scene(reversed_ratio)
    assert reversed_ratio['state']['cells'][1]['stretch'] > reversed_ratio['state']['cells'][0]['stretch']
    assert reversed_ratio['scene']['camera'] == camera
    cases['reversedRatio'] = reversed_ratio
    captures.append(capture(lab,out,'desktop-reversed-ratio'))
    equal = edit(lab,'ratio',1)
    verify_state(equal);verify_scene(equal)
    close(equal['state']['cells'][0]['stretch'],equal['state']['cells'][1]['stretch'],'Equal-area shared force')
    soft = edit(lab,'mu',500);verify_state(soft);verify_scene(soft)
    stiff = edit(lab,'mu',5000);verify_state(stiff);verify_scene(stiff)
    assert stiff['state']['extensionM'] < soft['state']['extensionM']/5
    edit(lab,'mu',1500)
    narrower = edit(lab,'area',.0003);verify_state(narrower);verify_scene(narrower)
    wider = edit(lab,'area',.001);verify_state(wider);verify_scene(wider)
    assert wider['state']['extensionM'] < narrower['state']['extensionM']/2
    cases.update(soft=soft,stiff=stiff,narrower=narrower,wider=wider)
    # A coarse valid mesh must display its actual nonequilibrated resultants.
    edit(lab,'area',.0003);edit(lab,'ratio',.5);edit(lab,'mu',500)
    coarse = edit(lab,'iterations',8)
    coarse_oracle = verify_state(coarse);verify_scene(coarse)
    verify_visible_readouts(lab,coarse)
    assert not coarse['state']['converged']
    assert any(abs(r)>1e-10 for r in coarse_oracle['residualsN'])
    expect(lab).to_have_attribute('data-converged','false')
    expect(lab.locator('.serial-solve-status')).to_contain_text('Force residuals exceed 1e-10 N')
    expect(lab.locator('.serial-solve-status')).to_contain_text('not a qualified shared-force equilibrium')
    # Rejection also retains a nonequilibrated preceding approximation and its warning.
    coarse_warning = lab.locator('.serial-solve-status').inner_text()
    lab.locator('[data-action=reject-volume]').click()
    coarse_rejected = snapshot(lab)
    assert coarse_rejected['parameters'] == coarse['parameters'] and coarse_rejected['state'] == coarse['state']
    assert coarse_rejected['scene']['meshes'] == coarse['scene']['meshes']
    assert coarse_rejected['scene']['camera'] == coarse['scene']['camera']
    assert coarse_rejected['lastCandidate']['accepted'] is False
    assert not coarse_rejected['state']['converged']
    expect(lab).to_have_attribute('data-converged','false')
    assert lab.locator('.serial-solve-status').inner_text() == coarse_warning
    expect(lab.locator('.serial-candidate')).to_contain_text('preceding displayed approximation was retained')
    assert 'valid solved' not in lab.locator('.serial-candidate').inner_text()
    verify_state(coarse_rejected);verify_scene(coarse_rejected);verify_visible_readouts(lab,coarse_rejected)
    cases['coarseRejectedGlobalVolume'] = coarse_rejected
    captures.append(capture(lab,out,'desktop-coarse-rejected'))
    fine = edit(lab,'iterations',64)
    fine_oracle = verify_state(fine);verify_scene(fine)
    verify_visible_readouts(lab,fine)
    assert fine['state']['converged'] and max(abs(r) for r in fine_oracle['residualsN'])<1e-10
    assert max(abs(r) for r in fine_oracle['residualsN']) < max(abs(r) for r in coarse_oracle['residualsN'])/1000
    cases.update(coarse=coarse,fine=fine)
    captures.append(capture(lab,out,'desktop-refined'))
    # Opposite local volume defects must never reach the accepted mesh buffers.
    before = snapshot(lab)
    lab.locator('[data-action=reject-volume]').click()
    rejected = snapshot(lab)
    assert rejected['parameters'] == before['parameters'] and rejected['state'] == before['state']
    assert rejected['scene']['meshes'] == before['scene']['meshes'] and rejected['scene']['camera'] == before['scene']['camera']
    candidate = rejected['lastCandidate']
    expect(lab.locator('.serial-candidate')).to_contain_text('preceding displayed approximation was retained')
    assert candidate['accepted'] is False
    close(candidate['totalVolumeRatio'],1.,'Rejected candidate global volume cancellation')
    assert all(abs(c['J']-1)>1e-3 and abs(c['lateralStressPa'])>1 for c in candidate['candidateCells'])
    verify_state(rejected);verify_scene(rejected)
    cases['rejectedGlobalVolume'] = rejected
    # Invalid controls preserve accepted parameters, state and geometry exactly.
    invalid_control = lab.locator('input[type=number][data-param=force]')
    for invalid in ['', '.101']:
        invalid_control.fill(invalid)
        expect(invalid_control).to_have_attribute('aria-invalid','true')
        invalid_state = snapshot(lab)
        assert invalid_state['parameters'] == rejected['parameters'] and invalid_state['state'] == rejected['state']
        assert invalid_state['scene']['meshes'] == rejected['scene']['meshes']
        assert invalid_state['scene']['camera'] == rejected['scene']['camera']
    edit(lab,'force',.08)
    valid = snapshot(lab);verify_state(valid);verify_scene(valid)
    assert valid['parameters']['force'] == .08
    # Actual preset and download include the accepted SI state, not a canned string.
    lab.locator('[data-action=copy]').click()
    copied = json.loads(lab.locator('textarea.preset').input_value())
    assert copied['parameters'] == valid['parameters'] and copied['state'] == valid['state']
    with page.expect_download() as info:
        lab.locator('[data-action=export]').click()
    info.value.save_as(str(out/'actual-downloaded-state.json'))
    downloaded = json.loads((out/'actual-downloaded-state.json').read_text())
    assert downloaded['parameters'] == valid['parameters'] and downloaded['state'] == valid['state']
    lab.locator('[data-action=summary]').click()
    assert lab.locator('.announce').inner_text().strip()
    # Front/orbit views must alter the actual camera and pixels, then reset restores it.
    lab.locator('[data-action=front]').click()
    front = snapshot(lab);verify_scene(front)
    assert front['scene']['camera'] != camera
    captures.append(capture(lab,out,'desktop-front'))
    host = lab.locator('.scene-host canvas')
    box = host.bounding_box();assert box
    page.mouse.move(box['x']+box['width']*.45,box['y']+box['height']*.5)
    page.mouse.down();page.mouse.move(box['x']+box['width']*.65,box['y']+box['height']*.6,steps=8);page.mouse.up()
    orbited = snapshot(lab)
    assert orbited['scene']['camera'] != front['scene']['camera'], 'Native orbit must change actual camera'
    assert orbited['scene']['renderCount'] > front['scene']['renderCount']
    lab.locator('[data-action=reset]').click()
    reset = snapshot(lab);verify_state(reset);verify_scene(reset)
    assert reset['parameters'] == initial['parameters'] and reset['state'] == initial['state']
    assert reset['scene']['camera'] == camera, 'Explicit reset restores default oblique view'
    lab.locator('[data-action=front]').click();lab.locator('[data-action=oblique]').click()
    assert snapshot(lab)['scene']['camera'] == camera
    # Native WebGL context-loss event, no synthetic handler invocation.
    loss = host.evaluate('''canvas=>{const gl=canvas.getContext('webgl2')||canvas.getContext('webgl');const ext=gl.getExtension('WEBGL_lose_context');if(!ext)return false;ext.loseContext();return true;}''')
    assert loss, 'Chromium must expose native WEBGL_lose_context for this qualification'
    expect(lab).to_have_attribute('data-scene-state','error')
    lost = snapshot(lab)
    assert lost['state'] == reset['state'] and lost['parameters'] == reset['parameters']
    lab.locator('[data-action=start]').click()
    expect(lab).to_have_attribute('data-scene-state','ready',timeout=30000)
    retry = snapshot(lab);verify_state(retry);verify_scene(retry)
    assert retry['state'] == reset['state']
    captures.append(capture(lab,out,'desktop-context-retry'))
    # Phone viewport emulation retains all controls and actual nonblank geometry.
    page.set_viewport_size({'width':390,'height':844})
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
    lab.locator('[data-action=reset]').click()
    mobile = snapshot(lab);verify_state(mobile);verify_scene(mobile)
    captures.append(capture(lab,out,'mobile-default'))
    lab.screenshot(path=str(out/'mobile-controls.png'))
    cases.update(reset=reset,contextLossRetained=lost,contextRetry=retry,mobile=mobile,pixelSignature=pixels)
    (out/'observed-states.json').write_text(json.dumps(cases,indent=2)+'\n')
    return {'cases':cases,'captures':captures,'scope':'Actual Chromium WebGL rendering; mobile viewport emulation, not a physical phone; no biological validation.'}


def no_gl(browser, url):
    page = browser.new_page(viewport={'width':390,'height':844})
    page.add_init_script("const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(kind,...args){return kind.startsWith('webgl')?null:original.call(this,kind,...args);};")
    errors = [];page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(url,wait_until='networkidle')
    lab = page.locator('#lab-serial-specimen')
    page.wait_for_function('document.querySelector("#lab-serial-specimen").serialLab != null')
    before = snapshot(lab);verify_state(before)
    lab.locator('[data-action=start]').click()
    expect(lab).to_have_attribute('data-scene-state','error')
    assert lab.locator('.static-figure').is_visible()
    assert lab.locator('.scene-notice').inner_text().strip()
    changed = edit(lab,'force',-.1);verify_state(changed)
    assert changed['state']['extensionM'] < 0 and changed['scene']['sceneState'] == 'error'
    lab.locator('[data-action=reset]').click()
    assert snapshot(lab)['state'] == before['state']
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
    assert not errors, errors
    page.close()
    return {'unavailableWebGL':'Actual getContext failure injected before page load','textControlsWork':True,'staticFigureVisible':True,'javascriptErrors':errors}


def displayed_proofs(page, site):
    receipt = site/'serial-real-proof-status.json'
    if not receipt.exists():
        assert page.locator('.proof-card').count() == 0, 'Integrated serial lesson is missing its proof receipt'
        return None
    record = json.loads(receipt.read_text())
    source = site/record['source']
    mapping = site/'proofs/serial-specimen-real-claims.json'
    assert record['source_sha256'] == digest(source) == digest(ROOT/record['source'])
    assert record['claims_sha256'] == digest(mapping) == digest(ROOT/'proofs/serial-specimen-real-claims.json')
    assert len(record['claims']) == 12
    cards = []
    normal = lambda text:' '.join(text.split())
    for claim in record['claims']:
        assert claim['status'] == 'checked' and set(claim['axioms']) <= {'propext','Classical.choice','Quot.sound'}
        card = page.locator('#proof-'+claim['id']);expect(card).to_have_count(1)
        text = card.inner_text();statement = card.locator('pre').first.inner_text()
        assert 'theorem '+claim['theorem'].split('.')[-1] in statement
        assert sum(line.startswith('theorem ') for line in statement.splitlines()) == 1
        for key in ['claim','assumptions','limitations','implementation']:
            assert normal(claim[key]) in normal(text), (claim['id'],key)
        cards.append({'id':claim['id'],'theorem':claim['theorem'],'card_text':text,'card_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'statement_text_sha256':hashlib.sha256(statement.encode()).hexdigest()})
    return {'scope':'Actual displayed claims bound to delivered checked source and kernel receipt; no Lean rerun in this browser test','receipt_sha256':digest(receipt),'source_sha256':record['source_sha256'],'claims_sha256':record['claims_sha256'],'cards':cards}


def qualify(site, out, full=True):
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(site)))
    Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
            page = browser.new_page(viewport={'width':1280,'height':1000},reduced_motion='reduce')
            page.set_default_timeout(30000)
            errors = [];page.on('pageerror',lambda error:errors.append(str(error)))
            url = f'http://127.0.0.1:{server.server_port}/index.html'
            page.goto(url,wait_until='networkidle')
            proofs = displayed_proofs(page,site)
            result = check(page,out,full)
            assert not errors, errors
            cards = page.locator('.proof-card').count()
            page.close()
            fallback = no_gl(browser,url) if full else None
            version = browser.version
            browser.close()
            return {'status':'PASS','browser_version':version,'observed':result,'fallback':fallback,'javascript_errors':errors,'proof_cards':cards,'proof_evidence':proofs}
    finally:
        server.shutdown();server.server_close()


def main():
    from build_serial_preview import build
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site',nargs='?',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'dist/serial-qa')
    parser.add_argument('--negative-controls',action='store_true')
    args = parser.parse_args()
    out = args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    (out/'receipt.json').unlink(missing_ok=True)
    temporary = ROOT/'.browser-tmp';temporary.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=temporary) as temp:
        base = Path(temp)
        site = args.site.resolve() if args.site else base/'site'
        if args.site is None:
            build(site)
        inputs = {str(path.relative_to(site)):digest(path) for path in sorted(site.rglob('*')) if path.is_file() and path.suffix in ['.html','.mjs','.js','.css']}
        names = ['web/serial-specimen.mjs','web/continuum-properties.mjs','web/scene-status.mjs','web/serial-lab.mjs','web/serial-lab.css','web/style.css','web/app.mjs','tools/serial_lab.py','tools/build_serial_preview.py','tests/serial_browser.py']
        source_hashes = {name:digest(ROOT/name) for name in names}
        result = qualify(site,out)
        result.update(scope='Actual serial specimen production controls, independent numerical and actual indexed WebGL geometry checks; not a full-book release or Lean rerun',delivered_input_sha256=inputs,source_input_sha256=source_hashes,test_sha256=source_hashes['tests/serial_browser.py'],source_base_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),worktree_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),build_manifest_sha256=digest(site/'build-manifest.json') if (site/'build-manifest.json').exists() else None,preview_manifest_sha256=digest(site/'serial-preview-manifest.json') if (site/'serial-preview-manifest.json').exists() else None)
        assert all(digest(site/name)==value for name,value in inputs.items()), 'Delivered executable changed during qualification'
        assert all(digest(ROOT/name)==value for name,value in source_hashes.items()), 'Source changed during qualification'
        result['output_sha256'] = {str(path.relative_to(out)):digest(path) for path in sorted(out.rglob('*')) if path.is_file() and 'negative-controls' not in path.parts and path.name != 'receipt.json'}
        if args.negative_controls:
            negatives = []
            mutations = [
                ('nominal-current-area','web/serial-specimen.mjs','const residual=lambda=>area*nominalStress(mu,lambda)-force;','const residual=lambda=>area/lambda*nominalStress(mu,lambda)-force;','Independent cubic Newton root'),
                ('display-lateral-volume','web/serial-lab.mjs','export function displayedVertices(cell){return cell.currentVertices.map(vertex=>[...vertex]);}','export function displayedVertices(cell){return cell.currentVertices.map(vertex=>[vertex[0],vertex[1]*1.1,vertex[2]*1.1]);}','Actual rendered vertex'),
            ]
            for name, module_name, old, new, expected in mutations:
                copy = base/name;build(copy)
                module = copy/module_name;source = module.read_text()
                assert source.count(old)==1,(name,'Exact negative mutation anchor changed')
                original_module_sha256 = digest(module)
                module.write_text(source.replace(old,new))
                subprocess.run([str(ROOT/'node_modules/.bin/esbuild'),str(copy/'web/serial-lab.mjs'),'--bundle','--minify','--format=esm','--target=es2022',f'--outfile={copy/"assets/serial-app.js"}','--legal-comments=external'],check=True)
                negative_out = out/'negative-controls'/name;negative_out.mkdir(parents=True,exist_ok=True)
                shutil.copy2(module,negative_out/module.name)
                shutil.copy2(copy/'assets/serial-app.js',negative_out/'delivered-serial-app.js')
                try:
                    qualify(copy,negative_out,False)
                except AssertionError as error:
                    assert expected in str(error), ('Negative copy failed outside its independent oracle',name,str(error))
                    negatives.append({'case':name,'detected':True,'reason':str(error),'module':module_name,'original_module_sha256':original_module_sha256,'module_sha256':digest(module),'delivered_input_sha256':{str(path.relative_to(copy)):digest(path) for path in sorted(copy.rglob('*')) if path.is_file() and path.suffix in ['.html','.mjs','.js','.css']},'output_sha256':{str(path.relative_to(out)):digest(path) for path in sorted(negative_out.rglob('*')) if path.is_file()}})
                else:
                    raise AssertionError('Negative control unexpectedly passed: '+name)
            result['negative_controls'] = negatives
        (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
        print('PASS actual serial specimen controls at '+str(out))


if __name__=='__main__':
    main()

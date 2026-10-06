"""Bind the serial lesson to fresh proofs, independent geometry and actual UI evidence."""
from pathlib import Path
import hashlib, importlib.util, json, math, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(destination=None):
    out = Path(destination) if destination else ROOT/'dist'
    read = lambda name: json.loads((out/name).read_text())
    manifest = read('build-manifest.json')
    proof = read('serial-real-proof-status.json')
    assert proof['source'] == 'proofs/SerialSpecimenReal.lean'
    assert proof['source_sha256'] == digest(ROOT/proof['source']) == digest(out/proof['source'])
    assert proof['claims_sha256'] == digest(ROOT/'proofs/serial-specimen-real-claims.json') == digest(out/'proofs/serial-specimen-real-claims.json')
    expected = json.loads((ROOT/'proofs/serial-specimen-real-claims.json').read_text())
    assert len(proof['claims']) == len(expected) == 12
    for actual, claim in zip(proof['claims'], expected):
        assert all(actual.get(key) == value for key, value in claim.items())
        assert actual['status'] == 'checked' and set(actual['axioms']) <= {'propext', 'Classical.choice', 'Quot.sound'}
    assert proof['mathlib'] == manifest['property_mathlib'] == json.loads((ROOT/'proofs/mathlib-lock.json').read_text())
    experiment = read('serial-experiment.json')
    for name, sha in experiment['inputs'].items():
        assert digest(ROOT/name) == sha, 'Changed serial experiment source: '+name
    for name, sha in manifest['serial_outputs'].items():
        assert digest(out/name) == sha, 'Changed serial generated output: '+name
    # Recreate the actual static projection and full numerical cases. A rehashed
    # false SVG or table still fails this binding; never mutate the checked build.
    with tempfile.TemporaryDirectory() as temporary:
        subprocess.run(['node', str(ROOT/'tools/serial-experiment.mjs'), temporary], check=True, capture_output=True)
        for name in ['serial-experiment.json', 'property-serial.svg']:
            delivered = out/name if name.endswith('.json') else out/'assets'/name
            assert digest(Path(temporary)/name) == digest(delivered), 'Serial generated physics/projection differs: '+name
    folder = out/'serial-qa'
    browser = json.loads((folder/'receipt.json').read_text())
    assert browser['status'] == 'PASS' and not browser['javascript_errors']
    assert browser['build_manifest_sha256'] == digest(out/'build-manifest.json'), 'Stale serial manifest binding'
    assert browser['test_sha256'] == digest(ROOT/'tests/serial_browser.py'), 'Stale serial browser test'
    for name, sha in browser['source_input_sha256'].items():
        assert digest(ROOT/name) == sha, 'Stale serial source binding: '+name
    inputs = browser['delivered_input_sha256']
    assert {'index.html','assets/app.js','assets/serial-lab.css','web/serial-specimen.mjs','web/serial-lab.mjs'} <= set(inputs)
    for name, sha in inputs.items():
        assert digest(out/name) == sha, 'Changed delivered serial input: '+name
    outputs = browser['output_sha256']
    assert {'observed-states.json','actual-downloaded-state.json','desktop-default.png','desktop-compression.png','desktop-tension.png','desktop-zero.png','desktop-reversed-ratio.png','desktop-refined.png','desktop-front.png','desktop-context-retry.png','mobile-default.png','mobile-controls.png','desktop-length-short.png','desktop-length-long.png'} <= set(outputs)
    for name, sha in outputs.items():
        assert digest(folder/name) == sha, 'Changed serial browser evidence: '+name
    cases = json.loads((folder/'observed-states.json').read_text())
    assert cases == browser['observed']['cases'], 'Serial observed-state copies disagree'
    required = {'default','-0.1','0.1','0','reversedRatio','soft','stiff','narrower','wider','coarse','fine','rejectedGlobalVolume','reset','contextLossRetained','contextRetry','mobile','pixelSignature','length-short','length-long'}
    assert required <= set(cases), 'Incomplete serial state and control coverage'
    # Reuse the independent browser qualification's cubic, tetrahedral and full
    # stress oracles on saved model/actual uploaded mesh buffers. No browser rerun.
    spec = importlib.util.spec_from_file_location('serial_browser_oracles', ROOT/'tests/serial_browser.py')
    oracle = importlib.util.module_from_spec(spec); spec.loader.exec_module(oracle)
    for state in experiment['cases'].values():
        oracle.verify_state({'parameters': state['parameters'], 'state': state})
    def same_model(actual, expected, label):
        if isinstance(expected, bool): assert actual is expected, label
        elif isinstance(expected, (float, int)): oracle.close(actual, expected, label)
        elif isinstance(expected, dict):
            assert actual.keys() == expected.keys(), label
            for key in expected: same_model(actual[key], expected[key], label+'/'+key)
        elif isinstance(expected, list):
            assert len(actual) == len(expected), label
            for index, (a, e) in enumerate(zip(actual, expected)): same_model(a, e, label+'/'+str(index))
        else: assert actual == expected, label
    for name, payload in cases.items():
        if name == 'pixelSignature': continue
        oracle.verify_state(payload)
        if name != 'contextLossRetained': oracle.verify_scene(payload)
    for name, key in [('default','tension'),('-0.1','compression'),('0','rest'),('reversedRatio','reversed')]:
        same_model(cases[name]['state'], experiment['cases'][key], 'Serial browser/static case disagreement: '+name)
    assert not cases['coarse']['state']['converged'] and cases['fine']['state']['converged']
    assert cases['reset']['state'] == cases['contextLossRetained']['state'] == cases['contextRetry']['state'] == cases['mobile']['state'] == cases['default']['state']
    rejected = cases['rejectedGlobalVolume']; candidate = rejected['lastCandidate']
    assert rejected['state'] == cases['fine']['state'] and rejected['scene']['meshes'] == cases['fine']['scene']['meshes']
    assert candidate['accepted'] is False and math.isclose(candidate['totalVolumeRatio'], 1., abs_tol=1e-12)
    p = rejected['parameters']; ratios = [1.1, 1-.1/p['ratio']]
    total = 0.
    for actual, cell, ratio in zip(candidate['candidateCells'], rejected['state']['cells'], ratios):
        oracle.close(actual['J'], ratio, 'Counterexample local determinant')
        oracle.close(actual['currentBoundaryVolumeM3'], cell['referenceVolumeM3']*ratio, 'Counterexample measured local volume')
        oracle.close(actual['lateralStressPa'], p['mu']/cell['stretch']*(ratio-1), 'Counterexample lateral traction', absolute=2e-9)
        total += actual['currentBoundaryVolumeM3']
    oracle.close(total, rejected['state']['referenceVolumeM3'], 'Counterexample total volume cancellation')
    assert browser['fallback']['textControlsWork'] and browser['fallback']['staticFigureVisible'] and not browser['fallback']['javascriptErrors']
    cards = sum(len(read(name)['claims']) for name in manifest['proof_families'])
    assert browser['proof_cards'] == cards
    evidence = browser['proof_evidence']
    assert evidence['receipt_sha256'] == digest(out/'serial-real-proof-status.json')
    assert evidence['source_sha256'] == proof['source_sha256'] and evidence['claims_sha256'] == proof['claims_sha256']
    assert [card['id'] for card in evidence['cards']] == [claim['id'] for claim in proof['claims']]
    assert 'Property lab 6' in (out/'index.html').read_text()
    print('PASS_SERIAL_SOURCE_PROOF_GEOMETRY_VISUAL_BROWSER_BINDING')
    return browser

if __name__ == '__main__':
    check(sys.argv[1] if len(sys.argv)>1 else None)

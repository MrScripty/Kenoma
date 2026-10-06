"""Damaged-copy checks for the serial artifact, preserving the checked original."""
from pathlib import Path
import argparse, hashlib, json, shutil, tempfile
from check_serial_artifact import check, ROOT, digest

def run(destination, output):
    source = Path(destination).resolve(); out = Path(output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    check(source)
    manifest = json.loads((source/'build-manifest.json').read_text())
    receipt = json.loads((source/'serial-qa/receipt.json').read_text())
    required = {'build-manifest.json', 'serial-experiment.json', 'serial-qa/receipt.json', 'proofs/SerialSpecimenReal.lean', 'proofs/serial-specimen-real-claims.json'} | set(manifest['proof_families']) | set(manifest['serial_outputs']) | set(receipt['delivered_input_sha256']) | {'serial-qa/'+name for name in receipt['output_sha256']}
    before = {name: digest(source/name) for name in required}
    scratch = ROOT/'.artifact-tmp'; scratch.mkdir(exist_ok=True)
    results = []
    cases = ['missing-browser-receipt','stale-manifest-binding','forged-rendered-local-volume','forged-local-constraint-rejection','rehashed-false-static-geometry','missing-real-claim']
    for name in cases:
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            copy = Path(temporary)
            for path in required:
                target = copy/path; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source/path, target)
            rp = copy/'serial-qa/receipt.json'; r = json.loads(rp.read_text())
            if name == 'missing-browser-receipt': rp.unlink()
            elif name == 'stale-manifest-binding':
                r['build_manifest_sha256'] = '0'*64; rp.write_text(json.dumps(r))
            elif name in ['forged-rendered-local-volume','forged-local-constraint-rejection']:
                path = copy/'serial-qa/observed-states.json'; states = json.loads(path.read_text())
                if name == 'forged-rendered-local-volume':
                    mesh = states['default']['scene']['meshes'][0]
                    # Alter an actual uploaded coordinate; leave correct reported
                    # state J and volume untouched, then rehash both saved copies.
                    if isinstance(mesh['positions'][0], list): mesh['positions'][0][1] *= 1.1
                    else: mesh['positions'][1] *= 1.1
                else:
                    states['rejectedGlobalVolume']['lastCandidate']['candidateCells'][0]['J'] = 1.
                path.write_text(json.dumps(states))
                r['observed']['cases'] = states
                r['output_sha256']['observed-states.json'] = digest(path)
                rp.write_text(json.dumps(r))
            elif name == 'rehashed-false-static-geometry':
                path = copy/'assets/property-serial.svg'
                path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Incorrect specimen</text></svg>')
                m = json.loads((copy/'build-manifest.json').read_text())
                m['serial_outputs']['assets/property-serial.svg'] = digest(path)
                (copy/'build-manifest.json').write_text(json.dumps(m))
                r['build_manifest_sha256'] = digest(copy/'build-manifest.json'); rp.write_text(json.dumps(r))
            else:
                path = copy/'serial-real-proof-status.json'; p = json.loads(path.read_text())
                p['claims'].pop(); path.write_text(json.dumps(p))
            try: check(copy)
            except (AssertionError, FileNotFoundError) as error:
                results.append({'case': name, 'detected': True, 'reason': str(error) or 'Required proof/receipt coverage rejected'})
            else: raise RuntimeError('Damaged serial artifact unexpectedly passed: '+name)
    assert before == {name: digest(source/name) for name in required}, 'Checked original changed during negative controls'
    out.write_text(json.dumps({'result':'PASS_SIX_DAMAGED_SERIAL_ARTIFACT_CONTROLS','source_manifest_sha256':digest(source/'build-manifest.json'),'checker_sha256':digest(ROOT/'tools/check_serial_artifact.py'),'qualifier_sha256':digest(Path(__file__)),'original_unchanged':True,'cases':results}, indent=2)+'\n')
    print('PASS six damaged-copy serial artifact controls')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path); parser.add_argument('output', type=Path)
    args = parser.parse_args(); run(args.site, args.output)

"""Review-only fresh kernel qualification; the ordinary build integration is separate."""
from pathlib import Path
import hashlib, json, os, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from check_property_proofs import check

OUT = Path(__file__).resolve().parent
target = OUT / 'qualification.json'
target.unlink(missing_ok=True)
existing = check()
dependency = ROOT / '.tools/mathlib4'
identity = {
    'actual_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=dependency, text=True).strip(),
    'manifest_sha256': hashlib.sha256((dependency / 'lake-manifest.json').read_bytes()).hexdigest(),
    'source_pristine': not subprocess.check_output(['git', 'status', '--porcelain'], cwd=dependency, text=True).strip(),
    'packages': [],
}
if (identity['actual_commit'] != existing['mathlib']['commit'] or
        identity['manifest_sha256'] != existing['mathlib']['manifest_sha256'] or
        not identity['source_pristine']):
    raise RuntimeError('Unqualified mathlib identity')
for package in json.loads((dependency / 'lake-manifest.json').read_text())['packages']:
    if package['type'] != 'git':
        continue
    directory = dependency / '.lake/packages' / package['name']
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=directory, text=True).strip()
    pristine = not subprocess.check_output(['git', 'status', '--porcelain'], cwd=directory, text=True).strip()
    if actual != package['rev'] or not pristine:
        raise RuntimeError('Unqualified package identity: ' + package['name'])
    identity['packages'].append({'name': package['name'], 'expected_commit': package['rev'],
                                'actual_commit': actual, 'source_pristine': pristine})
source = ROOT / 'proofs/SerialSpecimenReal.lean'
manifest = ROOT / 'proofs/serial-specimen-real-claims.json'
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
source_hash, manifest_hash = digest(source), digest(manifest)
body = re.sub(r'/\-.*?\-/', '', source.read_text(), flags=re.S)
if re.search(r'\b(sorry|admit|axiom|native_decide)\b', body):
    raise RuntimeError('Forbidden proof admission')
claims = json.loads(manifest.read_text())
if len(claims) != 12 or len({c['theorem'] for c in claims}) != 12:
    raise RuntimeError('Unexpected registered proof coverage')
if any('status' in claim for claim in claims):
    raise RuntimeError('Manually assigned claim status')
env = os.environ.copy()
env['PATH'] = str(ROOT / '.tools/lean-4.19.0-linux/bin') + os.pathsep + env['PATH']
env['MATHLIB_CACHE_DIR'] = str(ROOT / '.tools/mathlib-cache')
command = ['lake', '--no-cache', 'env', 'lean', '-DwarningAsError=true', str(source)]
result = subprocess.run(command, cwd=dependency, env=env, capture_output=True, text=True)
transcript = result.stdout + result.stderr
(OUT / 'lean-check.txt').write_text(transcript)
print(transcript, end='')
if result.returncode:
    raise SystemExit(result.returncode)
if (digest(source), digest(manifest)) != (source_hash, manifest_hash):
    raise RuntimeError('Qualification input changed during compilation')
for claim in claims:
    match = re.search(rf"'{re.escape(claim['theorem'])}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", transcript)
    if not match:
        raise RuntimeError('Missing kernel dependency report: ' + claim['theorem'])
    axioms = [item.strip() for item in (match.group(1) or '').split(',') if item.strip()]
    if not set(axioms) <= {'propext', 'Quot.sound', 'Classical.choice'}:
        raise RuntimeError('Unapproved kernel dependency')
    claim.update(status='checked', axioms=axioms)
for name in ['property-proof-status.json', 'property-lean-check.txt']:
    (OUT / name).write_bytes((ROOT / 'dist' / name).read_bytes())
payload = {
    'schema': 1, 'result': 'PASS_FRESH_REAL_SERIAL_KERNEL',
    'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'source': 'proofs/SerialSpecimenReal.lean', 'source_sha256': source_hash,
    'claims_sha256': manifest_hash, 'lean_version': existing['lean_version'],
    'mathlib': existing['mathlib'], 'mathlib_identity': identity, 'command': command, 'cwd': str(dependency),
    'claims': claims,
    'existing_property_receipt_sha256': digest(ROOT / 'dist/property-proof-status.json'),
    'scope': 'Real local homogeneous incompressible serial-block law only; no runtime, numerical, global-stability or biological qualification.',
}
target.write_text(json.dumps(payload, indent=2) + '\n')
print(f'PASS: {len(claims)} fresh local serial-specimen Real declarations')

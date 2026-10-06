from pathlib import Path
import hashlib, json, os, re, subprocess, sys

root = Path('/tmp/kenoma-real-constitutive/education')
sys.path.insert(0, str(root / 'tools'))
from check_property_proofs import check

out = root / 'review/real-constitutive' / sys.argv[1]
out.mkdir(parents=True, exist_ok=True)
target = out / 'qualification.json'
target.unlink(missing_ok=True)
existing = check()
dependency = root / '.tools/mathlib4'
lock = json.loads((root / 'proofs/mathlib-lock.json').read_text())
packages = []
for package in json.loads((dependency / 'lake-manifest.json').read_text())['packages']:
    if package['type'] != 'git':
        continue
    directory = dependency / '.lake/packages' / package['name']
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=directory, text=True).strip()
    if actual != package['rev'] or subprocess.check_output(['git', 'status', '--porcelain'], cwd=directory, text=True).strip():
        raise RuntimeError('Unqualified locked package: ' + package['name'])
    packages.append({'name': package['name'], 'expected_commit': package['rev'], 'actual_commit': actual, 'source_pristine': True})
source = root / 'proofs/ActuatorConstitutiveReal.lean'
manifest = root / 'proofs/actuator-real-claims.json'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source_digest = digest(source)
body = re.sub(r'/\-.*?\-/', '', source.read_text(), flags=re.S)
if re.search(r'\b(sorry|admit|axiom|native_decide)\b', body):
    raise RuntimeError('Forbidden proof admission')
claims = json.loads(manifest.read_text())
if len({c['theorem'] for c in claims}) != len(claims):
    raise RuntimeError('Duplicate registered theorem')
env = os.environ.copy()
env['PATH'] = str(root / '.tools/lean-4.19.0-linux/bin') + os.pathsep + env['PATH']
env['MATHLIB_CACHE_DIR'] = str(root / '.tools/mathlib-cache')
command = ['lake', '--no-cache', 'env', 'lean', '-DwarningAsError=true', str(source)]
result = subprocess.run(command, cwd=dependency, env=env, capture_output=True, text=True)
transcript = result.stdout + result.stderr
(out / 'lean-check.txt').write_text(transcript)
print(transcript, end='')
if result.returncode:
    raise SystemExit(result.returncode)
if digest(source) != source_digest:
    raise RuntimeError('Source changed during qualification')
for claim in claims:
    pattern = rf"'{re.escape(claim['theorem'])}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)"
    match = re.search(pattern, transcript)
    if not match:
        raise RuntimeError('Missing kernel dependency report: ' + claim['theorem'])
    axioms = [x.strip() for x in (match.group(1) or '').split(',') if x.strip()]
    if not set(axioms) <= {'propext', 'Quot.sound', 'Classical.choice'}:
        raise RuntimeError('Unapproved axiom dependency: ' + claim['theorem'])
    claim.update(status='checked', axioms=axioms)
payload = {'schema': 1, 'result': 'PASS_FRESH_REAL_ACTUATOR_KERNEL',
    'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
    'source': 'proofs/ActuatorConstitutiveReal.lean', 'source_sha256': source_digest,
    'claims_sha256': digest(manifest), 'lean_version': existing['lean_version'],
    'mathlib': lock, 'verified_packages': packages,
    'command': command, 'cwd': str(dependency), 'claims': claims,
    'existing_real_property_receipt_sha256': digest(root / 'dist/property-proof-status.json'),
    'scope': 'Real mathematical constitutive laws; no floating-point refinement or biological validation.'}
target.write_text(json.dumps(payload, indent=2) + '\n')
(out / 'property-proof-status.json').write_bytes((root / 'dist/property-proof-status.json').read_bytes())
(out / 'property-lean-check.txt').write_bytes((root / 'dist/property-lean-check.txt').read_bytes())
print(f'PASS: {len(claims)} fresh real actuator declarations; receipt {target}')

"""Fresh kernel check in an isolated packet; never writes book proof receipts."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/activation-equality-proofs-v1'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(directory, *args):
    return subprocess.check_output(['git', *args], cwd=directory, text=True).strip()


def audit_source(source, claims):
    # Lean block comments nest; discard comments without hiding declarations.
    body, depth, i = [], 0, 0
    while i < len(source):
        if source[i:i+2] == '/-':
            depth += 1
            i += 2
        elif depth and source[i:i+2] == '-/':
            depth -= 1
            i += 2
        elif not depth and source[i:i+2] == '--':
            end = source.find('\n', i)
            i = len(source) if end == -1 else end
        else:
            if not depth:
                body.append(source[i])
            i += 1
    if depth:
        raise RuntimeError('Unclosed Lean comment')
    body = ''.join(body)
    if re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', body):
        raise RuntimeError('Forbidden proof admission or unchecked execution')
    declared = ['KenomaActivation.' + x for x in re.findall(r'^theorem\s+(\w+)', body, re.M)]
    printed = re.findall(r'^#print axioms\s+(\S+)', body, re.M)
    expected = [x['theorem'] for x in claims]
    if len(set(expected)) != len(expected) or declared != expected or printed != expected:
        raise RuntimeError('Theorem, claim and dependency-report inventories differ')
    return body


def audit_transcript(transcript, claims):
    result = []
    for claim in claims:
        pattern = rf"'{re.escape(claim['theorem'])}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)"
        matches = list(re.finditer(pattern, transcript))
        if len(matches) != 1:
            raise RuntimeError('Missing or duplicate kernel report: ' + claim['theorem'])
        axioms = [x.strip() for x in (matches[0].group(1) or '').split(',') if x.strip()]
        if not set(axioms) <= ALLOWED_AXIOMS:
            raise RuntimeError('Unexpected kernel dependency: ' + claim['theorem'])
        result.append(dict(claim, status='checked', axioms=axioms))
    return result


def check(tools):
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = OUT / 'kernel-check.json'
    receipt.unlink(missing_ok=True)
    source = ROOT / 'proofs/ActivationEquality.lean'
    claim_file = ROOT / 'proofs/activation-equality-claims.json'
    claims = json.loads(claim_file.read_text())
    audit_source(source.read_text(), claims)
    dependency = tools / 'mathlib4'
    lock = json.loads((ROOT / 'proofs/mathlib-lock.json').read_text())
    if git(dependency, 'rev-parse', 'HEAD') != lock['commit']:
        raise RuntimeError('Pinned mathlib revision differs')
    if git(dependency, 'status', '--porcelain'):
        raise RuntimeError('Modified mathlib source')
    if sha(dependency / 'lake-manifest.json') != lock['manifest_sha256']:
        raise RuntimeError('Pinned dependency manifest differs')
    dependencies = []
    for package in json.loads((dependency / 'lake-manifest.json').read_text())['packages']:
        if package['type'] == 'git':
            path = dependency / '.lake/packages' / package['name']
            revision = git(path, 'rev-parse', 'HEAD')
            if revision != package['rev'] or git(path, 'status', '--porcelain'):
                raise RuntimeError('Modified or unpinned dependency: ' + package['name'])
            dependencies.append({'name': package['name'], 'commit': revision})
    env = os.environ.copy()
    env['PATH'] = str(tools / 'lean-4.19.0-linux/bin') + os.pathsep + env['PATH']
    version = subprocess.check_output(['lean', '--version'], env=env, text=True).strip()
    if 'version 4.19.0,' not in version:
        raise RuntimeError('Pinned Lean 4.19.0 required')
    command = ['lake', 'env', 'lean', '-DwarningAsError=true', str(source)]
    run = subprocess.run(command, cwd=dependency, env=env, capture_output=True, text=True)
    transcript = run.stdout + run.stderr
    (OUT / 'lean-check.log').write_text(transcript)
    if run.returncode:
        raise RuntimeError('Lean failed; see isolated lean-check.log')
    checked = audit_transcript(transcript, claims)
    statements = re.findall(r'(?ms)^theorem\s+.*?(?=\s*:= by)', source.read_text())
    source_paths = [
        'data/millard-reference-v1/upstream/MuscleFirstOrderActivationDynamicModel.cpp',
        'data/millard-reference-v1/upstream/manifest.json',
        'tools/millard_reference_benchmark.py',
        'tools/run_activation_equality_diagnostic.py',
        'web/vertical-force-model.js',
    ]
    payload = {
        'schema': 1, 'compiler_exit_code': run.returncode, 'lean_version': version,
        'mathlib': lock, 'dependencies': dependencies,
        'command': command, 'working_directory': str(dependency),
        'source': str(source.relative_to(ROOT)), 'source_sha256': sha(source),
        'claims_sha256': sha(claim_file), 'checker_sha256': sha(Path(__file__)),
        'transcript_sha256': sha(OUT / 'lean-check.log'),
        'equation_sources': [{'path': p, 'sha256': sha(ROOT / p)} for p in source_paths],
        'exact_statements': statements, 'claims': checked,
        'scope': 'Exact real algebra and fixed-activation excitation continuity; no numerical refinement or ODE solution theorem.',
    }
    receipt.write_text(json.dumps(payload, indent=2) + '\n')
    print(f'Fresh Lean kernel check: {len(checked)} declarations; exit {run.returncode}; {version}')
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tools', type=Path, default=ROOT / '.tools')
    check(parser.parse_args().tools.resolve())

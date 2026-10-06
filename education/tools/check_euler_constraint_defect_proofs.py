"""Fresh kernel check in an isolated packet; never writes book proof receipts."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/euler-constraint-defect-proofs-v1/review'
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
    declared = ['KenomaEuler.' + x for x in re.findall(r'^theorem\s+(\w+)', body, re.M)]
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


def check(tools, freeze):
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = OUT / 'kernel-check.json'
    if receipt.exists() or (OUT / 'lean-check.log').exists():
        raise RuntimeError('Refuse to overwrite an existing compiler receipt/log')
    source = ROOT / 'proofs/EulerConstraintDefect.lean'
    claim_file = ROOT / 'proofs/euler-constraint-defect-claims.json'
    claims = json.loads(claim_file.read_text())
    audit_source(source.read_text(), claims)
    freeze_tree = git(ROOT.parent, 'rev-parse', freeze + '^{tree}')
    for item in [source, claim_file, Path(__file__)]:
        name = str(item.relative_to(ROOT.parent))
        original = subprocess.check_output(['git', 'show', freeze + ':' + name], cwd=ROOT.parent)
        if item.read_bytes() != original:
            raise RuntimeError('Proof preparation differs from frozen source: ' + name)
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
        'tools/run_filippov_bounded_experiment.py',
        'tools/filippov_source_worker.mjs',
        'web/vertical-force-model.js',
        'research/mechanical-closure/antiwindup-continuation-analysis.md',
        'tools/vertical_force_reference.py',
        'data/millard-reference-v1/upstream/manifest.json',
        'research/mechanical-closure/filippov-bounded-experiment-results.md',
    ]
    payload = {
        'schema': 1, 'source_freeze_commit': freeze, 'source_freeze_tree': freeze_tree, 'compiler_exit_code': run.returncode, 'lean_version': version,
        'mathlib': lock, 'dependencies': dependencies,
        'compiler_binary_sha256': sha(tools / 'lean-4.19.0-linux/bin/lean'),
        'lake_binary_sha256': sha(tools / 'lean-4.19.0-linux/bin/lake'),
        'command': command, 'working_directory': str(dependency),
        'source': str(source.relative_to(ROOT)), 'source_sha256': sha(source),
        'claims_sha256': sha(claim_file), 'checker_sha256': sha(Path(__file__)),
        'transcript_sha256': sha(OUT / 'lean-check.log'),
        'equation_sources': [{'path': p, 'sha256': sha(ROOT / p)} for p in source_paths],
        'exact_statements': statements, 'claims': checked,
        'scope': 'Exact local real scalar Euler defect algebra and conditional remainder scaling; supplied slope, no derivative-kernel/C2 proof, floating-point, integration, convergence, accepted-state or anatomy theorem.',
        'sliding_steps_executed': 0, 'trajectory_states_added': 0, 'book_receipts_written': False,
    }
    receipt.write_text(json.dumps(payload, indent=2) + '\n')
    print(f'Fresh Lean kernel check: {len(checked)} declarations; exit {run.returncode}; {version}')
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tools', type=Path, default=ROOT / '.tools')
    parser.add_argument('--freeze-commit', required=True)
    args = parser.parse_args()
    check(args.tools.resolve(), args.freeze_commit)

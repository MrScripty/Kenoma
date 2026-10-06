"""Standalone research check; deliberately absent from publication claim registries."""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess

from bootstrap_proofwidgets import bootstrap, print_log_tail

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'proofs/MixedLogVolume.lean'
DEPENDENCY = ROOT / '.tools/mathlib4'
LOCK_FILE = ROOT / 'proofs/mathlib-lock.json'
THEOREMS = (
    'inner_comm', 'inner_add_right', 'inner_add_left',
    'inner_sub_right', 'inner_sub_left', 'inner_smul_right',
    'inner_smul_left', 'normSq_nonneg', 'normSq_eq_zero_iff', 'normSq_sub',
    'normSq_smul', 'project_eq_self_iff', 'project_idempotent', 'inner_project',
    'project_self_adjoint',
    'optimizer_mem', 'square_completion', 'optimizer_value',
    'objective_le_condensed', 'value_eq_iff_optimizer', 'unique_maximizer',
    'pythagoras', 'pointwise_minus_condensed', 'condensed_nonneg', 'gap_nonneg',
    'gap_zero_iff_represented', 'nested_energy_monotone',
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(path, *args):
    return subprocess.check_output(['git', *args], cwd=path, text=True).strip()


def environment():
    env = os.environ.copy()
    env['PATH'] = str(ROOT / '.tools/lean-4.19.0-linux/bin') + os.pathsep + env['PATH']
    env['MATHLIB_CACHE_DIR'] = str(ROOT / '.tools/mathlib-cache')
    env['MATHLIB_NO_CACHE_ON_UPDATE'] = '1'
    return env


def verify_dependencies(lock):
    if git(DEPENDENCY, 'rev-parse', 'HEAD') != lock['commit']:
        raise RuntimeError('Unexpected mathlib commit')
    if git(DEPENDENCY, 'status', '--porcelain'):
        raise RuntimeError('Modified mathlib sources')
    manifest = DEPENDENCY / 'lake-manifest.json'
    if digest(manifest) != lock['manifest_sha256']:
        raise RuntimeError('Unexpected dependency manifest')
    if (ROOT / 'proofs/lean-toolchain').read_text().strip() != lock['toolchain']:
        raise RuntimeError('Toolchain lock mismatch')
    identities = {}
    for package in json.loads(manifest.read_text())['packages']:
        if package['type'] != 'git':
            raise RuntimeError('Unrecognized dependency type')
        path = DEPENDENCY / '.lake/packages' / package['name']
        revision = git(path, 'rev-parse', 'HEAD')
        if revision != package['rev'] or git(path, 'status', '--porcelain'):
            raise RuntimeError('Modified/unpinned dependency: ' + package['name'])
        identities[package['name']] = revision
    return identities


def uncomment(text):
    """Remove nested Lean comments, retaining line breaks for import parsing."""
    output, i, depth = [], 0, 0
    while i < len(text):
        if text[i:i + 2] == '/-':
            depth += 1
            i += 2
        elif depth and text[i:i + 2] == '-/':
            depth -= 1
            i += 2
        elif depth:
            if text[i] == '\n':
                output.append('\n')
            i += 1
        elif text[i] == '"':
            # Quoted comment delimiters in upstream tactic sources are literals.
            output.append(text[i])
            i += 1
            while i < len(text):
                char = text[i]
                output.append(char)
                i += 1
                if char == '\\' and i < len(text):
                    output.append(text[i])
                    i += 1
                elif char == '"':
                    break
        elif text[i:i + 2] == '--':
            end = text.find('\n', i)
            i = len(text) if end < 0 else end
        else:
            output.append(text[i])
            i += 1
    if depth:
        raise RuntimeError('Unclosed comment')
    return ''.join(output)


def imports(source):
    return re.findall(r'^\s*import\s+(\S+)', uncomment(source.read_text()), re.M)


def build_dependencies(env):
    """Same two-job source-build strategy as the existing property proof tool."""
    bootstrap(DEPENDENCY, env)
    roots = [DEPENDENCY, *sorted((DEPENDENCY / '.lake/packages').iterdir())]
    graph = {}

    def source(name):
        for root in roots:
            path = root / (name.replace('.', '/') + '.lean')
            if path.is_file():
                return path
        if name.split('.')[0] in ('Init', 'Lean', 'Std', 'Lake'):
            return None
        raise RuntimeError('Unresolved source: ' + name)

    def visit(name):
        if name in graph:
            return
        path = source(name)
        if path is None:
            return
        graph[name] = set()
        for line in uncomment(path.read_text()).splitlines():
            if not line.strip() or line.strip() == 'prelude':
                continue
            match = re.match(r'^\s*(?:public\s+)?import\s+(.*)', line)
            if not match:
                break
            for dep in match[1].split():
                if source(dep) is not None:
                    graph[name].add(dep)
                    visit(dep)

    for name in imports(SOURCE):
        visit(name)
    logs = ROOT / '.tools/mixed-volume-mathlib-source-logs'
    logs.mkdir(parents=True, exist_ok=True)

    def build(name):
        log = logs / (name + '.txt')
        with log.open('w') as stream:
            result = subprocess.run(['lake', '--no-cache', 'build', name],
                                    cwd=DEPENDENCY, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT)
        if result.returncode:
            print_log_tail(log)
            raise RuntimeError('Dependency source build failed: ' + name)

    done, pending, jobs = set(), set(graph), {}
    print('SOURCE_MODULE_COUNT', len(graph), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        while pending or jobs:
            ready = sorted(name for name in pending if graph[name] <= done)
            for name in ready[:2 - len(jobs)]:
                jobs[pool.submit(build, name)] = name
                pending.remove(name)
            if not jobs:
                raise RuntimeError('Blocked import graph')
            finished, _ = concurrent.futures.wait(
                jobs, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in finished:
                name = jobs.pop(future)
                future.result()
                done.add(name)
                if len(done) % 25 == 0 or not pending:
                    print('SOURCE_PROGRESS', len(done), len(graph), name, flush=True)
    print('SOURCE_BUILD_COMPLETE', len(done), flush=True)


def check(output, prepare):
    output.mkdir(parents=True, exist_ok=True)
    receipt = output / 'receipt.json'
    receipt.unlink(missing_ok=True)
    compiled = output.resolve() / 'MixedLogVolume.olean'
    compiled.unlink(missing_ok=True)
    lock = json.loads(LOCK_FILE.read_text())
    env = environment()
    if prepare:
        if not DEPENDENCY.exists():
            subprocess.run(['git', 'clone', '--depth', '1', '--branch', lock['tag'],
                            lock['repository'], str(DEPENDENCY)], check=True)
        subprocess.run(['lake', '--no-cache', 'env', 'lean', '--version'],
                       cwd=DEPENDENCY, env=env, check=True)
    identities = verify_dependencies(lock)
    version = subprocess.check_output(['lean', '--version'], env=env, text=True).strip()
    if 'version 4.19.0,' not in version:
        raise RuntimeError('Pinned Lean 4.19.0 required')
    if prepare:
        build_dependencies(env)
        verify_dependencies(lock)
    body = uncomment(SOURCE.read_text())
    if re.search(r'\b(sorry|admit|axiom|native_decide)\b', body):
        raise RuntimeError('Forbidden admission or native decision')
    actual = re.findall(r'^theorem\s+(\w+)\b', body, re.M)
    if actual != list(THEOREMS):
        raise RuntimeError('Theorem inventory differs; review the checker inventory')
    source_hash = digest(SOURCE)
    command = ['lake', '--no-cache', 'env', 'lean', '-DwarningAsError=true',
               '-R', str(SOURCE.parent),
               '-o', str(compiled), str(SOURCE)]
    result = subprocess.run(command, cwd=DEPENDENCY, env=env, capture_output=True, text=True)
    transcript = output / 'lean-check.txt'
    transcript.write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(transcript.read_text())
    if digest(SOURCE) != source_hash:
        raise RuntimeError('Proof source changed during compilation')
    reports = {}
    for name in THEOREMS:
        full = 'KenomaMixedVolume.' + name
        match = re.search(rf"'{re.escape(full)}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",
                          transcript.read_text())
        if not match:
            raise RuntimeError('Missing kernel dependency report: ' + full)
        axioms = [s.strip() for s in (match.group(1) or '').split(',') if s.strip()]
        if not set(axioms) <= {'propext', 'Quot.sound', 'Classical.choice'}:
            raise RuntimeError('Unapproved dependency: ' + full + ': ' + str(axioms))
        reports[full] = axioms
    verify_dependencies(lock)
    payload = {
        'schema': 1, 'result': 'PASS_RESEARCH_WEIGHTED_PROJECTION_ALGEBRA',
        'source_commit': git(ROOT, 'rev-parse', 'HEAD'),
        'source_files_match_commit': not bool(git(ROOT, 'status', '--porcelain', '--',
            'proofs/MixedLogVolume.lean', 'tools/check_mixed_volume_proofs.py',
            'research/mixed-log-volume-projection.md')),
        'source': 'education/proofs/MixedLogVolume.lean', 'source_sha256': source_hash,
        'checker_sha256': digest(Path(__file__).resolve()),
        'explanation_sha256': digest(ROOT / 'research/mixed-log-volume-projection.md'),
        'lean_version': version, 'mathlib': lock, 'dependencies': identities,
        'command': command, 'command_cwd': str(DEPENDENCY),
        'transcript_sha256': digest(transcript), 'olean_sha256': digest(compiled),
        'theorems': reports,
        'limitations': 'Exact conditional finite-vector algebra only; no numerical projector, derivatives, solver, continuum or anatomy certification.',
    }
    receipt.write_text(json.dumps(payload, indent=2) + '\n')
    print(f'Checked {len(reports)} research declarations with {version}')
    print('SOURCE_SHA256', source_hash)
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dependencies', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / '.tools/mixed-volume-check')
    args = parser.parse_args()
    check(args.output, args.build_dependencies)

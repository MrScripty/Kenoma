"""Bounded contribution provenance/dependency gate; never builds the book or anatomy.

All generated receipts and dependency checkouts must be outside the source tree.
The official mathlib cache is an explicit bounded trust boundary, not the full
book's all-dependencies-from-source gate. The existing contribution Lean checker
rechecks every dependency revision and pristine source before compiling claims.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CONTRIBUTION = 'education/contributions/architecture-force'
SUPPORT = (
    '.github/workflows/education.yml',
    'education/tools/qualify_architecture_force.py',
    'education/tests/architecture_force_browser.py',
    'education/tests/test_architecture_force_qualification.py',
    'education/research/architecture-force-qualification.md',
    'education/tools/install_lean.py', 'education/requirements.txt',
    'education/proofs/mathlib-lock.json', 'education/proofs/lean-toolchain',
    'education/web/anatomical-material.mjs',
)
CACHE_ROOTS = ('Mathlib/Data/Real/Basic.lean', 'Mathlib/Tactic/FieldSimp.lean',
               'Mathlib/Tactic/Ring.lean')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


def external(path, root=ROOT):
    path = path.resolve()
    require(not path.is_relative_to(root.resolve()), 'Output/dependencies must be outside checkout')
    return path


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def snapshot(expected_head, root=ROOT):
    require(re.fullmatch(r'[0-9a-f]{40}', expected_head), 'Expected exact head SHA required')
    head = git('rev-parse', 'HEAD', cwd=root)
    require(head == expected_head, 'Checked-out commit differs from expected PR head')
    require(not git('status', '--porcelain', '--untracked-files=all', cwd=root), 'Pristine source required')
    tracked = git('ls-files', '-z', cwd=root).split('\0')
    paths = sorted({p for p in tracked if p.startswith(CONTRIBUTION + '/')} | set(SUPPORT))
    require(len([p for p in paths if p.startswith(CONTRIBUTION + '/')]) == 13,
            'Expected the reviewed 13-file contribution')
    require(set(paths) <= set(tracked), 'Qualification inputs must be tracked')
    files = {p: {'sha256': sha256(root / p), 'bytes': (root / p).stat().st_size} for p in paths}
    return {'commit': head, 'git_tree': git('rev-parse', 'HEAD^{tree}', cwd=root), 'files': files}


def source(args):
    output = external(args.output)
    require(not (output / 'source.json').exists(), 'Refusing to reuse previous source receipt')
    receipt = snapshot(args.expected_head)
    receipt['github'] = {key: os.environ.get(key) for key in (
        'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT', 'GITHUB_EVENT_NAME',
        'GITHUB_WORKFLOW_REF', 'GITHUB_WORKFLOW_SHA')}
    write_json(output / 'source.json', receipt)
    print('Bound qualification inputs to checked-out commit ' + receipt['commit'])


def contribution_checker():
    spec = importlib.util.spec_from_file_location('architecture_force_lean', ROOT / CONTRIBUTION / 'check_lean.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_mathlib(mathlib, require_packages=True):
    checker = contribution_checker()
    lock = json.loads((ROOT / 'education/proofs/mathlib-lock.json').read_text())
    require(lock['commit'] == checker.PIN and lock['manifest_sha256'] == checker.MANIFEST,
            'Repository lock and contribution pins disagree')
    require(lock['repository'] == 'https://github.com/leanprover-community/mathlib4', 'Unexpected mathlib origin')
    require(git('rev-parse', 'HEAD', cwd=mathlib) == lock['commit'], 'Wrong mathlib revision')
    require(not git('status', '--porcelain', cwd=mathlib), 'Dirty mathlib sources')
    require(sha256(mathlib / 'lake-manifest.json') == lock['manifest_sha256'], 'Changed mathlib manifest')
    require((mathlib / 'lean-toolchain').read_text().strip() == lock['toolchain'], 'Changed mathlib toolchain')
    packages = json.loads((mathlib / 'lake-manifest.json').read_text())['packages']
    for package in packages:
        require(package['type'] == 'git' and re.fullmatch(r'[A-Za-z0-9_-]+', package['name']), 'Unsupported package')
        require(re.fullmatch(r'[0-9a-f]{40}', package['rev']), 'Unpinned dependency')
        require(package['url'].startswith(('https://github.com/leanprover/',
                                          'https://github.com/leanprover-community/')), 'Unexpected dependency origin')
        if require_packages:
            path = mathlib / '.lake/packages' / package['name']
            require(git('rev-parse', 'HEAD', cwd=path) == package['rev'], 'Wrong package: ' + package['name'])
            require(not git('status', '--porcelain', cwd=path), 'Dirty package: ' + package['name'])
            if package['name'] == 'proofwidgets':
                verify_release_tag(path, package['inputRev'], package['rev'])
    return lock, packages


def checkout(url, revision, path):
    require(not path.exists(), 'Refusing to overwrite dependency directory ' + str(path))
    subprocess.run(['git', 'init', str(path)], check=True)
    subprocess.run(['git', '-C', str(path), 'remote', 'add', 'origin', url], check=True)
    subprocess.run(['git', '-C', str(path), 'fetch', '--depth', '1', 'origin', revision], check=True)
    subprocess.run(['git', '-C', str(path), 'checkout', '--detach', revision], check=True)


def verify_release_tag(path, tag, revision):
    require(re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', tag), 'Unexpected release tag')
    require(git('rev-parse', f'refs/tags/{tag}^{{}}', cwd=path) == revision,
            'Release tag does not match pinned package revision')


def fetch_release_tag(path, tag, revision):
    # Lake 4.19 resolves release URLs with git describe --tags --exact-match.
    # A SHA-only shallow checkout lacks that metadata; never follow an unpinned tag.
    require(re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', tag), 'Unexpected release tag')
    subprocess.run(['git', '-C', str(path), 'fetch', '--depth', '1', 'origin',
                    f'refs/tags/{tag}:refs/tags/{tag}'], check=True)
    verify_release_tag(path, tag, revision)


def dependencies(args):
    mathlib, output = external(args.mathlib), external(args.output)
    lock = json.loads((ROOT / 'education/proofs/mathlib-lock.json').read_text())
    checker = contribution_checker()
    require(lock['repository'] == 'https://github.com/leanprover-community/mathlib4'
            and lock['commit'] == checker.PIN and lock['manifest_sha256'] == checker.MANIFEST,
            'Unexpected repository dependency lock')
    if not args.verify_only:
        checkout(lock['repository'], lock['commit'], mathlib)
        _, packages = verify_mathlib(mathlib, require_packages=False)
        for package in packages:
            path = mathlib / '.lake/packages' / package['name']
            checkout(package['url'], package['rev'], path)
            if package['name'] == 'proofwidgets':
                fetch_release_tag(path, package['inputRev'], package['rev'])
    lock, packages = verify_mathlib(mathlib)
    if not args.verify_only:
        env = os.environ.copy()
        env['PATH'] = str(args.lean_bin.resolve()) + os.pathsep + env['PATH']
        # Only these three import closures; never an unbounded `cache get`.
        subprocess.run(['lake', '--no-cache', 'exe', 'cache', 'get', *CACHE_ROOTS],
                       cwd=mathlib, env=env, check=True)
        verify_mathlib(mathlib)
    write_json(output / 'dependencies.json', {
        'mathlib_commit': lock['commit'], 'manifest_sha256': lock['manifest_sha256'],
        'packages': [{'name': p['name'], 'revision': p['rev']} for p in packages],
        'release_tags': [{'name': p['name'], 'tag': p['inputRev'], 'revision': p['rev']}
                         for p in packages if p['name'] == 'proofwidgets'],
        'cache_roots': list(CACHE_ROOTS), 'all_sources_pristine': True,
        'cache_fetched_in_this_command': not args.verify_only,
        'full_book_from_source_gate': False,
    })


def finish(args):
    output = external(args.output)
    before = json.loads((output / 'source.json').read_text())
    after = snapshot(args.expected_head)
    require(all(before[key] == after[key] for key in ('commit', 'git_tree', 'files')), 'Source changed during qualification')
    node = (output / 'node.txt').read_text()
    require(all(re.search(rf'^# {name} {count}$', node, re.M) for name, count in
                [('tests', 12), ('pass', 12), ('fail', 0), ('cancelled', 0), ('skipped', 0), ('todo', 0)]),
            'Expected twelve Node passes without skips or cancellations')
    symbolic = json.loads((output / 'symbolic.json').read_text())
    require(symbolic['count'] == 7 and len(symbolic['symbolic_identities']) == 7
            and all(v is True for v in symbolic['symbolic_identities'].values())
            and symbolic['performs_lean_compilation'] is False, 'Missing independent symbolic checks')
    proof = json.loads((output / 'formal/architecture-force-proof-status.json').read_text())
    checker = contribution_checker()
    require(proof['source_sha256'] == after['files'][CONTRIBUTION + '/ArchitectureForce.lean']['sha256'], 'Lean source mismatch')
    require(proof['mathlib_commit'] == checker.PIN and proof['manifest_sha256'] == checker.MANIFEST, 'Lean dependency mismatch')
    require(len(proof['claims']) == 6 and {c['theorem'] for c in proof['claims']} ==
            {'KenomaArchitectureForce.' + name for name in checker.THEOREMS}, 'Missing Lean contracts')
    require(all(c['status'] == 'checked' and set(c['axioms']) <= {'propext', 'Quot.sound', 'Classical.choice'}
                for c in proof['claims']) and proof['book_registered'] is False, 'Invalid Lean result')
    dependency = json.loads((output / 'dependencies.json').read_text())
    require(dependency['mathlib_commit'] == checker.PIN and dependency['manifest_sha256'] == checker.MANIFEST
            and dependency['cache_roots'] == list(CACHE_ROOTS) and dependency['all_sources_pristine'] is True
            and dependency['cache_fetched_in_this_command'] is True
            and dependency['full_book_from_source_gate'] is False, 'Missing bounded dependency receipt')
    browser = json.loads((output / 'browser/browser.json').read_text())
    require(browser['status'] == 'passed' and browser['no_javascript_static_fallback'] is True
            and [(r['width'], r['height']) for r in browser['checks']] == [(1280, 1000), (393, 852)], 'Missing browser checks')
    require(browser['visual_acceptance'] == 'pending human inspection', 'Automated checks cannot assert visual acceptance')
    controls = [f'{control}:{key}' for control in ('stretch', 'volume', 'packing', 'angle')
                for key in ('Home', 'End')]
    for row in browser['checks']:
        require(row['horizontal_overflow'] is False and row['range_keyboard_input'] is True
                and row['controls'] == controls and row['force_length_toggle'] is True
                and row['repeated_reset'] is True and row['local_links'] is True
                and row['browser_errors'] == [], 'Incomplete browser control evidence')
    expected_sources = {p for p in after['files'] if p.startswith(CONTRIBUTION + '/')}
    require(set(browser['source_sha256']) == expected_sources, 'Incomplete browser source binding')
    expected_captures = {'lab-1280-default.jpg', 'lab-1280-force-length.jpg',
                         'lab-393-default.jpg', 'lab-393-force-length.jpg', 'lab-393-no-javascript.jpg'}
    require(len(browser['captures']) == 5 and {c['file'] for c in browser['captures']} == expected_captures,
            'Missing desktop/mobile captures')
    for path, digest in browser['source_sha256'].items():
        require(after['files'][path]['sha256'] == digest, 'Browser source mismatch: ' + path)
    for capture in browser['captures']:
        capture_path = output / 'browser' / capture['file']
        require(capture['format'] == 'jpeg' and capture['quality'] == 85
                and capture_path.read_bytes().startswith(b'\xff\xd8\xff'), 'Expected JPEG85 capture')
        require(sha256(capture_path) == capture['sha256'], 'Capture mismatch')
    write_json(output / 'qualification.json', {
        'commit': after['commit'], 'source_manifest_sha256': sha256(output / 'source.json'),
        'node_tests': 12, 'symbolic_checks': 7, 'lean_contracts': 6,
        'browser_controls': 'passed', 'visual_acceptance': 'pending human inspection',
        'full_book_qualification': False, 'anatomical_qualification': False,
        'book_registration_changed': False, 'pages_deployment': False,
        'artifact_sha256': {str(p.relative_to(output)): sha256(p) for p in sorted(output.rglob('*'))
                            if p.is_file() and p.name != 'qualification.json'},
    })
    print('Bounded automated contribution checks passed; capture inspection remains required.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name, action in [('source', source), ('finish', finish), ('dependencies', dependencies)]:
        p = sub.add_parser(name)
        p.add_argument('--output', type=Path, required=True)
        p.set_defaults(action=action)
        if name == 'dependencies':
            p.add_argument('--mathlib', type=Path, required=True)
            p.add_argument('--lean-bin', type=Path, required=True)
            p.add_argument('--verify-only', action='store_true')
        else:
            p.add_argument('--expected-head', required=True)
    args = parser.parse_args()
    args.action(args)

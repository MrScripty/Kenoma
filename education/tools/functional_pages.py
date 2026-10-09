"""Assemble known historical URLs from fixed source, without research execution.

The old portable manifest is a qualification inventory, not a live-site read.
Original records are preserved privately; presentation derivatives have new hashes.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

from preserve_legacy_pages import REPO, PUBLISHED, TREE, inventory, no_symlinks, sha, git, output
from clean_reading_edition import PRIVATE, COORDINATION, TEXT_EXT

PLAN = REPO/'education/book/functional-pages.json'
CODE_LITERAL_EXCEPTIONS = {
    'data/anatomical-arm-v1/audit/contact-missed-soft-v3/tools/anatomical-contact-experiment.mjs': ['/tmp/'],
    'data/anatomical-arm-v1/audit/release-source-transition-v1/tools/anatomical-release-refinement-experiment.mjs': ['/tmp/'],
    'standalone/pressure-projection-lab-check.py': ['http://127.0.0.1'],
}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n')


def dependencies(directory):
    if os.environ.get('ESBUILD_BINARY_PATH'): raise ValueError('Unsealed esbuild override is not supported')
    directory = Path(directory).resolve()
    versions = {name: json.loads((directory/name/'package.json').read_text())['version'] for name in ['three', 'esbuild']}
    expected = json.loads(PLAN.read_text())['renderer_dependencies']
    if any(versions[n] != expected[n] for n in versions): raise ValueError('Static dependency version mismatch')
    files = {str(p.relative_to(directory)): sha(p.read_bytes()) for p in sorted(directory.rglob('*')) if p.is_file()}
    # Package launchers may be symlinks; seal their resolved bytes as well.
    if not files or not (directory/'.bin/esbuild').is_file(): raise ValueError('Missing static bundler')
    packages = {}
    for line in (REPO/'education/functional-requirements.lock').read_text().splitlines():
        name, version = line.split('==')
        packages[name] = importlib.metadata.version(name)
        if packages[name] != version: raise ValueError('Static plotting dependency mismatch: '+name)
    return {'versions': versions, 'files': files, 'python_packages': packages}


def candidate_sources():
    paths = git('ls-files', 'education/tools', 'education/web/functional-reader-boot.mjs',
                'education/web/archive-inspector-boot.mjs', 'education/web/functional-presentation.css', 'education/book/functional-pages.json',
                'education/functional-requirements.lock', '.github/workflows/reading-edition.yml').decode().splitlines()
    candidate = {}
    for name in paths:
        raw = git('show', 'HEAD:'+name)
        if (REPO/name).is_symlink() or (REPO/name).read_bytes() != raw: raise ValueError('Candidate source changed: '+name)
        candidate[name] = {'blob': git('rev-parse', 'HEAD:'+name).decode().strip(), 'sha256': sha(raw)}
    return candidate


def seal(destination, node_modules):
    destination = output(destination)
    if destination.exists(): raise FileExistsError(destination)
    if git('status', '--porcelain'): raise ValueError('Commit candidate before sealing')
    plan = json.loads(PLAN.read_text())
    if git('rev-parse', PUBLISHED+'^{tree}').decode().strip() != TREE: raise ValueError('Canonical tree changed')
    m = inventory()
    missing = set(m['missing']); core = set(plan['missing_presentation_paths'])
    review = sorted(missing-core)
    if len(core) != 32 or len(review) != 228 or any(not n.startswith(tuple(plan['unavailable_review_prefixes'])) for n in review):
        raise ValueError('Functional contract does not classify every missing historical path')
    write(destination, {'kind': 'PINNED_FUNCTIONAL_PAGES_INPUTS',
        'candidate_commit': git('rev-parse', 'HEAD').decode().strip(),
        'candidate_tree': git('rev-parse', 'HEAD^{tree}').decode().strip(),
        'plan_sha256': sha(PLAN.read_bytes()), 'candidate_sources': candidate_sources(),
        'canonical_commit': PUBLISHED, 'canonical_tree': TREE,
        'qualification_revision': plan['qualification_revision'],
        'historical_inventory': m, 'unavailable_review_paths': review,
        'dependencies': dependencies(node_modules),
        'proof_compilation': 'UNRUN', 'held_campaigns_executed': False,
        'live_root_read': False, 'publication': 'NOT_EXECUTED'})
    destination.chmod(0o444)


def verify(manifest, node_modules):
    m = json.loads(Path(manifest).read_text())
    plan = json.loads(PLAN.read_text())
    if (m['canonical_commit'], m['canonical_tree'], m['qualification_revision']) != (PUBLISHED, TREE, plan['qualification_revision']):
        raise ValueError('Historical identity differs from the fixed contract')
    expected = inventory()
    if m['historical_inventory'] != expected:
        raise ValueError('Historical inventory differs from fixed Git evidence')
    core = set(plan['missing_presentation_paths'])
    review = sorted(set(expected['missing'])-core)
    if len(core) != 32 or len(review) != 228 or m['unavailable_review_paths'] != review:
        raise ValueError('Historical path classification differs from the fixed contract')
    if (m['candidate_commit'], m['candidate_tree']) != tuple(git('rev-parse', 'HEAD', 'HEAD^{tree}').decode().splitlines()):
        raise ValueError('Candidate identity differs from seal')
    if git('status', '--porcelain') or sha(PLAN.read_bytes()) != m['plan_sha256']: raise ValueError('Candidate is not clean/sealed')
    if candidate_sources() != m['candidate_sources']: raise ValueError('Candidate source set or bytes differ from fixed Git evidence')
    if dependencies(node_modules) != m['dependencies']: raise ValueError('Static dependencies changed after seal')
    if git('rev-parse', PUBLISHED+'^{tree}').decode().strip() != m['canonical_tree']: raise ValueError('Canonical source changed')
    return m


def export_source(destination):
    destination.mkdir()
    with tempfile.TemporaryFile() as archive:
        subprocess.run(['git', 'archive', PUBLISHED, 'education'], cwd=REPO, stdout=archive, check=True)
        archive.seek(0)
        with tarfile.open(fileobj=archive) as tar: tar.extractall(destination, filter='data')
    no_symlinks(destination)


def original_url(f):
    source = f['git']
    return 'https://github.com/MrScripty/Kenoma/blob/'+source['commit']+'/'+source['path']


def bookkeeping(name, raw, missing):
    if Path(name).suffix != '.json': return False
    review = name.startswith(('qa/', 'real-proof-review/', 'property-book-review/', 'material-qa/', 'dissipative-qa/', 'serial-qa/'))
    text = raw.decode()
    stale = any(n in text or (review and Path(n).name in text) for n in missing)
    return stale or name == 'build-manifest.json'


def literal_exception(name, text):
    expected = CODE_LITERAL_EXCEPTIONS.get(name)
    return expected is not None and sorted(set(x.group(0) for x in PRIVATE.finditer(text))) == expected and not COORDINATION.search(text)


def availability_record(name, f, reason):
    return {'kind': 'HISTORICAL_RECORD_AVAILABILITY', 'path': name,
        'status': 'ORIGINAL_PRESERVED_NOT_A_FRESH_QUALIFICATION',
        'reason': reason, 'original_sha256': f['sha256'],
        'original_commit': PUBLISHED, 'original_blob': f['git']['blob'],
        'original_source': original_url(f), 'original_bytes_retained_in_private_archive': True,
        'unavailable_captures': 'See legacy-availability.json; no replacement captures or receipts were fabricated.'}


def install_gates(root):
    assets = root/'assets'
    for name in ['functional-reader-boot.mjs', 'archive-inspector-boot.mjs', 'functional-presentation.css']:
        shutil.copyfile(REPO/'education/web'/name, assets/name)
    page = root/'index.html'; text = page.read_text()
    old = '<script type="module" src="assets/app.js"></script>'
    if text.count(old) != 1: raise ValueError('Root startup script not uniquely identified')
    text = text.replace(old, '<script type="module" src="assets/functional-reader-boot.mjs"></script>')
    page.write_text(text.replace('</head>', '<link rel="stylesheet" href="assets/functional-presentation.css"></head>'))
    for entry in ['anatomical-arm', 'coupled-fixture']:
        page = root/entry/'index.html'; text = page.read_text()
        old = '<script type="module" src="inspect.js"></script>'
        if text.count(old) != 1: raise ValueError('Inspector startup script not uniquely identified')
        text = text.replace(old, '<script type="module" src="../assets/archive-inspector-boot.mjs" data-archive-entry="inspect.js"></script>')
        status = 'Loading the accepted resting receipt…' if entry == 'anatomical-arm' else 'Ready. Numerical controls work without starting 3D.'
        if text.count(status) != 1: raise ValueError('Static inspector status not uniquely identified')
        text = text.replace(status, 'Historical evidence is available. The archived computational model has not started.')
        page.write_text(text.replace('<main>', '<main><noscript><p>JavaScript is disabled. Read the historical evidence and download links; computational controls require an explicit model launch with JavaScript enabled.</p></noscript>', 1))
    for entry in ['anatomy-inspection', 'anatomical-arm', 'coupled-fixture']:
        page = root/entry/'index.html'; text = page.read_text()
        # These compact historical templates omit an explicit head closing tag.
        if text.count('</style>') != 1: raise ValueError('Inspector style not uniquely identified')
        page.write_text(text.replace('</style>', '</style><link rel="stylesheet" href="../assets/functional-presentation.css">'))


def build(manifest, reader, destination, node_modules):
    m = verify(manifest, node_modules)
    reader = Path(reader).resolve(); destination = output(destination)
    if destination.exists(): raise FileExistsError(destination)
    no_symlinks(reader)
    rm = json.loads((reader/'reading-manifest.json').read_text())
    if (rm['candidate_commit'], rm['candidate_tree']) != (m['candidate_commit'], m['candidate_tree']): raise ValueError('Reader was not built from this sealed candidate')
    actual = {str(p.relative_to(reader)) for p in reader.rglob('*') if p.is_file()}-{'reading-manifest.json'}
    if actual != set(rm['files']): raise ValueError('Reader file set changed')
    for name, h in rm['files'].items():
        if sha((reader/name).read_bytes()) != h: raise ValueError('Reader bytes changed: '+name)
    destination.mkdir(); private = destination/'private'; private.mkdir()
    root = destination/'pages'; root.mkdir(); archive = private/'original-records'; archive.mkdir()
    exported = private/'canonical-source'; export_source(exported)
    preserved = {}; wrappers = {}; exceptions = {}
    for name, f in m['historical_inventory']['files'].items():
        if not f['git']: continue
        raw = git('cat-file', 'blob', f['git']['blob'])
        if sha(raw) != f['sha256']: raise ValueError('Historical original changed: '+name)
        original = archive/name; original.parent.mkdir(parents=True, exist_ok=True); original.write_bytes(raw)
        target = root/name; target.parent.mkdir(parents=True, exist_ok=True)
        text = raw.decode() if Path(name).suffix in TEXT_EXT else ''
        exempt = literal_exception(name, text)
        privacy_hit = bool(PRIVATE.search(text) or COORDINATION.search(text)) and not exempt
        packaging = bookkeeping(name, raw, m['unavailable_review_paths'])
        if (privacy_hit or packaging) and name not in ['kenoma-mechanics.md']:
            reason = 'Historical packaging metadata names unavailable outputs.' if packaging else 'Historical operational text contains environment paths or coordination metadata.'
            record = availability_record(name, f, reason)
            if target.suffix == '.json': write(target, record)
            else: target.write_text(json.dumps(record, indent=2)+'\n')
            wrappers[name] = record
        else:
            target.write_bytes(raw); preserved[name] = f
            if exempt: exceptions[name] = {'sha256': f['sha256'], 'allowed_literals': CODE_LITERAL_EXCEPTIONS[name], 'reason': 'Immutable executable test/output-path literals, not current environment metadata.'}
    from functional_static import regenerate
    result = regenerate(exported, root, {'node_modules': str(Path(node_modules).resolve())})
    for name in json.loads(PLAN.read_text())['missing_presentation_paths']:
        if not (root/name).is_file(): raise ValueError('Missing regenerated presentation URL: '+name)
    # Reading presentation derivatives keep original numeric content; raw originals stay archived.
    (root/'kenoma-mechanics.md').write_text((archive/'kenoma-mechanics.md').read_text().replace('This worker verified', 'The audit verified'))
    shutil.copyfile(reader/'historical/kenoma-mechanics-reading.pdf', root/'kenoma-mechanics.pdf')
    for name in ['kenoma-mechanics.md', 'kenoma-mechanics.pdf']: preserved.pop(name, None)
    install_gates(root)
    shutil.copytree(reader, root/'reading-edition')
    availability = {'kind': 'FUNCTIONAL_HISTORICAL_URL_AVAILABILITY',
        'canonical_commit': PUBLISHED, 'canonical_tree': TREE,
        'known_inventory_revision': m['qualification_revision'],
        'live_root_read': False, 'coverage': 'Known source-based historical URLs; current live-site completeness unverified.',
        'unavailable_review_files': {n: {'historical_sha256': m['historical_inventory']['files'][n]['sha256'], 'status': 'UNAVAILABLE_NOT_RECREATED'} for n in m['unavailable_review_paths']},
        'public_historical_record_wrappers': wrappers,
        'historical_proof_and_numerical_receipts': 'Snapshot evidence only; no fresh proof or anatomical compilation/execution.',
        'later_research_results_included': False,
        'held_runtime_qualification': 'UNRUN; default startup gates do not initialize held calculations.'}
    write(root/'legacy-availability.json', availability)
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Historical evidence availability</title><body><main><h1>Historical evidence availability</h1><p>This reader reconstructs known URLs from fixed canonical sources. It does not establish the contents of the current live site.</p><p>Historical proof and numerical records describe their source snapshots. New proof compilation and archived computational models are not qualified by this release.</p><p>Unavailable review captures are not recreated. Operational and packaging records have explicit availability entries; original bytes remain bound to immutable Git sources.</p><p><a href="legacy-availability.json">File availability and original source bindings</a> · <a href="index.html">Historical reader</a> · <a href="reading-edition/index.html">Expanded reading edition</a></p></main></body></html>'
    (root/'legacy-availability.html').write_text(page)
    for name, f in preserved.items():
        if sha((root/name).read_bytes()) != f['sha256']: raise ValueError('Protected scientific/source bytes changed: '+name)
    for name, f in m['historical_inventory']['files'].items():
        if f['git'] and sha((archive/name).read_bytes()) != f['sha256']: raise ValueError('Original record archive changed')
    write(private/'construction.json', {'static': result, 'protected_public_files': preserved,
        'public_availability_wrappers': wrappers, 'privacy_literal_exceptions': exceptions,
        'original_record_count': len(preserved)+len(wrappers)+2,
        'input_manifest_sha256': sha(Path(manifest).read_bytes()),
        'proof_compilation': 'UNRUN', 'anatomical_execution': 'UNRUN', 'held_campaigns_executed': False,
        'publication': 'NOT_EXECUTED'})
    from qualify_functional_pages import qualify
    receipt = qualify(root, private, m, manifest)
    write(destination/'ci-diagnostics/functional-qualification.json', receipt)
    files = {str(p.relative_to(root)): sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file()}
    write(root/'functional-manifest.json', {'kind': 'SOURCE_BOUND_FUNCTIONAL_PAGES_OUTPUTS',
        'candidate_commit': m['candidate_commit'], 'candidate_tree': m['candidate_tree'],
        'input_manifest_sha256': sha(Path(manifest).read_bytes()), 'files': files,
        'qualification': receipt, 'live_root_read': False, 'publication': 'NOT_EXECUTED'})
    print(json.dumps({'candidate_commit': m['candidate_commit'], 'candidate_tree': m['candidate_tree'],
        'public_files': len(files)+1, 'pages': str(root), 'qualification': receipt}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('seal'); p.add_argument('manifest'); p.add_argument('--node-modules', required=True)
    p = sub.add_parser('build'); p.add_argument('manifest'); p.add_argument('reader'); p.add_argument('destination'); p.add_argument('--node-modules', required=True)
    args = parser.parse_args()
    if args.action == 'seal': seal(args.manifest, args.node_modules)
    else: build(args.manifest, args.reader, args.destination, args.node_modules)

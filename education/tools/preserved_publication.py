"""Recover the pinned, already-published book through immutable Git objects.

Only the official repository is fetched. The existing publication assembler
checks every preserved file and canonical source input before reuse.
"""
from contextlib import contextmanager
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PUBLICATION = REPO / '.github/publications/kenoma-20261009.json'
ASSEMBLER = REPO / '.github/scripts/assemble-preserved-book.py'
OFFICIAL_REPOSITORY = 'https://github.com/MrScripty/Kenoma.git'
DEFAULT_CACHE = ROOT / '.artifacts/teaching-preview-inputs'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains_commit(repository, commit):
    return subprocess.run(['git', '-C', str(repository), 'cat-file', '-e', commit + '^{commit}'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def object_repository(commit, cache, offline):
    if contains_commit(REPO, commit):
        return REPO
    objects = cache / 'objects.git'
    if objects.exists() and contains_commit(objects, commit):
        return objects
    if offline:
        raise RuntimeError('Pinned Git commit unavailable locally: ' + commit +
                           '. Run once without --offline to populate the ignored cache.')
    if not objects.exists():
        subprocess.run(['git', 'init', '--bare', '--quiet', str(objects)], check=True)
    print('Fetching existing publication Git commit ' + commit, flush=True)
    subprocess.run(['git', '-C', str(objects), 'fetch', '--no-tags', '--depth=1',
                    OFFICIAL_REPOSITORY, commit], check=True)
    if not contains_commit(objects, commit):
        raise RuntimeError('Fetch did not supply the pinned commit: ' + commit)
    return objects


def export(repository, commit, destination):
    """Export a clean snapshot, never the possibly modified current worktree."""
    archive = destination.with_suffix('.tar')
    subprocess.run(['git', '-C', str(repository), 'archive', '--format=tar',
                    '--output=' + str(archive), commit], check=True)
    try:
        with tarfile.open(archive) as stream:
            for member in stream.getmembers():
                if not (member.isfile() or member.isdir()):
                    raise ValueError('Publication snapshot contains a non-regular entry: ' + member.name)
            stream.extractall(destination, filter='data')
    finally:
        archive.unlink(missing_ok=True)


@contextmanager
def preserved_book(cache=DEFAULT_CACHE, offline=False):
    descriptor = json.loads(PUBLICATION.read_text())
    for field in ['payload_commit', 'source_equivalent_to']:
        if not re.fullmatch('[0-9a-f]{40}', descriptor[field]):
            raise ValueError('Publication requires an immutable full SHA: ' + field)
    cache = Path(cache).resolve()
    cache.mkdir(parents=True, exist_ok=True)
    source_repo = object_repository(descriptor['source_equivalent_to'], cache, offline)
    payload_repo = object_repository(descriptor['payload_commit'], cache, offline)
    with tempfile.TemporaryDirectory(prefix='assembly-', dir=cache) as staging:
        staging = Path(staging)
        source, payload, preserved = [staging / name for name in ['source', 'payload', 'preserved']]
        export(source_repo, descriptor['source_equivalent_to'], source)
        export(payload_repo, descriptor['payload_commit'], payload)
        # Isolation keeps PYTHONOPTIMIZE from disabling the assembler's checks.
        subprocess.run([sys.executable, '-I', str(ASSEMBLER), str(source), str(payload), str(preserved)], check=True)
        if digest(preserved / 'build-manifest.json') != descriptor['preserved_build_manifest_sha256']:
            raise ValueError('Publication descriptor does not match the assembled build manifest')
        yield preserved, {
            'repository': OFFICIAL_REPOSITORY,
            'payload_commit': descriptor['payload_commit'],
            'source_equivalent_to': descriptor['source_equivalent_to'],
            'descriptor_sha256': digest(PUBLICATION),
            'assembler_sha256': digest(ASSEMBLER),
            'published_files_sha256': digest(payload / 'published-files.json'),
            'publication_receipt_sha256': digest(preserved / 'publication-receipt.json'),
            'qualification': 'Reconstructed existing publication; no fresh scientific or release qualification.',
        }

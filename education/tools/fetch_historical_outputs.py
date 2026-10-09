"""Recover exact archived output bytes into ignored storage; never rerun a solve."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def safe_path(value):
    path = PurePosixPath(value)
    if not value or path.is_absolute() or '..' in path.parts or '\\' in value:
        raise ValueError('Unsafe historical input path')
    return path


def verify(raw, record):
    if len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
        raise ValueError('Historical input byte count or SHA256 mismatch')
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if blob != record['gitBlob']:
        raise ValueError('Historical input Git blob mismatch')


def recover(path, record, commit, root=ROOT, allow_network=True):
    """Validate first, then atomically save below .artifacts/historical-inputs."""
    relative = safe_path(path)
    if not (len(commit) == 40 and all(c in '0123456789abcdef' for c in commit)):
        raise ValueError('Expected an immutable full commit SHA')
    # Every output component must be an ordinary directory, never a symlink.
    target = root / '.artifacts/historical-inputs' / commit / relative
    for parent in [target, *target.parents]:
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError('Historical output path crosses a symlink')
    if target.exists():
        verify(target.read_bytes(), record)
        return target
    ref = commit + ':education/' + relative.as_posix()
    result = subprocess.run(['git', 'cat-file', 'blob', ref], cwd=root,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        raw = result.stdout
    elif allow_network:
        expected = 'https://raw.githubusercontent.com/MrScripty/Kenoma/' + commit + '/education/' + relative.as_posix()
        if record['url'] != expected:
            raise ValueError('Historical URL does not match the pinned repository path')
        with urlopen(expected, timeout=60) as response:
            raw = response.read(record['bytes'] + 1)
    else:
        raise RuntimeError('Exact historical Git object unavailable; network acquisition disabled')
    verify(raw, record)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(raw)
    try:
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', action='append', default=[])
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'tools/historical-output-manifest.json').read_text())
    chosen = list(manifest['files']) if args.all else args.path
    if not chosen:
        for path in manifest['files']:
            print(path)
    for path in chosen:
        if path not in manifest['files']:
            parser.error('Path is absent from the explicit historical manifest: ' + path)
        print(recover(path, manifest['files'][path], manifest['commit'], allow_network=not args.offline))


if __name__ == '__main__':
    main()

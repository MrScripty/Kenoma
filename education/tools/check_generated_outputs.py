"""Fail closed for tracked build downloads, compiled Lean objects and review captures."""
from pathlib import Path
import json, subprocess, sys


def violations(paths):
    forbidden = []
    for name in paths:
        path = Path(name)
        if path.suffix.lower() in {'.pdf', '.zip', '.olean'}:
            forbidden.append(name)
        elif name.startswith('education/review/') and path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
            forbidden.append(name)
        elif name.startswith('education/.artifacts/') or name.startswith('education/dist/'):
            forbidden.append(name)
    return forbidden


def check(root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[2]
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    blocked = violations(paths)
    pins = json.loads((root/'education/tools/preserved-generated-inputs.json').read_text())['files']
    entries = subprocess.check_output(['git', 'ls-files', '-s', '-z'], cwd=root).decode().split('\0')
    records = [entry.split('\t', 1) for entry in filter(None, entries)]
    objects = ''.join(metadata.split()[1]+'\n' for metadata, _ in records)
    sizes = subprocess.check_output(['git', 'cat-file', '--batch-check=%(objectname) %(objectsize)'], cwd=root, input=objects.encode()).decode().splitlines()
    object_sizes = {line.split()[0]: int(line.split()[1]) for line in sizes}
    for metadata, name in records:
        blob = metadata.split()[1]
        generated = name.startswith('education/review/') or (name.startswith('education/data/') and any(part in {'audit', 'review'} for part in Path(name).parts))
        if generated and not name.startswith('education/data/elbow-v1/'):
            size = object_sizes[blob]
            if size > 1000000 and pins.get(name) != {'gitBlob': blob, 'bytes': size}:
                blocked.append(name)

    if blocked:
        raise RuntimeError('Generated outputs must be untracked: '+', '.join(blocked))
    print('PASS tracked-output guard: no PDF/ZIP/olean, review captures or unaccepted large generated collection')


if __name__ == '__main__':
    check(sys.argv[1] if len(sys.argv)>1 else None)

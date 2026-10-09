"""Give mutating research replays an exact-HEAD checkout, separate from the book.

The book's frozen-source guard remains unchanged. Research outputs are retained
in the second checkout and uploaded independently, never substituted for the
canonical, source-bound evidence used to assemble the book.
"""
from pathlib import Path
import argparse
import json
import subprocess


def prepare(source: Path, destination: Path) -> dict:
    source = source.resolve()
    destination = destination.resolve()
    if destination == source or source in destination.parents:
        raise RuntimeError('Research workspace must be outside the frozen source tree')
    if destination.exists():
        raise RuntimeError('Research workspace already exists; preserve it before rerunning')
    status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=source)
    if status.strip():
        raise RuntimeError('Research preparation requires a clean frozen source tree')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    subprocess.run(['git', 'worktree', 'add', '--detach', str(destination), head], cwd=source, check=True)
    for name in ('.tools', 'node_modules'):
        dependency = source / 'education' / name
        if dependency.exists():
            (destination / 'education' / name).symlink_to(dependency, target_is_directory=True)
    receipt = {'schema': 1, 'sourceHead': head,
               'scope': 'Independent research rerun; outputs do not replace canonical book inputs.'}
    evidence = destination / 'education' / '.artifacts'
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / 'research-workspace.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.destination)))

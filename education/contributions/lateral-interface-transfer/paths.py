"""Private output admission; source-overlap, symlink and hardlink aliases fail.

Every writer in this contribution must call this before creating output.
No existing global output rule is changed by this standalone helper.
"""
from pathlib import Path
import hashlib,os,subprocess

HERE=Path(__file__).resolve().parent
CHECKOUT=HERE.parents[2]

def source_roots():
    """Protect every preserved Git worktree, including physically sparse trees."""
    result=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=HERE,text=True)
    return [Path(line.removeprefix('worktree ')).resolve() for line in result.splitlines() if line.startswith('worktree ')]

def checked_output(path, fresh=True):
    path=Path(path).absolute()
    if '..' in path.parts:
        raise ValueError('Parent aliases are not admitted')
    for part in [path,*path.parents]:
        if part.is_symlink():
            raise ValueError('Output symlink aliases are not admitted: '+str(part))
    resolved=path.resolve()
    if any(resolved.is_relative_to(root) or root.is_relative_to(resolved) for root in source_roots()):
        raise ValueError('Explicit private output must be disjoint from every source worktree')
    # An optional portable restriction may narrow the explicit CLI destination.
    # The author environment uses its agreed private root; public users choose
    # their own dedicated outside-checkout path without a workspace dependency.
    if configured:=os.environ.get('KENOMA_LATERAL_OUTPUT_ROOT'):
        private=Path(configured).absolute()
        if '..' in private.parts or any(p.is_symlink() for p in [private,*private.parents]):
            raise ValueError('Configured output root must not use aliases')
        if not resolved.is_relative_to(private.resolve()):
            raise ValueError('Destination outside the configured private output root')
    if path.exists():
        if not path.is_dir():
            raise ValueError('Output must be a directory')
        for child in path.rglob('*'):
            if child.is_symlink() or (child.is_file() and child.stat().st_nlink!=1):
                raise ValueError('Output symlink/hardlink aliases are not admitted')
        if fresh and any(path.iterdir()):
            raise ValueError('Use a fresh output directory')
    path.mkdir(parents=True,exist_ok=True)
    return path

def source_hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.iterdir())
            if p.is_file() and p.name!='.DS_Store'}

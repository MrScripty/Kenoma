"""Bind shipped HTML and JavaScript bytes to the build exercised by browsers."""
from pathlib import Path
import hashlib,json

SUFFIXES={'.html','.js','.mjs','.cjs'}

def executable_outputs(directory,scope=None):
    directory=Path(directory)
    base=directory/scope if scope else directory
    return {str(p.relative_to(directory)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(base.rglob('*')) if p.is_file() and p.suffix in SUFFIXES}

def executable_digest(outputs):
    return hashlib.sha256(json.dumps(outputs,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def checked_build_outputs(directory):
    directory=Path(directory)
    actual=executable_outputs(directory)
    declared=json.loads((directory/'build-manifest.json').read_text()).get('executable_outputs')
    if not actual or actual!=declared:
        raise RuntimeError('Executable outputs differ from the built bytes')
    return actual

def unchanged_outputs(directory,checked,scope=None):
    if executable_outputs(directory,scope)!=checked:
        raise RuntimeError('Executable outputs changed during browser checks')

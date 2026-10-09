"""Fixed Git identities and output helpers for the scoped source pipeline."""
import hashlib
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[2]
BASE = '6a72e01b66e4d5724c8d6c74f98cf38a90b21e31'
TREE = '24c45eb71a391ce516d666378a5a46b2c969ddbe'
PUBLISHED = '596df78f5cb652b4ac70917a82d8aa908b617056'
def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO)

def identity(ref):
    return git('rev-parse', ref+'^{tree}').decode().strip()

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')

def outside(path):
    path = Path(path).resolve()
    if path.is_relative_to(REPO):
        raise ValueError('Deliverables must be outside Git')
    return path

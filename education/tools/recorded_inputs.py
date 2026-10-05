"""Exact recorded-byte binding for the enumerated release source transition."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def recorded_input_matches(relative,expected):
    if not isinstance(relative,str) or Path(relative).is_absolute() or '..' in Path(relative).parts or not isinstance(expected,str) or not re.fullmatch('[a-f0-9]{64}',expected):return False
    digest=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    if digest(relative)==expected:return True
    record=json.loads((ROOT/'tools/release-source-transition.json').read_text())['files'].get(relative)
    if not record or record['recordedSHA256']!=expected or digest(record['archivePath'])!=expected:return False
    if record['kind']=='source':return digest(relative)==record['currentSHA256']
    return record['kind']=='historical-derived-receipt'

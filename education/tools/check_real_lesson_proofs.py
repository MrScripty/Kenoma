"""Fresh pinned Real checks; no receipt is emitted after partial qualification."""
from pathlib import Path
import hashlib, json, os, re, subprocess
from check_property_proofs import check as check_existing_real_properties
ROOT = Path(__file__).resolve().parents[1]
FAMILIES = [
    ('MaterialResponseReal.lean', 'material-real-claims.json', 'material-real', 5),
    ('MechanicsReal.lean', 'mechanics-real-claims.json', 'mechanics-real', 3),
    ('ActuatorConstitutiveReal.lean', 'actuator-real-claims.json', 'actuator-real', 11),
    ('DissipativeBarReal.lean', 'dissipative-real-claims.json', 'dissipative-real', 11),
    ('SerialSpecimenReal.lean', 'serial-specimen-real-claims.json', 'serial-real', 12),
]

def check(existing=None):
    out = ROOT / 'dist'; out.mkdir(exist_ok=True)
    for _, _, prefix, _ in FAMILIES:
        (out / (prefix + '-proof-status.json')).unlink(missing_ok=True)
    # The ordinary entry point fresh-checks every unchanged dependency pin,
    # pristine locked source and Lean version before compiling these claims.
    # build() supplies its immediately preceding successful property check.
    existing = existing or check_existing_real_properties()
    env = os.environ.copy()
    env['PATH'] = str(ROOT / '.tools/lean-4.19.0-linux/bin') + os.pathsep + env['PATH']
    env['MATHLIB_CACHE_DIR'] = str(ROOT / '.tools/mathlib-cache')
    receipts = []
    for source_name, map_name, prefix, count in FAMILIES:
        source = ROOT / 'proofs' / source_name
        claim_file = ROOT / 'proofs' / map_name
        body = re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
        if re.search(r'\b(sorry|admit|axiom|native_decide)\b',body):
            raise RuntimeError('Forbidden proof admission: ' + source_name)
        claims = json.loads(claim_file.read_text())
        if len(claims) != count or len({c['theorem'] for c in claims}) != count:
            raise RuntimeError('Unexpected Real proof coverage: ' + map_name)
        command = ['lake','--no-cache','env','lean','-DwarningAsError=true',str(source)]
        result = subprocess.run(command,cwd=ROOT/'.tools/mathlib4',env=env,capture_output=True,text=True)
        transcript = result.stdout + result.stderr
        (out / (prefix + '-lean-check.txt')).write_text(transcript)
        if result.returncode: raise RuntimeError(transcript)
        for claim in claims:
            match = re.search(rf"'{re.escape(claim['theorem'])}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",transcript)
            if not match: raise RuntimeError('Missing kernel dependency report: ' + claim['theorem'])
            axioms = [x.strip() for x in (match.group(1) or '').split(',') if x.strip()]
            if not set(axioms) <= {'propext','Quot.sound','Classical.choice'}:
                raise RuntimeError('Unapproved kernel dependency')
            claim.update(status='checked',axioms=axioms)
        receipts.append({'schema':1,'lean_version':existing['lean_version'],'mathlib':existing['mathlib'],
            'source':'proofs/'+source_name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'claims_sha256':hashlib.sha256(claim_file.read_bytes()).hexdigest(),
            'command':'lake --no-cache env lean -DwarningAsError=true proofs/'+source_name+' (from pinned mathlib workspace)',
            'claims':claims})
    for receipt, (_,_,prefix,_) in zip(receipts,FAMILIES):
        (out / (prefix + '-proof-status.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'Freshly compiled {sum(len(r["claims"]) for r in receipts)} additional Real declarations')
    return receipts
if __name__ == '__main__': check()

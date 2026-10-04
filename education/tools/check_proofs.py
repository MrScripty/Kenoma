"""Fail closed: generate evidence only from a fresh successful Lean invocation."""
from pathlib import Path
import hashlib,json,os,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'

def check():
    OUT.mkdir(exist_ok=True)
    target=OUT/'proof-status.json'
    target.unlink(missing_ok=True)
    source=ROOT/'proofs/Mechanics.lean'
    claims=json.loads((ROOT/'proofs/claims.json').read_text())
    lean=os.environ.get('LEAN','lean')
    version=subprocess.check_output([lean,'--version'],text=True).strip()
    if 'version 4.19.0,' not in version: raise RuntimeError('Use pinned Lean 4.19.0')
    result=subprocess.run([lean,'-DwarningAsError=true',str(source)],capture_output=True,text=True)
    transcript=result.stdout+result.stderr
    (OUT/'lean-check.txt').write_text(transcript)
    if result.returncode: raise RuntimeError(transcript)
    # Output is a fresh kernel dependency report, not a handwritten whitelist badge.
    allowed={'propext','Quot.sound','Classical.choice'}
    for c in claims:
        pattern=rf"'{re.escape(c['theorem'])}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)"
        m=re.search(pattern,transcript)
        if not m: raise RuntimeError('Missing dependency report: '+c['theorem'])
        axioms=[x.strip() for x in (m.group(1) or '').split(',') if x.strip()]
        if not set(axioms)<=allowed: raise RuntimeError('Unapproved axioms: '+str(axioms))
        c.update(axioms=axioms,status='checked')
    if re.search(r'\b(sorry|admit|axiom|native_decide)\b',source.read_text()):
        raise RuntimeError('Proof source contains a forbidden admission or custom axiom')
    payload={'schema':1,'lean_version':version,'mathlib':'not used; bundled Std only',
             'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'claims_sha256':hashlib.sha256((ROOT/'proofs/claims.json').read_bytes()).hexdigest(),
             'source':'proofs/Mechanics.lean','command':'lean -DwarningAsError=true proofs/Mechanics.lean',
             'claims':claims}
    target.write_text(json.dumps(payload,indent=2)+'\n')
    print(f"Checked {len(claims)} theorems with {version}")
    return payload
if __name__=='__main__': check()

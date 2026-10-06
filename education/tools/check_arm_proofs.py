"""Fresh pinned kernel check of narrow atlas-frame algebraic claims."""
from pathlib import Path
import hashlib,json,os,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
def check():
    out=ROOT/'data/anatomical-arm-v1/audit';target=out/'arm-proof-status.json';target.unlink(missing_ok=True)
    source=ROOT/'proofs/AnatomicalArm.lean';claims_file=ROOT/'proofs/arm-claims.json'
    lean=os.environ.get('LEAN','lean');version=subprocess.check_output([lean,'--version'],text=True).strip()
    if 'version 4.19.0,' not in version:raise RuntimeError('Pinned Lean 4.19.0 required')
    result=subprocess.run([lean,'-DwarningAsError=true',str(source)],capture_output=True,text=True)
    transcript=result.stdout+result.stderr;(out/'arm-lean-check.txt').write_text(transcript)
    if result.returncode:raise RuntimeError(transcript)
    if re.search(r'\b(sorry|admit|axiom|native_decide)\b',source.read_text()):raise RuntimeError('Forbidden proof admission')
    claims=json.loads(claims_file.read_text())
    for c in claims:
        match=re.search(rf"'{re.escape(c['theorem'])}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",transcript)
        if not match:raise RuntimeError('Missing kernel dependency report')
        axioms=[s.strip() for s in (match.group(1) or '').split(',') if s.strip()]
        if not set(axioms)<={'propext','Quot.sound','Classical.choice'}:raise RuntimeError('Unapproved kernel dependency')
        c.update(status='checked',axioms=axioms)
    payload={'schema':1,'lean_version':version,'source':'proofs/AnatomicalArm.lean','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'claims_sha256':hashlib.sha256(claims_file.read_bytes()).hexdigest(),'command':'lean -DwarningAsError=true proofs/AnatomicalArm.lean','claims':claims}
    target.write_text(json.dumps(payload,indent=2)+'\n');print(f'Checked {len(claims)} arm algebraic claims with {version}');return payload
if __name__=='__main__':check()

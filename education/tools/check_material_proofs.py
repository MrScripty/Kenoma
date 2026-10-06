"""Fail closed: compile the five material contracts freshly with pinned Lean Std."""
from pathlib import Path
import hashlib,json,os,re,subprocess
ROOT=Path(__file__).resolve().parents[1]

def check(destination=None):
    out=Path(destination) if destination else ROOT/'dist';out.mkdir(parents=True,exist_ok=True)
    target=out/'material-proof-status.json';target.unlink(missing_ok=True)
    source=ROOT/'proofs/MaterialResponse.lean';claim_file=ROOT/'proofs/material-claims.json'
    lean=os.environ.get('LEAN','lean')
    version=subprocess.check_output([lean,'--version'],text=True).strip()
    if 'version 4.19.0,' not in version:raise RuntimeError('Pinned Lean 4.19.0 required')
    body=re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
    if re.search(r'\b(sorry|admit|axiom|native_decide)\b',body):raise RuntimeError('Forbidden proof admission')
    result=subprocess.run([lean,'-DwarningAsError=true',str(source)],capture_output=True,text=True)
    transcript=result.stdout+result.stderr;(out/'material-lean-check.txt').write_text(transcript)
    if result.returncode:raise RuntimeError(transcript)
    claims=json.loads(claim_file.read_text())
    for c in claims:
        match=re.search(rf"'{re.escape(c['theorem'])}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",transcript)
        if not match:raise RuntimeError('Missing kernel dependency report: '+c['theorem'])
        axioms=[x.strip() for x in (match.group(1) or '').split(',') if x.strip()]
        if not set(axioms)<={'propext','Quot.sound','Classical.choice'}:raise RuntimeError('Unapproved kernel dependency')
        c.update(status='checked',axioms=axioms)
    payload={'schema':1,'lean_version':version,'mathlib':'not used; bundled Std only','source':'proofs/MaterialResponse.lean',
             'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'claims_sha256':hashlib.sha256(claim_file.read_bytes()).hexdigest(),
             'command':'lean -DwarningAsError=true proofs/MaterialResponse.lean','claims':claims}
    target.write_text(json.dumps(payload,indent=2)+'\n');print(f'Freshly compiled {len(claims)} material contracts with {version}');return payload

if __name__=='__main__':check()

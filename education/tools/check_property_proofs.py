"""Fresh real-number kernel check against the pinned official mathlib source."""
from pathlib import Path
import hashlib,json,os,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
def check():
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    target=out/'property-proof-status.json';target.unlink(missing_ok=True)
    source=ROOT/'proofs/ContinuumProperties.lean';claim_file=ROOT/'proofs/property-claims.json'
    dependency=ROOT/'.tools/mathlib4';lock=json.loads((ROOT/'proofs/mathlib-lock.json').read_text())
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=dependency,text=True).strip()
    if actual!=lock['commit']:raise RuntimeError('Pinned mathlib commit differs')
    if subprocess.check_output(['git','status','--porcelain'],cwd=dependency,text=True).strip():raise RuntimeError('Modified mathlib source')
    if hashlib.sha256((dependency/'lake-manifest.json').read_bytes()).hexdigest()!=lock['manifest_sha256']:raise RuntimeError('Dependency manifest differs')
    for package in json.loads((dependency/'lake-manifest.json').read_text())['packages']:
        if package['type']=='git':
            revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=dependency/'.lake/packages'/package['name'],text=True).strip()
            if revision!=package['rev']:raise RuntimeError('Dependency revision differs: '+package['name'])
            if subprocess.check_output(['git','status','--porcelain'],cwd=dependency/'.lake/packages'/package['name'],text=True).strip():raise RuntimeError('Modified dependency source: '+package['name'])
    env=os.environ.copy();env['PATH']=str(ROOT/'.tools/lean-4.19.0-linux/bin')+os.pathsep+env['PATH'];env['MATHLIB_CACHE_DIR']=str(ROOT/'.tools/mathlib-cache')
    version=subprocess.check_output(['lean','--version'],env=env,text=True).strip()
    if 'version 4.19.0,' not in version:raise RuntimeError('Pinned Lean 4.19.0 required')
    command=['lake','env','lean','-DwarningAsError=true',str(source)]
    result=subprocess.run(command,cwd=dependency,env=env,capture_output=True,text=True)
    transcript=result.stdout+result.stderr;(out/'property-lean-check.txt').write_text(transcript)
    if result.returncode:raise RuntimeError(transcript)
    # Strip comments before checking proof admissions: comments describe limitations.
    body=re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
    if re.search(r'\b(sorry|admit|axiom|native_decide)\b',body):raise RuntimeError('Forbidden proof admission')
    claims=json.loads(claim_file.read_text())
    for claim in claims:
        match=re.search(rf"'{re.escape(claim['theorem'])}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",transcript)
        if not match:raise RuntimeError('Missing kernel dependency report')
        axioms=[x.strip() for x in (match.group(1) or '').split(',') if x.strip()]
        if not set(axioms)<={'propext','Quot.sound','Classical.choice'}:raise RuntimeError('Unapproved kernel dependency')
        claim.update(status='checked',axioms=axioms)
    payload={'schema':1,'lean_version':version,'mathlib':lock,'source':'proofs/ContinuumProperties.lean','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'claims_sha256':hashlib.sha256(claim_file.read_bytes()).hexdigest(),'command':'lake env lean -DwarningAsError=true proofs/ContinuumProperties.lean (from pinned mathlib workspace)','claims':claims}
    target.write_text(json.dumps(payload,indent=2)+'\n');print(f'Checked {len(claims)} real kinematic/material claims with {version}');return payload
if __name__=='__main__':check()

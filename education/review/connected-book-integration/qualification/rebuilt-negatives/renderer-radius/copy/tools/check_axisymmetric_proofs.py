"""Check the separate prototype's Real identities; never update book families."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys
from check_property_proofs import check as verify_pins_and_existing
ROOT=Path(__file__).resolve().parents[1]
def check(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);target=out/'axisymmetric-proof-status.json';target.unlink(missing_ok=True)
    pin=verify_pins_and_existing();source=ROOT/'proofs/AxisymmetricSpecimenReal.lean';mapping=ROOT/'proofs/axisymmetric-specimen-real-claims.json'
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inputs={str(p.relative_to(ROOT)):digest(p) for p in [source,mapping,Path(__file__)]}
    body=re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
    if re.search(r'\b(sorry|admit|axiom|native_decide)\b',body):raise RuntimeError('Forbidden proof admission')
    claims=json.loads(mapping.read_text());assert len(claims)==9 and len({c['theorem'] for c in claims})==9
    env=os.environ.copy();env['PATH']=str(ROOT/'.tools/lean-4.19.0-linux/bin')+os.pathsep+env['PATH']
    command=['lake','--no-cache','env','lean','-DwarningAsError=true',str(source)]
    result=subprocess.run(command,cwd=ROOT/'.tools/mathlib4',env=env,capture_output=True,text=True)
    transcript=result.stdout+result.stderr;(out/'axisymmetric-lean-check.txt').write_text(transcript)
    if result.returncode:raise RuntimeError(transcript)
    for claim in claims:
        name=claim['theorem'].split('.')[-1]
        match=re.search(r'(theorem '+re.escape(name)+r'\b.*?)(?= := by)',source.read_text(),re.S)
        assert match and match.group(1)==claim['statement'],'Claim statement differs from complete source'
        match=re.search(r"'"+re.escape(claim['theorem'])+r"' depends on axioms: \[([^\]]*)\]",transcript)
        assert match,'Missing fresh kernel dependency report'
        axioms=[x.strip() for x in match.group(1).split(',') if x.strip()]
        assert set(axioms)<={'propext','Quot.sound','Classical.choice'},'Unapproved dependency'
        claim.update(status='checked',axioms=axioms)
    assert all(digest(ROOT/n)==h for n,h in inputs.items())
    payload={'status':'PASS','lean_version':pin['lean_version'],'mathlib':pin['mathlib'],'source':'proofs/AxisymmetricSpecimenReal.lean','source_sha256':inputs['proofs/AxisymmetricSpecimenReal.lean'],'claims_sha256':inputs['proofs/axisymmetric-specimen-real-claims.json'],'input_sha256':inputs,'command':'lake --no-cache env lean -DwarningAsError=true proofs/AxisymmetricSpecimenReal.lean, from pinned official mathlib workspace','claims':claims,'scope':'Nine local prototype identities; no book-family or publication change and no numerical/continuum/stability/anatomical certification'}
    target.write_text(json.dumps(payload,indent=2)+'\n');print('PASS nine fresh local Real identities; existing four kinematic declarations and all dependency pins checked')
    return payload
if __name__=='__main__':check(Path(sys.argv[1]))

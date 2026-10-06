"""Fresh pinned real-domain checks; proposed sources never imply checked status."""
from pathlib import Path
import hashlib,json,os,re,subprocess
from check_property_proofs import check as check_existing_real_properties
ROOT=Path(__file__).resolve().parents[1]

def check():
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    target=out/'real-lesson-proof-status.json';target.unlink(missing_ok=True)
    # This checks unchanged pins, all locked transitive dependencies, pristine
    # tracked source, Lean version and existing real proofs before new claims.
    existing=check_existing_real_properties()
    manifest=ROOT/'proofs/real-lesson-claims.json'
    claims=json.loads(manifest.read_text())
    env=os.environ.copy();env['PATH']=str(ROOT/'.tools/lean-4.19.0-linux/bin')+os.pathsep+env['PATH']
    env['MATHLIB_CACHE_DIR']=str(ROOT/'.tools/mathlib-cache')
    sources={};transcripts={}
    for relative in sorted({c['source'] for c in claims}):
        source=ROOT/relative
        body=re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
        if re.search(r'\b(sorry|admit|axiom|native_decide)\b',body):raise RuntimeError('Forbidden proof admission: '+relative)
        result=subprocess.run(['lake','--no-cache','env','lean','-DwarningAsError=true',str(source)],cwd=ROOT/'.tools/mathlib4',env=env,capture_output=True,text=True)
        transcript=result.stdout+result.stderr
        (out/(source.stem+'-lean-check.txt')).write_text(transcript)
        if result.returncode:raise RuntimeError(transcript)
        sources[relative]=hashlib.sha256(source.read_bytes()).hexdigest();transcripts[relative]=transcript
    for claim in claims:
        transcript=transcripts[claim['source']]
        match=re.search(rf"'{re.escape(claim['theorem'])}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",transcript)
        if not match:raise RuntimeError('Missing kernel dependency report: '+claim['theorem'])
        axioms=[x.strip() for x in (match.group(1) or '').split(',') if x.strip()]
        if not set(axioms)<={'propext','Quot.sound','Classical.choice'}:raise RuntimeError('Unapproved kernel dependency')
        claim.update(status='checked',axioms=axioms)
    payload={'schema':1,'lean_version':existing['lean_version'],'mathlib':existing['mathlib'],
             'source_hashes':sources,'claims_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
             'existing_real_properties_receipt_sha256':hashlib.sha256((out/'property-proof-status.json').read_bytes()).hexdigest(),
             'claims':claims,'scope':'Real geometric/bulk/contact and force/torque product algebra under explicit assumptions. No constitutive derivatives, nonlinear root, numerical refinement or empirical certificate.'}
    target.write_text(json.dumps(payload,indent=2)+'\n')
    print(f'Freshly compiled {len(claims)} additional real-domain declarations')
    return payload

if __name__=='__main__':check()

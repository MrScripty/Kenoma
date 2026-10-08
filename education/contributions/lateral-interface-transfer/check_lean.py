"""Compile only six new Real declarations using existing pinned dependencies.

No cache retrieval or dependency build. An explicit private output is required.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess
from paths import HERE,checked_output,source_hashes

PIN='c44e0c8ee63ca166450922a373c7409c5d26b00b'
MANIFEST='5c6421b650bc87a2427a892a39e5522dc44543ca4ac1bd6e9f08d536c044a752'
THEOREMS=['material_resultants','stationary_solution','matched_end_resultants',
          'energy_completion_unique_minimum','transfer_stiffness_bounds','interface_stiffness_difference']

def run(args):
    # A warm compiler wrapper may already have written its own transcript here.
    # Admit that scoped nonempty tree only after all the same alias guards.
    out=checked_output(args.output,fresh=False);source=HERE/'LateralInterfaceTransfer.lean'
    for name in ['lateral-transfer-lean.txt','lateral-transfer-proof-status.json']:
        if (out/name).exists():raise RuntimeError('Refuse to overwrite existing owned receipt: '+name)
    mathlib=args.mathlib.resolve();env=os.environ.copy()
    env['PATH']=str(args.lean_bin.resolve())+os.pathsep+env['PATH']
    def git(*a,cwd=mathlib):return subprocess.check_output(['git',*a],cwd=cwd,text=True).strip()
    if git('rev-parse','HEAD')!=PIN or git('status','--porcelain'):
        raise RuntimeError('Pristine pinned mathlib source required')
    manifest=mathlib/'lake-manifest.json'
    if hashlib.sha256(manifest.read_bytes()).hexdigest()!=MANIFEST:raise RuntimeError('Dependency manifest mismatch')
    for pkg in json.loads(manifest.read_text())['packages']:
        if pkg['type']=='git':
            path=mathlib/'.lake/packages'/pkg['name']
            if git('rev-parse','HEAD',cwd=path)!=pkg['rev'] or git('status','--porcelain',cwd=path):
                raise RuntimeError('Pristine pinned package required: '+pkg['name'])
    version=subprocess.check_output(['lean','--version'],env=env,text=True).strip()
    if 'version 4.19.0,' not in version:raise RuntimeError('Pinned Lean required')
    body=re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
    if re.search(r'\b(sorry|admit|axiom|native_decide)\b',body):raise RuntimeError('No admissions allowed')
    declared=re.findall(r'^theorem\s+(\w+)',body,re.M)
    claims=json.loads((HERE/'claims.json').read_text())
    if declared!=THEOREMS or [c['theorem'] for c in claims]!=['KenomaLateralTransfer.'+t for t in THEOREMS]:
        raise RuntimeError('Exactly six source/map declarations required')
    # The direct compiler never invokes lake build. Missing cache is a blocker.
    command=['lake','--no-cache','env','lean','-DwarningAsError=true',str(source)]
    r=subprocess.run(command,cwd=mathlib,env=env,capture_output=True,text=True)
    transcript=r.stdout+r.stderr;(out/'lateral-transfer-lean.txt').write_text(transcript)
    if r.returncode:raise RuntimeError(transcript)
    checked=[]
    for claim in claims:
        full=claim['theorem']
        match=re.search(rf"'{re.escape(full)}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",transcript)
        if not match:raise RuntimeError('Missing kernel dependency report: '+full)
        axioms=[x.strip() for x in (match.group(1) or '').split(',') if x.strip()]
        if not set(axioms)<={'propext','Quot.sound','Classical.choice'}:raise RuntimeError('Unapproved kernel dependency')
        checked.append({**claim,'status':'checked','axioms':axioms})
    receipt={'status':'passed','lean_version':version,'mathlib_commit':PIN,'manifest_sha256':MANIFEST,
      'source_sha256':source_hashes(),'claims':checked,'command':command,'book_registered':False,
      'transcript_sha256':hashlib.sha256(transcript.encode()).hexdigest(),
      'scope':'Six Real identities for this discrete model only; no certified differentiation, continuum, floating-point or biological validity.'}
    (out/'lateral-transfer-proof-status.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Fresh kernel compilation passed for six candidate declarations; book registration remains separate.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mathlib',type=Path,required=True)
    p.add_argument('--lean-bin',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args())

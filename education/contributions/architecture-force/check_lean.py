"""Compile only this contribution with the repository-pinned Lean/mathlib.

Read-only with respect to source and existing proof manifests. An explicit output
directory is mandatory so generated receipts never enter the source contribution.
This program does not install dependencies or launch numerical experiments.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess

PIN='c44e0c8ee63ca166450922a373c7409c5d26b00b'
MANIFEST='5c6421b650bc87a2427a892a39e5522dc44543ca4ac1bd6e9f08d536c044a752'
THEOREMS=['material_cut_force','parallel_area_aggregation','projection_once',
          'two_group_projected_sum','series_balance_telescopes','paired_exchange_power']

def run(args):
 source=Path(__file__).with_name('ArchitectureForce.lean').resolve()
 mathlib=args.mathlib.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env['PATH']=str(args.lean_bin.resolve())+os.pathsep+env['PATH']
 def git(*a,cwd=mathlib):
  return subprocess.check_output(['git',*a],cwd=cwd,text=True).strip()
 assert git('rev-parse','HEAD')==PIN,'Pinned mathlib revision required'
 assert not git('status','--porcelain'),'Pristine mathlib source required'
 manifest=mathlib/'lake-manifest.json';assert hashlib.sha256(manifest.read_bytes()).hexdigest()==MANIFEST
 for package in json.loads(manifest.read_text())['packages']:
  if package['type']=='git':
   path=mathlib/'.lake/packages'/package['name']
   assert git('rev-parse','HEAD',cwd=path)==package['rev'],package['name']
   assert not git('status','--porcelain',cwd=path),package['name']
 version=subprocess.check_output(['lean','--version'],env=env,text=True).strip()
 assert 'version 4.19.0,' in version,version
 body=re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
 assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',body),'No admissions allowed'
 command=['lake','--no-cache','env','lean','-DwarningAsError=true',str(source)]
 r=subprocess.run(command,cwd=mathlib,env=env,capture_output=True,text=True)
 transcript=r.stdout+r.stderr;(out/'architecture-force-lean.txt').write_text(transcript)
 if r.returncode:raise RuntimeError(transcript)
 claims=[]
 for theorem in THEOREMS:
  full='KenomaArchitectureForce.'+theorem
  match=re.search(rf"'{re.escape(full)}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",transcript)
  assert match,'Missing kernel dependency report: '+full
  axioms=[x.strip() for x in (match.group(1) or '').split(',') if x.strip()]
  assert set(axioms)<={'propext','Quot.sound','Classical.choice'},axioms
  claims.append({'theorem':full,'axioms':axioms,'status':'checked'})
 receipt={'lean_version':version,'mathlib_commit':PIN,'manifest_sha256':MANIFEST,
          'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'claims':claims,
          'book_registered':False,'scope':'Real algebra only; no anatomy, biology, JavaScript or solver qualification.'}
 (out/'architecture-force-proof-status.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(f'Checked {len(claims)} candidate declarations. Book registration remains separate.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mathlib',type=Path,required=True)
 p.add_argument('--lean-bin',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 run(p.parse_args())

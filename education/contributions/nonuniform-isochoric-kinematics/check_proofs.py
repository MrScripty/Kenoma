"""Compile this standalone source afresh; never manufacture a checked flag."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess

SOURCE=Path(__file__).resolve().parent
REPOSITORY=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=SOURCE,text=True).strip())
parser=argparse.ArgumentParser()
parser.add_argument('--mathlib',type=Path,required=True)
parser.add_argument('--lean-bin',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
receipt=args.output/'nonuniform-proof-status.json';receipt.unlink(missing_ok=True)
lock=json.loads(subprocess.check_output(['git','show','HEAD:education/proofs/mathlib-lock.json'],cwd=REPOSITORY,text=True))
if subprocess.check_output(['git','status','--porcelain'],cwd=REPOSITORY).strip():raise RuntimeError('Final proof check requires a clean frozen source tree')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPOSITORY,text=True).strip()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if subprocess.check_output(['git','rev-parse','HEAD'],cwd=args.mathlib,text=True).strip()!=lock['commit']:raise RuntimeError('Wrong mathlib revision')
if subprocess.check_output(['git','status','--porcelain'],cwd=args.mathlib).strip():raise RuntimeError('Modified mathlib source')
if sha(args.mathlib/'lake-manifest.json')!=lock['manifest_sha256']:raise RuntimeError('Wrong dependency manifest')
for package in json.loads((args.mathlib/'lake-manifest.json').read_text())['packages']:
 p=args.mathlib/'.lake/packages'/package['name']
 if subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()!=package['rev']:raise RuntimeError('Wrong transitive dependency')
 if subprocess.check_output(['git','status','--porcelain'],cwd=p).strip():raise RuntimeError('Modified transitive dependency')
source=SOURCE/'NonuniformIsochoric.lean';claimFile=SOURCE/'claims.json';claims=json.loads(claimFile.read_text())
body=re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
if re.search(r'\b(sorry|admit|axiom|native_decide)\b',body):raise RuntimeError('Forbidden admission or custom axiom')
declared=re.findall(r'^theorem ([a-zA-Z_0-9]+)',body,re.M)
if declared!=[c['theorem'].split('.')[-1] for c in claims]:raise RuntimeError('Incomplete proof inventory')
env=os.environ.copy();env['PATH']=str(args.lean_bin)+os.pathsep+env['PATH'];env['MATHLIB_NO_CACHE_ON_UPDATE']='1'
version=subprocess.check_output(['lean','--version'],env=env,text=True).strip()
if 'version 4.19.0,' not in version:raise RuntimeError('Wrong Lean version')
command=['lake','env','lean','-DwarningAsError=true',str(source)]
result=subprocess.run(command,cwd=args.mathlib,env=env,capture_output=True,text=True)
transcript=result.stdout+result.stderr;(args.output/'nonuniform-lean-check.txt').write_text(transcript)
if result.returncode:raise RuntimeError(transcript)
for claim in claims:
 match=re.search(rf"'{re.escape(claim['theorem'])}' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",transcript)
 if not match:raise RuntimeError('Missing kernel dependency report')
 axioms=[s.strip() for s in (match.group(1) or '').split(',') if s.strip()]
 if not set(axioms)<={'propext','Quot.sound','Classical.choice'}:raise RuntimeError('Unapproved kernel dependency')
 claim.update(status='checked',axioms=axioms)
payload={'result':'PASS_SIX_FRESH_REAL_CONTRACTS','sourceHead':head,'leanVersion':version,'mathlib':lock,'sourceSha256':sha(source),'claimsSha256':sha(claimFile),'checkerSha256':sha(Path(__file__)),'command':command,'claims':claims,'bookRegistration':'NOT_REGISTERED_PENDING_INDEPENDENT_ACCEPTANCE','scope':'Declared gradient determinant, positive interval stretch, and a Real straight-cell error formula. No formal derivative, integration, triangulation, floating-point, equilibrium or biological theorem.'}
receipt.write_text(json.dumps(payload,indent=2)+'\n');print(payload['result'],head)

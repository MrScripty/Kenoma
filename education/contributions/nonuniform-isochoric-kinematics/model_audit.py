"""Separate symbolic, high-precision geometry and topology audit of the JS model."""
from pathlib import Path
from collections import Counter
from decimal import Decimal,localcontext
import argparse,hashlib,itertools,json,subprocess
import sympy as sp
import mpmath

assert sp.__version__=='1.14.0' and mpmath.__version__=='1.3.0','Use the pinned audit dependencies'

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
S,Y,Z,a=sp.symbols('S Y Z a',real=True);m,L=sp.symbols('m L',positive=True)
lam=m*(1+a*(2*S/L-1));b=1/sp.sqrt(lam)
phi=sp.Matrix([m*((1-a)*S+a*S**2/L),b*Y,b*Z])
F=sp.simplify(phi.jacobian([S,Y,Z]));expected=sp.Matrix([[lam,0,0],[-sp.diff(lam,S)*Y/(2*lam**sp.Rational(3,2)),b,0],[-sp.diff(lam,S)*Z/(2*lam**sp.Rational(3,2)),0,b]])
assert sp.simplify(F-expected)==sp.zeros(3)
assert sp.simplify(F.det())==1
assert sp.simplify(phi[0].subs(S,L)-phi[0].subs(S,0))==m*L
assert sp.simplify(sp.integrate(lam,(S,0,L))/L)==m
r=sp.symbols('r',positive=True)
cell=(1+r**2)*(1+1/r+1/r**2)/6
factor=(r-1)**2*(r**2+3*r+1)/(6*r**2)
assert sp.simplify(cell-1-factor)==0

cases=[{'mean':mean,'gradient':gradient,'compensate':compensate,'cells':cells} for mean,gradient,compensate,cells in itertools.product([.6,1,1.4],[-.6,0,.6],[True,False],[8,16,32,64,128])]
script="""import {state} from './model.mjs';import fs from 'node:fs';
const input=JSON.parse(fs.readFileSync(0,'utf8'));
for(const p of input)console.log(JSON.stringify(state(p)));"""
result=subprocess.run(['node','--input-type=module','-e',script],input=json.dumps(cases),text=True,cwd=ROOT,capture_output=True,check=True)
states=[json.loads(line) for line in result.stdout.splitlines()];assert len(states)==90
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def boundary(mesh):
 with localcontext() as context:
  context.prec=50
  vertices=[[Decimal(str(x)) for x in row] for row in mesh['vertices']]
  value=Decimal(0)
  for i,j,k in mesh['faces']:
   c=cross(vertices[j],vertices[k]);value+=sum(x*y for x,y in zip(vertices[i],c))/6
  return value
maxBoundaryError=0;maxCellError=0;maxReferenceError=0;refinement={};closedMeshes=0
for p,s in zip(cases,states,strict=True):
 mesh=s['deformed'];vertices=mesh['vertices'];faces=mesh['faces'];edges=Counter()
 for face in faces:
  assert len(set(face))==3
  for i,j in zip(face,face[1:]+face[:1]):edges[i,j]+=1
  ab=[vertices[face[1]][i]-vertices[face[0]][i] for i in range(3)];ac=[vertices[face[2]][i]-vertices[face[0]][i] for i in range(3)]
  assert sum(x*x for x in cross(ab,ac))>0
 assert all(count==1 and edges[j,i]==1 for (i,j),count in edges.items())
 assert len(vertices)-len(edges)//2+len(faces)==2
 rings=[vertices[i*s['parameters']['sides']][0] for i in range(p['cells']+1)]
 assert all(y>x for x,y in zip(rings,rings[1:]));closedMeshes+=1
 precise=float(boundary(mesh));maxBoundaryError=max(maxBoundaryError,abs(precise-s['meshVolume']))
 assert abs(precise-s['meshVolume'])<1e-17
 reference=float(sp.N(sp.Rational(16,2)*sp.sin(sp.pi/8)*sp.Rational(15,1000)**2*sp.Rational(12,100),50))
 maxReferenceError=max(maxReferenceError,abs(reference-s['referenceVolume']));assert abs(reference-s['referenceVolume'])<1e-17
 ratios=[]
 for i,row in enumerate(s['rows']):
  u=p['mean']*(1+p['gradient']*(2*i/p['cells']-1));v=p['mean']*(1+p['gradient']*(2*(i+1)/p['cells']-1))
  ratio=float(cell.subs(r,sp.sqrt(sp.Float(v,40)/sp.Float(u,40)))) if p['compensate'] else (u+v)/2
  maxCellError=max(maxCellError,abs(ratio-row['cellVolumeRatio']));assert abs(ratio-row['cellVolumeRatio'])<1e-12
  assert abs(row['J']-(1 if p['compensate'] else (u+v)/2))<1e-12
  ratios.append(ratio)
 assert abs(sum(ratios)/p['cells']-s['meshVolumeRatio'])<1e-12
 if p['compensate'] and p['gradient']:
  assert s['relativeMeshVolumeError']>0
  refinement.setdefault((p['mean'],p['gradient']),[]).append(s['relativeMeshVolumeError'])
 elif p['compensate']:assert abs(s['relativeMeshVolumeError'])<1e-12
 else:assert abs(s['meshVolumeRatio']-p['mean'])<1e-12
for errors in refinement.values():assert all(b<a/3.7 for a,b in zip(errors,errors[1:]))
text=(ROOT/'index.template.html').read_text()
phrases=['no force balance, material response, activation or anatomical prediction','centerline strains','signed volume','Pointwise J','straight mesh cell approximates','b′Y','b′Z','does not establish local volume preservation','not establish a passive equilibrium']
for phrase in phrases:assert phrase.lower() in text.lower(),phrase
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
payload={'result':'PASS_SEPARATE_SYMBOLIC_GEOMETRY_TOPOLOGY_AND_TEXT_AUDIT','sourceHashes':{name:sha(ROOT/name) for name in ['model.mjs','index.template.html','model_audit.py']},'independentDerivation':{'fullJacobian':str(F),'determinant':str(sp.simplify(F.det())),'axialSpan':'m*L','uncompensatedMeanVolumeRatio':'m','cellErrorFactorization':str(factor),'strictCellErrorCondition':'r>0 and r != 1; numerator and denominator are positive.','continuumVolumeArgument':'On the positive-stretch material interval, x(S) is strictly increasing and b(S)>0. The map is injective and C1 on a neighbourhood of the prism. Change of variables gives the stated continuum volume; this integral argument is not a compiled Lean theorem.'},'numericalChecks':{'states':len(states),'closedOrientedMeshes':closedMeshes,'maximumBoundaryDifferenceM3':maxBoundaryError,'maximumReferenceDifferenceM3':maxReferenceError,'maximumIndependentCellRatioDifference':maxCellError,'refinementFamilies':len(refinement),'minimumReductionFactorRequired':3.7},'textScopeChecks':phrases,'physicsReview':'Prescribed compatible finite kinematics, with true off-axis shear. Centerline lambda-1 is not surface-fibre extension. No balance law or tissue material law is introduced. A 16-sided prism is authored reference geometry. Finite-volume error is measured rather than hidden.','peerAcceptance':'PENDING_PARENT_INDEPENDENT_REVIEW; separate audit routes are not a substitute for an independent human/agent acceptance.','anatomicalCompletion':False,'authorCampaignInvocations':0}
payload['auditDependencies']={'sympy':sp.__version__,'mpmath':mpmath.__version__,'requirementsSha256':sha(ROOT/'requirements-audit.txt')}
(args.output/'model-audit.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n');print(payload['result'],len(states),'states')

import pathlib, json, hashlib, math, itertools, fractions, sys
import numpy as np
import subprocess
from fractions import Fraction as F
repo=pathlib.Path('/workspace/Kenoma-patch-runner'); root=repo/'education'; prefdir=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'review/selective-fixed-patch-preflight-20261007'
pref=json.loads((prefdir/'preflight.json').read_text()); manifest=json.loads((root/'research/selective-fixed-patch-20261007-inputs.json').read_text()); report={'sourceCommit':pref['sourceCommit'],'specimenCalls':0,'checks':{}}
hashf=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in pref['sourceHashes'].items():assert hashlib.sha256(subprocess.check_output(['git','show',pref['sourceCommit']+':education/'+p],cwd=repo)).hexdigest()==h,p
for p,h in pref['artifactHashes'].items():assert hashf(prefdir/p)==h,p
report['checks']['frozenSourceAndArtifactHashes']=len(pref['sourceHashes'])+len(pref['artifactHashes'])
schedule=pref['schedule']; assert len(schedule)==15
assert sum(2*r['points'] for r in schedule)-4000==497500
assert sum(2*(r['depth']+1) for r in schedule)==634
source=next(x for x in json.loads((root/'data/anatomical-arm-v1/generated/arm-reference.json').read_text())['muscles'] if x['element_id']=='FJ1486'); arrays=json.loads((root/'review/fixed-field-integration-run-20261007/saved-arrays.json').read_text()); ids=source['elements_ten_node']; xyz=np.array(source['nodes_m']); fields={k:np.array(v) for k,v in arrays['positionsM'].items()}
G=np.array([[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]]); edges=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
def monos(degree):return [a for a in itertools.product(range(degree+1),repeat=4) if sum(a)<=degree]
def bounds(s,depth):return (F(0),F(1,2**depth)) if s=='core' else (F(1,2**int(s[1:])),F(1,2**(int(s[1:])-1)))
cache={}
def integral(a,lo,hi):
 key=(a,lo,hi)
 if key in cache:return cache[key]
 p=sum(a[1:]); angular=F(6*math.prod(math.factorial(x) for x in a[1:]),math.factorial(p+2)); radial=sum((F((-1)**k*math.comb(a[0],k),p+3+k)*(hi**(p+3+k)-lo**(p+3+k)) for k in range(a[0]+1)),F(0));cache[key]=angular*radial;return cache[key]
def det_polynomial(e):
 X=[[F(float(x)) for x in row] for row in xyz[ids[e]]]; coeff=[[[F(0) for _ in range(4)] for _ in range(3)] for _ in range(3)]
 for n in range(10):
  for k in range(4):
   grad=[int((4*(n==k)-1)*G[n,j]) if n<4 else 4*int((edges[n-4][0]==k)*G[edges[n-4][1],j]+(edges[n-4][1]==k)*G[edges[n-4][0],j]) for j in range(3)]
   for d in range(3):
    for j in range(3):coeff[d][j][k]+=X[n][d]*grad[j]
 out={}
 for perm in itertools.permutations(range(3)):
  inversions=sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3));sign=(-1)**inversions
  for ks in itertools.product(range(4),repeat=3):
   alpha=tuple(ks.count(k) for k in range(4));v=sign*math.prod(coeff[d][perm[d]][ks[d]] for d in range(3));out[alpha]=out.get(alpha,F(0))+v
 return out
polys={e:det_polynomial(e) for e in {r['element'] for r in schedule}}
normalized_checks=0; max_norm_error=0.; norms={}
for r in schedule:
 key=f"{r['id']}-c{r['corner']}"
 if key in norms:continue
 assert ids[r['element']][r['corner']]==92
 expected_face=[i for i in range(4) if i!=r['corner']]
 if r['id']=='X44':expected_face=[2,3,1]
 assert r['faceOrder']==expected_face
 norms[key]=r
 for s in [f's{i}' for i in range(1,r['depth']+1)]+['core']:
  q=np.fromfile(prefdir/f'{key}-{s}-points.f64le',dtype='<f8').reshape(-1,6);L=q[:,:4];w=q[:,4];rad=q[:,5];lo,hi=bounds(s,r['depth']);assert np.isfinite(q).all() and (q>0).all();assert np.max(np.abs(L.sum(axis=1)-1))<1e-15;assert np.max(np.abs(rad-(1-L[:,r['corner']])))<1e-15;assert (rad>float(lo)).all() and (rad<float(hi)).all()
  canonical=L[:,[r['corner'],*r['faceOrder']]]
  for a in monos(5):
   actual=np.dot(w,np.prod(canonical**np.array(a),axis=1));expected=float(integral(a,lo,hi));err=abs(actual-expected)/expected;assert err<=2e-11,(key,s,a,err);max_norm_error=max(max_norm_error,err);normalized_checks+=1
physical_checks=0;geometry_checks=0;max_weight_error=0.;max_physical_error=0.;minimumJ=math.inf;minimumRef=math.inf
for r in schedule:
 key=f"{r['id']}-c{r['corner']}";e=r['element'];corner_order=[r['corner'],*r['faceOrder']]
 for s in [f's{i}' for i in range(1,r['depth']+1)]+['core']:
  q=np.fromfile(prefdir/f'{key}-{s}-points.f64le',dtype='<f8').reshape(-1,6);L=q[:,:4];w=q[:,4];lo,hi=bounds(s,r['depth']);grad=np.empty((len(q),10,3));grad[:,:4,:]=(4*L[:,:,None]-1)*G[None,:,:]
  for n,(i,j) in enumerate(edges,4):grad[:,n,:]=4*(L[:,i,None]*G[j]+L[:,j,None]*G[i])
  R=np.einsum('nd,qnj->qdj',xyz[ids[e]],grad);refdet=np.linalg.det(R);assert (refdet>1e-15).all();minimumRef=min(minimumRef,float(refdet.min()));physical=np.fromfile(prefdir/f'{e}-{r["id"]}-{s}-weights.f64le',dtype='<f8');expected=w*refdet/6;err=float(np.max(np.abs(physical-expected)/physical));assert err<2e-13;max_weight_error=max(max_weight_error,err)
  for field in ['control45','terminal46']:
   current=np.einsum('nd,qnj->qdj',fields[field][ids[e]],grad);J=np.linalg.det(current)/refdet;assert (J>1e-6).all();minimumJ=min(minimumJ,float(J.min()));geometry_checks+=len(J)
  for a in monos(2):
   expected=sum((value*integral(tuple(a[corner_order[i]]+b[corner_order[i]] for i in range(4)),lo,hi)/6 for b,value in polys[e].items()),F(0));actual=np.dot(physical,np.prod(L**np.array(a),axis=1));err=abs(actual-float(expected))/float(expected);assert err<2e-10,(e,r['id'],s,a,err);max_physical_error=max(max_physical_error,err);physical_checks+=1
assert normalized_checks==29358 and physical_checks==4755 and geometry_checks==501500
binary=sum(p.stat().st_size for p in prefdir.glob('*.f64le'));assert binary==12782000
plan=json.loads((prefdir/'storage-plan.json').read_text());assert sum(plan['files'].values())==46172592;assert len(plan['files'])==1232;assert plan['maximumCombinedBytes']==48925104
assert not (root/'research/selective-fixed-patch-authorization-20261007.json').exists();assert not (root/'review/selective-fixed-patch-run-20261007').exists()
report['checks'].update({'newCalls':497500,'logicalRows':634,'normalizedMoments':normalized_checks,'physicalMoments':physical_checks,'geometrySamples':geometry_checks,'maxNormalizedRelativeError':max_norm_error,'maxPhysicalMomentRelativeError':max_physical_error,'maxPhysicalWeightRelativeError':max_weight_error,'minimumSampleJ':minimumJ,'minimumReferenceJacobian':minimumRef,'binaryBytes':binary,'planFiles':1232,'planDeclaredBytes':48925104,'authorizationAbsent':True,'executionDirectoryAbsent':True})
report['verdict']='GEOMETRY_AND_IDENTITIES_PASS_RESOURCE_REVIEW_PENDING';out=pathlib.Path('/tmp/selective-independent-structural.json');out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

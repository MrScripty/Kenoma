#!/usr/bin/env python3
"""Independent P2 Jacobian/weight/moment replay; only JSON and mathematical geometry."""
import runpy, json, math, itertools, pathlib, time
from fractions import Fraction as Q
import numpy as np
D={}
geometry_source=pathlib.Path('/tmp/fine-window-geometry-independent/check_geometry.py').read_text().split('\nstart=time.monotonic();result=')[0]
exec(compile(geometry_source,'independent_geometry_definitions','exec'),D)
mesh=D['mesh'];expected=D['expected'];GX=D['GAUSS_X'];GW=D['GAUSS_W'];OUT=D['OUT']
ROOT=pathlib.Path('/tmp/Kenoma-fine-window-schedule/education')
source=next(s for s in json.loads((ROOT/'data/anatomical-arm-v1/generated/arm-reference.json').read_text())['muscles'] if s['element_id']=='FJ1486')
arrays=json.loads((ROOT/'review/fixed-field-integration-run-20261007/saved-arrays.json').read_text())
CORNER={197:3,200:3,203:2,206:1,246:0,247:0,248:0}
EDGES=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)];G=np.array([[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]])
MONOS=[a for a in itertools.product(range(3),repeat=4) if sum(a)<=2]

def shape(L):
 out=(4*L[:,:,None]-1)*G[None,:,:]
 edges=np.stack([4*(L[:,i,None]*G[j]+L[:,j,None]*G[i]) for i,j in EDGES],axis=1)
 return np.concatenate((out,edges),axis=1)

def det3(cols):
 a,b,c=cols
 return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

def jacobian_polynomial(X):
 # Independent corner-Jacobian interpolation with exact input dyadic fractions.
 x=[[Q(float(v)) for v in row] for row in X]
 grad=shape(np.eye(4));mat=[]
 for r in range(4):
  mat.append([[sum(x[n][a]*int(grad[r,n,b]) for n in range(10)) for a in range(3)] for b in range(3)])
 poly={}
 for i,j,k in itertools.product(range(4),repeat=3):
  alpha=tuple((i,j,k).count(n) for n in range(4))
  poly[alpha]=poly.get(alpha,Q(0))+det3((mat[i][0],mat[j][1],mat[k][2]))
 return poly

u,v,w=np.meshgrid(GX,GX,GX,indexing='ij');u=u.ravel();v=v.ravel();w=w.ravel();B=np.stack((1-u,u*(1-v),u*v*(1-w),u*v*w),axis=1)
wu,wv,ww=np.meshgrid(GW,GW,GW,indexing='ij');base=6*wu.ravel()*wv.ravel()*ww.ravel()*u**2*v
start=time.monotonic();rows=[];count=0;checks=0;maximum=0;minref=math.inf;minw=math.inf;minJ={s:math.inf for s in ('control45','terminal46')}
for name,m,rp in [('I0',4,1),('I1',8,2)]:
 denominator,regions=mesh(m,rp,0)
 for element,corner in CORNER.items():
  ids=source['elements_ten_node'][element];X=np.array([source['nodes_m'][n] for n in ids]);poly=jacobian_polynomial(X);order=[corner]+[k for k in range(4) if k!=corner]
  for s,tets in regions:
   verts=np.array([v for v,d in tets],dtype=np.float64)/denominator
   canonical=np.einsum('pj,tjk->tpk',B,verts).reshape(-1,4);L=np.zeros_like(canonical);L[:,order]=canonical
   norm=(np.array([d/denominator**3 for v,d in tets])[:,None]*base).ravel()
   grad=shape(L);refmat=np.einsum('na,pnb->pab',X,grad);ref=np.linalg.det(refmat);weights=norm*ref/6
   assert np.all(np.isfinite(ref)) and np.min(ref)>1e-15
   assert np.all(np.isfinite(weights)) and np.min(weights)>0
   minref=min(minref,float(np.min(ref)));minw=min(minw,float(np.min(weights)));localJ={}
   for state in minJ:
    current=np.array([arrays['positionsM'][state][n] for n in ids]);cmat=np.einsum('na,pnb->pab',current,grad);J=np.linalg.det(cmat)/ref
    assert np.all(np.isfinite(J)) and np.min(J)>1e-6
    localJ[state]=float(np.min(J));minJ[state]=min(minJ[state],localJ[state]);count+=len(L)
   lo=Q(1,2**(s+1)) if s<20 else Q(0);hi=Q(1,2**s) if s<20 else Q(1,2**20);localmax=0
   for alpha in MONOS:
    truth=sum(c*expected(tuple((alpha[k]+a[k]) for k in order),lo,hi) for a,c in poly.items())/6
    expected_float=float(truth);actual=float(np.sum(weights*np.prod(L**np.array(alpha),axis=1)))
    error=abs(actual-expected_float)/expected_float;assert truth>0 and error<=2e-10,(name,element,s,alpha,error)
    localmax=max(localmax,error);maximum=max(maximum,error);checks+=1
   rows.append({'recipe':name,'element':element,'corner':corner,'region':'s'+str(s+1) if s<20 else 'core','points':len(L),'physicalMomentChecks':len(MONOS),'maximumPhysicalMomentRelativeError':localmax,'minimumSampleJ':localJ})
result={'schema':1,'status':'PASS_INDEPENDENT_PHYSICAL_GEOMETRY_DESIGN','specimenCalls':0,'materialLawInvocations':0,'geometricStatePointChecks':count,'physicalMomentChecks':checks,'maximumPhysicalMomentRelativeError':maximum,'minimumReferenceJacobian':minref,'minimumPhysicalWeightM3':minw,'minimumSampleJ':minJ,'seconds':time.monotonic()-start,'rows':rows,'productionPhysicalWeightsReviewed':False}
(OUT/'physical-geometry-design-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))

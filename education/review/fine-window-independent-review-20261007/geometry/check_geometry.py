#!/usr/bin/env python3
"""Independent exact topology and streaming geometry moments; no repository imports."""
import itertools, math, json, hashlib, pathlib, time
from fractions import Fraction as Q
from collections import Counter
import numpy as np
OUT=pathlib.Path('/tmp/fine-window-geometry-independent')
GAUSS_X=np.array([.046910077030668,.23076534494715845,.5,.7692346550528415,.953089922969332])
GAUSS_W=np.array([.11846344252809454,.23931433524968324,.28444444444444444,.23931433524968324,.11846344252809454])
MONOS=[a for a in itertools.product(range(6),repeat=4) if sum(a)<=5]
ASSERTIONS=0
def check(v,message):
 global ASSERTIONS
 ASSERTIONS+=1
 assert v,message

def determinant(v):
 a,b,c=[tuple(v[k][i]-v[0][i] for i in range(1,4)) for k in range(1,4)]
 return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

def triangles(m):
 rows=[]
 for i in range(m+1):
  for j in range(m+1-i):
   if i+j<=m-1:rows.append(sorted([(i,j),(i+1,j),(i,j+1)]))
   if i+j<=m-2:rows.append(sorted([(i+1,j),(i+1,j+1),(i,j+1)]))
 return rows

def mesh(m,rp,corner):
 D=(2**20)*m*rp; face=[k for k in range(4) if k!=corner]; regions=[]
 ts=triangles(m)
 for s in range(21):
  if s<20:
   lo=2**(19-s)*m*rp;hi=2**(20-s)*m*rp
   ranges=[(lo+(hi-lo)*k//rp,lo+(hi-lo)*(k+1)//rp) for k in range(rp)]
  else:ranges=[(0,m*rp)]
  tets=[]
  for lo,hi in ranges:
   for tri in ts:
    vertices=[]
    for radius in (lo,hi):
     for i,j in tri:
      v=[0]*4;v[corner]=D-radius
      for k,n in zip(face,(i,j,m-i-j)):v[k]=radius*n//m
      check(sum(v)==D,'vertex barycentric sum');vertices.append(tuple(v))
    A0,A1,A2,B0,B1,B2=vertices
    candidates=[(A0,A1,A2,B2),(A0,A1,B1,B2),(A0,B0,B1,B2)] if lo else [(tuple(D if k==corner else 0 for k in range(4)),B0,B1,B2)]
    for v in candidates:
     d=determinant(v);check(d!=0,'zero tet')
     if d<0:v=(v[0],v[1],v[3],v[2]);d=-d
     tets.append((v,d))
  regions.append((s,tets))
 return D,regions

def permutation_sign(xs):
 return -1 if sum(xs[i]>xs[j] for i in range(len(xs)) for j in range(i+1,len(xs)))%2 else 1

def topology(m,rp,corner):
 D,regions=mesh(m,rp,corner);faces={};dets=0;per_region=[]
 for s,tets in regions:
  expected=((3*rp) if s<20 else 1)*m*m
  check(len(tets)==expected,'tet count')
  regiondet=sum(d for v,d in tets);lo=Q(1,2**(s+1)) if s<20 else Q(0);hi=Q(1,2**s) if s<20 else Q(1,2**20)
  check(Q(regiondet,D**3)==hi**3-lo**3,'exact normalized region mass')
  per_region.append(regiondet)
  for v,d in tets:
   dets+=d
   for excluded in range(4):
    oriented=[v[k] for k in range(4) if k!=excluded];key=tuple(sorted(oriented));ranks=[key.index(x) for x in oriented]
    sign=(-1)**excluded*permutation_sign(ranks)
    row=faces.setdefault(key,[0,0]);row[0]+=1;row[1]+=sign
 check(dets==D**3,'exact full normalized mass')
 boundary=0;counts=Counter()
 for face,(count,sign) in faces.items():
  check(count in (1,2),'nonmanifold face')
  if count==2:check(sign==0,'inconsistent internal face orientation')
  else:
   boundary+=1;zero=[k for k in range(4) if all(v[k]==0 for v in face)]
   check(len(zero)==1,'exposed interior face / gap');counts[zero[0]]+=1
 check(counts[corner]==m*m,'outer face coverage')
 for k in range(4):
  if k!=corner:check(counts[k]==40*m*rp+m,'side face coverage')
 return {'corner':corner,'microtetrahedra':sum(len(t) for s,t in regions),'faces':len(faces),'boundaryTriangles':boundary,'exactNormalizedMass':'1','positiveOrientation':True,'internalFaceOrientationAndMultiplicity':True}

def expected(alpha,lo,hi):
 a0=alpha[0];t=sum(alpha[1:]);value=Q(0)
 for k in range(a0+1):
  p=t+3+k;value+=Q(math.comb(a0,k)*(-1)**k,p)*(hi**p-lo**p)
 return Q(6*math.prod(math.factorial(x) for x in alpha[1:]),math.factorial(t+2))*value

def numerical(m,rp):
 D,regions=mesh(m,rp,0);checks=0;maxerr=0;minimum=math.inf;hashes=[]
 U,V,W=np.meshgrid(GAUSS_X,GAUSS_X,GAUSS_X,indexing='ij');U=U.ravel();V=V.ravel();W=W.ravel()
 B=np.stack((1-U,U*(1-V),U*V*(1-W),U*V*W),axis=1)
 wu,wv,ww=np.meshgrid(GAUSS_W,GAUSS_W,GAUSS_W,indexing='ij');base=6*wu.ravel()*wv.ravel()*ww.ravel()*U**2*V
 for s,tets in regions:
  vertices=np.array([v for v,d in tets],dtype=np.float64)/D
  points=np.einsum('pj,tjk->tpk',B,vertices).reshape(-1,4)
  weights=(np.array([d/D**3 for v,d in tets])[:,None]*base).ravel()
  check(np.all(np.isfinite(points)) and np.all(points>0) and np.all(points<1),'interior finite points')
  check(np.max(np.abs(np.sum(points,axis=1)-1))<1e-14,'point barycentric sum')
  check(np.all(np.isfinite(weights)) and np.min(weights)>0,'positive finite weights')
  minimum=min(minimum,float(np.min(weights)))
  lo=Q(1,2**(s+1)) if s<20 else Q(0);hi=Q(1,2**s) if s<20 else Q(1,2**20)
  for alpha in MONOS:
   truth=float(expected(alpha,lo,hi));value=float(np.sum(weights*np.prod(points**np.array(alpha),axis=1)))
   error=abs(value-truth)/truth;check(error<=2e-11,'normalized degree5 moment');maxerr=max(maxerr,error);checks+=1
  h=hashlib.sha256(points.astype('<f8').tobytes()+weights.astype('<f8').tobytes()).hexdigest();hashes.append(h)
 return {'corner':0,'normalizedDegree5Checks':checks,'maximumRelativeError':maxerr,'minimumNormalizedWeight':minimum,'regionPointWeightFingerprints':hashes,'peakPointsHeld':max(len(t)*125 for s,t in regions),'otherCorners':'Exact coordinate permutations; all topology charts checked separately. Actual source serialization/hash review still required.'}

start=time.monotonic();result={'schema':1,'status':'PASS_INDEPENDENT_GEOMETRY_DESIGN','specimenCalls':0,'materialLawInvocations':0,'sourceEdits':0,'degreeProof':{'polynomialTotalDegree':5,'weightedDuffyMaxDegrees':[7,6,5],'gauss5ExactThroughDegreePerAxis':9},'recipes':{}}
for name,m,rp in [('I0',4,1),('I1',8,2)]:
 result['recipes'][name]={'topology':[topology(m,rp,c) for c in range(4)],'numerical':numerical(m,rp)}
result['assertions']=ASSERTIONS;result['seconds']=time.monotonic()-start
(OUT/'geometry-design-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='recipes'},indent=2))

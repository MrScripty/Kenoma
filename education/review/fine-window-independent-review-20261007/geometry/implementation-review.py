#!/usr/bin/env python3
"""Independent frozen implementation geometry review; no law imports/calls."""
import json, pathlib, hashlib, itertools, subprocess, math, time, sys
from fractions import Fraction as Q
import numpy as np
ROOT=pathlib.Path('/tmp/Kenoma-fine-window-runner');OUT=pathlib.Path('/tmp/fine-window-geometry-independent');PREF=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('/tmp/kenoma-fine-preflight-initial-20261007')
HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();D={}
exec(compile((OUT/'check_geometry.py').read_text().split('\nstart=time.monotonic();result=')[0],'independent_geometry_definitions','exec'),D)
check=D['check'];det=D['determinant'];GX=D['GAUSS_X'];GW=D['GAUSS_W'];expected=D['expected'];MONOS=D['MONOS']

def ordered_triangles(m):
 ts=[]
 for i in range(m):
  for j in range(m-i):ts.append(sorted(((i,j),(i+1,j),(i,j+1))))
 for i in range(m-1):
  for j in range(m-1-i):ts.append(sorted(((i+1,j),(i+1,j+1),(i,j+1))))
 return ts

def ordered_tets(m,rp,corner,s):
 den=2**20*m*rp;face=[n for n in range(4) if n!=corner];lo=2**(19-s)*m*rp if s<20 else 0;hi=2**(20-s)*m*rp if s<20 else m*rp;idx=0
 def vertex(radius,ij):
  i,j=ij;v=[0]*4;v[corner]=den-radius
  for k,n in zip(face,(i,j,m-i-j)):v[k]=radius*n//m
  return tuple(v)
 for tri in ordered_triangles(m):
  intervals=[(lo+(hi-lo)*k//rp,lo+(hi-lo)*(k+1)//rp) for k in range(rp)] if s<20 else [(0,hi)]
  for low,high in intervals:
   A=[vertex(low,p) for p in tri];B=[vertex(high,p) for p in tri]
   candidates=[(A[0],A[1],A[2],B[2]),(A[0],A[1],B[1],B[2]),(A[0],B[0],B[1],B[2])] if low else [(tuple(den if k==corner else 0 for k in range(4)),*B)]
   for v in candidates:
    determinant=det(v)
    if determinant<0:v=(v[0],v[1],v[3],v[2]);determinant=-determinant
    yield {'vertices':[list(x) for x in v],'det':str(determinant),'D':den,'index':idx};idx+=1

u,v,w=np.meshgrid(GX,GX,GX,indexing='ij');u=u.ravel();v=v.ravel();w=w.ravel();B=np.stack((1-u,u*(1-v),u*v*(1-w),u*v*w),axis=1)
wu,wv,ww=np.meshgrid(GW,GW,GW,indexing='ij');base=6*wu.ravel()*wv.ravel()*ww.ravel()*u**2*v
start=time.monotonic();sourcefiles=['fine-window-maps.mjs','fine-window-protocol.mjs','fine-window-moments.mjs','preflight-fine-window.mjs'];sourcehash={}
for name in sourcefiles:
 p=ROOT/'education/tools'/name;f=p.read_bytes();check(f==subprocess.check_output(['git','cat-file','blob',HEAD+':education/tools/'+name],cwd=ROOT),'frozen source identity');sourcehash['education/tools/'+name]=hashlib.sha256(f).hexdigest()
metadata=iter((OUT/'implementation-tets.jsonl').open());tetchecks=0;pointchecks=0;moments=0;maxcoords=0;maxweights=0;maxmoment=0;arrays=[]
for name,m,rp in [('I0',4,1),('I1',8,2)]:
 for corner in range(4):
  order=[corner]+[k for k in range(4) if k!=corner]
  for s in range(21):
   region='s'+str(s+1) if s<20 else 'core';tets=list(ordered_tets(m,rp,corner,s))
   # Export source enumerates corners in0,1,2,3 by elements247,206,203,197.
   for tet in tets:
    actual=json.loads(next(metadata));check(actual['id']==name and actual['corner']==corner and actual['region']==region,'metadata identity')
    for k in tet:check(actual[k]==tet[k],'exact tet metadata '+k)
    tetchecks+=1
   filename=f'{name}-c{corner}-{region}-points.f64le';p=PREF/filename;raw=p.read_bytes();x=np.frombuffer(raw,dtype='<f8').reshape(-1,6)
   vertices=np.array([t['vertices'] for t in tets],dtype=np.float64)/tets[0]['D'];coords=np.einsum('pj,tjk->tpk',B,vertices).reshape(-1,4)
   weights=(np.array([int(t['det'])/t['D']**3 for t in tets])[:,None]*base).ravel();coordinate_error=float(np.max(np.abs(x[:,:4]-coords)));weight_error=float(np.max(np.abs(x[:,4]-weights)/weights))
   check(len(x)==len(tets)*125,'point count');check(coordinate_error<=8e-16,'independent actual point map');check(weight_error<=2e-15,'independent actual normalized weight');check(np.all(x[:,4]>0),'positive normalized weights');check(np.max(np.abs(x[:,:4].sum(axis=1)-1))<1e-14,'actual barycentric sum');check(np.max(np.abs(x[:,5]-x[:,order[1:]].sum(axis=1)))<1e-15,'r=sumopposite');maxcoords=max(maxcoords,coordinate_error);maxweights=max(maxweights,weight_error);pointchecks+=len(x)
   lo=Q(1,2**(s+1)) if s<20 else Q(0);hi=Q(1,2**s) if s<20 else Q(1,2**20);canonical=x[:,order]
   for alpha in MONOS:
    truth=float(expected(alpha,lo,hi));value=float(np.sum(x[:,4]*np.prod(canonical**np.array(alpha),axis=1)));error=abs(value-truth)/truth;check(error<=2e-11,'actual normalizeddegree5');moments+=1;maxmoment=max(maxmoment,error)
   arrays.append({'filename':filename,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'points':len(x),'maximumCoordinateDifference':coordinate_error,'maximumRelativeWeightDifference':weight_error})
try:next(metadata);raise AssertionError('extra metadata')
except StopIteration:pass
result={'schema':1,'status':'PASS_FROZEN_IMPLEMENTATION_MAPS_PREFLIGHT_PENDING','sourceCommit':HEAD,'sourceHashes':sourcehash,'specimenCalls':0,'materialLawInvocations':0,'sourceEdits':0,'tetrahedraExactMetadataChecks':tetchecks,'pointChecks':pointchecks,'normalizedDegree5Checks':moments,'maximumIndependentCoordinateDifference':maxcoords,'maximumIndependentRelativeWeightDifference':maxweights,'maximumActualNormalizedMomentRelativeError':maxmoment,'preflightDirectory':str(PREF),'preflightCompleted':False,'arrays':arrays,'seconds':time.monotonic()-start}
if (PREF/'preflight.json').exists():
 prefraw=(PREF/'preflight.json').read_bytes();pref=json.loads(prefraw);check(pref['sourceCommit']==HEAD,'preflight source');check(pref['specimenCalls']==0 and pref['materialLawInvocations']==0,'preflightzero calls');check(pref['result']=='PASS_FINE_WINDOW_STRUCTURAL_PREFLIGHT_NO_SPECIMEN_CALLS','prefpass')
 for r in arrays:check(pref['artifactHashes'][r['filename']]==r['sha256'],'closed actual array hash')
 for p,h in pref['sourceHashes'].items():check(hashlib.sha256((ROOT/'education'/p).read_bytes()).hexdigest()==h,'sourcehash '+p)
 result.update(status='PASS_FROZEN_IMPLEMENTATION_GEOMETRY',preflightCompleted=True,preflightSha256=hashlib.sha256(prefraw).hexdigest(),preflightCounters={k:pref[k] for k in ['normalizedMomentChecks','physicalMomentChecks','geometryPointChecks','minimumSampleJ','newPlannedCallbacks','newBinaryBytes','worstCaseCombinedOutputBytes']})
result['assertions']=D['ASSERTIONS'];(OUT/'implementation-map-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='arrays'},indent=2))

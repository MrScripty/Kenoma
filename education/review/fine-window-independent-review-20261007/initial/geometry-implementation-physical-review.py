#!/usr/bin/env python3
"""Independent actual-array physical weight/moment check, no material calls."""
import pathlib,json,hashlib,subprocess,sys,time,math
import numpy as np
from fractions import Fraction as Q
OUT=pathlib.Path('/tmp/fine-window-geometry-independent');ENV={}
exec(compile((OUT/'check_physical_geometry.py').read_text().split('\nstart=time.monotonic();rows=')[0],'independent_physical_definitions','exec'),ENV)
shape=ENV['shape'];polynomial=ENV['jacobian_polynomial'];expected=ENV['expected'];MONOS=ENV['MONOS'];CORNERS=ENV['CORNER']
ROOT=pathlib.Path('/tmp/Kenoma-fine-window-runner');EDU=ROOT/'education';PREF=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('/tmp/kenoma-fine-preflight-initial-20261007')
HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();source=next(s for s in json.loads((EDU/'data/anatomical-arm-v1/generated/arm-reference.json').read_text())['muscles'] if s['element_id']=='FJ1486');arrays=json.loads((EDU/'review/fixed-field-integration-run-20261007/saved-arrays.json').read_text());rawdir=EDU/'review/selective-fixed-patch-run-20261007/material'
start=time.monotonic();moments=0;pointchecks=0;maximum=0;maxweights=0;minref=math.inf;minweight=math.inf;minJ={s:math.inf for s in ('control45','terminal46')};rows=[]
for name in ['I0','I1']:
 for element,corner in CORNERS.items():
  ids=source['elements_ten_node'][element];X=np.array([source['nodes_m'][n] for n in ids]);poly=polynomial(X);order=[corner]+[k for k in range(4) if k!=corner]
  for s in range(21):
   region='s'+str(s+1) if s<20 else 'core';pointname=f'{name}-c{corner}-{region}-points.f64le';weightname=f'{element}-{name}-{region}-weights.f64le';raw=(PREF/pointname).read_bytes();wraw=(PREF/weightname).read_bytes();points=np.frombuffer(raw,dtype='<f8').reshape(-1,6);L=points[:,:4];weights=np.frombuffer(wraw,dtype='<f8');assert len(weights)==len(points)
   grad=shape(L);ref=np.linalg.det(np.einsum('na,pnb->pab',X,grad));expectedweights=points[:,4]*ref/6;werr=float(np.max(np.abs(weights-expectedweights)/expectedweights));assert werr<=2e-12
   assert np.all(np.isfinite(weights)) and np.min(weights)>0;maxweights=max(maxweights,werr);minref=min(minref,float(np.min(ref)));minweight=min(minweight,float(np.min(weights)));localJ={}
   for state in minJ:
    current=np.array([arrays['positionsM'][state][n] for n in ids]);J=np.linalg.det(np.einsum('na,pnb->pab',current,grad))/ref;assert np.all(np.isfinite(J)) and np.min(J)>1e-6;localJ[state]=float(np.min(J));minJ[state]=min(minJ[state],localJ[state]);pointchecks+=len(L)
   lo=Q(1,2**(s+1)) if s<20 else Q(0);hi=Q(1,2**s) if s<20 else Q(1,2**20);localmax=0
   for alpha in MONOS:
    truth=sum(c*expected(tuple(alpha[k]+a[k] for k in order),lo,hi) for a,c in poly.items())/6;value=float(np.sum(weights*np.prod(L**np.array(alpha),axis=1)));error=abs(value-float(truth))/float(truth);assert truth>0 and error<=2e-10;maximum=max(maximum,error);localmax=max(localmax,error);moments+=1
   rows.append({'filename':weightname,'sha256':hashlib.sha256(wraw).hexdigest(),'bytes':len(wraw),'points':len(points),'maximumPhysicalMomentRelativeError':localmax,'maximumIndependentRelativeWeightDifference':werr,'minimumSampleJ':localJ})
result={'schema':1,'status':'PASS_FROZEN_IMPLEMENTATION_PHYSICAL_ARRAYS_PREFLIGHT_PENDING','sourceCommit':HEAD,'specimenCalls':0,'materialLawInvocations':0,'sourceEdits':0,'physicalMomentChecks':moments,'geometricStatePointChecks':pointchecks,'maximumPhysicalMomentRelativeError':maximum,'maximumIndependentRelativeWeightDifference':maxweights,'minimumReferenceJacobian':minref,'minimumPhysicalWeightM3':minweight,'minimumSampleJ':minJ,'arrays':rows,'preflightCompleted':False,'preflightDirectory':str(PREF),'outside236Qualified':False,'seconds':time.monotonic()-start}
if (PREF/'preflight.json').exists():
 raw=(PREF/'preflight.json').read_bytes();pref=json.loads(raw);assert pref['sourceCommit']==HEAD and pref['specimenCalls']==0 and pref['materialLawInvocations']==0
 for r in rows:assert pref['artifactHashes'][r['filename']]==r['sha256']
 aliaschecks=0
 for name,region in pref['regions'].items():
  n=region['normalizedOrigin'];w=region['weightOrigin'];np=(rawdir if n['kind']=='historical' else PREF)/n['name'];wp=(rawdir if w['kind']=='historical' else PREF)/w['name'];assert hashlib.sha256(np.read_bytes()).hexdigest()==region['normalizedSha256'];assert hashlib.sha256(wp.read_bytes()).hexdigest()==region['physicalSha256'];aliaschecks+=2
 result.update(status='PASS_FROZEN_IMPLEMENTATION_PHYSICAL_GEOMETRY_AND_REUSE_ALIASES',preflightCompleted=True,preflightSha256=hashlib.sha256(raw).hexdigest(),normalizedPhysicalOriginHashChecks=aliaschecks)
(OUT/'implementation-physical-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='arrays'},indent=2))

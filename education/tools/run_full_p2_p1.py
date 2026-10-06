"""Source-bound controlled solves/replays; refuses overwriting earlier evidence."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
import numpy as np
from scipy.linalg import eigh,solve,cho_solve
from full_p2_p1 import Body,mesh,shape,PARAM,ACTIVATION
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/anatomical-arm-v1/review/full-p2-p1'
SOURCES=['tools/full_p2_p1.py','tools/full-p2-p1-replay.mjs','tools/run_full_p2_p1.py',
 'tests/test_full_p2_p1.py','research/mechanical-closure/full-p2-p1-protocol.md',
 'web/anatomical-material.mjs','web/anatomical-modal.mjs','web/anatomical-element.mjs',
 'web/anatomical-intersections.mjs','tools/anatomical-compression-quadrature.mjs']
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def serial(value):
 if isinstance(value,np.ndarray):return value.tolist()
 if isinstance(value,np.generic):return value.item()
 if isinstance(value,dict):return {k:serial(v) for k,v in value.items()}
 if isinstance(value,list):return [serial(v) for v in value]
 return value
def save(name,data):
 path=OUT/name
 with path.open('x') as f:json.dump(serial(data),f,indent=2,allow_nan=False);f.write('\n')
def replay(m,x,p,depth):
 proc=subprocess.run(['node',str(ROOT/'tools/full-p2-p1-replay.mjs')],
  input=json.dumps(dict(mesh=serial(m),positionsM=x.tolist(),pressurePa=p.tolist(),material=PARAM,activation=ACTIVATION,depth=depth)),
  text=True,capture_output=True,check=True)
 return json.loads(proc.stdout)
def coupling(B,r):
 f=B.m['free'];D=r['D'][:,f].toarray();A=B.A[f][:,f].toarray()
 scaled=D@solve(A,D.T,assume_a='pos')
 eig=eigh(scaled,B.M,eigvals_only=True)
 rank=int(np.sum(eig>max(eig)*1e-10))
 return dict(pressureCount=B.m['nv'],rank=rank,dimensionlessEigenvalues=eig,
  beta=float(np.sqrt(max(0,eig[0]))),relativeRankThreshold=1e-10,
  convention='reference H1 displacement seminorm; pressure mass; free lateral surfaces; no pressure mode removed')
def interpolate(coarse,positions,fineX):
 values=[]
 for X in fineX:
  candidates=[]
  for ids in coarse['tets']:
   V=coarse['X'][ids[:4]]; natural=np.linalg.solve((V[1:]-V[0]).T,X-V[0]);L=np.r_[1-natural.sum(),natural]
   if L.min()>=-1e-10 and L.max()<=1+1e-10:
    N,_=shape(L);candidates.append(N[0]@positions[ids])
  if not candidates:raise ValueError('Refinement node outside coarse reference mesh')
  if np.max(np.linalg.norm(np.array(candidates)-candidates[0],axis=1))>1e-10:raise ValueError('Nonconforming coarse interpolation')
  values.append(candidates[0])
 return np.array(values)
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if (OUT/'summary.json').exists() or any(OUT.glob('coarse-*.json')):raise RuntimeError('Preserve original runs')
 source={p:digest(ROOT/p) for p in SOURCES}
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 start=time.time();records={};meshes={}
 for label,counts in [('coarse',(4,1,1)),('fine',(8,2,2))]:
  m=mesh(counts);B=Body(m);meshes[label]=m
  save(label+'-mesh.json',dict(sourceHashes=source,sourceCommit=commit,mesh=m,referenceVolumeM3=B.volume))
  for stretch in [1.,1.01,1.25]:
   name=f'{label}-{stretch:.2f}';initial,analyticX,analytic=B.initial(stretch)
   print('START',name,'free',len(m['free']),flush=True)
   x,r,history,reason=B.newton(initial)
   replays={};checks=[]
   for depth in [1,2]:
    q=replay(m,x,r['p'],depth);qr=B if depth==2 else Body(m,depth)
    weak=np.array(q['weak']);q['weakPressureRMS']=float(np.sqrt(max(0,weak@cho_solve(qr.Mfactor,weak)/qr.volume)))
    q['maximumGradientDifferenceN']=float(np.max(np.abs(r['g']-q['gradientN'])))
    replays[str(4*8**depth)]=q
    checks.extend([q['freeNodalResidualN']<=1e-4,q['maximumGradientDifferenceN']<=2e-6,
     abs(q['capForceN']-q['virtualForceN'])<=1e-3,q['weakPressureRMS']<=1e-6,
     q['pointwisePressureRMS']<=1e-6,q['Jmin']>=.98,q['Jmax']<=1.02,q['surface']['crossingPairs']==0,
     abs(q['capForceN']-analytic['capForceN'])/analytic['capForceN']<=.01])
   checks.extend([np.isfinite(x).all(),np.array_equal(initial[m['cap']],x[m['cap']])])
   stationary=bool(all(checks));spectrum=None
   if stationary and stretch!=1:
    eig,v=eigh(r['H'],subset_by_index=[0,5]);direction=np.zeros(x.size);direction[m['free']]=v[:,0];direction=direction.reshape(x.shape)
    Hv=r['H']@v[:,0];finite=[]
    for h in [1e-7,5e-8]:
     gp=B.evaluate(x+h*direction)['g'][m['free']];gm=B.evaluate(x-h*direction)['g'][m['free']]
     fd=(gp-gm)/(2*h);finite.append(dict(stepM=h,relativeError=float(np.linalg.norm(fd-Hv)/np.linalg.norm(Hv))))
    spectrum=dict(lowestEigenvaluesNPerM=eig,witnessDirection=direction,
     witnessUnitNorm=float(np.linalg.norm(direction)),firstVariationN=float(r['g']@direction.ravel()),
     gradientDifferenceChecks=finite,gradientDifferencePass=all(c['relativeError']<=1e-4 for c in finite),
     convention='physical condensed displacement Hessian, not mixed saddle pressure Hessian')
   couple=coupling(B,r) if stationary else None
   qualified=bool(stationary and (stretch==1 or (spectrum['lowestEigenvaluesNPerM'][0]>0 and spectrum['gradientDifferencePass'])))
   rec=dict(schema=1,sourceHashes=source,sourceCommit=commit,name=name,material=PARAM,activation=ACTIVATION,
    stretch=stretch,quadraturePoints=256,freeDisplacementCount=len(m['free']),pressureCount=m['nv'],
    initialPositionsM=initial,terminalPositionsM=x,terminalPressurePa=r['p'],analytic=analytic,
    terminal=dict(energyJ=r['energy'],fullGradientN=r['g'],forceResidualN=r['residual'],
     weakPressureRMS=r['weakRMS'],pointwisePressureRMS=r['pointwiseRMS'],Jmin=r['Jmin'],Jmax=r['Jmax']),
    history=history,reason=reason,replays=replays,coupling=couple,spectrum=spectrum,
    stationaryAccepted=stationary,stationaryStabilityDiagnosticPass=qualified,
    result='PASS_STATIONARY_CONTROL' if stationary else 'REJECTED_CONTROL_NO_HISTORY_ADVANCEMENT',
    limits=['Independent prescribed-cap specimens; no trajectory/history advancement.',
     'Homogeneous controlled patch only; no anatomy/material/reference calibration.',
     'The stretch-one passive cutoff has no two-sided Hessian classification.' if stretch==1 else
     'Physical spectrum classified only after original stationarity/geometry/replay gates.'])
   save(name+'.json',rec);records[name]=rec
   print('RESULT',name,rec['result'],'steps',len(history)-1,'residual',r['residual'],'spectrum',None if spectrum is None else eig[:2].tolist(),flush=True)
 refinement=[]
 for stretch in [1.,1.01,1.25]:
  c=records[f'coarse-{stretch:.2f}'];f=records[f'fine-{stretch:.2f}'];stationary=c['stationaryAccepted'] and f['stationaryAccepted']
  if stationary:
   interp=interpolate(meshes['coarse'],c['terminalPositionsM'],meshes['fine']['X']);diff=np.linalg.norm(interp-f['terminalPositionsM'],axis=1)
   force=abs(c['replays']['256']['capForceN']-f['replays']['256']['capForceN'])/abs(f['replays']['256']['capForceN'])
   j=max(abs(c['terminal'][k]-f['terminal'][k]) for k in ['Jmin','Jmax'])
   ratio=f['coupling']['beta']/c['coupling']['beta']
   refinement.append(dict(stretch=stretch,maximumInterpolatedPositionDifferenceM=float(diff.max()),
    relativeCapForceDifference=force,JExtremaDifference=j,infSupBetaRatio=ratio,
    matchedStationaryRefinementPass=bool(diff.max()<=.0005 and force<=.01 and j<=.005),
    infSupTrendConcern=ratio<.5))
  else:refinement.append(dict(stretch=stretch,result='UNQUALIFIED_NONSTATIONARY_LEVEL'))
 summary=dict(schema=1,sourceHashes=source,sourceCommit=commit,elapsedSeconds=time.time()-start,
  cases=[dict(name=r['name'],result=r['result'],stationaryAccepted=r['stationaryAccepted'],
   stationaryStabilityDiagnosticPass=r['stationaryStabilityDiagnosticPass'],forceResidualN=r['terminal']['forceResidualN'],
   iterations=len(r['history'])-1,capForceN=r['replays']['256']['capForceN'],pressurePointwiseRMS=r['terminal']['pointwisePressureRMS'],
   Jmin=r['terminal']['Jmin'],Jmax=r['terminal']['Jmax'],beta=None if r['coupling'] is None else r['coupling']['beta'],
   lowestEigenvalueNPerM=None if r['spectrum'] is None else r['spectrum']['lowestEigenvaluesNPerM'][0]) for r in records.values()],
  refinement=refinement,limits=['No atlas solve, anatomical map, self-consistent loaded motion, tissue-envelope or skin qualification.',
   'Two deterministic homogeneous mesh levels do not prove a stable mesh family or nonuniform convergence.'])
 save('summary.json',summary)
 print('COMPLETE',json.dumps(serial(summary['cases'])),flush=True)
if __name__=='__main__':main()

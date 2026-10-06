"""Fresh source/acceptance replay and original-Node gradient witness checks."""
import json,hashlib,sys
from pathlib import Path
import numpy as np
from scipy.linalg import cho_solve
from full_p2_p1 import Body,PARAM,ACTIVATION,constitutive
from run_full_p2_p1 import OUT,ROOT,digest,replay,save

def decomposition(B,x,p,v):
 F=np.einsum('eni,eqna->eqia',x[B.m['tets']],B.grad)
 dF=np.einsum('eni,eqna->eqia',v[B.m['tets']],B.grad)
 pq=p[B.pi]@B.L.T
 _,C,_,J,G,lam=constitutive(F,pq,tangent=True)
 fixed=float(np.einsum('eqia,eqiajb,eqjb,eq->',dF,C,dF,B.w))
 n=F[:,:,:,0]/lam[...,None];df=dF[:,:,:,0];proj=np.sum(n*df,axis=-1)
 transverse=np.sum(df*df,axis=-1)-proj*proj
 u=(lam-1)/PARAM['activeWidth'];curve=np.where(abs(u)<1,(1-u*u)**2,0)
 prime=np.where(abs(u)<1,-4*u*(1-u*u)/PARAM['activeWidth'],0)
 active=float(np.sum(B.w*ACTIVATION*PARAM['sigma0']*(prime*proj*proj+curve/lam*transverse)))
 exp=np.expm1(PARAM['b']*np.maximum(lam-1,0))
 k=PARAM['kf']/PARAM['b']*exp;kp=np.where(lam>1,PARAM['kf']*np.exp(PARAM['b']*(lam-1)),0)
 passive=float(np.sum(B.w*(kp*proj*proj+k/lam*transverse)))
 invd=np.einsum('eqai,eqib->eqab',np.linalg.inv(F),dF)
 geometric=float(-np.sum(B.w*pq*np.einsum('eqab,eqba->eq',invd,invd)))
 directionalLog=np.einsum('eqia,eqia->eq',G,dF)
 dbLocal=np.einsum('qi,eq,eq->ei',B.L,directionalLog,B.w);db=np.zeros(B.m['nv']);np.add.at(db,B.pi,dbLocal)
 constraint=float(PARAM['bulk']*db@cho_solve(B.Mfactor,db))
 return dict(matrixNPerM=fixed-geometric-passive-active,passiveFiberNPerM=passive,
  activeNPerM=active,pressureGeometricNPerM=geometric,weakVolumeConstraintNPerM=constraint,
  totalNPerM=fixed+constraint,
  interpretation='Exact physical Rayleigh components at stationary candidate; no numerical Hessian shift')

def main():
 if (OUT/'verification.json').exists():raise RuntimeError('Preserve replay')
 summary=json.loads((OUT/'summary.json').read_text());hashes=summary['sourceHashes']
 for name,h in hashes.items():assert digest(ROOT/name)==h,name
 results=[]
 for case in summary['cases']:
  name=case['name'];r=json.loads((OUT/(name+'.json')).read_text());level=name.split('-')[0]
  m=json.loads((OUT/(level+'-mesh.json')).read_text())['mesh']
  m={k:np.array(v) if isinstance(v,list) else v for k,v in m.items()};B=Body(m)
  x=np.array(r['terminalPositionsM']);initial=np.array(r['initialPositionsM']);state=B.evaluate(x,hessian=r['stretch']!=1)
  assert np.array_equal(initial[m['cap']],x[m['cap']]),'Fixed cap drift'
  assert state['residual']<=1e-4 and state['pointwiseRMS']<=1e-6 and state['weakRMS']<=1e-6
  assert .98<=state['Jmin']<=state['Jmax']<=1.02
  output=dict(name=name,stationaryAccepted=True,stabilityAssessed=r['stretch']!=1,
   stabilityClassification='UNASSESSED_PASSIVE_CUTOFF' if r['stretch']==1 else
    ('NEGATIVE_STATIONARY_DIRECTION' if r['spectrum']['lowestEigenvaluesNPerM'][0]<0 else 'POSITIVE_SAMPLED_FULL_SPECTRUM'),
   forceResidualN=state['residual'])
  if r['spectrum'] is not None:
   v=np.array(r['spectrum']['witnessDirection']);assert abs(np.linalg.norm(v)-1)<1e-12 and np.max(abs(v[m['cap']]))==0
   Hv=state['H']@v.ravel()[m['free']];checks=[]
   for h in [1e-7,5e-8]:
    gradients=[];sideChecks=[]
    for sign in [1,-1]:
     probe=x+sign*h*v;z=B.evaluate(probe);q=replay(m,probe,z['p'],2)
     gradients.append(np.array(q['gradientN'])[m['free']]);error=np.max(abs(z['g']-q['gradientN']))
     weak=np.array(q['weak']);weakRMS=float(np.sqrt(max(0,weak@cho_solve(B.Mfactor,weak)/B.volume)))
     assert error<=2e-6 and weakRMS<=1e-6
     sideChecks.append(dict(sign=sign,maximumIndependentForceDifferenceN=float(error),
                           weakPressureRMS=weakRMS,pointwisePressureRMS=q['pointwisePressureRMS'],Jmin=q['Jmin'],Jmax=q['Jmax']))
    fd=(gradients[0]-gradients[1])/(2*h);error=np.linalg.norm(fd-Hv)/np.linalg.norm(Hv)
    assert error<=1e-4,(name,h,error)
    checks.append(dict(stepM=h,independentNodeGradientRelativeError=float(error),probeChecks=sideChecks))
   components=decomposition(B,x,state['p'],v)
   eigen=r['spectrum']['lowestEigenvaluesNPerM'][0]
   assert abs(components['totalNPerM']-eigen)<=1e-6*max(1,abs(eigen))
   output.update(gradientChecks=checks,rayleighComponents=components)
  results.append(output);print('PASS',name,output['stabilityClassification'],flush=True)
 record=dict(result='PASS_FRESH_ORIGINAL_STRESS_GRADIENT_REPLAY',sourceHashes={**hashes,'tools/verify_full_p2_p1.py':digest(Path(__file__))},
  inputSHA256={str(p.relative_to(ROOT)):digest(p) for p in OUT.glob('*.json')},cases=results,
  rawLabelCorrection='Original stretch-one receipts set stationaryStabilityDiagnosticPass=true by equilibrium shortcut; no spectrum was assessed. Treat that label as UNASSESSED_PASSIVE_CUTOFF. This fresh record corrects classification without rewriting source-bound raw evidence.',
  limits=['Gradient probes are derivative tests, not accepted physical state/history advancement.'])
 save('verification.json',record)
if __name__=='__main__':main()

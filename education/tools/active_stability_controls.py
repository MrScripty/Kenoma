"""Fixed-coefficient active isolation and control-regime diagnostics. No solve."""
import json,subprocess,itertools
from pathlib import Path
import numpy as np
from scipy.linalg import eigh,null_space
from full_p2_p1 import Body,PARAM,ACTIVATION,constitutive,LENGTHS
from run_full_p2_p1 import ROOT,serial,digest
OLD=ROOT/'data/anatomical-arm-v1/review/full-p2-p1'
OUT=ROOT/'data/anatomical-arm-v1/review/active-stability-controls'
def evaluate(B,x,a,hessian=False):
 r=B.evaluate(x,hessian);F=np.einsum('eni,eqna->eqia',x[B.m['tets']],B.grad);pq=r['p'][B.pi]@B.L.T
 P,C,E,*_=constitutive(F,pq,activation=a,tangent=hessian)
 Pold,Cold,Eold,*_=constitutive(F,pq,activation=ACTIVATION,tangent=hessian)
 delta=np.einsum('eqia,eqna,eq->eni',P-Pold,B.grad,B.w).reshape(-1,30)
 np.add.at(r['g'],B.di,delta);r['residual']=float(np.linalg.norm(r['g'][B.m['free']]))
 r['energy']+=float(np.sum((E-Eold)*B.w))
 if hessian:
  local=np.empty((len(B.m['tets']),30,30))
  for e in range(len(local)):
   local[e]=np.einsum('qna,qiajb,qmb,q->nimj',B.grad[e],C[e]-Cold[e],B.grad[e],B.w[e],optimize=True).reshape(30,30)
  change=B.assemble(local,B.di,B.di,x.size,x.size);f=B.m['free'];r['H']+=change[f][:,f].toarray()
 return r

def original(data):
 p=subprocess.run(['node',str(ROOT/'tools/full-p2-p1-replay.mjs')],input=json.dumps(serial(data)),text=True,capture_output=True,check=True)
 return json.loads(p.stdout)
def replay(B,x,a):
 r=evaluate(B,x,a)
 return original(dict(mesh=B.m,positionsM=x,pressurePa=r['p'],material=PARAM,activation=a,depth=2))
def local(B,stretch,a):
 _,analytic=B.analytic(stretch);F=np.diag([stretch,analytic['transverseStretch'],analytic['transverseStretch']]);p=analytic['pressurePa']
 raw=original(dict(materialSamples=[dict(F=F.ravel(),p=p)],material=PARAM,activation=a))[0]
 C=np.array(raw['C']).reshape(3,3,3,3);G=np.linalg.inv(F).T;rows=[]
 for j in range(181):
  theta=j*np.pi/360;m=np.array([np.cos(theta),np.sin(theta),0]);g=G@m;normal=g/np.linalg.norm(g)
  seed=np.eye(3)[np.argmin(abs(normal))];u=seed-normal*(normal@seed);u/=np.linalg.norm(u);v=np.cross(normal,u)
  basis=np.stack([u,v],axis=1);Q=np.einsum('iajb,a,b->ij',C,m,m);ev,vec=eigh(basis.T@Q@basis)
  direction=basis@vec[:,0]
  rows.append(dict(angleRad=theta,valuePa=ev[0],m=m,u=direction,constraint=float(g@direction)))
 worst=min(rows,key=lambda x:x['valuePa']);H=np.outer(worst['u'],worst['m']);expected=np.einsum('iajb,jb->ia',C,H)
 checks=[]
 for h in [1e-6,5e-7]:
  samples=[]
  for sign in [1,-1]:
   f=F+sign*h*H;samples.append(dict(F=f.ravel(),p=PARAM['bulk']*np.log(np.linalg.det(f))))
  r=original(dict(materialSamples=samples,material=PARAM,activation=a));fd=(np.array(r[0]['P'])-r[1]['P']).reshape(3,3)/(2*h)
  error=np.linalg.norm(fd-expected)/np.linalg.norm(expected);checks.append(dict(step=h,relativeError=float(error),passGate=bool(error<=1e-4)))
 return dict(referenceF=F,pressurePa=p,angleCount=181,rows=rows,worst=worst,derivativeChecks=checks,
  limits='Strict rank-one first-order volume admissibility at controlled homogeneous field; finite scan not ellipticity proof.')
def axial(B,stretch,a):
 _,analytic=B.analytic(stretch);s=analytic['transverseStretch'];F=np.diag([stretch,s,s])[None];p=np.array([analytic['pressurePa']])
 P,C,_,_,G,_=constitutive(F,p,activation=a,tangent=True);C=C[0]+PARAM['bulk']*np.einsum('ia,jb->iajb',G[0],G[0])
 ds=-C[1,1,0,0]/(C[1,1,1,1]+C[1,1,2,2]);area=LENGTHS[1]*LENGTHS[2]
 derivative=area*(C[0,0,0,0]+(C[0,0,1,1]+C[0,0,2,2])*ds)/LENGTHS[0];checks=[]
 for h in [1e-6,5e-7]:
  R=[]
  for sign in [1,-1]:
   lam=stretch+sign*h;_,ref=B.analytic(lam);f=np.diag([lam,ref['transverseStretch'],ref['transverseStretch']])[None]
   R.append(float(constitutive(f,np.array([ref['pressurePa']]),activation=a)[0][0,0,0]*area))
  fd=(R[0]-R[1])/(2*h*LENGTHS[0]);error=abs(fd-derivative)/max(1,abs(derivative))
  checks.append(dict(stretchStep=h,derivativeNPerM=fd,relativeError=error,passGate=error<=1e-4))
 return dict(reactionN=float(P[0,0,0]*area),axialDerivativeNPerM=float(derivative),transverseDerivative=float(ds),
  minimumSeriesSpringThresholdNPerM=float(max(0,-derivative)),finiteChecks=checks,
  lengthControl='global axial coordinate held; interior full-nodal modes remain',
  deadForceControl='linear external work has zero curvature; global axial mode sign is derivative',
  seriesControl='strict kseries+derivative>0 necessary for global mode; no coefficient selected; cap-only spring does not act on zero-cap interior witnesses')
def save(name,r):
 with (OUT/name).open('x') as f:json.dump(serial(r),f,indent=2,allow_nan=False);f.write('\n')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if (OUT/'summary.json').exists() or list(OUT.glob('case-*.json')):raise RuntimeError('Preserve prior run')
 old=json.loads((OLD/'summary.json').read_text())
 for name,h in old['sourceHashes'].items():assert digest(ROOT/name)==h,name
 hashes={**old['sourceHashes'],'tools/active_stability_controls.py':digest(Path(__file__)),
  'research/mechanical-closure/active-stability-controls-protocol.md':digest(ROOT/'research/mechanical-closure/active-stability-controls-protocol.md')}
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();cases=[]
 for level in ['coarse','fine']:
  m=json.loads((OLD/(level+'-mesh.json')).read_text())['mesh'];m={k:np.array(v) if isinstance(v,list) else v for k,v in m.items()};B=Body(m)
  for stretch in [1.01,1.25]:
   name=f'{level}-{stretch:.2f}';prior=json.loads((OLD/(name+'.json')).read_text());x=np.array(prior['terminalPositionsM']);base=evaluate(B,x,.01,True);passive=evaluate(B,x,0.,True)
   for a in [.01,0.]:
    print('START',name,'activation',a,flush=True);r=base if a==.01 else passive
    replays={};gates=[]
    for depth in [1,2]:
     q=original(dict(mesh=m,positionsM=x,pressurePa=r['p'],material=PARAM,activation=a,depth=depth))
     weak=np.array(q['weak']);q['weakRMS']=float(np.sqrt(max(0,weak@np.linalg.solve(B.M,weak)/B.volume)))
     q['forceDifferenceN']=float(np.max(abs(r['g']-q['gradientN'])));replays[str(4*8**depth)]=q
     gates.extend([q['freeNodalResidualN']<=1e-4,q['forceDifferenceN']<=2e-6,q['weakRMS']<=1e-6,
      q['pointwisePressureRMS']<=1e-6,abs(q['capForceN']-q['virtualForceN'])<=1e-3,
      .98<=q['Jmin']<=q['Jmax']<=1.02,q['surface']['crossingPairs']==0])
    accepted=all(gates);spectrum=None;weakProjection=None;checks=[]
    if accepted:
     eigen,V=eigh(r['H'],subset_by_index=[0,2]);v=np.zeros(x.size);v[m['free']]=V[:,0];v=v.reshape(x.shape);Hv=r['H']@V[:,0]
     for h in [1e-7,5e-8]:
      gp=np.array(replay(B,x+h*v,a)['gradientN'])[m['free']];gm=np.array(replay(B,x-h*v,a)['gradientN'])[m['free']]
      error=float(np.linalg.norm((gp-gm)/(2*h)-Hv)/np.linalg.norm(Hv));checks.append(dict(stepM=h,relativeError=error,passGate=error<=1e-4))
     spectrum=dict(eigenvaluesNPerM=eigen,witness=v,firstVariationN=float(r['g']@v.ravel()),gradientChecks=checks)
     D=r['D'][:,m['free']].toarray();Z=null_space(D,rcond=1e-10);constraint=float(np.linalg.norm(D@Z)/np.linalg.norm(D))
     projected=eigh(Z.T@r['H']@Z,subset_by_index=[0,0]);w=np.zeros(x.size);w[m['free']]=Z@projected[1][:,0]
     weakProjection=dict(freeCount=len(m['free']),nullDimension=Z.shape[1],rank=len(m['free'])-Z.shape[1],
       relativeConstraint=constraint,constraintPass=constraint<=1e-12,minimumEigenvalueNPerM=projected[0][0],witness=w.reshape(x.shape),
       interpretation='Weak discrete P1 first-order pressure constraint only')
    record=dict(sourceCommit=commit,sourceHashes=hashes,priorReceiptSHA256=digest(OLD/(name+'.json')),
     name=name,activation=a,positionsM=x,pressurePa=r['p'],forceResidualN=r['residual'],
     stationaryAccepted=bool(accepted),result='PASS_STATIONARY_ISOLATION' if accepted else 'REJECTED_ISOLATION_NO_ADVANCEMENT',
     replays=replays,spectrum=spectrum,weakProjection=weakProjection,
     local=local(B,stretch,a),axial=axial(B,stretch,a),
     originalWitnessActiveRayleighNPerM=float(np.array(prior['spectrum']['witnessDirection']).ravel()[m['free']]@(base['H']-passive['H'])@np.array(prior['spectrum']['witnessDirection']).ravel()[m['free']]) if a==.01 else None)
    save(f'case-{name}-a{a:.2f}.json',record)
    cases.append(dict(name=name,activation=a,stationaryAccepted=bool(accepted),forceResidualN=r['residual'],
     fullMinimumNPerM=None if spectrum is None else spectrum['eigenvaluesNPerM'][0],
     weakProjectedMinimumNPerM=None if weakProjection is None else weakProjection['minimumEigenvalueNPerM'],
     strictLocalMinimumPa=record['local']['worst']['valuePa'],axialDerivativeNPerM=record['axial']['axialDerivativeNPerM'],
     derivativeChecksPass=all(c['passGate'] for c in checks+record['local']['derivativeChecks']+record['axial']['finiteChecks'])))
    print('RESULT',json.dumps(serial(cases[-1])),flush=True)
 save('summary.json',dict(result='COMPLETED_BOUNDED_ACTIVE_CONTROL_COMPARISON',sourceHashes=hashes,sourceCommit=commit,cases=cases,
  limits=['No optimizer, changed coefficient, constitutive switch, anatomical calibration or dynamic stability claim.',
   'Activation-zero isolation is not a proposed active muscle replacement.']))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Independent BPoly/Brent/DOP853/Radau replay of the declared scalar equations.
No source-curve construction changes, gain search or anatomical calibration.
"""
from pathlib import Path
import json,math
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import DOP853,Radau,quad
from millard_reference_benchmark import Curve,activation_rhs

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'education/data/vertical-force-command-v1'
P=json.loads((DATA/'protocol.json').read_text())
CONTROLS=json.loads((ROOT/'education/data/millard-reference-v1/review/native-controls.json').read_text())
C={name:Curve(rec) for name,rec in CONTROLS.items()}

class TrialFailure(ValueError):
    def __init__(self,code,message,t=None,z=None):
        super().__init__(message);self.code=code;self.t=t;self.z=None if z is None else list(map(float,z))

def phases(cfg):
    W=cfg['m']*P['gravity_m_per_s2'];target=cfg['target'];name=cfg['caseName']
    if name=='pulse':return [dict(end=.05,target=W),dict(end=.10,target=target),dict(end=.15,target=W),dict(end=.25,target=.8*W,brake=1),dict(end=.3,target=W)]
    if name=='lower':return [dict(end=.05,target=W),dict(end=.1,target=target),dict(end=.2,target=1.2*W,brake=-1),dict(end=.3,target=W)]
    if name=='release':return [dict(end=.05,target=W),dict(end=.3,target=0,mode='release')]
    if name=='high':return [dict(end=.05,target=W),dict(end=.15,target=target),dict(end=.3,target=W)]
    return [dict(end=.15 if name.startswith('descending') else .3,target=target,mode='fixed' if name=='descending_fixed' else 'PI')]

def output(z,cfg,phase):
    if not np.all(np.isfinite(z)):raise TrialFailure('nonfinite','Nonfinite intermediate state')
    y,w,a,q,I=z[:5]
    if a<.01-1e-12 or a>1+1e-12:raise TrialFailure('activation-bound','Activation left source bounds')
    if q<=.4441:raise TrialFailure('fiber-bound','Unqualified fiber lower-length event')
    s=(cfg['L0']-y-.1*q)/.2
    if s<=1:raise TrialFailure('slack','Unqualified tendon slack event')
    ft=100*C['tendon'].value(s);fal=C['active'].value(q);fp=100*C['passive'].value(q);e=(phase['target']-ft)/100;raw=cfg['ub']+.4*e+I;mode=phase.get('mode','PI')
    u=cfg['ub'] if mode=='fixed' else .01 if mode=='release' else float(np.clip(raw,.01,1))
    residual=lambda v:100*(a*fal*C['velocity'].value(v)+.1*v)+fp-ft
    v=brentq(residual,-10,10,xtol=5e-15,rtol=1e-15,maxiter=64)
    if abs(residual(v))>1e-7:raise TrialFailure('force-residual','Fiber force residual failed')
    lf_dot=v;fa=100*a*fal*C['velocity'].value(v);fd=10*v
    frozen=mode in ['fixed','release'] or (raw>=1 and e>0) or (raw<=.01 and e<0)
    return dict(FT=ft,s=s,v=v,u=u,uraw=raw,e=e,Idot=0 if frozen else 8*e,adot=0 if mode=='fixed' else activation_rhs(a,u),FA=fa,FP=fp,FD=fd,residual=residual(v),Pactive=-fa*lf_dot,D=fd*lf_dot,loadPower=ft*w,fiberPower=fp*lf_dot,tendonPower=ft*(-w-lf_dot),acceleration=(ft-cfg['m']*P['gravity_m_per_s2'])/cfg['m'])

def rhs(t,z,cfg,phase):
    try:o=output(z,cfg,phase)
    except (TrialFailure,ValueError) as e:
        if not isinstance(e,TrialFailure):e=TrialFailure('velocity-root',str(e))
        e.t=float(t);e.z=list(map(float,z));raise e
    return np.array([z[1],o['acceleration'],o['adot'],10*o['v'],o['Idot'],o['Pactive'],o['D'],o['loadPower'],o['fiberPower'],o['tendonPower'],o['FT']-cfg['m']*P['gravity_m_per_s2']])

def row(t,z,cfg,phase):
    o=output(z,cfg,phase);return dict(t=float(t),z=list(map(float,z)),target=phase['target'],mode=phase.get('mode','PI'),**{k:float(v) for k,v in o.items()})

def replay(cfg,method):
    t=0.;z=np.array(cfg['z'],float);history=[];events=[];failure=None;dense=[]
    def save(t,z,phase):
        r=row(t,z,cfg,phase)
        if history and abs(history[-1]['t']-t)<1e-12:history[-1]=r
        else:history.append(r)
    for index,phase in enumerate(phases(cfg)):
        if phase['end']<=t+1e-12:continue
        save(t,z,phase);armed=False
        solver=method(lambda t,z:rhs(t,z,cfg,phase),t,z,phase['end'],rtol=1e-9,atol=1e-11,max_step=.0005)
        crossing=False
        while solver.status=='running':
            before=t;old=z.copy();direction=phase.get('brake',0)
            if direction and z[1]*direction>1e-5:armed=True
            try:
                solver.step()
                if solver.status=='failed':raise TrialFailure('ODE-step',str(solver.status),before,old)
                new_t=float(solver.t);new_z=solver.y.copy();output(new_z,cfg,phase);solution=solver.dense_output()
                if direction and armed and old[1]*direction>0 and new_z[1]*direction<=0:
                    crossing=True;new_t=brentq(lambda t:float(solution(t)[1]),before,new_t,xtol=1e-10);new_z=solution(new_t);output(new_z,cfg,phase)
                # Material/output events are sampled only from valid accepted steps.
                grids=np.arange(math.floor((before+1e-10)/.001)+1,math.floor((new_t+1e-10)/.001)+1)*.001
                for ti in grids:save(ti,solution(ti),phase)
                dense.append((before,new_t,solution,phase.copy()));t=new_t;z=new_z
                if crossing:save(t,z,phase);events.append(dict(type='brake-crossing',t=t,armed=True,direction=direction));break
            except (TrialFailure,ValueError) as e:
                t=before;z=old
                failure=dict(code=getattr(e,'code','reference-root'),message=str(e),acceptedTime=t,acceptedState=list(map(float,z)),failedStageTime=getattr(e,'t',None),failedStageState=getattr(e,'z',None));save(t,z,phase);break
        if failure:break
        save(t,z,phase)
        if phase.get('brake') and not crossing:events.append(dict(type='brake-timeout',t=t,armed=armed))
        events.append(dict(type='phase-end',t=t,phase=index))
    return dict(cfg=cfg,method=method.__name__,acceptedTime=t,history=history,events=events,failure=failure),dense

if __name__=='__main__':
    from argparse import ArgumentParser
    p=ArgumentParser();p.add_argument('--method',choices=['DOP853','Radau'],required=True);p.add_argument('--case');args=p.parse_args();out=DATA/'review';cases=json.loads((out/'cases.json').read_text());method={'DOP853':DOP853,'Radau':Radau}[args.method]
    for entry in cases:
        if args.case and entry['id']!=args.case:continue
        r,_=replay(entry['cfg'],method);(out/f"{entry['id']}-{args.method}.json").write_text(json.dumps(r)+'\n');print(entry['id'],args.method,r['acceptedTime'],r['failure']['code'] if r['failure'] else 'completed',flush=True)

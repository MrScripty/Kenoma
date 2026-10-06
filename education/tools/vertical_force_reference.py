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
    try:
        o=output(z,cfg,phase)
        if phase.get('mode','PI')=='PI' and '_acceptedRaw' in phase:
            edot=-(100/.2*C['tendon'].value(o['s'],True)*(-z[1]-o['v']))/100
            frozen=.4*edot;integrating=frozen+8*o['e'];previous=phase['_acceptedRaw']
            crossed=lambda limit:(previous-limit)*(o['uraw']-limit)<=0 and previous!=o['uraw']
            if (crossed(1) and o['e']>0 and frozen<0<integrating) or (crossed(.01) and o['e']<0 and integrating<0<frozen):
                raise TrialFailure('antiwindup-surface','Unqualified opposing anti-windup switching surface')
    except (TrialFailure,ValueError) as e:
        if not isinstance(e,TrialFailure):e=TrialFailure('velocity-root',str(e))
        e.t=float(t);e.z=list(map(float,z));raise e
    return np.array([z[1],o['acceleration'],o['adot'],10*o['v'],o['Idot'],o['Pactive'],o['D'],o['loadPower'],o['fiberPower'],o['tendonPower'],o['FT']-cfg['m']*P['gravity_m_per_s2']])

def jacobian(t,z,cfg,phase):
    """Exact within-mode Jacobian; diagnostic accumulators have ZERO columns.
    Avoids finite-difference factor overflow in autonomous quadrature columns.
    Nonsmooth controller/activation guards remain part of the model, not smoothed.
    """
    o=output(z,cfg,phase);y,w,a,q,I=z[:5];v=o['v'];mode=phase.get('mode','PI')
    dft=np.array([-100/.2*C['tendon'].value(o['s'],True),0,0,-100*.1/.2*C['tendon'].value(o['s'],True),0])
    fl=C['active'].value(q);flq=C['active'].value(q,True);fv=C['velocity'].value(v);fvv=C['velocity'].value(v,True);pq=C['passive'].value(q,True)
    dv=dft.copy();dv[2]-=100*fl*fv;dv[3]-=100*(a*flq*fv+pq);dv/=100*(a*fl*fvv+.1)
    dfa=100*a*fl*fvv*dv;dfa[2]+=100*fl*fv;dfa[3]+=100*a*flq*fv
    dfp=np.zeros(5);dfp[3]=100*pq;de=-dft/100;du=.4*de;du[4]+=1
    if mode in ['fixed','release'] or o['uraw']<=.01 or o['uraw']>=1:du=np.zeros(5)
    ae=float(np.clip(a,.01,1));mask=1 if .01<=a<=1 else 0
    tau=.01*(.5+1.5*ae) if o['u']>ae else .04/(.5+1.5*ae)
    dtau=.015 if o['u']>ae else -.06/(.5+1.5*ae)**2
    da=du/tau;da[2]-=mask/tau+(o['u']-ae)*dtau*mask/tau**2
    if mode=='fixed':da=np.zeros(5)
    frozen=mode in ['fixed','release'] or (o['uraw']>=1 and o['e']>0) or (o['uraw']<=.01 and o['e']<0)
    dw=np.array([0,1,0,0,0]);J=np.zeros((11,11));J[0,:5]=dw;J[1,:5]=dft/cfg['m'];J[2,:5]=da;J[3,:5]=10*dv;J[4,:5]=0 if frozen else 8*de
    J[5,:5]=-dfa*v-o['FA']*dv;J[6,:5]=20*v*dv;J[7,:5]=dft*w+o['FT']*dw
    J[8,:5]=dfp*v+o['FP']*dv;J[9,:5]=dft*(-w-v)-o['FT']*(dw+dv);J[10,:5]=dft
    return J

def row(t,z,cfg,phase):
    o=output(z,cfg,phase);return dict(t=float(t),z=list(map(float,z)),target=phase['target'],mode=phase.get('mode','PI'),**{k:float(v) for k,v in o.items()})

def replay(cfg,method,with_quadrature=False):
    t=0.;z=np.array(cfg['z'],float);history=[];events=[];failure=None;dense=[];integrals=np.zeros(6)
    nodes,weights=np.polynomial.legendre.leggauss(8)
    def save(t,z,phase):
        r=row(t,z,cfg,phase)
        if history and abs(history[-1]['t']-t)<1e-12:history[-1]=r
        else:history.append(r)
    for index,phase in enumerate(phases(cfg)):
        if phase['end']<=t+1e-12:continue
        save(t,z,phase);armed=False
        kwargs=dict(jac=lambda t,z:jacobian(t,z,cfg,phase)) if method is Radau else {}
        solver=method(lambda t,z:rhs(t,z,cfg,phase),t,z,phase['end'],rtol=1e-9,atol=1e-11,max_step=.0005,**kwargs)
        crossing=False
        while solver.status=='running':
            before=t;old=z.copy();direction=phase.get('brake',0)
            phase['_acceptedRaw']=output(old,cfg,phase)['uraw']
            if direction and z[1]*direction>1e-5:armed=True
            try:
                solver.step()
                if solver.status=='failed':raise TrialFailure('ODE-step',str(solver.status),before,old)
                new_t=float(solver.t);new_z=solver.y.copy();output(new_z,cfg,phase);solution=solver.dense_output()
                if new_t-before<1e-10 or len(dense)>=10000:
                    raise TrialFailure('ODE-stall','Independent replay reached a tiny-step/accepted-step failure budget',new_t,new_z)
                if direction and armed and old[1]*direction>0 and new_z[1]*direction<=0:
                    crossing=True;new_t=brentq(lambda t:float(solution(t)[1]),before,new_t,xtol=1e-10);new_z=solution(new_t);output(new_z,cfg,phase)
                # Material/output events are sampled only from valid accepted steps.
                grids=np.arange(math.floor((before+1e-10)/.001)+1,math.floor((new_t+1e-10)/.001)+1)*.001
                for ti in grids:save(ti,solution(ti),phase)
                if with_quadrature:
                    for node,weight in zip(nodes,weights):
                        ti=before+(new_t-before)*(node+1)/2;zi=solution(ti);o=output(zi,cfg,phase)
                        integrals+=(new_t-before)*weight/2*np.array([o['Pactive'],o['D'],o['loadPower'],o['fiberPower'],o['tendonPower'],o['FT']-cfg['m']*P['gravity_m_per_s2']])
                dense.append((before,new_t,solution,phase.copy()));t=new_t;z=new_z
                if crossing:save(t,z,phase);events.append(dict(type='brake-crossing',t=t,armed=True,direction=direction));break
            except (TrialFailure,ValueError) as e:
                t=before;z=old
                failure=dict(code=getattr(e,'code','reference-root'),message=str(e),acceptedTime=t,acceptedState=list(map(float,z)),failedStageTime=getattr(e,'t',None),failedStageState=getattr(e,'z',None));save(t,z,phase);break
        if failure:break
        save(t,z,phase)
        if phase.get('brake') and not crossing:events.append(dict(type='brake-timeout',t=t,armed=armed))
        events.append(dict(type='phase-end',t=t,phase=index))
    result=dict(cfg=cfg,method=method.__name__,acceptedTime=t,history=history,events=events,failure=failure)
    if with_quadrature:
        errors=np.abs(integrals-(z[5:11]-np.array(cfg['z'][5:11])))
        gates=np.array([P['budgets']['component_combined_work_J']]*5+[P['budgets']['momentum_N_s']])
        result['independent_quadrature']=dict(passed=bool(np.all(errors<=gates)),method='Gauss-Legendre 8 on every actual accepted solver dense polynomial; independent power/force reevaluation',errors=dict(zip(['active_J','dissipation_J','load_J','fiber_J','tendon_J','momentum_N_s'],errors.tolist())),integrals=integrals.tolist(),accepted_interval_count=len(dense))
    return result,dense

if __name__=='__main__':
    from argparse import ArgumentParser
    p=ArgumentParser();p.add_argument('--method',choices=['DOP853','Radau'],required=True);p.add_argument('--case');p.add_argument('--quadrature',action='store_true');args=p.parse_args();out=DATA/'review';cases=json.loads((out/'cases.json').read_text());method={'DOP853':DOP853,'Radau':Radau}[args.method]
    for entry in cases:
        if args.case and entry['id']!=args.case:continue
        r,_=replay(entry['cfg'],method,args.quadrature);(out/f"{entry['id']}-{args.method}.json").write_text(json.dumps(r)+'\n');print(entry['id'],args.method,r['acceptedTime'],r['failure']['code'] if r['failure'] else 'completed',r.get('independent_quadrature',{}).get('passed','no quadrature'),flush=True)

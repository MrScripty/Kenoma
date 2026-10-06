#!/usr/bin/env python3
"""Frozen incoming-only experiment: tighter ordinary roots feed acceptance/restart.

Activation and attracting localization are unchanged. Actual dense coefficients
are retained for every accepted interval and every crossing auxiliary.
"""
import hashlib,json,math,time
import numpy as np
from scipy.integrate import DOP853,Radau
from run_filippov_bounded_experiment import Engine,Failure,ROOT

DATA=ROOT/'education/data/ordinary-crossing-consistency-v1'
OUT=DATA/'review'
PROTOCOL=json.loads((DATA/'protocol.json').read_text())

def verify_inputs():
    for path,digest in {**PROTOCOL['input_sha256'],**PROTOCOL.get('source_sha256',{})}.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:
            raise ValueError('Frozen experiment input changed: '+path)

def dense_record(method,left,right,old,dense,stages):
    common=dict(left_s=left,right_s=right,y_old=old.tolist())
    if method.startswith('RK4'):
        h=right-left;a,b,c,d=stages
        # Store the actual derivatives, not derivatives reconstructed later.
        return dict(**common,kind='RK4-cubic',coefficients=np.stack([h*a,h*(-1.5*a+b+c-.5*d),h*(2*a/3-2*(b+c)/3+2*d/3)]).tolist())
    if method=='DOP853':return dict(**common,kind='DOP853-nested',F=dense.F.tolist())
    if method=='Radau':return dict(**common,kind='Radau-power',Q=dense.Q.tolist())
    raise ValueError('Undeclared dense representation')

def replay_dense(record,t):
    u=(t-record['left_s'])/(record['right_s']-record['left_s']);old=np.array(record['y_old'])
    if record['kind']=='RK4-cubic':return old+np.array([u,u*u,u**3])@np.array(record['coefficients'])
    if record['kind']=='Radau-power':return old+np.array(record['Q'])@np.cumprod(np.full(len(record['Q'][0]),u))
    if record['kind']=='DOP853-nested':
        y=np.zeros_like(old)
        for i,f in enumerate(reversed(record['F'])):
            y+=f;y*=u if i%2==0 else 1-u
        return old+y
    raise ValueError('Unknown dense representation')

class CrossingEngine(Engine):
    def __init__(self,case,rep,method):
        if case not in PROTOCOL['cases'] or rep not in PROTOCOL['representations'] or method not in PROTOCOL['methods']:raise ValueError('Undeclared cell')
        super().__init__(case,rep,method)
    def slide(self):raise Failure('experiment-no-sliding','Sliding is prohibited')
    def step_rk(self,t,x,h):
        a=self.rhs(t,x);b=self.rhs(t+h/2,x+h*a/2);c=self.rhs(t+h/2,x+h*b/2);d=self.rhs(t+h,x+h*c)
        self.actual_rk_rates=[a,b,c,d]
        def dense(ti):
            u=(ti-t)/h
            return x+h*((u-1.5*u*u+2*u**3/3)*a+(u*u-2*u**3/3)*(b+c)+(-u*u/2+2*u**3/3)*d)
        return t+h,dense(t+h),dense
    def localize(self,left,right,dense):
        lo,hi=left,right;records=[];self.localization_records=records
        _,a=self.evaluate(dense(lo));_,b=self.evaluate(dense(hi));direction=1 if self.controller_mode=='integrating' else -1
        if not direction*a['H']<0<=direction*b['H']:raise Failure('event-bracket','Incoming extension has no oriented crossing bracket')
        for iteration in range(PROTOCOL['event_localization_iterations']):
            mid=(lo+hi)/2;x=dense(mid);z,o=self.evaluate(x)
            if self.eta*o['e']<=0:raise Failure('event-error-direction','Outward error lost in localization',mid,z)
            records.append(dict(t=mid,z=z.tolist(),H=o['H'],u=o['u'],residual_N=o['residual'],accepted=False))
            if direction*o['H']<0:lo=mid
            else:hi=mid
            on,off=o['normal_on'],o['normal_off']
            attracting=on>1e-8 and off<-1e-8
            width,residual=(1e-7,1e-9) if attracting else (PROTOCOL['ordinary_target_bracket_width_s'],PROTOCOL['ordinary_target_surface_residual'])
            if hi-lo<=width and abs(o['H'])<=residual:
                if attracting:classification='attracting'
                elif direction==1 and on>1e-8 and off>1e-8:classification='ordinary-outward'
                elif direction==-1 and on<-1e-8 and off<-1e-8:classification='ordinary-inward'
                else:raise Failure('event-strict-sign','Candidate is neither certified crossing nor strict attraction',mid,z)
                return dict(t=mid,x=x.tolist(),z=z.tolist(),H=o['H'],normal_on=on,normal_off=off,classification=classification,weight=-o['d']/o['k'] if attracting else None,bracket=[lo,hi],iterations=iteration+1,probes=records,accepted=False,solver_target_bracket_s=width,solver_target_H=residual)
        raise Failure('event-localization','Unchanged 32-iteration localization budget exhausted')
    def advance(self,end,seek_entry):
        solver=None
        while self.t<end-1e-12 and not self.failure:
            self.stage_records=[];before=self.t;old=self.x.copy();record=None
            try:
                if self.mode!='incoming':raise Failure('experiment-no-sliding','Nonincoming state prohibited')
                if self.method.startswith('RK4'):
                    h=min(float(self.method.split('-')[1]),end-self.t,((math.floor((self.t+1e-10)/.001)+1)*.001)-self.t)
                    nt,nx,dense=self.step_rk(self.t,self.x,h)
                else:
                    if solver is None:
                        cls={'DOP853':DOP853,'Radau':Radau}[self.method]
                        solver=cls(self.rhs,self.t,self.x,end,rtol=1e-9,atol=1e-11,max_step=.0005,**({'jac':self.jac} if cls is Radau else {}))
                    solver.step()
                    if solver.status=='failed':raise Failure('ODE-step','Adaptive step failed')
                    nt,nx,dense=float(solver.t),solver.y.copy(),solver.dense_output()
                if nt-before<1e-10 or self.steps>=PROTOCOL['accepted_step_watchdog']:raise Failure('ODE-stall','Tiny-step or declared accepted-step watchdog')
                record=dense_record(self.method,before,nt,old,dense,getattr(self,'actual_rk_rates',None))
                for ti in [before,(before+nt)/2,nt]:
                    if np.max(np.abs(replay_dense(record,ti)-dense(ti)))>1e-12:raise Failure('dense-serialization','Actual polynomial reproduction failed')
                _,o=self.evaluate(nx);direction=1 if self.controller_mode=='integrating' else -1
                if seek_entry and direction*o['H']>=0:
                    candidate=self.localize(before,nt,dense)
                    auxiliary=dict(start=before,trialEnd=nt,startState=old.tolist(),stages=self.stage_records,dense=record,incoming_controller_mode=self.controller_mode,accepted=False)
                    if candidate['classification']!='attracting':
                        auxiliary['ordinary_crossing']=candidate;self.probes.append(auxiliary)
                        self.accept(candidate['t'],np.array(candidate['x']),dense)
                        self.intervals[-1]['dense']=record
                        self.events.append(dict(type=candidate['classification'],t=self.t,bracket=candidate['bracket'],H=candidate['H'],normal_on=candidate['normal_on'],normal_off=candidate['normal_off'],integral_reset=False,mechanical_jump=0.))
                        self.controller_mode='frozen' if direction==1 else 'integrating';self.save(self.t,self.x);solver=None;continue
                    self.candidate=candidate;auxiliary['candidate']=candidate;self.probes.append(auxiliary);return
                self.accept(nt,nx,dense);self.intervals[-1]['dense']=record
            except Failure as e:
                self.probes.append(dict(start=before,stages=self.stage_records,dense=record,localization_probes=getattr(self,'localization_records',[]),accepted=False,failure=e.code));self.stop(e);return
        self.save(self.t,self.x)

def main():
    from argparse import ArgumentParser
    p=ArgumentParser();p.add_argument('--case',required=True,choices=PROTOCOL['cases']);p.add_argument('--rep',required=True,choices=PROTOCOL['representations']);p.add_argument('--method',required=True,choices=PROTOCOL['methods']);args=p.parse_args()
    verify_inputs();OUT.mkdir(parents=True,exist_ok=True);dest=OUT/f'{args.case}-{args.rep}-{args.method}.json'
    if dest.exists():raise ValueError('Refuse to overwrite experiment evidence')
    started=time.monotonic();e=CrossingEngine(args.case,args.rep,args.method)
    try:
        e.entry();r=e.result();r.update(experiment_only=True,diagnostic_complete=e.candidate is not None and e.failure is None,sliding_allowed=False,activation_handling_changed=False,elapsed_s=time.monotonic()-started,protocol_sha256=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest(),executed_source_sha256=PROTOCOL['source_sha256'])
        assert all(row['mode']=='incoming' for row in r['history'])
        assert r['candidate'] is None or not r['candidate']['accepted']
        dest.write_text(json.dumps(r,indent=2)+'\n')
        print(args.case,args.rep,args.method,'stop',e.t,'candidate',e.candidate['t'] if e.candidate else None,'failure',e.failure,'steps',e.steps,'elapsed',r['elapsed_s'],flush=True)
    finally:
        if e.source:e.source.close()

if __name__=='__main__':main()

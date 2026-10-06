#!/usr/bin/env python3
"""Lower incoming prefix, literal-control versus continuous activation split.

No projection or law change. One-sided extensions are used only by trial fields;
accepted split intervals are checked on the appropriate original physical side.
"""
import hashlib,json,math,subprocess,time
import numpy as np
from scipy.integrate import DOP853,Radau
from run_ordinary_crossing_consistency import CrossingEngine,dense_record,replay_dense
from run_filippov_bounded_experiment import ROOT,Source,Failure,NODES

DATA=ROOT/'education/data/activation-equality-diagnostic-v1'
OUT=DATA/'review'
PROTOCOL=json.loads((DATA/'protocol.json').read_text())

def verify_inputs():
    for path,digest in {**PROTOCOL['input_sha256'],**PROTOCOL.get('source_sha256',{})}.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:raise ValueError('Frozen activation input changed: '+path)

def one_sided_rate(a,u,branch):
    a=float(np.clip(a,.01,1));tau=.01*(.5+1.5*a) if branch=='activation' else .04/(.5+1.5*a)
    return (u-a)/tau

class ActivationSource(Source):
    def __init__(self):
        self.branch=None
        self.process=subprocess.Popen(['node',str(ROOT/'education/tools/activation_equality_worker.mjs')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
    def evaluate(self,z,cfg,target,sliding,bound):
        self.process.stdin.write(json.dumps(dict(z=list(map(float,z)),cfg=cfg,target=target,sliding=sliding,activation_branch=self.branch))+'\n');self.process.stdin.flush()
        answer=json.loads(self.process.stdout.readline())
        if not answer['ok']:raise Failure(answer['code'],answer['message'])
        return answer['output']

class ActivationEngine(CrossingEngine):
    def __init__(self,rep,method,policy):
        if rep not in PROTOCOL['representations'] or method not in PROTOCOL['methods'] or policy not in PROTOCOL['policies']:raise ValueError('Undeclared cell')
        self.policy=policy;self.activation_branch='activation' if policy=='split' else None;self.activation_event=None;self.activation_auxiliaries=[];self.remainder_end=None
        super().__init__('mass-1',rep,method)
        if self.source:self.source.close();self.source=ActivationSource()
        self.save(0.,self.x)
    def evaluate(self,x):
        if isinstance(getattr(self,'source',None),ActivationSource):self.source.branch=self.activation_branch
        z,o=super().evaluate(x)
        if self.activation_branch and not self.source:o['adot']=one_sided_rate(z[2],o['u'],self.activation_branch)
        return z,o
    def g(self,x):
        z,o=self.evaluate(x);return o['u']-z[2]
    def activation_localize(self,left,right,dense):
        lo,hi=left,right;records=[];self.activation_localization_records=records
        if not self.g(dense(lo))>0>=self.g(dense(hi)):raise Failure('activation-bracket','No positive-to-negative equality bracket')
        for iteration in range(PROTOCOL['event_localization_iterations']):
            mid=(lo+hi)/2;x=dense(mid);z,o=self.evaluate(x);g=o['u']-z[2]
            if not .01<o['u']<1:raise Failure('activation-interior','Equality at an excitation bound is undeclared')
            records.append(dict(t=mid,z=z.tolist(),g=g,force_residual_N=o['residual'],accepted=False))
            if g>0:lo=mid
            else:hi=mid
            if hi-lo<=PROTOCOL['activation_target_bracket_s'] and abs(g)<=PROTOCOL['activation_target_g']:
                rates={b:one_sided_rate(z[2],o['u'],b) for b in ['activation','deactivation']}
                normals={b:o['d']+o['Idot']-rate for b,rate in rates.items()}
                if max(normals.values())>=-1e-8:raise Failure('activation-transversality','Positive-to-negative transversal margin lost')
                return dict(t=mid,x=x.tolist(),g=g,u=o['u'],bracket=[lo,hi],iterations=iteration+1,one_sided_rates=rates,one_sided_normals_per_s=normals,normal_at_exact_equality_per_s=o['d']+o['Idot'],surface_timing_proxy_s={b:abs(g/n) for b,n in normals.items()},force_residual_N=o['residual'],probes=records,accepted=False,state_projected=False)
        raise Failure('activation-localization','Unchanged 32-iteration budget exhausted')
    def accept(self,stop,newx,dense):
        if self.policy=='split':
            for ti in [self.t,stop]+[self.t+(stop-self.t)*(node+1)/2 for node in NODES]:
                g=self.g(dense(ti))
                if (self.activation_branch=='activation' and g<-1e-13) or (self.activation_branch=='deactivation' and g>1e-13):raise Failure('activation-missed-side','Wrong-side auxiliary cannot enter accepted interval',ti,self.decode(dense(ti)))
        super().accept(stop,newx,dense)
    def entry(self):self.advance(PROTOCOL['endpoint_s'],True)
    def advance(self,end,seek_entry):
        solver=None
        while self.t<end-1e-12 and not self.failure:
            self.stage_records=[];before=self.t;old=self.x.copy();record=None
            try:
                if self.method.startswith('RK4'):
                    h=min(float(self.method.split('-')[1]),end-self.t,((math.floor((self.t+1e-10)/.001)+1)*.001)-self.t)
                    if self.remainder_end is not None:h=min(h,self.remainder_end-self.t)
                    nt,nx,dense=self.step_rk(self.t,self.x,h)
                else:
                    if solver is None:
                        cls={'DOP853':DOP853,'Radau':Radau}[self.method]
                        solver=cls(self.rhs,self.t,self.x,end,rtol=1e-9,atol=1e-11,max_step=.0005,**({'jac':self.jac} if cls is Radau else {}))
                    solver.step()
                    if solver.status=='failed':raise Failure('ODE-step','Adaptive step failed')
                    nt,nx,dense=float(solver.t),solver.y.copy(),solver.dense_output()
                if nt-before<1e-10 or self.steps>=PROTOCOL['accepted_step_watchdog']:raise Failure('ODE-stall','Tiny-step or declared watchdog')
                record=dense_record(self.method,before,nt,old,dense,getattr(self,'actual_rk_rates',None))
                for ti in [before,(before+nt)/2,nt]:
                    if np.max(np.abs(replay_dense(record,ti)-dense(ti)))>1e-12:raise Failure('dense-serialization','Actual polynomial reproduction failed')
                _,o=self.evaluate(nx)
                if o['H']>=0:raise Failure('ordinary-crossing-stop','First ordinary controller crossing is outside this diagnostic; trial rejected',nt,self.decode(nx))
                if self.activation_event is None and self.g(old)>0>=self.g(nx):
                    c=self.activation_localize(before,nt,dense)
                    self.activation_auxiliaries.append(dict(start=before,trialEnd=nt,startState=old.tolist(),dense=record,stages=self.stage_records,activation_event=c,incoming_activation_branch=self.activation_branch,accepted=False))
                    if self.policy=='split':
                        self.accept(c['t'],np.array(c['x']),dense);self.intervals[-1].update(dense=record,activation_branch='activation')
                        # No coordinate is projected/reset. Commit the branch only
                        # after every unchanged state/ledger check has succeeded.
                        self.activation_branch='deactivation';c['accepted']=True;self.activation_event=c
                        self.events.append(dict(type='activation-equality',t=self.t,bracket=c['bracket'],g=c['g'],state_reset=False));self.save(self.t,self.x)
                        if self.method.startswith('RK4'):self.remainder_end=nt
                        solver=None;continue
                    self.activation_event=c
                self.accept(nt,nx,dense);self.intervals[-1].update(dense=record,activation_branch=self.activation_branch)
                if self.remainder_end is not None and abs(nt-self.remainder_end)<1e-12:self.remainder_end=None
            except Failure as e:
                self.probes.append(dict(start=before,stages=self.stage_records,dense=record,activation_localization_probes=getattr(self,'activation_localization_records',[]),accepted=False,failure=e.code));self.stop(e);return
        self.save(self.t,self.x)

def main():
    from argparse import ArgumentParser
    p=ArgumentParser();p.add_argument('--rep',required=True,choices=PROTOCOL['representations']);p.add_argument('--method',required=True,choices=PROTOCOL['methods']);p.add_argument('--policy',required=True,choices=PROTOCOL['policies']);args=p.parse_args()
    verify_inputs();OUT.mkdir(parents=True,exist_ok=True);dest=OUT/f'{args.policy}-{args.rep}-{args.method}.json'
    if dest.exists():raise ValueError('Refuse to overwrite activation evidence')
    started=time.monotonic();e=ActivationEngine(args.rep,args.method,args.policy)
    try:
        e.entry();r=e.result();r.update(diagnostic_only=True,policy=args.policy,diagnostic_complete=abs(e.t-PROTOCOL['endpoint_s'])<1e-12 and e.activation_event is not None and e.failure is None,declared_endpoint_s=PROTOCOL['endpoint_s'],activation_event=e.activation_event,activation_auxiliaries=e.activation_auxiliaries,sliding_allowed=False,elapsed_s=time.monotonic()-started,protocol_sha256=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest(),executed_source_sha256=PROTOCOL['source_sha256'])
        assert all(x['mode']=='incoming' and x['controller_mode']=='integrating' for x in r['history'])
        assert r['candidate'] is None and not r['qualified']
        dest.write_text(json.dumps(r,indent=2)+'\n')
        print(args.policy,args.rep,args.method,'stop',e.t,'equality',e.activation_event['t'] if e.activation_event else None,'failure',e.failure,'steps',e.steps,'elapsed',r['elapsed_s'],flush=True)
    finally:
        if e.source:e.source.close()

if __name__=='__main__':main()

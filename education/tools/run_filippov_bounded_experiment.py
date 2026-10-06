#!/usr/bin/env python3
"""Approved, bounded research experiment. Immutable original files are read only.

Full coordinates call the actual JS source kernels; reduced sliding coordinates
use independent BPoly/Brent kernels. Entry is independently localized for all
20 cells before any entry is accepted. A case failing the common event/controller
checks is retained at its last pre-entry state, without post-entry advancement.
"""
from pathlib import Path
import json, math, subprocess, hashlib, time
import numpy as np
from scipy.integrate import DOP853, Radau
from vertical_force_reference import ROOT, P, C, output as reference_output, activation_rhs

OUT=ROOT/'education/data/filippov-bounded-v1/review'
CASES={r['id']:r['cfg'] for r in json.loads((ROOT/'education/data/vertical-force-command-v1/review/cases.json').read_text()) if r['id'] in ['high','mass-1']}
ENDS={'high':.107,'mass-1':.264}
METHODS=['RK4-0.0002','RK4-0.0001','RK4-0.00005','DOP853','Radau']
REPS=['full-source','reduced-independent']
NODES,WEIGHTS=np.polynomial.legendre.leggauss(8)

class Failure(ValueError):
    def __init__(self,code,message,t=None,z=None):
        super().__init__(message);self.code=code;self.t=t;self.z=None if z is None else list(map(float,z))

class Source:
    def __init__(self):
        self.process=subprocess.Popen(['node',str(ROOT/'education/tools/filippov_source_worker.mjs')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
    def evaluate(self,z,cfg,target,sliding,bound):
        self.process.stdin.write(json.dumps(dict(z=list(map(float,z)),cfg=cfg,target=target,sliding=sliding,bound=bound))+'\n');self.process.stdin.flush()
        answer=json.loads(self.process.stdout.readline())
        if not answer['ok']:raise Failure(answer['code'],answer['message'])
        return answer['output']
    def close(self):
        self.process.stdin.close();self.process.wait(timeout=10);self.process.stdout.close()

class Engine:
    def __init__(self,case,rep,method):
        self.case,self.rep,self.method=case,rep,method;self.cfg=CASES[case]
        self.bound,self.eta=(1.,1.) if case=='high' else (.01,-1.)
        self.source=Source() if rep=='full-source' else None
        self.mode='incoming';self.target=self.cfg['m']*P['gravity_m_per_s2'] if case=='high' else self.cfg['target']
        self.t=0.;self.x=np.array(self.cfg['z'],float);self.history=[];self.events=[];self.probes=[];self.intervals=[];self.failure=None;self.candidate=None
        self.stage_records=[];self.max_residual=0.;self.min_q=float('inf');self.min_s=float('inf')
        self.quad=np.zeros(6);self.steps=0;self.save(0.,self.x)
    def decode(self,x):
        if self.mode=='sliding' and self.rep=='reduced-independent':
            ft=100*C['tendon'].value((self.cfg['L0']-x[0]-.1*x[3])/.2)
            I=self.bound-self.cfg['ub']-.4*(self.target-ft)/100
            return np.r_[x[:4],I,x[4:]]
        return np.array(x)
    def evaluate(self,x):
        z=self.decode(x)
        try:
            if self.source:o=self.source.evaluate(z,self.cfg,self.target,self.mode=='sliding',self.bound)
            else:
                o=reference_output(z,self.cfg,{'target':self.target});o['kt']=500*C['tendon'].value(o['s'],True)
                if self.mode=='sliding':o['u']=self.bound;o['adot']=activation_rhs(z[2],self.bound)
        except ValueError as e:
            if isinstance(e,Failure):raise
            raise Failure(getattr(e,'code','reference-root'),str(e)) from e
        d=.4*o['kt']*(z[1]+o['v'])/100;k=8*o['e']
        o.update(H=self.eta*(o['uraw']-self.bound),normal_on=self.eta*(d+k),normal_off=self.eta*d,d=d,k=k)
        self.max_residual=max(self.max_residual,abs(o['residual']));self.min_q=min(self.min_q,z[3]);self.min_s=min(self.min_s,o['s'])
        if self.mode=='sliding':
            if self.eta*o['e']<=0 or o['normal_on']<=1e-8 or o['normal_off']>=-1e-8:
                raise Failure('strict-sign-loss','Strict attracting/outward-error margin lost; no automatic exit')
            o['Idot']=-d
        else:o['Idot']=8*o['e']  # declared incoming auxiliary; clipping remains in output
        return z,o
    def rhs(self,t,x):
        try:
            z,o=self.evaluate(x)
            rate=np.array([z[1],o['acceleration'],o['adot'],10*o['v'],o['Idot'],o['Pactive'],o['D'],o['loadPower'],o['fiberPower'],o['tendonPower'],o['FT']-self.cfg['m']*P['gravity_m_per_s2']])
            if self.mode=='incoming':self.stage_records.append(dict(t=float(t),z=z.tolist(),H=o['H'],u=o['u'],force_residual_N=o['residual'],accepted=False))
            return np.r_[rate[:4],rate[5:]] if self.mode=='sliding' and self.rep=='reduced-independent' else rate
        except Failure as e:e.t=float(t);e.z=self.decode(x).tolist();raise
    def jac(self,t,x):
        # Fixed physical-column differences; all ledger columns are exactly zero.
        # No adaptive FD factors for quadrature states (the original overflow).
        n=4 if self.mode=='sliding' and self.rep=='reduced-independent' else 5
        J=np.zeros((len(x),len(x)))
        for j in range(n):
            h=1e-7*max(1.,abs(x[j]));a=x.copy();b=x.copy();a[j]+=h;b[j]-=h
            J[:,j]=(self.rhs(t,a)-self.rhs(t,b))/(2*h)
        return J
    def save(self,t,x):
        z,o=self.evaluate(x)
        if self.mode=='sliding' and abs(o['H'])>1e-9:raise Failure('constraint-drift','Full state constraint drift exceeds 1e-9',t,z)
        r=dict(t=float(t),z=z.tolist(),target=self.target,mode=self.mode,**{k:float(o[k]) for k in ['FT','u','uraw','e','H','normal_on','normal_off','residual','v']})
        if self.history and abs(self.history[-1]['t']-t)<1e-12:self.history[-1]=r
        else:self.history.append(r)
    def step_rk(self,t,x,h):
        a=self.rhs(t,x);b=self.rhs(t+h/2,x+h*a/2);c=self.rhs(t+h/2,x+h*b/2);d=self.rhs(t+h,x+h*c)
        def dense(ti):
            u=(ti-t)/h
            return x+h*((u-1.5*u*u+2*u**3/3)*a+(u*u-2*u**3/3)*(b+c)+(-u*u/2+2*u**3/3)*d)
        return t+h,dense(t+h),dense
    def localize(self,left,right,dense):
        lo,hi=left,right;records=[]
        self.localization_records=records
        _,a=self.evaluate(dense(lo));_,b=self.evaluate(dense(hi))
        if not a['H']<0<=b['H']:raise Failure('event-bracket','Incoming extension has no oriented crossing bracket')
        for iteration in range(32):
            mid=(lo+hi)/2;x=dense(mid);z,o=self.evaluate(x)
            if self.eta*o['e']<=0:raise Failure('event-error-direction','Outward error lost in localization',mid,z)
            records.append(dict(t=mid,z=z.tolist(),H=o['H'],u=o['u'],residual_N=o['residual'],accepted=False))
            if o['H']<0:lo=mid
            else:hi=mid
            if hi-lo<=1e-7 and abs(o['H'])<=1e-9:
                if o['normal_on']<=1e-8 or o['normal_off']>=-1e-8:raise Failure('event-strict-sign','Candidate is not certified strictly attracting',mid,z)
                return dict(t=mid,x=x.tolist(),z=z.tolist(),H=o['H'],normal_on=o['normal_on'],normal_off=o['normal_off'],weight=-o['d']/o['k'],bracket=[lo,hi],iterations=iteration+1,probes=records,accepted=False)
        raise Failure('event-localization','32-iteration bracket/constraint criterion not met')
    def accept(self,stop,newx,dense):
        before=self.t;old=self.x.copy();old_quad=self.quad.copy();old_history=list(self.history)
        try:
            additions=[];increment=np.zeros(6)
            # All evaluations are validated before any accepted state/ledger mutation.
            for node,weight in zip(NODES,WEIGHTS):
                ti=before+(stop-before)*(node+1)/2;xi=dense(ti);z,o=self.evaluate(xi)
                if self.mode=='incoming' and o['H']>1e-9:raise Failure('missed-entry','Auxiliary beyond-surface point cannot enter accepted interval',ti,z)
                if self.mode=='sliding' and abs(o['H'])>1e-9:raise Failure('constraint-drift','Dense sliding constraint exceeds 1e-9',ti,z)
                # Independent kernels re-evaluate accepted dense physical powers.
                ref=reference_output(z,self.cfg,{'target':self.target})
                increment+=(stop-before)*weight/2*np.array([ref['Pactive'],ref['D'],ref['loadPower'],ref['fiberPower'],ref['tendonPower'],ref['FT']-self.cfg['m']*P['gravity_m_per_s2']])
            grids=np.arange(math.floor((before+1e-10)/.001)+1,math.floor((stop+1e-10)/.001)+1)*.001
            for ti in grids:additions.append((float(ti),dense(ti)))
            self.evaluate(newx)
            for ti,xi in additions:self.save(ti,xi)
            self.t=float(stop);self.x=newx.copy();self.quad+=increment;self.steps+=1
            self.intervals.append(dict(start=before,end=stop,mode=self.mode,auxiliary_suffix_excluded=True))
        except Failure:
            self.t=before;self.x=old;self.quad=old_quad;self.history=old_history;raise
    def stop(self,e):
        self.failure=dict(code=e.code,message=str(e),acceptedTime=self.t,acceptedState=self.decode(self.x).tolist(),failedStageTime=e.t,failedStageState=e.z)
        self.save(self.t,self.x)
    def advance(self,end,seek_entry):
        solver=None
        while self.t<end-1e-12 and not self.failure:
            self.stage_records=[];before=self.t;old=self.x.copy()
            try:
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
                if nt-before<1e-10 or self.steps>=10000:raise Failure('ODE-stall','Tiny-step or 10000-step budget reached')
                _,o=self.evaluate(nx)
                if seek_entry and o['H']>=0:
                    candidate=self.localize(before,nt,dense)
                    # Keep the candidate extension privately until all methods agree.
                    self.candidate=candidate;self.pending_dense=dense
                    self.probes.append(dict(start=before,trialEnd=nt,startState=self.decode(old).tolist(),candidate=candidate,stages=self.stage_records,accepted=False))
                    return
                self.accept(nt,nx,dense)
            except Failure as e:
                self.probes.append(dict(start=before,stages=self.stage_records,localization_probes=getattr(self,'localization_records',[]),accepted=False,failure=e.code));self.stop(e);return
        self.save(self.t,self.x)
    def entry(self):
        if self.case=='high':
            self.advance(.05,False)
            if self.failure:return
            self.events.append(dict(type='scheduled-command',t=.05,from_target=self.target,to_target=self.cfg['target'],physical_state_and_I_continuous=True))
            self.target=self.cfg['target'];self.save(self.t,self.x)
        self.advance(ENDS[self.case],True)
        if not self.failure and self.candidate is None:self.stop(Failure('missing-entry','Fixed endpoint reached without declared entry'))
    def slide(self):
        c=self.candidate
        try:
            x=np.array(c['x']);self.accept(c['t'],x,self.pending_dense)
            z=self.decode(x);self.mode='sliding'
            if self.rep=='reduced-independent':self.x=np.r_[x[:4],x[5:]]
            reconstructed=self.decode(self.x)
            discrepancy=abs(z[4]-reconstructed[4])
            if discrepancy>1e-9:raise Failure('event-coordinate','Reduced event coordinate inconsistency exceeds 1e-9')
            self.events.append(dict(type='sliding-entry',t=self.t,bracket=c['bracket'],H=c['H'],weight=c['weight'],normal_on=c['normal_on'],normal_off=c['normal_off'],coordinate_discrepancy=discrepancy,mechanical_jump=0.,integral_reset=False))
            self.candidate['accepted']=True;self.save(self.t,self.x);self.advance(ENDS[self.case],False)
        except Failure as e:self.stop(e)
    def result(self):
        self.save(self.t,self.x);z=self.decode(self.x);qerrors=np.abs(self.quad-z[5:11])
        return dict(case=self.case,representation=self.rep,method=self.method,cfg=self.cfg,declared_endpoint_s=ENDS[self.case],acceptedTime=self.t,history=self.history,events=self.events,failure=self.failure,candidate=self.candidate,localization_auxiliaries=self.probes,accepted_intervals=self.intervals,independent_quadrature=dict(integrals=self.quad.tolist(),errors=qerrors.tolist(),passed=bool(np.all(qerrors<=np.array([1e-5]*5+[1e-7]))),scope='GL8 on actual method dense polynomials, accepted intervals only; independent BPoly/Brent powers'),accepted_steps=self.steps,max_stage_force_residual_N=self.max_residual,min_stage_q=self.min_q,min_stage_s=self.min_s,convention='Filippov single strictly attracting surface; no exit rule',qualified=False)

def entry_agreement(engines):
    if len(engines)!=10 or any(e.failure or not e.candidate for e in engines):return dict(passed=False,reason='missing-or-failed-entry-cell')
    times=[e.candidate['t'] for e in engines];span=max(times)-min(times)
    # Compare full/reduced incoming integral and raw at a common pre-entry grid.
    maps=[{round(r['t'],9):r for r in e.history} for e in engines];common=sorted(set.intersection(*(set(m) for m in maps)))
    maxI=maxraw=0.
    for t in common:
        vals=[m[t] for m in maps];maxI=max(maxI,max(r['z'][4] for r in vals)-min(r['z'][4] for r in vals));maxraw=max(maxraw,max(r['uraw'] for r in vals)-min(r['uraw'] for r in vals))
    return dict(passed=span<=2e-6 and maxI<=1e-9 and maxraw<=1e-8,event_time_span_s=span,event_gate_s=2e-6,common_pre_entry_grid_count=len(common),max_integral_difference=maxI,integral_gate=1e-9,max_raw_difference=maxraw,raw_gate=1e-8,times={e.rep+'/'+e.method:e.candidate['t'] for e in engines})

def main():
    OUT.mkdir(parents=True,exist_ok=True);engines=[];entry_checks={};started=time.monotonic()
    try:
        for case in CASES:
            group=[]
            for rep in REPS:
                for method in METHODS:
                    e=Engine(case,rep,method);engines.append(e);group.append(e);e.entry()
                    print('ENTRY',case,rep,method,e.candidate['t'] if e.candidate else e.t,e.failure['code'] if e.failure else 'candidate',flush=True)
            check=entry_agreement(group);entry_checks[case]=check
            print('ENTRY AGREEMENT',case,check,flush=True)
            for e in group:
                if check['passed']:e.slide()
                elif not e.failure:e.stop(Failure('entry-refinement-block','Common independent event/controller checks failed; candidate not accepted'))
                r=e.result();(OUT/f'{case}-{e.rep}-{e.method}.json').write_text(json.dumps(r,indent=2)+'\n')
                print('RESULT',case,e.rep,e.method,e.t,e.failure['code'] if e.failure else 'bounded-endpoint',flush=True)
        sources=['education/tools/run_filippov_bounded_experiment.py','education/tools/filippov_source_worker.mjs','education/tools/vertical_force_reference.py','education/web/vertical-force-model.js','education/data/vertical-force-command-v1/protocol.json','education/data/millard-reference-v1/review/native-controls.json']
        receipt=dict(scope='Owner-approved isolated bounded experiment, pending independent review',entry_checks=entry_checks,required_cells=20,executed_cells=len(engines),source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},elapsed_s=time.monotonic()-started,original_trajectories_modified=False,physical_gains_gates_changed=False)
        (OUT/'matrix-execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
    finally:
        for e in engines:
            if e.source:e.source.close()

if __name__=='__main__':main()

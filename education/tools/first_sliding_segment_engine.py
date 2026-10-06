#!/usr/bin/env python3
"""Transactional approved scalar-model sliding segment; no undeclared exit."""
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import numpy as np
from scipy.integrate import DOP853, Radau
from run_filippov_bounded_experiment import ROOT, Source, Failure, NODES, WEIGHTS
from run_ordinary_crossing_consistency import dense_record, replay_dense
from first_sliding_segment_preflight import custody, json_native_scalar
from vertical_force_reference import output as reference_output, activation_rhs, C, P

DATA=ROOT/'education/data/first-sliding-segment-exploratory-v1'
PREP=ROOT/'education/data/first-sliding-segment-protocol-v1'
STATE_NAMES=['y_m','w_m_per_s','a','q','FT_N','I','raw']
STATE_GATES=np.array([1e-6,1e-5,2e-6,2e-6,1e-4,1e-9,1e-8])
BALANCE_GATES=np.array([1e-5]*4+[1e-7,1e-5])
QUAD_GATES=np.array([1e-5]*5+[1e-7])
WITNESSES=[.26225,.2625,.26275,.263]
END=.263


def dump_new(path,value):
    if path.exists():raise ValueError('Refuse to overwrite evidence: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,default=json_native_scalar,allow_nan=False)+'\n')


def verify_bindings():
    p=json.loads((DATA/'protocol.json').read_text())
    if not p['explicit_execution_authorized'] or not p['protocol_scoped_ACK']:
        raise ValueError('Execution authorization absent')
    for path,digest in {**p['input_sha256'],**p['source_sha256']}.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:
            raise ValueError('Frozen input/source changed: '+path)
    freeze=json.loads((DATA/'preflight/source-freeze.json').read_text())
    import subprocess
    if subprocess.check_output(['git','rev-parse',freeze['commit']+'^{tree}'],cwd=ROOT,text=True).strip()!=freeze['tree']:
        raise ValueError('Source freeze tree mismatch')
    for path in list(p['source_sha256'])+['education/data/first-sliding-segment-exploratory-v1/protocol.json']:
        if subprocess.check_output(['git','show',freeze['commit']+':'+path],cwd=ROOT)!=(ROOT/path).read_bytes():
            raise ValueError('Executed source differs from frozen commit: '+path)
    return p


def independent_field(z,cfg,sliding):
    o=reference_output(z,cfg,{'target':cfg['target']})
    o['kt']=500*C['tendon'].value(o['s'],True)
    o['_mass']=cfg['m']
    if sliding:
        o['u']=.01
        o['adot']=activation_rhs(z[2],.01)
    return complete_field(z,o,sliding)


def complete_field(z,o,sliding):
    d=.4*o['kt']*(z[1]+o['v'])/100;k=8*o['e']
    o=dict(o,H=.01-o['uraw'],d=d,k=k,normal_on=-(d+k),normal_off=-d,
           theta=-d/k if k else None,Idot=-d if sliding else k,g=o['u']-z[2])
    rate=np.array([z[1],o['acceleration'],o['adot'],10*o['v'],o['Idot'],
                   o['Pactive'],o['D'],o['loadPower'],o['fiberPower'],o['tendonPower'],
                   o['FT']-P['gravity_m_per_s2']*o.get('_mass',1.)])
    return o,rate


def native_field(z,cfg,source,sliding):
    o=source.evaluate(z,cfg,cfg['target'],sliding,.01)
    o['_mass']=cfg['m']
    return complete_field(z,o,sliding)


def decode_reduced(x,cfg):
    s=(cfg['L0']-x[0]-.1*x[3])/.2
    ft=100*C['tendon'].value(s)
    I=.01-cfg['ub']-.4*(cfg['target']-ft)/100
    return np.r_[x[:4],I,x[4:]]


def validate_diagnostics(z,o,sliding,constraint=True):
    if not np.all(np.isfinite(z)) or not all(np.isfinite(o[k]) for k in ['H','d','k','normal_on','normal_off','residual','g']):
        raise Failure('nonfinite','Nonfinite trial diagnostics')
    if abs(o['residual'])>1e-7:raise Failure('force-residual','Original force gate failed')
    if not .01<z[2]<1:raise Failure('activation-bound','Activation equality/bound is undeclared')
    if z[3]<=.4441 or o['s']<=1:raise Failure('physical-domain','Original fiber/taut-tendon domain lost')
    if o['g']>=-1e-13:raise Failure('activation-side-ambiguity','Deactivation side lost; no extra guard declared')
    if -o['e']<=0 or o['normal_on']<=1e-8 or o['normal_off']>=-1e-8:
        raise Failure('strict-sign-loss','Strict attraction/outward error lost; no exit law')
    if o['theta'] is None or not 0<o['theta']<1:
        raise Failure('nonconvex-weight','Weight outside open unit interval; no clipping')
    if sliding and constraint and abs(o['H'])>1e-9:
        raise Failure('constraint-drift','Original sliding constraint gate failed')
    if not sliding and o['H']>1e-9:
        raise Failure('incoming-prefix-side','Incoming suffix cannot enter accepted prefix')


def balance_errors(z,base,cfg):
    o=reference_output(z,cfg,{'target':cfg['target']})
    s0=(cfg['L0']-base[0]-.1*base[3])/.2
    ef=10*C['passive'].integral(base[3],z[3])
    et=20*C['tendon'].integral(s0,o['s'])
    el=.5*cfg['m']*(z[1]**2-base[1]**2)+cfg['m']*P['gravity_m_per_s2']*(z[0]-base[0])
    a,d,l,f,t,j=np.array(z[5:11])-np.array(base[5:11])
    return np.array([ef-f,et-t,el-l,ef+et+el-a+d,cfg['m']*(z[1]-base[1])-j,a-d-l-f-t])


def check_balances(errors):
    if np.any(np.abs(errors)>BALANCE_GATES):
        raise Failure('work-impulse-gate','Original component/combined work or impulse gate failed')


def compare_rows(a,b,times):
    ma={round(v['t'],12):v for v in a};mb={round(v['t'],12):v for v in b}
    missing=[t for t in times if round(t,12) not in ma or round(t,12) not in mb]
    if missing:return dict(passed=False,missing_times=missing,samples=0)
    values=[]
    for t in times:
        x,y=ma[round(t,12)],mb[round(t,12)]
        values.append(np.r_[np.array(x['z'][:4])-y['z'][:4],x['FT']-y['FT'],x['z'][4]-y['z'][4],x['uraw']-y['uraw']])
    values=np.array(values);maximum=np.max(np.abs(values),axis=0)
    return dict(passed=bool(np.all(maximum<=STATE_GATES)),samples=len(times),times=times,
                max_errors=dict(zip(STATE_NAMES,maximum.tolist())),
                margins=dict(zip(STATE_NAMES,(STATE_GATES-maximum).tolist())),
                signed_maximum_witnesses={n:dict(t=times[int(np.argmax(abs(values[:,j])))],signed_error=float(values[int(np.argmax(abs(values[:,j]))),j])) for j,n in enumerate(STATE_NAMES)},
                absolute_times=True,event_alignment=False)


class SegmentEngine:
    def __init__(self,incoming,prepared,source=None):
        self.rep=incoming['representation'];self.method=incoming['method'];self.cfg=copy.deepcopy(incoming['cfg'])
        self.prepared=prepared;self.candidate=copy.deepcopy(prepared['readonly_refined_candidate'])
        self.original=copy.deepcopy(incoming['history']);self.events=copy.deepcopy(incoming['events'])
        self.source=source if source is not None else Source() if self.rep=='full-source' else None
        self.owns_source=source is None and self.source is not None
        self.t=float(incoming['acceptedTime']);self.x=np.array(incoming['history'][-1]['z'])
        self.quad=np.array(incoming['independent_quadrature']['integrals']);self.history=copy.deepcopy(self.original)
        self.mode='incoming';self.intervals=[];self.probes=[];self.stages=[];self.jacobian_probes=[]
        self.old_steps=incoming['accepted_steps'];self.accepted_steps=0;self.failure=None;self.entry_state=None;self.entry_quad=None;self.handoff=None
        self.incoming_dense=incoming['combined_arbitrations'][-1]['dense']
        self.cfg_hash=hashlib.sha256(json.dumps(self.cfg,sort_keys=True).encode()).hexdigest()

    def close(self):
        if self.owns_source:self.source.close()

    def fingerprint(self):
        return json.dumps(dict(t=self.t,x=self.x.tolist(),quad=self.quad.tolist(),history=self.history,
                               events=self.events,intervals=self.intervals,steps=self.accepted_steps,
                               mode=self.mode,entry_state=None if self.entry_state is None else self.entry_state.tolist(),
                               entry_quad=None if self.entry_quad is None else self.entry_quad.tolist(),handoff=self.handoff),sort_keys=True)

    def decode(self,x,mode=None):
        mode=mode or self.mode
        return decode_reduced(x,self.cfg) if mode=='sliding' and self.rep=='reduced-independent' else np.array(x)

    def evaluate(self,t,x,role='diagnostic',mode=None,constraint=True):
        mode=mode or self.mode;z=self.decode(x,mode);sliding=mode=='sliding';record=dict(t=float(t),x=np.array(x).tolist(),z=z.tolist(),role=role,accepted=False)
        try:
            if hashlib.sha256(json.dumps(self.cfg,sort_keys=True).encode()).hexdigest()!=self.cfg_hash:
                raise Failure('configuration-change','Undeclared configuration/command change')
            o,rate=native_field(z,self.cfg,self.source,sliding) if self.source else independent_field(z,self.cfg,sliding)
            validate_diagnostics(z,o,sliding,constraint)
            ref,ref_rate=independent_field(z,self.cfg,sliding)
            validate_diagnostics(z,ref,sliding,constraint)
            if abs(o['FT']-ref['FT'])>1e-7 or max(abs(o['normal_on']-ref['normal_on']),abs(o['normal_off']-ref['normal_off']))>1e-8:
                raise Failure('independent-field-gate','Independent force or mode-normal disagreement')
            tangent=abs(ref['d']+rate[4]) if sliding else None
            if sliding and tangent>1e-8:raise Failure('tangency-gate','Independent tangent residual failed')
            cumulative=balance_errors(z,self.cfg['z'],self.cfg)
            if role!='Jacobian-auxiliary':check_balances(cumulative)
            segment=balance_errors(z,self.entry_state,self.cfg) if sliding and self.entry_state is not None else np.zeros(6)
            if role!='Jacobian-auxiliary':check_balances(segment)
            record.update(H=o['H'],normal_on=o['normal_on'],normal_off=o['normal_off'],theta=o['theta'],
                          g=o['g'],force_residual_N=o['residual'],independent_force_residual_N=ref['residual'],
                          independent_tangent_residual_per_s=tangent,cumulative_balance_errors=cumulative.tolist(),
                          segment_balance_errors=segment.tolist(),rate_full=rate.tolist(),
                          constraint_checked=constraint,ledger_checked=role!='Jacobian-auxiliary',mode=mode)
            return z,o,rate,record
        except ValueError as error:
            if not isinstance(error,Failure):error=Failure(getattr(error,'code','source-or-reference-root'),str(error))
            error.t=float(t);error.z=z.tolist();record.update(failure=error.code,message=str(error));self.probes.append(record)
            raise error

    def row(self,t,x,mode=None):
        z,o,rate,record=self.evaluate(t,x,'history-witness',mode)
        return dict(t=float(t),z=z.tolist(),target=self.cfg['target'],mode=mode or self.mode,
                    controller_mode='sliding' if (mode or self.mode)=='sliding' else 'integrating',
                    activation_branch='deactivation',**{k:float(o[k]) for k in ['FT','u','uraw','e','H','normal_on','normal_off','residual','v','Idot']},
                    theta=o['theta'],g=o['g'],diagnostics=record)

    def rhs(self,t,x):
        z,o,rate,record=self.evaluate(t,x,'ODE-stage')
        self.stages.append(record)
        return np.r_[rate[:4],rate[5:]] if self.rep=='reduced-independent' else rate

    def jac(self,t,x):
        # The old fixed physical-column FD convention. These off-surface
        # probes never become stages, accepted states or quadrature points.
        n=4 if self.rep=='reduced-independent' else 5;J=np.zeros((len(x),len(x)))
        for j in range(n):
            h=1e-7*max(1.,abs(x[j]));a=x.copy();b=x.copy();a[j]+=h;b[j]-=h
            rates=[]
            for xx in [a,b]:
                z,o,rate,record=self.evaluate(t,xx,'Jacobian-auxiliary',mode='sliding',constraint=False)
                self.jacobian_probes.append(record)
                rates.append(np.r_[rate[:4],rate[5:]] if self.rep=='reduced-independent' else rate)
            J[:,j]=(rates[0]-rates[1])/(2*h)
        return J

    def prepare_interval(self,stop,newx,dense,record,mode=None):
        mode=mode or self.mode;before=self.t;increment=np.zeros(6);samples=[]
        times=sorted(set([before,(before+stop)/2,stop]+[before+(stop-before)*(n+1)/2 for n in NODES]))
        for ti in times:
            z,o,rate,diag=self.evaluate(ti,dense(ti),'dense-guard',mode);samples.append(diag)
        for node,weight in zip(NODES,WEIGHTS):
            ti=before+(stop-before)*(node+1)/2;z,o,rate,diag=self.evaluate(ti,dense(ti),'GL8',mode)
            ref,rr=independent_field(z,self.cfg,mode=='sliding')
            increment+=(stop-before)*weight/2*rr[5:11]
        z,o,rate,diag=self.evaluate(stop,newx,'trial-endpoint',mode)
        newquad=self.quad+increment
        if np.any(np.abs(newquad-z[5:11])>QUAD_GATES):raise Failure('quadrature-gate','Cumulative independent GL8 gate failed',stop,z)
        if mode=='sliding' and self.entry_quad is not None:
            if np.any(np.abs(newquad-self.entry_quad-(z[5:11]-self.entry_state[5:11]))>QUAD_GATES):
                raise Failure('segment-quadrature-gate','Independent entry-to-endpoint GL8 gate failed',stop,z)
        grids=[float(k*.001) for k in range(math.floor((before+1e-10)/.001)+1,math.floor((stop+1e-10)/.001)+1)]
        witness=[t for t in WITNESSES if before<t<=stop]
        rows=[self.row(ti,dense(ti),mode) for ti in sorted(set(grids+witness+[float(stop)])) if ti>before]
        return dict(stop=float(stop),x=np.array(newx),quad=newquad,rows=rows,
                    interval=dict(start=before,end=float(stop),mode=mode,dense=record,guard_samples=samples,
                                  stages=copy.deepcopy(self.stages),GL8_increment=increment.tolist(),auxiliary_suffix_excluded=True))

    def commit(self,proposal):
        # All checks precede this mutation; no output/kernel calls occur here.
        self.t=proposal['stop'];self.x=proposal['x'].copy();self.quad=proposal['quad'].copy()
        for row in proposal['rows']:
            if self.history and row['t']==self.history[-1]['t']:self.history[-1]=row
            else:self.history.append(row)
        self.intervals.append(proposal['interval']);self.accepted_steps+=1

    def prepare_entry(self):
        c=self.candidate;z=np.array(c['state']);dense=lambda t:replay_dense(self.incoming_dense,t)
        if not np.array_equal(z,dense(c['t'])):raise Failure('entry-custody','Own actual polynomial does not reproduce candidate')
        prefix=self.prepare_interval(c['t'],z,dense,self.incoming_dense,'incoming')
        x=np.r_[z[:4],z[5:]] if self.rep=='reduced-independent' else z.copy()
        decoded=self.decode(x,'sliding')
        if not np.array_equal(np.r_[z[:4],z[5:]],np.r_[decoded[:4],decoded[5:]]):
            raise Failure('handoff-other-ten','Other ten coordinates not preserved')
        dz=float(decoded[4]-z[4]);before=independent_field(z,self.cfg,False)[0]['uraw'];after=independent_field(decoded,self.cfg,True)[0]['uraw']
        if abs(dz)>1e-9 or abs(after-before)>1e-9:raise Failure('entry-coordinate','Original finite I/raw coordinate gate failed')
        self.evaluate(c['t'],x,'proposed-sliding-entry','sliding')
        return dict(prefix=prefix,sliding_x=x,decoded=decoded,
                    handoff=dict(signed_delta_I=dz,signed_delta_raw=float(after-before),I_bitwise_preserved=bool(decoded[4]==z[4]),
                                 full_I_retained=self.rep=='full-source',other_ten_bitwise_preserved=True,
                                 exact_eleven_coordinate_continuity=self.rep=='full-source',incoming=z.tolist(),decoded=decoded.tolist()))

    def enter(self,proposal,all_entries_passed):
        if not all_entries_passed:raise Failure('entry-matrix-block','All twelve checks must pass before acceptance')
        self.commit(proposal['prefix'])
        self.mode='sliding';self.x=proposal['sliding_x'].copy();self.entry_state=proposal['decoded'].copy();self.entry_quad=self.quad.copy();self.handoff=proposal['handoff']
        self.candidate['accepted']=True
        self.events.append(dict(type='sliding-entry',t=self.t,bracket=self.candidate['bracket'],**self.handoff))
        # This row was validated before acceptance, so replace without a kernel call.
        self.history[-1]=proposal['sliding_entry_row']

    def advance(self):
        solver=None
        while self.t<END:
            before=self.t;old=self.x.copy();fingerprint=self.fingerprint();self.stages=[];self.jacobian_probes=[];record=None
            try:
                if self.method.startswith('RK4'):
                    h=min(float(self.method.split('-')[1]),END-before,(math.floor((before+1e-10)/.001)+1)*.001-before)
                    a=self.rhs(before,old);b=self.rhs(before+h/2,old+h*a/2);c=self.rhs(before+h/2,old+h*b/2);d=self.rhs(before+h,old+h*c)
                    rates=[a,b,c,d]
                    def dense(t):
                        u=(t-before)/h
                        return old+h*((u-1.5*u*u+2*u**3/3)*a+(u*u-2*u**3/3)*(b+c)+(-u*u/2+2*u**3/3)*d)
                    nt=before+h;nx=dense(nt)
                else:
                    if solver is None:
                        cls={'DOP853':DOP853,'Radau':Radau}[self.method]
                        solver=cls(self.rhs,before,old,END,rtol=1e-9,atol=1e-11,max_step=.0005,**({'jac':self.jac} if cls is Radau else {}))
                    solver.step()
                    if solver.status=='failed':raise Failure('ODE-step','Adaptive solver failed')
                    nt=float(solver.t);nx=solver.y.copy();dense=solver.dense_output();rates=None
                if nt-before<1e-10 or self.old_steps+self.accepted_steps>=12000:raise Failure('ODE-stall','Original watchdog/tiny step gate')
                record=dense_record(self.method,before,nt,old,dense,rates)
                for ti in [before,(before+nt)/2,nt]:
                    if np.max(np.abs(replay_dense(record,ti)-dense(ti)))>1e-12:raise Failure('dense-serialization','Actual dense polynomial reproduction failed')
                proposal=self.prepare_interval(nt,nx,dense,record)
                proposal['interval']['jacobian_auxiliaries']=copy.deepcopy(self.jacobian_probes)
                self.commit(proposal)
            except ValueError as error:
                if not isinstance(error,Failure):error=Failure(getattr(error,'code','solver-exception'),str(error))
                assert self.fingerprint()==fingerprint,'Rejected trial changed accepted custody'
                self.failure=dict(code=error.code,message=str(error),acceptedTime=self.t,acceptedState=self.decode(self.x).tolist(),
                                  failedStageTime=error.t,failedStageState=error.z,rollback_exact=True)
                self.probes.append(dict(start=before,startState=old.tolist(),dense=record,stages=copy.deepcopy(self.stages),
                                        jacobian_auxiliaries=copy.deepcopy(self.jacobian_probes),failure=error.code,accepted=False))
                return

    def result(self):
        z=self.decode(self.x);errors=abs(self.quad-z[5:11]);segment_errors=None
        if self.entry_state is not None:segment_errors=abs(self.quad-self.entry_quad-(z[5:11]-self.entry_state[5:11])).tolist()
        return dict(case='mass-1',representation=self.rep,method=self.method,cfg=self.cfg,
                    declared_endpoint_s=END,acceptedTime=self.t,acceptedState=z.tolist(),history=self.history,events=self.events,
                    candidate=self.candidate,failure=self.failure,accepted_intervals=self.intervals,failed_probes=self.probes,
                    accepted_new_intervals=self.accepted_steps,total_accepted_steps=self.old_steps+self.accepted_steps,sliding_steps=sum(i['mode']=='sliding' for i in self.intervals),
                    independent_quadrature=dict(integrals=self.quad.tolist(),errors=errors.tolist(),passed=bool(np.all(errors<=QUAD_GATES)),segment_errors=segment_errors),
                    incoming_path=self.prepared['path'],incoming_sha256=self.prepared['input_sha256'],entry_preparation=self.prepared,
                    handoff=self.handoff,entry_state=None if self.entry_state is None else self.entry_state.tolist(),
                    entry_quad=None if self.entry_quad is None else self.entry_quad.tolist(),qualified=False,
                    completed=bool(self.failure is None and self.t==END),hidden_root_theorem=False,
                    full_combined_external_raw_replay_complete=False,historical_activation_external_raw_replay_complete=False,
                    convention='Approved Filippov single strict-attraction surface; no exit law; finite reduced I/raw handoff disclosed')

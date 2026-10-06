#!/usr/bin/env python3
"""Frozen, incoming-only 25-us diagnostic. No sliding or qualification path.

Reuses immutable fields, RK4 stages, physical gates and original localization.
Only the separately predeclared accepted-step watchdog accommodates 10560 steps.
Activation-root observations never split/alter an accepted step.
"""
import json,hashlib,math,time
from pathlib import Path
import numpy as np
from run_filippov_bounded_experiment import Engine,Failure,ROOT

DATA=ROOT/'education/data/filippov-incoming-convergence-v1'
PROTOCOL=json.loads((DATA/'protocol.json').read_text())
OUT=DATA/'review'

def verify_inputs():
    for path,digest in {**PROTOCOL['input_sha256'],**PROTOCOL.get('diagnostic_source_sha256',{})}.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:
            raise ValueError('Frozen diagnostic input changed: '+path)

class DiagnosticEngine(Engine):
    def __init__(self,case,rep):
        if case not in PROTOCOL['cases'] or rep not in PROTOCOL['representations']:raise ValueError('Undeclared cell')
        super().__init__(case,rep,'RK4-0.000025')
        self.activation_probes=[]
    def slide(self):raise Failure('diagnostic-no-sliding','Sliding is prohibited in this diagnostic')
    def activation_probe(self,left,right,dense):
        if self.case!='mass-1' or right<.002 or left>.003:return None
        lo,hi=max(left,.002),min(right,.003)
        _,a=self.evaluate(dense(lo));_,b=self.evaluate(dense(hi));ga=a['u']-dense(lo)[2];gb=b['u']-dense(hi)[2]
        if ga*gb>=0:return None
        records=[]
        for iteration in range(32):
            mid=(lo+hi)/2;z,o=self.evaluate(dense(mid));g=o['u']-z[2]
            records.append(dict(t=mid,z=z.tolist(),g=g,force_residual_N=o['residual'],accepted=False))
            if g*ga>0:lo=mid;ga=g
            else:hi=mid
            if hi-lo<=1e-12 and abs(g)<=1e-13:
                derivative=o['d']+o['Idot']-o['adot'] if .01<o['u']<1 else -o['adot']
                return dict(t=mid,z=z.tolist(),g=g,bracket=[lo,hi],iterations=iteration+1,normal_per_s=derivative,surface_residual_timing_proxy_s=abs(g/derivative),probes=records,accepted=False,step_split=False)
        return dict(bracket=[lo,hi],probes=records,accepted=False,step_split=False,diagnostic_failure='activation-root-resolution')
    def advance(self,end,seek_entry):
        # RK-only copy of the reviewed acceptance path; no adaptive/new controller.
        while self.t<end-1e-12 and not self.failure:
            self.stage_records=[];before=self.t;old=self.x.copy()
            try:
                if self.mode!='incoming':raise Failure('diagnostic-no-sliding','Nonincoming state prohibited')
                h=min(PROTOCOL['additional_step_s'],end-self.t,((math.floor((self.t+1e-10)/.001)+1)*.001)-self.t)
                nt,nx,dense=self.step_rk(self.t,self.x,h)
                if nt-before<1e-10 or self.steps>=PROTOCOL['accepted_step_watchdog']:raise Failure('diagnostic-watchdog','Tiny-step or predeclared accepted-step watchdog')
                _,o=self.evaluate(nx);direction=1 if self.controller_mode=='integrating' else -1
                if seek_entry and direction*o['H']>=0:
                    candidate=self.localize(before,nt,dense)
                    auxiliary=dict(start=before,trialEnd=nt,startState=self.decode(old).tolist(),stages=self.stage_records,accepted=False)
                    if candidate['classification']!='attracting':
                        auxiliary['ordinary_crossing']=candidate;self.probes.append(auxiliary)
                        self.accept(candidate['t'],np.array(candidate['x']),dense)
                        self.events.append(dict(type=candidate['classification'],t=self.t,bracket=candidate['bracket'],H=candidate['H'],normal_on=candidate['normal_on'],normal_off=candidate['normal_off'],integral_reset=False,mechanical_jump=0.))
                        self.controller_mode='frozen' if direction==1 else 'integrating';self.save(self.t,self.x);continue
                    self.candidate=candidate;auxiliary['candidate']=candidate;self.probes.append(auxiliary)
                    return  # even a perfectly agreed candidate is NEVER accepted
                activation=self.activation_probe(before,nt,dense)
                self.accept(nt,nx,dense)
                if activation:self.activation_probes.append(activation)
            except Failure as e:
                self.probes.append(dict(start=before,stages=self.stage_records,localization_probes=getattr(self,'localization_records',[]),accepted=False,failure=e.code));self.stop(e);return
        self.save(self.t,self.x)

def main():
    from argparse import ArgumentParser
    parser=ArgumentParser();parser.add_argument('--case',required=True,choices=PROTOCOL['cases']);parser.add_argument('--rep',required=True,choices=PROTOCOL['representations']);args=parser.parse_args()
    verify_inputs();OUT.mkdir(parents=True,exist_ok=True);dest=OUT/f'{args.case}-{args.rep}-RK4-0.000025.json'
    if dest.exists():raise ValueError('Refuse to overwrite diagnostic evidence: '+str(dest))
    started=time.monotonic();e=DiagnosticEngine(args.case,args.rep)
    try:
        e.entry();r=e.result()
        r.update(diagnostic_only=True,diagnostic_complete=e.candidate is not None and e.failure is None,diagnostic_termination='Attracting candidate held; last incoming state retained',activation_dense_probes=e.activation_probes,sliding_allowed=False,accepted_step_watchdog=PROTOCOL['accepted_step_watchdog'],elapsed_s=time.monotonic()-started,protocol_sha256=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest(),executed_source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['education/tools/run_filippov_incoming_diagnostic.py','education/tools/run_filippov_bounded_experiment.py','education/tools/filippov_source_worker.mjs']})
        assert all(x['mode']=='incoming' for x in r['history'])
        assert r['candidate'] is None or not r['candidate'].get('accepted',False)
        dest.write_text(json.dumps(r,indent=2)+'\n')
        print(args.case,args.rep,'accepted incoming stop',e.t,'candidate',e.candidate['t'] if e.candidate else None,'failure',e.failure,'accepted steps',e.steps,'elapsed',r['elapsed_s'],flush=True)
    finally:
        if e.source:e.source.close()

if __name__=='__main__':main()

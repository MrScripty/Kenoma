#!/usr/bin/env python3
"""Audit common times, source-force closure, endpoint work, and independent
eight-point quadrature on actual accepted Radau dense polynomials.
The earlier failed history-Hermite diagnostic remains reproducible separately.
No interpolation is used to claim an unaccepted state or continue a failure.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from vertical_force_reference import P,C,output,jacobian,ROOT

OUT=ROOT/'education/data/vertical-force-command-v1/review'
B=P['budgets']; G=P['gravity_m_per_s2']; checks=[]

def record(name,passed,**detail):
    checks.append(dict(name=name,passed=bool(passed),**detail))

def compare(a,b):
    # Match only stored accepted timestamps; no terminal extrapolation.
    aa={round(r['t'],9):r for r in a['history']};bb={round(r['t'],9):r for r in b['history']}
    times=sorted(aa.keys()&bb.keys());err=np.zeros(5)
    for t in times:
        x,y=aa[t],bb[t];err=np.maximum(err,[abs(x['z'][0]-y['z'][0]),abs(x['z'][1]-y['z'][1]),abs(x['z'][2]-y['z'][2]),abs(x['z'][3]-y['z'][3]),abs(x['FT']-y['FT'])])
    gates=[B['y_m'],B['w_m_per_s'],B['activation_q'],B['activation_q'],B['replay_force_N']]
    ev_a=[e['t'] for e in a['events'] if e['type']=='brake-crossing'];ev_b=[e['t'] for e in b['events'] if e['type']=='brake-crossing']
    event=max([abs(x-y) for x,y in zip(ev_a,ev_b)],default=0)
    return dict(passed=bool(len(times)>2 and np.all(err<=gates) and len(ev_a)==len(ev_b) and event<=B['event_time_s']),matched_count=len(times),matched_end=times[-1],max_errors=dict(zip(['y_m','w_m_s','a','q','force_N'],err.tolist())),budgets=dict(zip(['y_m','w_m_s','a','q','force_N'],gates)),brake_time_error_s=event)

def balance(result):
    cfg=result['cfg'];start=result['history'][0]['z'];s0=(cfg['L0']-start[0]-.1*start[3])/.2
    errors=np.zeros(6); residual=0.;minq=float('inf');mins=float('inf')
    for r in result['history']:
        z=r['z'];phase={'target':r['target'],'mode':r['mode']};o=output(z,cfg,phase);q=z[3]
        fiber=10*C['passive'].integral(start[3],q);tendon=20*C['tendon'].integral(s0,o['s']);load=.5*cfg['m']*(z[1]**2-start[1]**2)+cfg['m']*G*(z[0]-start[0])
        errors=np.maximum(errors,np.abs([fiber-z[8],tendon-z[9],load-z[7],fiber+tendon+load-z[5]+z[6],cfg['m']*(z[1]-start[1])-z[10],z[5]-z[6]-z[7]-z[8]-z[9]]))
        residual=max(residual,abs(o['residual']),abs(o['FT']-r['FT']));minq=min(minq,q);mins=min(mins,o['s'])
    names=['fiber_J','tendon_J','load_J','combined_J','momentum_N_s','power_ledger_J'];gates=np.array([B['component_combined_work_J']]*4+[B['momentum_N_s'],B['component_combined_work_J']])
    return dict(passed=bool(np.all(errors<=gates) and residual<=B['force_N'] and minq>.4441 and mins>1),max_errors=dict(zip(names,errors.tolist())),source_force_residual_N=residual,min_q=minq,min_s=mins)

NODES,WEIGHTS=np.polynomial.legendre.leggauss(8)
def quadrature(result):
    """Independent history reconstruction, curve integration and force evaluation.
    Left phase is used for both endpoint derivatives at scheduled mode changes.
    """
    cfg=result['cfg'];total=np.zeros(6)
    for left,right in zip(result['history'],result['history'][1:]):
        h=right['t']-left['t'];a=np.array(left['z'][:5]);b=np.array(right['z'][:5]);phase={'target':left['target'],'mode':left['mode']}
        oa=output(left['z'],cfg,phase);ob=output(right['z'],cfg,phase)
        da=np.array([a[1],oa['acceleration'],oa['adot'],10*oa['v'],oa['Idot']]);db=np.array([b[1],ob['acceleration'],ob['adot'],10*ob['v'],ob['Idot']])
        for node,weight in zip(NODES,WEIGHTS):
            u=(node+1)/2;z=(2*u**3-3*u**2+1)*a+(u**3-2*u**2+u)*h*da+(-2*u**3+3*u**2)*b+(u**3-u**2)*h*db
            rate=(6*u*u-6*u)*a/h+(3*u*u-4*u+1)*da+(-6*u*u+6*u)*b/h+(3*u*u-2*u)*db
            lfdot=.1*rate[3];v=lfdot;ft=100*C['tendon'].value((cfg['L0']-z[0]-.1*z[3])/.2);fp=100*C['passive'].value(z[3]);fa=100*z[2]*C['active'].value(z[3])*C['velocity'].value(v)
            total+=h*weight/2*np.array([-fa*lfdot,10*v*v,ft*z[1],fp*lfdot,ft*(-z[1]-lfdot),ft-cfg['m']*G])
    end=np.array(result['history'][-1]['z']);err=np.abs(total-end[5:11]);gates=np.array([B['component_combined_work_J']]*5+[B['momentum_N_s']])
    return dict(passed=bool(np.all(err<=gates)),max_errors=dict(zip(['active_J','dissipation_J','load_J','fiber_J','tendon_J','momentum_N_s'],err.tolist())),quadrature='Gauss-Legendre 8 / cubic Hermite / accepted-history intervals')

def main():
    cases=json.loads((OUT/'cases.json').read_text());results=[]
    for case in cases:
        ident=case['id'];rs={method:json.loads((OUT/f'{ident}-{method}.json').read_text()) for method in ['coarse','fine','DOP853','Radau']}
        cmp={method:compare(rs['fine'],rs[method]) for method in ['coarse','DOP853','Radau']}
        bal={method:balance(rs[method]) for method in rs};quad=rs['Radau']['independent_quadrature']
        failure=rs['fine']['failure'];full=failure is None
        retention=all(r['failure'] is None or (r['acceptedTime']==r['failure']['acceptedTime'] and r['history'][-1]['z']==r['failure']['acceptedState'] and r['history'][-1]['t']==r['acceptedTime']) for r in rs.values())
        record(ident,all(r['passed'] for r in cmp.values()) and all(r['passed'] for r in bal.values()) and quad['passed'] and retention,full_trajectory=full,accepted_times={k:r['acceptedTime'] for k,r in rs.items()},failure_codes={k:r['failure']['code'] if r['failure'] else None for k,r in rs.items()},comparisons=cmp,balances=bal,independent_quadrature=quad,last_accepted_state_retained=retention,tracking=rs['fine']['tracking'])
        results.append(rs['fine'])
        print(ident,checks[-1]['passed'],'full' if full else 'prefix',flush=True)
    # Source/static descending Jacobian keeps the unobservable integral/motion mode.
    cfg=next(c['cfg'] for c in cases if c['id']=='desc-pi-plus').copy();cfg['z']=cfg['z'].copy();cfg['z'][3]=1.1
    z=np.array(cfg['z']);phase={'target':cfg['m']*G,'mode':'PI'}
    # At u=a source activation is one-sided; derive each branch's same physical Jacobian.
    J=jacobian(0,z,cfg,phase)[:5,:5];a=z[2];tau_d=.04/(.5+1.5*a);tau_a=.01*(.5+1.5*a)
    eig={}
    for label,tau in [('activation',tau_a),('deactivation',tau_d)]:
        j=J.copy();j[2,:]*=tau_d/tau;values=np.linalg.eigvals(j);eig[label]=[{'real':float(v.real),'imag':float(v.imag)} for v in values]
        record('descending-modes-'+label,any(abs(v)<1e-7 for v in values) and any(v.real>0 for v in values),eigenvalues=eig[label],static_stiffness_N_m=100/.1*(a*C['active'].value(1.1,True)+C['passive'].value(1.1,True)),tau_s=tau)
    pulse=next(r for r in results if r['cfg']['caseName']=='pulse');r=min(pulse['history'],key=lambda r:abs(r['t']-.14))
    record('weight-command-retains-motion',abs(r['target']-.5*G)<1e-10 and r['z'][1]>1e-5,time_s=r['t'],force_N=r['FT'],weight_N=.5*G,velocity_m_s=r['z'][1],acceleration_m_s2=r['acceleration'])
    # Bind tests to exact executed authored source, protocol and frozen controls.
    paths=['education/web/vertical-force-model.js','education/tools/vertical_force_reference.py','education/tools/audit_vertical_force.py','education/data/vertical-force-command-v1/protocol.json','education/data/millard-reference-v1/review/native-controls.json']
    receipt=dict(passed=all(c['passed'] for c in checks),checks=checks,source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},full_presets=sum(r['failure'] is None for r in results),prefix_only_presets=[c['id'] for c,r in zip(cases,results) if r['failure']],gains=dict(kp=P['kp'],ki_per_s=P['ki_per_s']),all_negative_eigenvalue_acceptance=False)
    (OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if not receipt['passed']:raise SystemExit('FAILED: inspect retained validation.json; no budgets relaxed')

if __name__=='__main__':main()

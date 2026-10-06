#!/usr/bin/env python3
"""Algebra and frozen-state diagnostics ONLY: no time integration, event
localization, continuation implementation, accepted advancement or projection.
"""
from pathlib import Path
import json,hashlib,sys
import sympy as S
import numpy as np
from vertical_force_reference import ROOT,P,C,output,activation_rhs

OUT=ROOT/'education/data/antiwindup-continuation-analysis-v1/review'
INPUT=ROOT/'education/data/vertical-force-command-v1/review'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    d,k,eta=S.symbols('d k eta',nonzero=True);theta=-d/k
    identities={
        'unoriented_tangency':S.simplify(theta*(d+k)+(1-theta)*d),
        'oriented_tangency':S.simplify(eta*(d+theta*k)),
        'integrator_tangent_rate':S.simplify(theta*k+d),
        'normal_jump':S.simplify(eta*(d+k)-eta*d-eta*k),
    }
    Fa,Fp,Fd,Ft,w,lfdot=S.symbols('Fa Fp Fd Ft w lfdot')
    total=Fp*lfdot+Ft*(-w-lfdot)+Ft*w
    identities['mechanical_work']=S.simplify((total-(-Fa*lfdot-Fd*lfdot)).subs(Ft,Fa+Fp+Fd))
    assert all(v==0 for v in identities.values()),identities
    checks=[];records=[];bindings={}
    for case in ['high','mass-1']:
        B,orientation=(1,1) if case=='high' else (.01,-1)
        paths=[INPUT/f'{case}-{m}.json' for m in ['coarse','fine','DOP853','Radau']]
        paths += [INPUT/'pre-surface-guard'/f'{case}-{m}.json' for m in ['DOP853','Radau'] if (INPUT/'pre-surface-guard'/f'{case}-{m}.json').exists()]
        for path in paths:
            result=json.loads(path.read_text());z=np.array(result['failure']['acceptedState']);row=result['history'][-1];o=output(z,result['cfg'],dict(target=row['target']))
            kt=100/.2*C['tendon'].value(o['s'],True)
            edot=kt*(z[1]+o['v'])/100;normal_frozen=P['kp']*edot;kval=P['ki_per_s']*o['e'];normal_integrating=normal_frozen+kval;weight=-normal_frozen/kval
            nu_on=orientation*normal_integrating;nu_off=orientation*normal_frozen
            # One-sided boundary fields at the same mechanical p. No state is
            # reset to the boundary. Since h is independent of a, its normal
            # derivative is unchanged by evaluating the activation limit u=B.
            physical=np.array([z[1],o['acceleration'],activation_rhs(z[2],B),10*o['v']])
            def h(probe):
                ft=100*C['tendon'].value((result['cfg']['L0']-probe[0]-.1*probe[3])/.2)
                return result['cfg']['ub']+P['kp']*(row['target']-ft)/100+probe[4]-B
            fd_errors={}
            for mode,Idot,exact in [('integrating',kval,normal_integrating),('frozen',0,normal_frozen)]:
                vector=np.r_[physical,Idot];eps=1e-7
                estimate=(h(z[:5]+eps*vector)-h(z[:5]-eps*vector))/(2*eps)
                fd_errors[mode]=abs(estimate-exact)
            root_slope=100*(z[2]*C['active'].value(z[3])*C['velocity'].value(o['v'],True)+.1)
            passed=bool(nu_on>0>nu_off and 0<weight<1 and root_slope>=10-1e-12 and abs(o['residual'])<=P['budgets']['force_N'] and max(fd_errors.values())<=1e-6)
            assert passed,(path,fd_errors)
            key=str(path.relative_to(ROOT));bindings[key]=hashlib.sha256(path.read_bytes()).hexdigest()
            stage=output(result['failure']['failedStageState'],result['cfg'],dict(target=row['target']))
            records.append(dict(input=key,case=case,accepted_time_s=result['acceptedTime'],failed_stage_time_s=result['failure'].get('failedStageTime'),failed_stage_raw=stage['uraw'],failed_stage_oriented_h=orientation*(stage['uraw']-B),failed_stage_force_residual_N=stage['residual'],failed_stage_is_not_an_accepted_orbit_point=True,failed_code=result['failure']['code'],boundary=B,orientation=orientation,raw=o['uraw'],unoriented_h=o['uraw']-B,e=o['e'],edot_per_s=edot,kt_N_per_m=kt,normal_integrating_per_s=normal_integrating,normal_frozen_per_s=normal_frozen,oriented_integrating_per_s=nu_on,oriented_frozen_per_s=nu_off,formal_integrating_weight=weight,formal_tangent_Idot_per_s=-normal_frozen,velocity_root_derivative_N=root_slope,force_residual_N=o['residual'],directional_derivative_errors_per_s=fd_errors,linear_event_time_diagnostic_s=result['acceptedTime']-(o['uraw']-B)/normal_integrating,linear_event_time_is_not_a_localized_or_qualified_event=True,accepted_state_modified=False))
            checks.append(dict(name=key,passed=passed))
    for case in ['high','mass-1']:
        for m in ['coarse','fine']:
            path=INPUT/'pre-surface-guard'/f'{case}-{m}.json'
            bindings[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    sources=['education/tools/check_antiwindup_continuation_analysis.py','education/tools/vertical_force_reference.py','education/web/vertical-force-model.js','education/data/vertical-force-command-v1/protocol.json','education/data/millard-reference-v1/review/native-controls.json']
    receipt=dict(passed=True,scope='Evaluation-only symbolic/local diagnostics, not a controller or trajectory solver',symbolic_residuals={n:str(v) for n,v in identities.items()},checks=checks,records=records,input_sha256=bindings,source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},frozen_commit='504585b962fc4d1a5ad359d24e902d86cc3d7c4b',new_trajectories=0,new_qualified_trajectories=0,continuation_implemented=False,physics_gains_tolerances_events_changed=False,finite_difference_check_budget_per_s=1e-6,finite_difference_budget_is_not_a_trajectory_acceptance_gate=True)
    (OUT/'algebra-and-frozen-state-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS',len(identities),'symbolic identities;',len(checks),'frozen-state diagnostics; zero trajectories advanced')
    for case in ['high','mass-1']:
        r=next(r for r in records if r['case']==case and '/pre-surface-guard/' in r['input'] and r['input'].endswith('-Radau.json'))
        print(case,'near-boundary',r['accepted_time_s'],'on/off',r['normal_integrating_per_s'],r['normal_frozen_per_s'],'theta',r['formal_integrating_weight'],'tangent I_dot',r['formal_tangent_Idot_per_s'])

if __name__=='__main__':main()

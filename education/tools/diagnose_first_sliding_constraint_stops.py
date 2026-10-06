#!/usr/bin/env python3
"""Read-only reevaluation of already rejected states; no solver or acceptance."""
import hashlib
import json
import inspect
import numpy as np
import scipy
from scipy.integrate._ivp.common import select_initial_step
from first_sliding_segment_engine import DATA,Source,native_field,independent_field,dump_new,verify_bindings


def main():
    p=verify_bindings();source=Source();records={}
    try:
        for key in p['entry_inputs']:
            path=DATA/'review'/('mass-1-'+key.replace('/','-')+'.json');r=json.loads(path.read_text())
            if not r['failure']:continue
            z=np.array(r['failure']['failedStageState']);t=r['failure']['failedStageTime'];cfg=r['cfg']
            native,nr=native_field(z,cfg,source,True);ref,rr=independent_field(z,cfg,True)
            old=np.array(r['entry_state']);entry=r['candidate']['t'];o0,rate0=native_field(old,cfg,source,True)
            euler=old+(t-entry)*rate0
            is_euler=bool(np.array_equal(euler,z))
            origin='RK4 first midpoint Euler predictor' if r['method'].startswith('RK4') else 'adaptive constructor initial-step selection Euler RHS probe'
            if not is_euler:origin='RHS probe; Euler correspondence is not bitwise exact'
            records[key]=dict(result_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),failed_t=t,accepted_t=r['acceptedTime'],
                              rejected_state=z.tolist(),native_H=native['H'],independent_H=ref['H'],constraint_gate=1e-9,
                              original_failure=r['failure'],role=origin,entry_plus_dt_initial_RHS_bitwise_match=is_euler,
                              Euler_predictor_max_difference=float(max(abs(euler-z))),time_offset_from_entry_s=t-entry,
                              native_force_residual_N=native['residual'],independent_force_residual_N=ref['residual'],
                              native_normal_on=native['normal_on'],native_normal_off=native['normal_off'],theta=native['theta'],
                              outward_error=-native['e'],g=.01-z[2],q=z[3],tendon_s=native['s'],
                              force_and_strict_residence_domain_pass=bool(abs(native['residual'])<=1e-7 and native['normal_on']>1e-8 and native['normal_off']<-1e-8 and native['e']<0 and 0<native['theta']<1 and .01-z[2]<-1e-13 and z[3]>.4441 and native['s']>1),
                              constraint_exceeds_original_gate=abs(native['H'])>1e-9,accepted=False,state_advanced=False)
            print(key,'rejected H',native['H'],'ref H',ref['H'],'Euler exact',is_euler,'force/sign valid',records[key]['force_and_strict_residence_domain_pass'],flush=True)
        dump_new(DATA/'review/constraint-stop-diagnosis.json',dict(scope='Read-only already rejected state diagnosis; no salvage/retry/projection or new ODE step',records=records,
            source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest(),scipy_version=scipy.__version__,
            select_initial_step_source_sha256=hashlib.sha256(inspect.getsource(select_initial_step).encode()).hexdigest(),
            no_constitutive_assumption_changed=True,physical_failure_retries=0,accepted_states_added=0,new_ODE_steps=0))
    finally:source.close()


if __name__=='__main__':main()

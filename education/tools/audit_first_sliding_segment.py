#!/usr/bin/env python3
"""Independent dense/stage/ledger replay and all-pair absolute-time checks."""
import hashlib
import itertools
import json
import math
import numpy as np
from first_sliding_segment_engine import DATA,ROOT,verify_bindings,dump_new,STATE_NAMES,STATE_GATES,WITNESSES
from vertical_force_reference import output as reference_output, activation_rhs,C,P


def polynomial(record,t):
    u=(t-record['left_s'])/(record['right_s']-record['left_s']);old=np.array(record['y_old'])
    if record['kind']=='RK4-cubic':
        co=np.array(record['coefficients']);return old+u*(co[0]+u*(co[1]+u*co[2]))
    if record['kind']=='Radau-power':
        power=u;value=old.copy()
        for coefficient in np.array(record['Q']).T:value+=coefficient*power;power*=u
        return value
    if record['kind']=='DOP853-nested':
        value=np.zeros_like(old)
        for index,coefficient in enumerate(record['F'][::-1]):value=(value+np.array(coefficient))*(u if index%2==0 else 1-u)
        return old+value
    raise ValueError('Unknown polynomial')


def decode(x,r,mode):
    if r['representation']=='reduced-independent' and mode=='sliding':
        ft=100*C['tendon'].value((r['cfg']['L0']-x[0]-.1*x[3])/.2)
        return np.concatenate((x[:4],[.01-r['cfg']['ub']-.4*(r['cfg']['target']-ft)/100],x[4:]))
    return np.array(x)


def independent(z,cfg,sliding):
    o=reference_output(z,cfg,{'target':cfg['target']});d=.4*500*C['tendon'].value(o['s'],True)*(z[1]+o['v'])/100;k=8*o['e']
    if sliding:o['adot']=activation_rhs(z[2],.01)
    I_rate=-d if sliding else k
    rate=np.array([z[1],o['acceleration'],o['adot'],10*o['v'],I_rate,o['Pactive'],o['D'],o['loadPower'],o['fiberPower'],o['tendonPower'],o['FT']-cfg['m']*P['gravity_m_per_s2']])
    return o,d,k,rate


def work(z,base,cfg):
    s=(cfg['L0']-z[0]-.1*z[3])/.2;s0=(cfg['L0']-base[0]-.1*base[3])/.2
    ef=10*C['passive'].integral(base[3],z[3]);et=20*C['tendon'].integral(s0,s)
    el=cfg['m']*((z[1]**2-base[1]**2)/2+P['gravity_m_per_s2']*(z[0]-base[0]))
    active,diss,load,fiber,tendon,impulse=np.array(z[5:])-base[5:]
    return np.abs([ef-fiber,et-tendon,el-load,ef+et+el-active+diss,cfg['m']*(z[1]-base[1])-impulse,active-diss-load-fiber-tendon])


def audit_run(r):
    original=json.loads((ROOT/r['incoming_path']).read_text());cfg=r['cfg'];issues=[]
    if hashlib.sha256((ROOT/r['incoming_path']).read_bytes()).hexdigest()!=r['incoming_sha256'] or cfg!=original['cfg']:issues.append('incoming-binding')
    c=r['candidate'];incoming=np.array(c['state']);entry=np.array(r['entry_state']);h=r['handoff']
    ten=np.r_[incoming[:4],incoming[5:]];decoded_ten=np.r_[entry[:4],entry[5:]]
    if not np.array_equal(ten,decoded_ten) or entry[4]-incoming[4]!=h['signed_delta_I'] or abs(h['signed_delta_I'])>1e-9:issues.append('finite-handoff')
    if r['representation']=='full-source' and not np.array_equal(incoming,entry):issues.append('full-I-not-retained')
    if r['representation']=='reduced-independent' and h['exact_eleven_coordinate_continuity']:issues.append('false-exact-continuity')
    if [e['type'] for e in r['events']]!=['activation-equality','ordinary-outward','ordinary-inward','sliding-entry']:issues.append('event-order')
    history={round(row['t'],12):row for row in r['history']};grid=[float(k*.001) for k in range(264)]
    missing=[t for t in grid+WITNESSES if round(t,12) not in history]
    complete=bool(r['failure'] is None and r['acceptedTime']==.263 and not missing and c['accepted'])
    if r['completed']!=complete:issues.append('completion-label')
    cumulative=np.zeros(6);segment=np.zeros(6);maxforce=maxnormal=maxtangent=maxH=maxrate=dense_error=0.
    quad=np.array(original['independent_quadrature']['integrals']);entry_quad=None;nodes,weights=np.polynomial.legendre.leggauss(8)
    counts=dict(dense_points=0,accepted_ODE_stages=0,GL8_points=0)
    def check_point(z,t,mode,stored=None,stage=False):
        nonlocal cumulative,segment,maxforce,maxnormal,maxtangent,maxH,maxrate
        sliding=mode=='sliding';o,d,k,rate=independent(z,cfg,sliding)
        cumulative=np.maximum(cumulative,work(z,np.array(cfg['z']),cfg))
        if sliding:segment=np.maximum(segment,work(z,entry,cfg))
        maxforce=max(maxforce,abs(o['residual']))
        if sliding:
            theta=-d/k if k else float('nan');H=.01-o['uraw'];maxH=max(maxH,abs(H))
            if not (o['e']<0 and -(d+k)>1e-8 and -d < -1e-8 and 0<theta<1 and .01-z[2]<-1e-13 and .01<z[2]<1):issues.append('strict-residence-or-additional-guard')
            if abs(H)>1e-9:issues.append('independent-constraint')
        else:
            if .01-o['uraw']>1e-9 or o['u']-z[2]>-1e-13:issues.append('incoming-prefix-side')
        if stored:
            maxnormal=max(maxnormal,abs(stored['normal_on']+d+k),abs(stored['normal_off']+d))
            if 'FT' in stored:maxforce=max(maxforce,abs(stored['FT']-o['FT']))
            if sliding:
                Idot=stored['rate_full'][4] if 'rate_full' in stored else stored['Idot'];maxtangent=max(maxtangent,abs(d+Idot))
            if stage:maxrate=max(maxrate,float(np.max(abs(rate-np.array(stored['rate_full'])))))
        return rate
    # Every new accepted polynomial, stage and GL8 point is replayed. Historical
    # source-bound incoming history is checked for balances/normals separately.
    for interval in r['accepted_intervals']:
        left,right=interval['start'],interval['end'];mode=interval['mode'];record=interval['dense']
        if record['left_s']!=left or right>record['right_s'] or right<=left:issues.append('dense-domain-custody')
        for t in sorted(set([left,(left+right)/2,right]+[left+(right-left)*(node+1)/2 for node in nodes])):
            z=decode(polynomial(record,t),r,mode);check_point(z,t,mode);counts['dense_points']+=1
        for stage in interval['stages']:
            z=decode(np.array(stage['x']),r,mode)
            if not np.array_equal(z,np.array(stage['z'])):issues.append('stage-decoding')
            check_point(z,stage['t'],mode,stage,True);counts['accepted_ODE_stages']+=1
        increment=np.zeros(6)
        for node,weight in zip(nodes,weights):
            t=left+(right-left)*(node+1)/2;z=decode(polynomial(record,t),r,mode)
            rate=check_point(z,t,mode);increment+=(right-left)*weight/2*rate[5:11];counts['GL8_points']+=1
        if np.max(abs(increment-np.array(interval['GL8_increment'])))>1e-12:issues.append('GL8-receipt-replay')
        quad+=increment
        if mode=='incoming':entry_quad=quad.copy()
        for row in interval['guard_samples']:
            z=decode(polynomial(record,row['t']),r,mode);dense_error=max(dense_error,float(np.max(abs(z-np.array(row['z'])))))
        for row in r['history']:
            if left<row['t']<=right:
                z=decode(polynomial(record,row['t']),r,mode);dense_error=max(dense_error,float(np.max(abs(z-np.array(row['z'])))))
    for row in r['history']:
        z=np.array(row['z']);o,d,k,rate=independent(z,cfg,row['mode']=='sliding')
        cumulative=np.maximum(cumulative,work(z,np.array(cfg['z']),cfg))
        maxforce=max(maxforce,abs(o['residual']),abs(o['FT']-row['FT']))
        maxnormal=max(maxnormal,abs(row['normal_on']+d+k),abs(row['normal_off']+d))
        if row['mode']=='sliding':check_point(z,row['t'],'sliding',row)
    final=np.array(r['acceptedState']);quaderror=abs(quad-final[5:11]);segmentquaderror=abs(quad-entry_quad-(final[5:11]-entry[5:11]))
    if not np.all(cumulative<=np.array([1e-5]*4+[1e-7,1e-5])) or not np.all(segment<=np.array([1e-5]*4+[1e-7,1e-5])):issues.append('work-impulse-gate')
    if not np.all(quaderror<=np.array([1e-5]*5+[1e-7])) or not np.all(segmentquaderror<=np.array([1e-5]*5+[1e-7])):issues.append('quadrature-gate')
    if maxforce>1e-7 or maxnormal>1e-8 or maxtangent>1e-8 or maxrate>1e-8 or maxH>1e-9 or dense_error>1e-12:issues.append('force-normal-tangent-RHS-constraint-dense-gate')
    rejected=[]
    for probe in r['failed_probes']:
        if not probe.get('failure') or 'z' not in probe:continue
        z=np.array(probe['z']);o,d,k,rate=independent(z,cfg,probe.get('mode')=='sliding' or r['candidate']['accepted'])
        rejected.append(dict(t=probe['t'],code=probe['failure'],independent_H=.01-o['uraw'],accepted=False))
    return dict(accepted_prefix_audit_passed=not issues,issues=sorted(set(issues)),segment_completed=complete,
                missing_absolute_witnesses=missing,cumulative_balance_maxima=cumulative.tolist(),segment_balance_maxima=segment.tolist(),
                cumulative_GL8_errors=quaderror.tolist(),segment_GL8_errors=segmentquaderror.tolist(),max_force_N=maxforce,
                max_normal_disagreement_per_s=maxnormal,max_tangent_residual_per_s=maxtangent,max_H=maxH,
                max_RHS_difference=maxrate,max_dense_replay_error=dense_error,counts=counts,rejected_probe_replay=rejected,qualified=False)


def comparison(a,b):
    times=[float(k*.001) for k in range(264)]+WITNESSES[:-1]
    ma={round(row['t'],12):row for row in a['history']};mb={round(row['t'],12):row for row in b['history']}
    missing=[t for t in times if round(t,12) not in ma or round(t,12) not in mb]
    available=[t for t in times if t not in missing];values=[]
    for t in available:
        x,y=ma[round(t,12)],mb[round(t,12)];values.append([*(np.array(x['z'][:4])-y['z'][:4]),x['FT']-y['FT'],x['z'][4]-y['z'][4],x['uraw']-y['uraw']])
    values=np.array(values);maximum=np.max(abs(values),axis=0)
    dt=a['candidate']['t']-b['candidate']['t']
    return dict(passed=bool(not missing and a['completed'] and b['completed'] and np.all(maximum<=STATE_GATES) and abs(dt)<=2e-6),
                prefix_state_agreement=bool(np.all(maximum<=STATE_GATES)),missing_absolute_times=missing,
                available_absolute_times=available,max_errors=dict(zip(STATE_NAMES,maximum.tolist())),
                margins=dict(zip(STATE_NAMES,(STATE_GATES-maximum).tolist())),signed_entry_time_difference_s=dt,event_margin_s=2e-6-abs(dt),
                signed_witnesses={n:dict(t=available[int(np.argmax(abs(values[:,j])))],signed_error=float(values[int(np.argmax(abs(values[:,j]))),j])) for j,n in enumerate(STATE_NAMES)},event_alignment=False)


def main():
    p=verify_bindings();results={key:json.loads((DATA/'review'/('mass-1-'+key.replace('/','-')+'.json')).read_text()) for key in p['entry_inputs']}
    runs={key:audit_run(r) for key,r in results.items()}
    pairs={a+' vs '+b:comparison(results[a],results[b]) for a,b in itertools.combinations(results,2)}
    passed=all(v['segment_completed'] and v['accepted_prefix_audit_passed'] for v in runs.values()) and len(pairs)==66 and all(c['passed'] for c in pairs.values())
    receipt=dict(passed=passed,status='bounded-exploratory-checks-pass-pending-independent-review' if passed else 'unqualified-retained-failures-or-partial-segments',runs=runs,comparisons=pairs,
                 required_cells=12,completed_cells=sum(r['completed'] for r in results.values()),required_pairs=66,
                 input_sha256={key:hashlib.sha256((DATA/'review'/('mass-1-'+key.replace('/','-')+'.json')).read_bytes()).hexdigest() for key in results},
                 source_sha256=p['source_sha256'],qualified=False,anatomical_qualification=False,fourth_order_qualification=False,
                 full_combined_external_raw_replay_complete=False,historical_activation_external_raw_replay_complete=False,hidden_root_theorem=False)
    dump_new(DATA/'review/audit.json',receipt)
    print('AUDIT completed',receipt['completed_cells'],'of12; accepted-prefix checks',all(r['accepted_prefix_audit_passed'] for r in runs.values()),'all66complete comparisons',all(c['passed'] for c in pairs.values()),'overall',passed,flush=True)
    for key,r in results.items():print(key,r['acceptedTime'],r['failure']['code'] if r['failure'] else 'endpoint',runs[key]['issues'],flush=True)


if __name__=='__main__':main()

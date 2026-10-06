#!/usr/bin/env python3
"""Supplemental matched-witness/constraint diagnostics and honest static render."""
import hashlib
import itertools
import json
import math
import numpy as np
from first_sliding_segment_engine import DATA,verify_bindings,dump_new,WITNESSES,STATE_GATES,STATE_NAMES


def post_compare(a,b):
    ma={round(row['t'],12):row for row in a['history']};mb={round(row['t'],12):row for row in b['history']}
    missing=[t for t in WITNESSES if round(t,12) not in ma or round(t,12) not in mb]
    if missing:return dict(passed=False,missing_absolute_witnesses=missing,samples=0,max_errors=None)
    values=[]
    for t in WITNESSES:
        x,y=ma[round(t,12)],mb[round(t,12)]
        values.append(np.r_[np.array(x['z'][:4])-y['z'][:4],x['FT']-y['FT'],x['z'][4]-y['z'][4],x['uraw']-y['uraw']])
    values=np.array(values);maximum=np.max(abs(values),axis=0)
    return dict(passed=bool(a['completed'] and b['completed'] and np.all(maximum<=STATE_GATES)),samples=4,times=WITNESSES,
                signed_samples=values.tolist(),max_errors=dict(zip(STATE_NAMES,maximum.tolist())),
                margins=dict(zip(STATE_NAMES,(STATE_GATES-maximum).tolist())),missing_absolute_witnesses=[])


def render(results,audit,diagnosis):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    keys=list(results);positions=np.arange(len(keys));fig,(left,right)=plt.subplots(1,2,figsize=(14,8),sharey=True,layout='constrained')
    labels=[]
    for j,key in enumerate(keys):
        r=results[key];start=r['candidate']['t']*1000;end=r['acceptedTime']*1000
        complete=r['completed'];color='#087f8c' if complete else '#b94724'
        left.plot([start,end],[j,j],color=color,lw=3)
        left.plot(start,j,'o',color='#666',ms=4)
        left.plot(end,j,'o' if complete else 'x',color=color,ms=7)
        if not complete:left.text(262.42,j,'constraint stop',color=color,va='center',fontsize=10)
        checked=max(audit['runs'][key]['max_H'],1e-19)
        right.plot(checked,j,'o',color='#087f8c',ms=6)
        if key in diagnosis['records']:
            rejected=abs(diagnosis['records'][key]['native_H'])
            right.plot(rejected,j,'o',mfc='none',mec='#b94724',mew=2,ms=8)
        short=key.replace('full-source/','Full  ').replace('reduced-independent/','Reduced  ').replace('RK4-0.000025','RK4 25 µs').replace('RK4-0.00005','RK4 50 µs').replace('RK4-0.0001','RK4 100 µs').replace('RK4-0.0002','RK4 200 µs')
        labels.append(short)
    left.set(yticks=positions,yticklabels=labels,xlim=(262.0,263.08),xlabel='Absolute time (ms)',title='Accepted entry → retained endpoint')
    left.invert_yaxis();left.axvline(263,color='#444',ls=':',lw=1.2);left.grid(axis='x',alpha=.2)
    right.set(xscale='log',xlim=(2e-19,1e-6),xlabel='Magnitude of checked H',title='Constraint checks and rejected probes')
    right.axvline(1e-9,color='#444',ls=':',lw=1.5,label='Unchanged gate 1e−9')
    right.plot([],[],'o',color='#087f8c',label='Largest accepted-trial check')
    right.plot([],[],'o',mfc='none',mec='#b94724',mew=2,label='Rejected probe; never accepted')
    right.legend(loc='lower right',fontsize=9);right.grid(axis='x',alpha=.2)
    fig.suptitle('First sliding segment: 9/12 endpoints; required matrix remains unqualified',fontsize=16)
    fig.supxlabel('Finite reduced I/raw adjustment disclosed. Samples provide no hidden-root theorem.',fontsize=10)
    for ext in ['png','svg']:fig.savefig(DATA/'review'/('segment-outcome.'+ext),dpi=170)
    svg=DATA/'review/segment-outcome.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)


def main():
    p=verify_bindings();results={key:json.loads((DATA/'review'/('mass-1-'+key.replace('/','-')+'.json')).read_text()) for key in p['entry_inputs']}
    audit=json.loads((DATA/'review/audit.json').read_text());diagnosis=json.loads((DATA/'review/constraint-stop-diagnosis.json').read_text())
    pairs={a+' vs '+b:post_compare(results[a],results[b]) for a,b in itertools.combinations(results,2)}
    associations={}
    for key in diagnosis['records']:
        r=results[key];batch=next(v for v in r['failed_probes'] if 'stages' in v);first=batch['stages'][0]
        if r['method'].startswith('RK4'):
            t=r['candidate']['t'];h=min(float(r['method'].split('-')[1]),.263-t,(math.floor((t+1e-10)/.001)+1)*.001-t);dt=h/2;role='RK4 first midpoint b=old+(h/2)*initial_RHS'
        else:dt=r['failure']['failedStageTime']-r['candidate']['t'];role='Adaptive constructor initial-step selection Euler RHS probe'
        proposed=np.array(r['entry_state'])+dt*np.array(first['rate_full']);failed=np.array(r['failure']['failedStageState'])
        associations[key]=dict(role=role,declared_formula_offset_s=dt,recorded_initial_stage_time=first['t'],
                               bitwise_matches_recorded_initial_rate_formula=bool(np.array_equal(proposed,failed)),
                               max_formula_difference=float(max(abs(proposed-failed))),accepted=False,
                               elapsed_time_subtraction_offset_s=r['failure']['failedStageTime']-r['candidate']['t'])
    adjacency={}
    for rep,methods in [('full-source',['RK4-0.0001','RK4-0.00005','RK4-0.000025']),('reduced-independent',['RK4-0.0002','RK4-0.0001','RK4-0.00005','RK4-0.000025'])]:
        differences=[]
        for a,b in zip(methods,methods[1:]):
            c=post_compare(results[rep+'/'+a],results[rep+'/'+b]);differences.append(c['max_errors']);adjacency[rep+':'+a+'/'+b]=c
        for index in range(len(differences)-1):
            adjacency[rep+':ratio-'+str(index)]=dict(ratios={n:differences[index][n]/differences[index+1][n] if differences[index+1][n]!=0 else None for n in STATE_NAMES},scope='Absolute four-witness finite differences with inherited incoming errors; not order qualification')
    completed_pairs=[c for c in pairs.values() if c['passed']]
    worst={n:max(c['max_errors'][n] for c in completed_pairs) for n in STATE_NAMES}
    summary=dict(required_cells=12,completed_cells=9,required_pairs=66,complete_post_witness_pairs_passed=sum(c['passed'] for c in pairs.values()),
                 required_matrix_passed=False,qualified=False,post_absolute_witnesses_s=WITNESSES,post_comparisons=pairs,
                 completed_pair_worst_errors=worst,completed_pair_remaining_margins={n:float(STATE_GATES[j]-worst[n]) for j,n in enumerate(STATE_NAMES)},
                 adjacent_RK_differences_and_ratios=adjacency,rejected_probe_formula_associations=associations,
                 accepted_ODE_RHS_evaluations=sum(r['counts']['accepted_ODE_stages'] for r in audit['runs'].values()),
                 ODE_RHS_evaluation_semantics='Counts include initialization/dense/error-control RHS probes attached to accepted trials; records remain accepted:false and are not accepted orbit points',
                 maximum_checked_work_J=max(max(r['cumulative_balance_maxima'][:4]+r['cumulative_balance_maxima'][5:]) for r in audit['runs'].values()),
                 maximum_impulse_error_N_s=max(r['cumulative_balance_maxima'][4] for r in audit['runs'].values()),
                 anatomical_qualification=False,fourth_order_qualification=False,hidden_root_theorem=False,
                 full_combined_external_raw_replay_complete=False,historical_activation_external_raw_replay_complete=False,
                 analysis_source_sha256=hashlib.sha256(open(__file__,'rb').read()).hexdigest())
    dump_new(DATA/'review/matched-witness-summary.json',summary);render(results,audit,diagnosis)
    print('Matched post-entry witnesses:36/66 complete pairs pass; nine endpoints; no matrix qualification',flush=True)
    print('Worst completed-pair errors',worst,flush=True)
    print('Rejected formula associations',associations,flush=True)


if __name__=='__main__':main()

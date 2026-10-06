#!/usr/bin/env python3
"""Frozen activation crossing-step/propagation comparisons on absolute time."""
import json,hashlib,itertools
import numpy as np
from run_activation_equality_diagnostic import ROOT,DATA,OUT,PROTOCOL,verify_inputs
from run_ordinary_crossing_consistency import replay_dense
from audit_filippov_bounded_experiment import balances
from vertical_force_reference import output as reference_output

NAMES=['y_m','w_m_per_s','a','q','FT_N','I','raw']

def grid_map(r):return {round(x['t'],9):x for x in r['history'] if abs(x['t']/.001-round(x['t']/.001))<1e-7}
def difference(x,y):return np.r_[np.array(x['z'][:4])-y['z'][:4],x['FT']-y['FT'],x['z'][4]-y['z'][4],x['uraw']-y['uraw']]
def compare(a,b):
    ma,mb=grid_map(a),grid_map(b);result={}
    for segment,(left,right) in PROTOCOL['windows'].items():
        times=[t for t in sorted(ma.keys()&mb.keys()) if left-1e-12<=t<=right+1e-12]
        if not times:result[segment]=dict(samples=0,missing=True);continue
        values=np.array([difference(ma[t],mb[t]) for t in times]);maximum=np.max(np.abs(values),axis=0);witness={}
        for name,j in [('I',5),('raw',6),('a',2)]:
            index=int(np.argmax(np.abs(values[:,j])));t=times[index];v=values[index]
            witness[name]=dict(t=t,absolute_error=abs(float(v[j])),signed_I=float(v[5]),signed_raw=float(v[6]),signed_force_term_to_raw=float(-.004*v[4]),signed_a=float(v[2]),raw_identity_residual=float(v[6]-v[5]+.004*v[4]))
        result[segment]=dict(samples=len(times),max_errors=dict(zip(NAMES,maximum.tolist())),witnesses=witness,margins=dict(zip(NAMES,(np.array(PROTOCOL['state_gates'])-maximum).tolist())),all_state_gates_passed=bool(np.all(maximum<=PROTOCOL['state_gates'])))
    return dict(windows=result,all_windows_passed=all(x.get('all_state_gates_passed',False) for x in result.values()),same_absolute_time=True,event_alignment=False,sliding_qualification=False)

def dense_row(r,t):
    if t==0:z=np.array(r['history'][0]['z'])
    else:
        intervals=[i for i in r['accepted_intervals'] if i['start']-1e-14<=t<=i['end']+1e-14]
        if not intervals:raise ValueError('Requested crossing-step time outside accepted dense intervals')
        interval=intervals[-1];z=replay_dense(interval['dense'],t)
    o=reference_output(z,r['cfg'],{'target':r['cfg']['target']})
    return dict(z=z.tolist(),FT=o['FT'],uraw=o['uraw'])

def crossing_compare(a,b):
    # Each RK method's nominal crossing step, fixed by its original time lattice.
    h=float(a['method'].split('-')[1]);event=a['activation_event'];left=np.floor(event['t']/h)*h;right=left+h
    if min(a['acceptedTime'],b['acceptedTime'])<right-1e-12:return dict(left_s=float(left),right_s=float(right),missing=True,reason='Crossing-step endpoint exceeds accepted prefix; no interpolation or retry')
    start=difference(dense_row(a,left),dense_row(b,left));end=difference(dense_row(a,right),dense_row(b,right));gate=np.array(PROTOCOL['state_gates'])
    return dict(left_s=float(left),right_s=float(right),left_signed_differences=dict(zip(NAMES,start.tolist())),right_signed_differences=dict(zip(NAMES,end.tolist())),crossing_step_signed_error_change=dict(zip(NAMES,(end-start).tolist())),right_absolute_errors=dict(zip(NAMES,np.abs(end).tolist())),right_margins=dict(zip(NAMES,(gate-np.abs(end)).tolist())),scope='Fixed absolute nominal RK crossing-step endpoints on actual accepted polynomials; subtracting inherited start error never corrects a state or acceptance check')

def event_check(r):
    c=r['activation_event']
    if not c:return dict(passed=False,missing=True)
    aux=r['activation_auxiliaries'][0];error=float(np.max(np.abs(replay_dense(aux['dense'],c['t'])-c['x'])))
    check=dict(passed=error<=1e-12,polynomial_state_error=error,bracket_width_s=c['bracket'][1]-c['bracket'][0],g=c['g'],normals=c['one_sided_normals_per_s'],rate_difference_at_localized_state=c['one_sided_rates']['activation']-c['one_sided_rates']['deactivation'],projected=False,accepted=c['accepted'])
    if r['policy']=='split':
        saved=[x for x in r['history'] if x['t']==c['t']];following=[i for i in r['accepted_intervals'] if i['start']==c['t']]
        if len(saved)!=1 or len(following)!=1:return dict(passed=False,missing_restart=True)
        check.update(saved_state_error=float(np.max(np.abs(np.array(saved[0]['z'])-c['x']))),restart_state_error=float(np.max(np.abs(np.array(following[0]['dense']['y_old'])-c['x']))))
        check['passed'] &= check['saved_state_error']==0 and check['restart_state_error']==0
    return check

def render(receipt):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(12,7),layout='constrained')
    for row,window in enumerate(PROTOCOL['windows']):
        for col,rep in enumerate(PROTOCOL['representations']):
            ax=axes[row,col]
            for policy,color in [('control','#b34a29'),('split','#126e82')]:
                for reference,style in [('DOP853','-'),('Radau','--')]:
                    pairs=[policy+'/'+rep+'/'+m+' vs split/'+rep+'/'+reference for m in PROTOCOL['methods'][:4]]
                    values=[max(receipt['comparisons'][pair]['windows'][window].get('max_errors',{}).get('I',float('nan')),1e-17) for pair in pairs]
                    ax.plot([200,100,50,25],values,'o'+style,color=color,label=policy+' versus split '+reference)
            ax.axhline(1e-9,color='#555',ls=':');ax.set(xscale='log',yscale='log',xticks=[25,50,100,200],xticklabels=['25','50','100','200'],xlabel='RK4 step (µs)',ylabel='Max |ΔI| on common 1 ms grid',title=rep+' / '+window);ax.grid(alpha=.2);ax.legend(fontsize=7)
    fig.suptitle('Activation-equality-only diagnostic — continuous split/restart, no ordinary crossing')
    for ext in ['png','svg']:fig.savefig(OUT/f'activation-refinement.{ext}',dpi=170)
    p=OUT/'activation-refinement.svg';p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n');plt.close(fig)

def main():
    verify_inputs();results={};inputs={};balance={};event_checks={};old_controls={}
    for policy,rep,method in itertools.product(PROTOCOL['policies'],PROTOCOL['representations'],PROTOCOL['methods']):
        key=policy+'/'+rep+'/'+method;p=OUT/f'{policy}-{rep}-{method}.json';r=json.loads(p.read_text());results[key]=r;inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        assert r['diagnostic_only'] and not r['qualified'] and r['candidate'] is None
        assert all(x['mode']=='incoming' and x['controller_mode']=='integrating' for x in r['history'])
        balance[key]=balances(r);event_checks[key]=event_check(r)
        if policy=='control':
            old=ROOT/PROTOCOL['baseline_results'][rep+'/'+method];oldr=json.loads(old.read_text());inputs[str(old.relative_to(ROOT))]=hashlib.sha256(old.read_bytes()).hexdigest();old_controls[key]=compare(r,oldr)
        print('AUDIT',key,'failure',r['failure'],'balance',balance[key]['passed'],'event',event_checks[key]['passed'],flush=True)
    comparisons={}
    # Canonical order is the declared cell order; also insert explicit directional
    # RK/reference pairs needed by render/crossing tables without dropping any.
    for a,b in itertools.combinations(results,2):comparisons[a+' vs '+b]=compare(results[a],results[b])
    crossing={}
    references=[p+'/'+r+'/'+m for p,r,m in itertools.product(PROTOCOL['policies'],PROTOCOL['representations'],PROTOCOL['methods'][4:])]
    for key,a in results.items():
        if not a['method'].startswith('RK4') or a['activation_event'] is None:continue
        for b in references:
            pair=key+' vs '+b
            if pair not in comparisons:comparisons[pair]=compare(a,results[b])
            crossing[pair]=crossing_compare(a,results[b])
    reference_pairs=[]
    for a,b in itertools.combinations(references,2):
        key=a+' vs '+b
        if key not in comparisons:key=b+' vs '+a
        reference_pairs.append(key)
    receipt=dict(scope='Activation-equality-only lower incoming diagnostic; no qualification or production adoption',protocol_sha256=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest(),input_sha256=inputs,comparisons=comparisons,crossing_step_comparisons=crossing,old_control_comparisons=old_controls,balances=balance,event_checks=event_checks,all_eight_adaptive_reference_pairs=reference_pairs,adaptive_reference_consistency=all(comparisons[k]['all_windows_passed'] for k in reference_pairs),physical_failures={k:r['failure'] for k,r in results.items() if r['failure']},qualified_trajectories=0,ordinary_events_accepted=0,sliding_states_accepted=0)
    (OUT/'analysis.json').write_text(json.dumps(receipt,indent=2)+'\n');render(receipt)
    print('REFERENCES',receipt['adaptive_reference_consistency'],'physical_failures',receipt['physical_failures'],flush=True)

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Segmented diagnostic; original states/classifications are never corrected.

RK4 auxiliary polynomials can be reconstructed from four actual stored stages.
Adaptive dense coefficients were not serialized: their roots are NOT inferred.
H/normal and |8e|*delta-time are local proxies, not rigorous orbit error bounds.
"""
import json,hashlib,math
from pathlib import Path
import numpy as np
from run_filippov_incoming_diagnostic import DATA,OUT,PROTOCOL,verify_inputs
from run_filippov_bounded_experiment import Engine,ROOT,REPS,Failure
from audit_filippov_bounded_experiment import balances

RK=['RK4-0.0002','RK4-0.0001','RK4-0.00005','RK4-0.000025']
METHODS=RK+['DOP853','Radau']
OLD=ROOT/'education/data/filippov-bounded-v1/review'

def dense_from_stages(e,aux):
    stages=aux['stages'];left,right=aux['start'],aux['trialEnd'];h=right-left
    if len(stages)!=4:raise ValueError('Cannot certify four-stage RK4 reconstruction')
    if max(abs(s['t']-t) for s,t in zip(stages,[left,left+h/2,left+h/2,right]))>2e-12:raise ValueError('Stored stage-time mismatch')
    z0=np.array(aux['startState']);k=[e.rhs(s['t'],np.array(s['z'])) for s in stages]
    def dense(t):
        u=(t-left)/h
        return z0+h*((u-1.5*u*u+2*u**3/3)*k[0]+(u*u-2*u**3/3)*(k[1]+k[2])+(-u*u/2+2*u**3/3)*k[3])
    return dense

def relocalize(e,dense,original):
    lo,hi=original['bracket'];direction=1 if e.controller_mode=='integrating' else -1
    _,a=e.evaluate(dense(lo));_,b=e.evaluate(dense(hi))
    if not direction*a['H']<=0<=direction*b['H']:return dict(diagnostic_failure='reconstructed-bracket-sign',accepted=False)
    records=[]
    for iteration in range(PROTOCOL['auxiliary_relocalization']['max_iterations']):
        mid=(lo+hi)/2;z,o=e.evaluate(dense(mid));H=o['H']
        records.append(dict(t=mid,H=H,force_residual_N=o['residual'],accepted=False))
        if direction*H<0:lo=mid
        else:hi=mid
        if hi-lo<=1e-12 and abs(H)<=1e-13:
            normal=o['normal_on'] if e.controller_mode=='integrating' else o['normal_off']
            return dict(t=mid,H=H,normal_per_s=normal,bracket=[lo,hi],iterations=iteration+1,probes=records,force_residual_N=o['residual'],surface_residual_timing_proxy_s=abs(H/normal),accepted=False)
    return dict(diagnostic_failure='tight-root-resolution',bracket=[lo,hi],probes=records,accepted=False)

def event_records(r):
    e=Engine(r['case'],r['representation'],r['method']);e.target=r['cfg']['target'];records={}
    try:
        for aux in r['localization_auxiliaries']:
            c=aux.get('candidate') or aux.get('ordinary_crossing')
            if not c:continue
            kind=c['classification'];e.controller_mode='frozen' if kind=='ordinary-inward' else 'integrating'
            z,o=e.evaluate(np.array(c['x']));normal=o['normal_off'] if e.controller_mode=='frozen' else o['normal_on']
            record=dict(original_time_s=c['t'],H=o['H'],normal_per_s=normal,integrating_rate_8e_per_s=8*o['e'],force_root_residual_N=o['residual'],original_bracket=c['bracket'],original_bracket_width_s=c['bracket'][1]-c['bracket'][0],bracket_radius_from_recorded_time_s=max(abs(c['t']-x) for x in c['bracket']),surface_residual_timing_proxy_s=abs(o['H']/normal),surface_proxy_is_not_orbit_error_bound=True,mechanical_force_residual_does_not_bound_position_raw_orbit_error=True,source_state_accepted=any(x['type']==kind and x['t']==c['t'] for x in r['events']),diagnostic_state_accepted=False)
            if r['method'].startswith('RK4'):
                dense=dense_from_stages(e,aux);difference=float(np.max(np.abs(dense(c['t'])-np.array(c['x']))))
                record['original_polynomial_state_reproduction_inf_error']=difference
                if difference>1e-12:record['relocalized']=dict(diagnostic_failure='polynomial-state-reproduction',accepted=False)
                else:
                    tight=relocalize(e,dense,c);record['relocalized']=tight
                    if 't' in tight:
                        dt=tight['t']-c['t'];record['diagnostic_self_time_shift_s']=dt;record['abs_8e_times_self_time_shift']=abs(8*o['e']*dt)
            else:record['relocalized']=dict(not_performed='Adaptive dense coefficients were not serialized; no substitute polynomial inferred',accepted=False)
            records[kind]=record
    finally:
        if e.source:e.source.close()
    return records

def segment_compare(a,b,case):
    ma={round(x['t'],9):x for x in a['history']};mb={round(x['t'],9):x for x in b['history']}
    # The grid requirement is diagnostic, not full trajectory qualification.
    times=[t for t in sorted(ma.keys()&mb.keys()) if abs(t/.001-round(t/.001))<1e-7]
    result={};anchor=.2;plateau=(ma[anchor]['z'][4]-mb[anchor]['z'][4]) if case=='mass-1' and anchor in ma and anchor in mb else None
    for segment,(left,right) in PROTOCOL['segments'][case].items():
        selected=[t for t in times if t>=left-1e-12 and (right is None or t<=right+1e-12)]
        if not selected:result[segment]=dict(samples=0,diagnostic_missing=True);continue
        maxima=np.zeros(7);witness={};increment=0.
        for t in selected:
            x,y=ma[t],mb[t];delta=np.r_[np.array(x['z'][:4])-y['z'][:4],x['FT']-y['FT'],x['z'][4]-y['z'][4],x['uraw']-y['uraw']]
            maxima=np.maximum(maxima,np.abs(delta))
            for name,j in [('I',5),('raw',6)]:
                if name not in witness or abs(delta[j])>witness[name]['absolute_error']:
                    witness[name]=dict(t=t,absolute_error=abs(float(delta[j])),signed_integral_difference=float(delta[5]),signed_force_contribution_to_raw=float(-.004*delta[4]),signed_raw_difference=float(delta[6]),raw_identity_residual=float(delta[6]-delta[5]+.004*delta[4]))
            if plateau is not None:increment=max(increment,abs(float(delta[5])-plateau))
        result[segment]=dict(samples=len(selected),first_s=selected[0],last_s=selected[-1],max_errors=dict(zip(['y_m','w_m_per_s','a','q','FT_N','I','raw'],maxima.tolist())),witnesses=witness,branch_mismatch_count=sum(ma[t]['controller_mode']!=mb[t]['controller_mode'] for t in selected),frozen_anchor_signed_integral_difference=plateau,supplemental_integral_increment_from_frozen_anchor=increment if plateau is not None else None,anchor_subtraction_is_not_state_correction_or_qualification=True)
    return result

def event_compare(a,b):
    results={}
    for kind in sorted(set(a)&set(b)):
        x,y=a[kind],b[kind];dt=x['original_time_s']-y['original_time_s'];rate=max(abs(x['integrating_rate_8e_per_s']),abs(y['integrating_rate_8e_per_s']))
        item=dict(original_signed_event_time_difference_s=dt,abs_8e_times_original_event_time_difference=rate*abs(dt),maximum_abs_integrating_rate_8e_per_s=rate,first_surface_residual_timing_proxy_s=x['surface_residual_timing_proxy_s'],second_surface_residual_timing_proxy_s=y['surface_residual_timing_proxy_s'],first_bracket_radius_s=x['bracket_radius_from_recorded_time_s'],second_bracket_radius_s=y['bracket_radius_from_recorded_time_s'],not_causal_attribution_or_rigorous_error_bound=True)
        if 't' in x.get('relocalized',{}) and 't' in y.get('relocalized',{}):
            tighter=x['relocalized']['t']-y['relocalized']['t'];item.update(diagnostic_relocalized_signed_time_difference_s=tighter,abs_8e_times_diagnostic_relocalized_time_difference=rate*abs(tighter),original_minus_relocalized_time_difference_s=dt-tighter)
        results[kind]=item
    return results

def analyze(results,event_data):
    comparisons={};ratios={}
    pairs=[]
    for rep in REPS:
        pairs += [(rep+'/'+a,rep+'/'+b) for a,b in zip(RK,RK[1:])]
        pairs += [(rep+'/'+a,rep+'/'+b) for a in RK for b in ['DOP853','Radau']]
    pairs += [(REPS[0]+'/'+method,REPS[1]+'/'+method) for method in METHODS]
    for first,second in pairs:
        a,b=results[first],results[second];comparisons[first+' vs '+second]=dict(segments=segment_compare(a,b,a['case']),events=event_compare(event_data[first],event_data[second]),accepted_times_s=[a['acceptedTime'],b['acceptedTime']],no_event_alignment=True)
    for rep in REPS:
        ratios[rep]={}
        adjacent=[comparisons[rep+'/'+a+' vs '+rep+'/'+b]['segments'] for a,b in zip(RK,RK[1:])]
        for segment in PROTOCOL['segments'][next(iter(results.values()))['case']]:
            errors={name:[x[segment].get('max_errors',{}).get(name) for x in adjacent] for name in ['I','raw','a','FT_N']}
            ratios[rep][segment]={name:dict(adjacent_errors=values,ratios=[values[j]/values[j+1] if values[j] is not None and values[j+1] is not None and values[j+1]>0 else None for j in [0,1]]) for name,values in errors.items()}
    return dict(comparisons=comparisons,adjacent_refinement_ratios_by_segment=ratios)

def render(analysis):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for row,case in enumerate(PROTOCOL['cases']):
        segments=['initial_equilibrium','command_transient','later_smooth_incoming'] if case=='high' else ['before_activation_equality','activation_transition_window','after_activation_before_frozen','frozen_interval','after_ordinary_inward']
        labels=['equilibrium','command','later smooth'] if case=='high' else ['before A','A window','after A','frozen','after inward']
        for col,rep in enumerate(REPS):
            ax=axes[row,col]
            for method,color in zip(RK,['#9a3f22','#c8872b','#126e82','#5c4a91']):
                comparison=analysis[case]['comparisons'][rep+'/'+method+' vs '+rep+'/DOP853']['segments']
                values=[max(comparison[s]['max_errors']['I'],1e-17) for s in segments]
                ax.plot(range(len(segments)),values,'o-',color=color,label=method.replace('RK4-','h='))
            ax.axhline(1e-9,color='#555',ls=':',label='original I diagnostic limit')
            ax.set(yscale='log',xticks=range(len(segments)),xticklabels=labels,ylabel='Max |ΔI| versus existing DOP853',title=case+' / '+rep)
            ax.grid(alpha=.2);ax.legend(fontsize=7)
    fig.suptitle('Incoming convergence diagnostic — all coarse levels retained; no sliding or qualification',fontsize=12)
    for ext in ['png','svg']:fig.savefig(OUT/f'segmented-refinement.{ext}',dpi=170)
    svg=OUT/'segmented-refinement.svg';svg.write_text('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n');plt.close(fig)

def main():
    verify_inputs();results={};events={};inputs={};new_balances={}
    for case in PROTOCOL['cases']:
        results[case]={};events[case]={}
        for rep in REPS:
            for method in METHODS:
                p=(OUT if method==RK[-1] else OLD)/f'{case}-{rep}-{method}.json';r=json.loads(p.read_text());key=rep+'/'+method
                results[case][key]=r;events[case][key]=event_records(r);inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
                if method==RK[-1]:
                    assert r['diagnostic_only'] and not r['qualified'] and all(x['mode']=='incoming' for x in r['history'])
                    new_balances[case+'/'+rep]=balances(r)
        print('Event diagnostic reconstruction',case,'complete',flush=True)
    analysis={case:analyze(results[case],events[case]) for case in PROTOCOL['cases']}
    receipt=dict(scope='Convergence diagnostic only; no pass/requalification label',protocol_sha256=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest(),input_sha256=inputs,source_sha256={str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},cases=analysis,events=events,new_prefix_balances=new_balances,new_qualified_trajectories=0,new_sliding_entries=0,old_twenty_cell_classification_unchanged=True)
    (OUT/'segmented-analysis.json').write_text(json.dumps(receipt,indent=2)+'\n');render(analysis)
    for case,a in analysis.items():print(case,json.dumps(a['adjacent_refinement_ratios_by_segment']['full-source']),flush=True)

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Absolute-time signed prefix comparisons; never a sliding qualification."""
import hashlib,json,itertools
import numpy as np
from run_ordinary_crossing_consistency import DATA,OUT,PROTOCOL,verify_inputs,replay_dense
from run_filippov_bounded_experiment import ROOT,Engine
from audit_filippov_bounded_experiment import balances,GATES,NAMES
from analyze_filippov_incoming_diagnostic import segment_compare,event_compare

def events(r):
    e=Engine(r['case'],r['representation'],r['method']);e.target=r['cfg']['target'];result={}
    try:
        for aux in r['localization_auxiliaries']:
            c=aux.get('ordinary_crossing') or aux.get('candidate')
            if c is None:continue
            kind=c['classification'];e.controller_mode=aux['incoming_controller_mode']
            z=replay_dense(aux['dense'],c['t']);error=float(np.max(np.abs(z-c['x'])))
            if error>1e-12:raise ValueError('Crossing polynomial reproduction')
            _,o=e.evaluate(z);normal=o['normal_on'] if e.controller_mode=='integrating' else o['normal_off']
            result[kind]=dict(original_time_s=c['t'],H=o['H'],normal_per_s=normal,integrating_rate_8e_per_s=8*o['e'],force_root_residual_N=o['residual'],original_bracket=c['bracket'],original_bracket_width_s=c['bracket'][1]-c['bracket'][0],bracket_radius_from_recorded_time_s=max(abs(c['t']-t) for t in c['bracket']),surface_residual_timing_proxy_s=abs(o['H']/normal),actual_dense_state_reproduction_error=error,accepted_ordinary_event=kind!='attracting',attracting_state_accepted=False,iterations=c['iterations'])
    finally:
        if e.source:e.source.close()
    return result

def compare(a,b,ea=None,eb=None):
    segments=segment_compare(a,b,a['case']);maxima={name:max(s.get('max_errors',{}).get(name,0) for s in segments.values()) for name in ['y_m','w_m_per_s','a','q','FT_N','I','raw']}
    gates=dict(zip(['y_m','w_m_per_s','a','q','FT_N','I','raw'],GATES.tolist()))
    ma={round(r['t'],9):r for r in a['history']};mb={round(r['t'],9):r for r in b['history']}
    signed={str(t):dict(delta_I=ma[t]['z'][4]-mb[t]['z'][4],delta_raw=ma[t]['uraw']-mb[t]['uraw'],delta_FT=ma[t]['FT']-mb[t]['FT']) for t in [.002,.003,.107,.108,.2,.249,.25,.261] if t in ma and t in mb}
    event_metrics=event_compare(ea,eb) if ea is not None else None
    event_max=max((abs(v['original_signed_event_time_difference_s']) for v in (event_metrics or {}).values()),default=0.)
    return dict(event_gate_s=2e-6,max_event_time_difference_s=event_max,event_margin_s=2e-6-event_max,event_gate_passed=event_max<=2e-6 if event_metrics else None,segments=segments,max_errors=maxima,gates=gates,margins={k:gates[k]-maxima[k] for k in gates},all_state_gates_passed=all(maxima[k]<=gates[k] for k in gates),signed_matched_time_differences=signed,events=event_metrics,event_alignment=False,sliding_qualification=False)

def render(analysis):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(12,7),layout='constrained')
    for row,case in enumerate(PROTOCOL['cases']):
        for col,rep in enumerate(PROTOCOL['representations']):
            ax=axes[row,col]
            for method,color in zip(PROTOCOL['methods'],['#9a3f22','#c8872b','#126e82','#5c4a91','#387b46','#b24d79']):
                c=analysis[case]['comparisons'][rep+'/'+method+' vs '+rep+'/Radau'] if method!='Radau' else None
                if c is None:continue
                segments=['initial_equilibrium','command_transient','later_smooth_incoming'] if case=='high' else ['before_activation_equality','activation_transition_window','after_activation_before_frozen','frozen_interval','after_ordinary_inward']
                ax.plot(range(len(segments)),[max(c['segments'][s]['max_errors']['I'],1e-17) for s in segments],'o-',label=method,color=color)
            ax.axhline(1e-9,color='#555',ls=':');ax.set(yscale='log',xticks=range(len(segments)),xticklabels=['equilibrium','command','later'] if case=='high' else ['before A','A window','after A','frozen','after inward'],title=case+' / '+rep,ylabel='Max |ΔI| versus new Radau');ax.legend(fontsize=7);ax.grid(alpha=.2)
    fig.suptitle('Ordinary-crossing consistency experiment — incoming prefixes only')
    for ext in ['png','svg']:fig.savefig(OUT/f'crossing-consistency.{ext}',dpi=170)
    p=OUT/'crossing-consistency.svg';p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n');plt.close(fig)

def main():
    verify_inputs();analysis={};inputs={};balance={};event_data={};old_new={};dense_checks={}
    reps=PROTOCOL['representations'];methods=PROTOCOL['methods']
    for case in PROTOCOL['cases']:
        rs={};ev={}
        for rep,method in itertools.product(reps,methods):
            key=rep+'/'+method;p=OUT/f'{case}-{rep}-{method}.json';r=json.loads(p.read_text());rs[key]=r;ev[key]=events(r)
            assert r['experiment_only'] and not r['qualified'] and not r['sliding_allowed']
            assert all(x['mode']=='incoming' for x in r['history'])
            assert r['candidate'] is None or not r['candidate']['accepted']
            inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest();balance[case+'/'+key]=balances(r)
            # Every accepted grid state is reproduced from the actual accepted
            # polynomial; event states are checked separately against auxiliaries.
            maximum=0.;samples=0
            grids={round(x['t'],9):x for x in r['history'] if abs(x['t']/.001-round(x['t']/.001))<1e-7}
            for interval in r['accepted_intervals']:
                assert 'dense' in interval
                for t in [round(j*.001,9) for j in range(int(np.floor((interval['start']+1e-10)*1000))+1,int(np.floor((interval['end']+1e-10)*1000))+1)]:
                    if t not in grids or t<interval['start']-1e-12:continue
                    error=float(np.max(np.abs(replay_dense(interval['dense'],t)-grids[t]['z'])))
                    maximum=max(maximum,error);samples+=1
            assert maximum<=1e-12
            dense_checks[case+'/'+key]=dict(samples=samples,max_grid_reproduction_error=maximum,accepted_intervals=len(r['accepted_intervals']),all_coefficients_retained=True)
            old=ROOT/PROTOCOL['baseline_results'][case+'/'+key];oldr=json.loads(old.read_text());inputs[str(old.relative_to(ROOT))]=hashlib.sha256(old.read_bytes()).hexdigest()
            old_new[case+'/'+key]=compare(r,oldr)
            print('AUDIT',case,key,'balances',balance[case+'/'+key]['passed'],'dense',maximum,flush=True)
        pairs=[]
        for rep in reps:
            rk=methods[:4];pairs += [(rep+'/'+a,rep+'/'+b) for a,b in zip(rk,rk[1:])]
            pairs += [(rep+'/'+a,rep+'/'+b) for a in rk for b in methods[4:]]
            pairs += [(rep+'/DOP853',rep+'/Radau')]
        pairs += [(reps[0]+'/'+m,reps[1]+'/'+m) for m in methods]
        pairs += [(reps[0]+'/DOP853',reps[1]+'/Radau'),(reps[0]+'/Radau',reps[1]+'/DOP853')]
        comparisons={a+' vs '+b:compare(rs[a],rs[b],ev[a],ev[b]) for a,b in pairs}
        reference_keys=[rep+'/'+m for rep,m in itertools.product(reps,methods[4:])]
        reference_pairs=[a+' vs '+b for a,b in itertools.combinations(reference_keys,2)]
        # Direction of one representation pair follows the explicit pair list.
        reference_pairs=[k if k in comparisons else ' vs '.join(reversed(k.split(' vs '))) for k in reference_pairs]
        checks={k:comparisons[k] for k in reference_pairs}
        analysis[case]=dict(comparisons=comparisons,all_four_adaptive_reference_pairs=list(checks),adaptive_state_consistency=all(c['all_state_gates_passed'] for c in checks.values()),adaptive_event_consistency=all(c['event_gate_passed'] for c in checks.values()),adaptive_prefix_consistency=all(c['all_state_gates_passed'] and c['event_gate_passed'] for c in checks.values()),reference_max_event_time_difference_s=max(c['max_event_time_difference_s'] for c in checks.values()),reference_max_errors={k:max(c['max_errors'][k] for c in checks.values()) for k in next(iter(checks.values()))['max_errors']},physical_failures={k:r['failure'] for k,r in rs.items() if r['failure']})
        event_data[case]=ev
    receipt=dict(scope='Ordinary-crossing accepted-state/restart experiment; incoming-only, not production adoption',protocol_sha256=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest(),input_sha256=inputs,cases=analysis,new_minus_original=old_new,events=event_data,balances=balance,dense_checks=dense_checks,qualified_trajectories=0,accepted_sliding_states=0,activation_handling_changed=False)
    (OUT/'analysis.json').write_text(json.dumps(receipt,indent=2)+'\n');render(analysis)
    for case,r in analysis.items():print(case,'adaptive_state_consistency',r['adaptive_state_consistency'],'max',r['reference_max_errors'],flush=True)

if __name__=='__main__':main()

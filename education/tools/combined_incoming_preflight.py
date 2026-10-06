#!/usr/bin/env python3
"""Preparation only: pure event arbitration and audits of old stored evidence.

No combined engine or trajectory execution is provided. Pending parent review
must be resolved before an execution source/protocol can be frozen separately.
"""
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'education/data/combined-incoming-protocol-v1'
P=json.loads((DATA/'protocol.json').read_text())

def verify_inputs():
    for path,digest in {**P['input_sha256'],**P.get('preparation_source_sha256',{})}.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:raise ValueError('Prepared protocol input changed: '+path)

def decide_trial(events,controller,activation,remainder_end=None,command_time=None):
    """Classify abstract candidate records before ANY state/time mutation."""
    result=dict(advance=False,controller=controller,activation=activation,restart_solver=False)
    if controller not in ['integrating','frozen']:return dict(**result,decision='stop',reason='invalid-controller-mode')
    for event in events:
        lo,hi=event['bracket']
        if not all(math.isfinite(t) for t in [lo,hi]) or lo>hi:return dict(**result,decision='stop',reason='invalid-event-bracket')
    if not events:return dict(**result,decision='no-event')
    ordered=sorted(events,key=lambda e:e['bracket'][0])
    if len(ordered)>1 and ordered[0]['bracket'][1]>=ordered[1]['bracket'][0]:return dict(**result,decision='stop',reason='unresolved-event-order')
    event=ordered[0];kind=event['kind']
    if command_time is not None and event['bracket'][0]<=command_time<=event['bracket'][1]:return dict(**result,decision='stop',reason='compound-command-root')
    result['discarded_later_candidates']=[e['kind'] for e in ordered[1:]]
    if kind=='attracting':return dict(**result,decision='hold',reason='attracting-candidate-unaccepted')
    if kind=='activation-equality':
        if activation!='activation' or controller!='integrating' or remainder_end is not None:return dict(**result,decision='stop',reason='unexpected-activation-crossing')
        if not event.get('interior',False) or not event.get('transverse',False):return dict(**result,decision='stop',reason='uncertified-activation-crossing')
        result.update(advance=True,activation='deactivation',restart_solver=True)
        return dict(**result,decision='activation-prefix',preserve_original_rk_trial_end=True)
    if kind in ['ordinary-outward','ordinary-inward']:
        expected='ordinary-outward' if controller=='integrating' else 'ordinary-inward'
        if kind!=expected or not event.get('same_direction_normals',False):return dict(**result,decision='stop',reason='uncertified-controller-crossing')
        # Clipping is continuous at b=B. A new activation side at that same
        # event would be an undeclared compound boundary, not a branch reset.
        if activation=='deactivation' and event.get('g',0)>=-1e-13:return dict(**result,decision='stop',reason='activation-side-ambiguity-at-controller-crossing')
        result.update(advance=True,controller='frozen' if controller=='integrating' else 'integrating',restart_solver=True)
        return dict(**result,decision='ordinary-prefix',preserve_original_rk_trial_end=remainder_end is not None,pending_activation_remainder_end=remainder_end)
    return dict(**result,decision='stop',reason='undeclared-event-type')

def staged_restart(previous,candidate,decision,validate):
    """Pure structural contract: all eleven event coordinates are retained.

The callback stands for the UNCHANGED physical/dense/ledger checks. This helper
does not compute those checks or authorize a physical state acceptance.
"""
    if not decision.get('advance',False):return dict(previous)
    coordinates=tuple(candidate['state'])
    if len(coordinates)!=11 or not all(math.isfinite(x) for x in coordinates):raise ValueError('Invalid eleven-coordinate candidate')
    if candidate['time']<=previous['time']:raise ValueError('Nonadvancing candidate')
    if not validate(candidate):return dict(previous)
    return dict(time=candidate['time'],state=coordinates,controller=decision['controller'],activation=decision['activation'],new_solver_required=True)

def stored_evidence():
    events={};branches={};gaps={};frozen_memory={}
    for case in P['stored_evidence_cases']:
        timeline={};case_branches={}
        for rep in P['representations']:
            for method in P['methods']:
                key=rep+'/'+method;r=json.loads((ROOT/P['ordinary_baselines'][case+'/'+key]).read_text());items=[]
                for aux in r['localization_auxiliaries']:
                    c=aux.get('ordinary_crossing') or aux.get('candidate')
                    if not c:continue
                    kind=c['classification'];items.append(dict(kind=kind,time=c['t'],bracket=c['bracket']))
                    if kind.startswith('ordinary'):
                        B=.01 if case=='mass-1' else 1.;g=B-c['x'][2]
                        case_branches[key+'/'+kind]=dict(a=c['x'][2],B=B,g_at_exact_controller_bound=g,original_normals=[c['normal_on'],c['normal_off']])
                timeline[key]=items
                if case=='mass-1':
                    frozen=[x for x in r['history'] if x['controller_mode']=='frozen']
                    if not frozen:raise ValueError('Stored mass-1 prefix has no frozen interval')
                    memory=frozen[0]['z'][4];error=max(abs(x['z'][4]-memory) for x in frozen)
                    if error!=0:raise ValueError('Stored original frozen integral memory changed')
                    frozen_memory[key]=dict(I=memory,samples=len(frozen),max_I_change=error)
        events[case]=timeline;branches[case]=case_branches
    activation={}
    for policy in ['control','split']:
        for rep in P['representations']:
            for method in P['methods']:
                key=policy+'/'+rep+'/'+method;r=json.loads((ROOT/P['activation_baselines'][key]).read_text());c=r['activation_event'];activation[key]=dict(time=c['t'],bracket=c['bracket'],accepted=c['accepted'],normal=c['normal_at_exact_equality_per_s'])
    latest_activation=max(x['bracket'][1] for x in activation.values())
    ordinary_out=[x for row in events['mass-1'].values() for x in row if x['kind']=='ordinary-outward'];ordinary_in=[x for row in events['mass-1'].values() for x in row if x['kind']=='ordinary-inward'];attract=[x for row in events['mass-1'].values() for x in row if x['kind']=='attracting']
    gaps=dict(activation_to_first_ordinary_s=min(x['bracket'][0] for x in ordinary_out)-latest_activation,ordinary_outward_to_inward_s=min(x['bracket'][0] for x in ordinary_in)-max(x['bracket'][1] for x in ordinary_out),ordinary_inward_to_attracting_s=min(x['bracket'][0] for x in attract)-max(x['bracket'][1] for x in ordinary_in),high_command_to_attracting_s=min(x['bracket'][0] for row in events['high'].values() for x in row if x['kind']=='attracting')-.05)
    if not all(g>.0005 for g in gaps.values()):raise ValueError('Stored nominal event spacing is not larger than original maximum trial step')
    if not all(x['g_at_exact_controller_bound']<-1e-13 for x in branches['mass-1'].values()):raise ValueError('Stored ordinary event changes activation side')
    high_ranges={}
    for rep in P['representations']:
        for method in P['methods']:
            key=rep+'/'+method;r=json.loads((ROOT/P['ordinary_baselines']['high/'+key]).read_text());before=[x['u']-x['z'][2] for x in r['history'] if x['t']<.05];after=[x['u']-x['z'][2] for x in r['history'] if x['t']>=.05]
            high_ranges[key]=dict(precommand_g_min=min(before),precommand_g_max=max(before),postcommand_g_min=min(after),postcommand_g_max=max(after))
    reviewed=json.loads((ROOT/'education/data/ordinary-crossing-consistency-v1/review/analysis.json').read_text());pair=reviewed['cases']['high']['comparisons']['full-source/RK4-0.0002 vs full-source/RK4-0.0001']
    return dict(scope='Old separate experiments only; not a composed trajectory',activation_observations=activation,ordinary_timelines=events,controller_bound_activation_sides=branches,original_frozen_integral_memory=frozen_memory,minimum_stored_bracket_separations_s=gaps,all_stored_event_gaps_exceed_original_max_step=True,high_initial_equality_ranges=high_ranges,high_unchanged_coarse_negative_control=dict(I_error=pair['max_errors']['I'],I_margin=pair['margins']['I'],raw_error=pair['max_errors']['raw'],raw_margin=pair['margins']['raw']),combined_candidate_prefixes_executed=0,activation_independent_review_disposition='pending')

def main():
    verify_inputs();dest=DATA/'preflight'/'stored-structure.json'
    if dest.exists():raise ValueError('Refuse to overwrite preparation evidence')
    dest.parent.mkdir(parents=True,exist_ok=True);r=stored_evidence();dest.write_text(json.dumps(r,indent=2)+'\n')
    print('PASS stored event ordering, negative activation side through ordinary crossings, and high persistent equality',flush=True)
    print('Stored bracket gaps',r['minimum_stored_bracket_separations_s'],flush=True)
    print('High unchanged coarse negative control',r['high_unchanged_coarse_negative_control'],flush=True)
    print('Combined matrix remains unexecuted; activation review pending',flush=True)

if __name__=='__main__':main()

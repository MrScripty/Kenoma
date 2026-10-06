#!/usr/bin/env python3
"""Completion, absolute-time/event refinement, independent force/work audit.
Reports failures without weakening any gate or treating a prefix as completion.
"""
import json,hashlib,math
from pathlib import Path
import numpy as np
from run_filippov_bounded_experiment import OUT,CASES,ENDS,METHODS,REPS,ROOT,P,C,reference_output

GATES=np.array([1e-6,1e-5,2e-6,2e-6,1e-4,1e-9,1e-8])
NAMES=['y_m','w_m_per_s','activation','q','FT_N','I','raw']

def completion(r):
    if r.get('case') not in ENDS:return dict(passed=False,issues=['undeclared-case'],missing_grid_times=[])
    end=ENDS[r['case']];h=r.get('history',[]);issues=[]
    if r.get('cfg')!=CASES[r['case']]:issues.append('initialization-or-command-mismatch')
    if r.get('declared_endpoint_s')!=end:issues.append('endpoint-policy-mismatch')
    if 'failure' not in r:issues.append('missing-failure-report')
    if r.get('failure') is not None:issues.append('failure')
    if abs(r.get('acceptedTime',-1)-end)>1e-9:issues.append('endpoint-not-reached')
    if not h or abs(h[0]['t'])>1e-9 or abs(h[-1]['t']-r.get('acceptedTime',-1))>1e-9 or any(b['t']<=a['t'] for a,b in zip(h,h[1:])):issues.append('invalid-history')
    times={round(x['t'],9) for x in h};needed={round(k*.001,9) for k in range(math.floor((end+1e-10)/.001)+1)}|{round(end,9)}
    missing=sorted(needed-times)
    if missing:issues.append('missing-common-grid')
    entries=[x for x in r.get('events',[]) if x['type']=='sliding-entry']
    if len(entries)!=1:issues.append('missing-or-duplicate-accepted-entry')
    if entries and not r.get('candidate',{}).get('accepted'):issues.append('unaccepted-candidate')
    return dict(passed=not issues,issues=issues,missing_grid_times=missing)

def compare(a,b):
    ma={round(r['t'],9):r for r in a['history']};mb={round(r['t'],9):r for r in b['history']};times=sorted(ma.keys()&mb.keys());errors=np.zeros(7)
    for t in times:
        x,y=ma[t],mb[t]
        errors=np.maximum(errors,[*(np.abs(np.array(x['z'][:4])-y['z'][:4])),abs(x['FT']-y['FT']),abs(x['z'][4]-y['z'][4]),abs(x['uraw']-y['uraw'])])
    ca,cb=a.get('candidate'),b.get('candidate');dt=abs(ca['t']-cb['t']) if ca and cb else None
    ea=[e for e in a['events'] if e['type'].startswith('ordinary-')];eb=[e for e in b['events'] if e['type'].startswith('ordinary-')]
    ordinary_match=[e['type'] for e in ea]==[e['type'] for e in eb]
    ordinary_errors=[abs(x['t']-y['t']) for x,y in zip(ea,eb)]
    numerical=bool(len(times)>2 and np.all(errors<=GATES) and dt is not None and dt<=2e-6 and ordinary_match and max(ordinary_errors,default=0)<=2e-6)
    return dict(passed=bool(numerical and completion(a)['passed'] and completion(b)['passed']),prefix_agreement_only=numerical,common_grid_count=len(times),common_end_s=times[-1] if times else None,max_errors=dict(zip(NAMES,errors.tolist())),gates=dict(zip(NAMES,GATES.tolist())),candidate_event_difference_s=dt,ordinary_event_types_match=ordinary_match,ordinary_event_differences_s=ordinary_errors,event_gate_s=2e-6,absolute_times_used=True,event_alignment_used=False)

def balances(r):
    cfg=r['cfg'];start=r['history'][0]['z'];s0=(cfg['L0']-start[0]-.1*start[3])/.2
    errors=np.zeros(6);maxforce=normals=tangent=constraint=0.;bounds=[];eta=1 if r['case']=='high' else -1
    for row in r['history']:
        z=row['z'];o=reference_output(z,cfg,{'target':row['target']});q=z[3]
        ef=10*C['passive'].integral(start[3],q);et=20*C['tendon'].integral(s0,o['s']);el=.5*cfg['m']*(z[1]**2-start[1]**2)+cfg['m']*P['gravity_m_per_s2']*(z[0]-start[0])
        errors=np.maximum(errors,np.abs([ef-z[8],et-z[9],el-z[7],ef+et+el-z[5]+z[6],cfg['m']*(z[1]-start[1])-z[10],z[5]-z[6]-z[7]-z[8]-z[9]]))
        maxforce=max(maxforce,abs(o['residual']),abs(o['FT']-row['FT']));bounds.append(q>.4441 and o['s']>1 and .01-1e-12<=z[2]<=1+1e-12)
        d=.4*500*C['tendon'].value(o['s'],True)*(z[1]+o['v'])/100;k=8*o['e']
        normals=max(normals,abs(eta*(d+k)-row['normal_on']),abs(eta*d-row['normal_off']))
        if row['mode']=='sliding':
            constraint=max(constraint,abs(row['H']));tangent=max(tangent,abs(d+row['Idot']))
            bounds.append(row['normal_on']>1e-8 and row['normal_off']<-1e-8 and eta*o['e']>0)
    gates=np.array([1e-5]*4+[1e-7,1e-5]);passed=bool(np.all(errors<=gates) and maxforce<=1e-7 and normals<=1e-8 and tangent<=1e-8 and constraint<=1e-9 and all(bounds) and r['independent_quadrature']['passed'])
    return dict(passed=passed,work_momentum_errors=dict(zip(['fiber_J','tendon_J','load_J','combined_J','momentum_N_s','power_ledger_J'],errors.tolist())),source_force_residual_N=maxforce,independent_normal_disagreement_per_s=normals,independent_tangent_residual_per_s=tangent,max_sliding_constraint=constraint,physical_and_strict_sign_bounds_passed=all(bounds),quadrature=r['independent_quadrature'],scope='Only accepted history; algebraic/ledger validity of a stopped prefix does not imply completion')

def qualify(results):
    required=[rep+'/'+m for rep in REPS for m in METHODS];missing=sorted(set(required)-set(results))
    if missing:return dict(passed=False,status='unqualified',missing_cells=missing)
    if any(f"{r.get('representation')}/{r.get('method')}"!=k for k,r in results.items()):return dict(passed=False,status='unqualified',issues=['cell-identity-mismatch'])
    comps={}
    for rep in REPS:
        for a,b in zip(METHODS[:3],METHODS[1:3]):comps[f'{rep}:{a}/{b}']=compare(results[rep+'/'+a],results[rep+'/'+b])
        comps[rep+':DOP853/Radau']=compare(results[rep+'/DOP853'],results[rep+'/Radau'])
        for adaptive in METHODS[3:]:comps[rep+':finest/'+adaptive]=compare(results[rep+'/'+METHODS[2]],results[rep+'/'+adaptive])
    for method in METHODS:comps['representations:'+method]=compare(results[REPS[0]+'/'+method],results[REPS[1]+'/'+method])
    complete={k:completion(v) for k,v in results.items()};balance={k:balances(v) for k,v in results.items()}
    passed=all(x['passed'] for x in [*comps.values(),*complete.values(),*balance.values()])
    times={k:r['candidate']['t'] if r.get('candidate') else None for k,r in results.items()}
    return dict(passed=passed,status='bounded-experiment-passes-authored-checks-pending-independent-review' if passed else 'unqualified',missing_cells=missing,completion=complete,comparisons=comps,balances=balance,candidate_entry_times_s=times,accepted_endpoints_s={k:r['acceptedTime'] for k,r in results.items()},failure_codes={k:r['failure']['code'] if r['failure'] else None for k,r in results.items()})

def render(results):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(13,4.1),layout='constrained')
    for ax,case in zip(axes[:2],CASES):
        rs=results[case];reference=rs['reduced-independent/DOP853'].get('candidate')
        if reference:
            for rep,color in zip(REPS,['#126e82','#ba4f23']):
                ys=[(rs[rep+'/'+m]['candidate']['t']-reference['t'])*1e9 if rs[rep+'/'+m].get('candidate') else float('nan') for m in METHODS]
                ax.plot(range(5),ys,'o-',color=color,label=rep)
        ax.text(.02,.03,'Required pairwise span ≤ 2,000 ns',transform=ax.transAxes,fontsize=8)
        ax.set(xticks=range(5),xticklabels=['RK4\n200 µs','RK4\n100 µs','RK4\n50 µs','DOP853','Radau'],ylabel='Candidate entry minus independent DOP853 (ns)',title=case+' entry refinement')
        ax.grid(alpha=.2);ax.legend(fontsize=7)
    for case,color in zip(CASES,['#126e82','#ba4f23']):
        r=results[case]['full-source/RK4-0.00005'];h=r['history'];accepted=any(e['type']=='sliding-entry' for e in r['events'])
        start=.104 if case=='high' else .260
        selected=[x for x in h if x['t']>=start]
        normal=r['candidate']['normal_on'] if r.get('candidate') else 1.
        axes[2].plot([(x['t']-start)*1000 for x in selected],[x['H']/normal*1e6 for x in selected],'o-',markersize=3,color=color,label=case+(' (sliding accepted)' if accepted else ' (entry blocked)'))
    axes[2].axhline(0,color='#555',lw=.8);axes[2].set(xlabel='Time from case-local plot start (ms)',ylabel='H / incoming entry normal (µs; diagnostic)',title='Accepted histories only');axes[2].grid(alpha=.2);axes[2].legend(fontsize=7)
    fig.suptitle('Bounded Filippov research experiment — authored evidence, pending independent review',fontsize=12)
    for ext in ['png','svg']:fig.savefig(OUT/f'entry-refinement.{ext}',dpi=180)
    svg=OUT/'entry-refinement.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)

def main():
    results={};inputs={}
    for case in CASES:
        results[case]={}
        for rep in REPS:
            for method in METHODS:
                p=OUT/f'{case}-{rep}-{method}.json';results[case][rep+'/'+method]=json.loads(p.read_text());inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    checks={case:qualify(rs) if all(r.get('case')==case for r in rs.values()) else dict(passed=False,status='unqualified',issues=['case-identity-mismatch']) for case,rs in results.items()}
    execution=json.loads((OUT/'matrix-execution.json').read_text())
    source_bindings=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in execution['source_sha256'].items())
    receipt=dict(passed=source_bindings and all(r['passed'] for r in checks.values()),checks=checks,required_cells=20,input_sha256=inputs,executed_source_bindings_passed=source_bindings,source_sha256={str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},qualification_scope='Short scalar research slices only; no adoption/anatomical/global continuation claim')
    (OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n');render(results)
    for case,r in checks.items():print(case,r['status'],r.get('failure_codes',r.get('issues')),flush=True)
    print('Overall authored bounded audit:',receipt['passed'],'— failures retained; no gates relaxed',flush=True)

if __name__=='__main__':main()

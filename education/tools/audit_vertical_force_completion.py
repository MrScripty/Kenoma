#!/usr/bin/env python3
"""Completion-aware successor to the immutable 765ce8 scalar audit.

Numerical prefix agreement is separate from full trajectory qualification.
No current protocol defines an early terminal event: brakes change phase and
domain/controller failures stop unqualified trials, not successful experiments.
"""
import json,math,hashlib
from pathlib import Path
import audit_vertical_force as frozen
from vertical_force_reference import phases

ROOT=frozen.ROOT
INPUT=frozen.OUT
OUT=ROOT/'education/data/vertical-force-completion-v1/review'
METHODS=('coarse','fine','DOP853','Radau')
TIME_EPS=1e-9  # existing round(t,9) metadata precision; not an ODE/event gate
CASES={'baseline','pulse','lower','release','high','mass','descending_fixed','descending_pi'}

def endpoint(cfg):
    if cfg.get('caseName') not in CASES:
        raise ValueError('No declared endpoint for this case')
    return float(phases(cfg)[-1]['end'])

def metadata(result,end):
    issues=[];history=result.get('history',[]);accepted=result.get('acceptedTime')
    if not isinstance(accepted,(int,float)) or not math.isfinite(accepted):
        issues.append('missing-or-nonfinite-accepted-time')
    times=[r.get('t') for r in history]
    finite=bool(times) and all(isinstance(t,(int,float)) and math.isfinite(t) for t in times)
    if not finite:issues.append('missing-or-nonfinite-history-time')
    elif abs(times[0])>TIME_EPS or any(b<=a for a,b in zip(times,times[1:])):
        issues.append('history-not-from-zero-or-not-strictly-increasing')
    if finite and isinstance(accepted,(int,float)) and math.isfinite(accepted):
        if abs(times[-1]-accepted)>TIME_EPS:issues.append('history-tail-disagrees-with-accepted-time')
        if accepted<0 or accepted>end+TIME_EPS:issues.append('accepted-time-outside-protocol')
    if 'failure' not in result:issues.append('missing-failure-report')
    return issues

def completion(result,end):
    issues=metadata(result,end)
    if result.get('failure') is not None:issues.append('method-failure')
    accepted=result.get('acceptedTime')
    if not isinstance(accepted,(int,float)) or not math.isfinite(accepted) or abs(accepted-end)>TIME_EPS:
        issues.append('declared-endpoint-not-reached')
    if not result.get('history') or not isinstance(result['history'][-1].get('t'),(int,float)) or abs(result['history'][-1]['t']-end)>TIME_EPS:
        issues.append('declared-endpoint-history-missing')
    return dict(passed=not issues,declared_endpoint_s=end,issues=issues)

def coverage(times,horizon):
    grid=frozen.P['output_grid_s']
    count=math.floor((horizon+TIME_EPS)/grid)
    expected=[round(k*grid,9) for k in range(count+1)]
    actual=set(times);missing=[t for t in expected if t not in actual]
    return dict(passed=not missing and len(expected)>2,required_grid_count=len(expected),missing_grid_times=missing,grid_s=grid,horizon_s=horizon)

def compare(a,b):
    """`passed` means full comparison; use `prefix_passed` explicitly for prefixes.
    An empty/sparse/truncated intersection cannot certify the declared endpoint.
    """
    try:end=endpoint(a['cfg'])
    except (KeyError,ValueError):return dict(passed=False,full_passed=False,prefix_passed=False,issues=['undeclared-protocol'])
    same=a.get('cfg')==b.get('cfg')
    structure=metadata(a,end)+metadata(b,end)
    ca,cb=completion(a,end),completion(b,end)
    if not same:structure.append('different-initial-condition-or-protocol')
    if structure:
        return dict(passed=False,full_passed=False,prefix_passed=False,issues=structure,completion={'primary':ca,'other':cb})
    horizon=min(a['acceptedTime'],b['acceptedTime'])
    aa={round(r['t'],9):r for r in a['history']};bb={round(r['t'],9):r for r in b['history']}
    times=sorted(aa.keys()&bb.keys());cov=coverage(times,horizon)
    full_cov=coverage(times,end)
    # Numerical kernels and budgets are unchanged. Prefix event checks include
    # only saved events within the common accepted interval, never future events.
    pair=[]
    for result in (a,b):
        copy=dict(result);copy['events']=[e for e in result['events'] if e['t']<=horizon+TIME_EPS];pair.append(copy)
    numerical=frozen.compare(*pair) if times else dict(passed=False,matched_count=0,matched_end=None)
    prefix=bool(numerical['passed'] and cov['passed'])
    full=bool(prefix and ca['passed'] and cb['passed'] and full_cov['passed'] and round(end,9) in times)
    return dict(**{k:v for k,v in numerical.items() if k!='passed'},passed=full,full_passed=full,prefix_passed=prefix,common_coverage=cov,full_coverage=full_cov,completion={'primary':ca,'other':cb},issues=[])

def qualify(results):
    missing=[m for m in METHODS if m not in results]
    if missing:return dict(full_trajectory=False,prefix_qualified=False,status='unqualified',missing_methods=missing,comparisons={})
    comparisons={m:compare(results['fine'],results[m]) for m in METHODS if m!='fine'}
    full=all(c['full_passed'] for c in comparisons.values())
    prefix=all(c['prefix_passed'] for c in comparisons.values())
    return dict(full_trajectory=full,prefix_qualified=prefix,status='full' if full else 'prefix-only' if prefix else 'unqualified',missing_methods=[],comparisons=comparisons)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cases=json.loads((INPUT/'cases.json').read_text());checks=[]
    for case in cases:
        ident=case['id'];results={m:json.loads((INPUT/f'{ident}-{m}.json').read_text()) for m in METHODS}
        qualification=qualify(results)
        # Recheck the original physical gates against unchanged raw trajectories.
        balances={m:frozen.balance(results[m]) for m in METHODS}
        quad=results['Radau']['independent_quadrature']
        retention=all(r['failure'] is None or (r['acceptedTime']==r['failure']['acceptedTime'] and r['history'][-1]['z']==r['failure']['acceptedState'] and r['history'][-1]['t']==r['acceptedTime']) for r in results.values())
        physical=all(b['passed'] for b in balances.values()) and quad['passed'] and retention
        if not physical:qualification.update(full_trajectory=False,prefix_qualified=False,status='unqualified')
        passed=physical and qualification['prefix_qualified']
        checks.append(dict(name=ident,passed=bool(passed),**qualification,balances=balances,independent_quadrature=quad,last_accepted_state_retained=retention))
        print(ident,passed,qualification['status'],flush=True)
    sources=['education/tools/audit_vertical_force_completion.py','education/tools/audit_vertical_force.py','education/tools/vertical_force_reference.py','education/web/vertical-force-model.js','education/data/vertical-force-command-v1/protocol.json','education/research/mechanical-closure/vertical-force-command-protocol.md','education/data/millard-reference-v1/review/native-controls.json']
    inputs=[INPUT/'cases.json']+[INPUT/f"{c['id']}-{m}.json" for c in cases for m in METHODS]
    receipt=dict(passed=all(c['passed'] for c in checks),checks=checks,full_presets=sum(c['full_trajectory'] for c in checks),prefix_only_presets=[c['name'] for c in checks if c['status']=='prefix-only'],required_methods=list(METHODS),source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},early_terminal_event_policy='none declared; brake events are intermediate',time_metadata_precision_s=TIME_EPS,physics_gains_tolerances_events_changed=False)
    (OUT/'completion-validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if not receipt['passed']:raise SystemExit('FAILED completion/prefix audit; retained evidence')

if __name__=='__main__':main()

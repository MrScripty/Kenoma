#!/usr/bin/env python3
"""Authored independent numerical replay/comparison, never full qualification."""
import hashlib
import itertools
import json
import math
import numpy as np
from run_combined_incoming_exploratory import DATA, OUT, ROOT, protocol, verify_inputs
from run_ordinary_crossing_consistency import replay_dense
from audit_filippov_bounded_experiment import balances
from vertical_force_reference import output as independent_output
from audit_activation_equality_diagnostic import crossing_compare

NAMES = ['y_m', 'w_m_per_s', 'a', 'q', 'FT_N', 'I', 'raw']


def grid_map(r):
    return {round(x['t'], 9): x for x in r['history'] if abs(x['t'] / .001 - round(x['t'] / .001)) < 1e-7}


def delta(x, y):
    return np.r_[np.array(x['z'][:4]) - y['z'][:4], x['FT'] - y['FT'],
                 x['z'][4] - y['z'][4], x['uraw'] - y['uraw']]


def event_map(r):
    events = {c['type']: c for c in r['events']}
    if r.get('candidate'):
        events['attracting'] = r['candidate']
    return events


def compare(a, b, windows=None):
    p = protocol()
    gates = np.array(p['state_gates'])
    ma, mb = grid_map(a), grid_map(b)
    common = sorted(ma.keys() & mb.keys())
    segments = {}
    plateau = float(ma[.2]['z'][4] - mb[.2]['z'][4]) if .2 in ma and .2 in mb else None
    for name, (left, right) in (windows or p['windows']).items():
        times = [t for t in common if left - 1e-12 <= t and (right is None or t <= right + 1e-12)]
        if not times:
            segments[name] = dict(samples=0, missing=True, all_state_gates_passed=False)
            continue
        values = np.array([delta(ma[t], mb[t]) for t in times])
        maximum = np.max(np.abs(values), axis=0)
        witnesses = {}
        for label, j in [('I', 5), ('raw', 6), ('FT_N', 4)]:
            k = int(np.argmax(np.abs(values[:, j])))
            v = values[k]
            witnesses[label] = dict(t=times[k], absolute_error=abs(float(v[j])),
                                    signed_I=float(v[5]), signed_raw=float(v[6]), signed_FT_N=float(v[4]),
                                    signed_force_term_to_raw=float(-.004 * v[4]),
                                    raw_identity_residual=float(v[6] - v[5] + .004 * v[4]))
        segments[name] = dict(samples=len(times), first_s=times[0], last_s=times[-1],
                              max_errors=dict(zip(NAMES, maximum.tolist())),
                              margins=dict(zip(NAMES, (gates - maximum).tolist())),
                              witnesses=witnesses, all_state_gates_passed=bool(np.all(maximum <= gates)),
                              controller_mismatches=sum(ma[t]['controller_mode'] != mb[t]['controller_mode'] for t in times),
                              frozen_anchor_signed_I=plateau,
                              supplemental_max_I_increment_from_frozen_anchor=float(np.max(np.abs(values[:, 5] - plateau))) if plateau is not None else None,
                              anchor_subtraction_is_not_state_correction=True)
    ea, eb = event_map(a), event_map(b)
    signed_times = {kind: ea[kind]['t'] - eb[kind]['t'] for kind in ea.keys() & eb.keys()}
    maxima = {name: max(s.get('max_errors', {}).get(name, 0.) for s in segments.values()) for name in NAMES}
    return dict(segments=segments, max_errors=maxima, gates=dict(zip(NAMES, gates.tolist())),
                margins={n: float(gates[j] - maxima[n]) for j, n in enumerate(NAMES)},
                all_windows_passed=all(s['all_state_gates_passed'] for s in segments.values()),
                signed_event_time_differences_s=signed_times,
                event_margins_s={kind: 2e-6 - abs(t) for kind, t in signed_times.items()},
                event_gates_passed=bool(signed_times) and all(abs(t) <= 2e-6 for t in signed_times.values()),
                signed_absolute_time_samples={str(t): dict(delta_I=float(delta(ma[t], mb[t])[5]),
                                                           delta_raw=float(delta(ma[t], mb[t])[6]),
                                                           delta_FT_N=float(delta(ma[t], mb[t])[4]))
                                              for t in [.002, .003, .107, .108, .2, .249, .25, .261] if t in ma and t in mb},
                same_absolute_time=True, event_alignment=False, qualified=False)


def audit_run(r):
    p = protocol()
    issues = []
    if r.get('failure'):
        issues.append('retained-physical-or-event-failure')
    from run_filippov_bounded_experiment import CASES
    if r.get('cfg') != CASES['mass-1']:
        issues.append('initialization-mismatch')
    if [e['type'] for e in r['events']] != ['activation-equality', 'ordinary-outward', 'ordinary-inward']:
        issues.append('unexpected-accepted-event-order')
    c = r.get('candidate')
    if c is None or c['accepted'] or c.get('classification') != 'attracting':
        issues.append('missing-or-accepted-attracting-candidate')
    if c is not None and not r['acceptedTime'] < c['t'] <= .264:
        issues.append('invalid-held-candidate-time')
    times = set(grid_map(r))
    missing = [round(k * .001, 9) for k in range(262) if round(k * .001, 9) not in times]
    if missing:
        issues.append('missing-original-witness-grid')
    if r['qualified'] or r['sliding_allowed'] or any(row['mode'] != 'incoming' for row in r['history']):
        issues.append('prohibited-qualification-or-mode')
    grid_error = 0.
    grid_samples = 0
    force_error = 0.
    poly_error = 0.
    restart_error = 0.
    rows = grid_map(r)
    restart_records = []
    for interval in r['accepted_intervals']:
        for k in range(math.floor((interval['start'] + 1e-10) * 1000) + 1,
                       math.floor((interval['end'] + 1e-10) * 1000) + 1):
            t = round(k * .001, 9)
            if t not in rows:
                continue
            z = replay_dense(interval['dense'], t)
            grid_error = max(grid_error, float(np.max(np.abs(z - rows[t]['z']))))
            o = independent_output(z, r['cfg'], {'target': r['cfg']['target']})
            force_error = max(force_error, abs(o['FT'] - rows[t]['FT']), abs(o['residual']))
            grid_samples += 1
    for aux in r['combined_arbitrations']:
        selected = min(aux['events'], key=lambda e: e['bracket'][0])
        if 'x' not in selected:
            continue
        z = replay_dense(aux['dense'], selected['t'])
        error = float(np.max(np.abs(z - selected['x'])))
        poly_error = max(poly_error, error)
        width = selected['bracket'][1] - selected['bracket'][0]
        if selected['kind'] == 'activation-equality':
            if width > 1e-12 or abs(selected['g']) > 1e-13 or selected['iterations'] > 32 or max(selected['one_sided_normals_per_s'].values()) >= -1e-8:
                issues.append('original-activation-event-gate-failure')
        elif selected['kind'] in ['ordinary-outward', 'ordinary-inward', 'attracting']:
            limits = (1e-7, 1e-9) if selected['kind'] == 'attracting' else (1e-12, 1e-13)
            if width > limits[0] or abs(selected['H']) > limits[1] or selected['iterations'] > 32:
                issues.append('original-controller-event-gate-failure')
        if aux['decision']['decision'] not in ['activation-prefix', 'ordinary-prefix']:
            continue
        following = [i for i in r['accepted_intervals'] if i['start'] == selected['t']]
        saved = [row for row in r['history'] if row['t'] == selected['t']]
        if len(following) != 1 or len(saved) != 1:
            issues.append('missing-exact-continuous-restart')
            continue
        re = float(np.max(np.abs(np.array(following[0]['dense']['y_old']) - selected['x'])))
        se = float(np.max(np.abs(np.array(saved[0]['z']) - selected['x'])))
        restart_error = max(restart_error, re, se)
        restart_records.append(dict(kind=selected['kind'], time=selected['t'],
                                    all_eleven_coordinates_retained=re == 0 and se == 0,
                                    restart_error=re, saved_error=se,
                                    incoming_activation_branch=aux['incoming_activation_branch'],
                                    incoming_controller_mode=aux['incoming_controller_mode'],
                                    pending_remainder_end=aux['pending_remainder_end']))
    frozen = [row for row in r['history'] if row['controller_mode'] == 'frozen']
    frozen_error = max((abs(row['z'][4] - frozen[0]['z'][4]) for row in frozen), default=float('inf'))
    if frozen_error != 0:
        issues.append('frozen-integral-memory-changed')
    if grid_error > 1e-12 or poly_error > 1e-12 or restart_error != 0 or force_error > 1e-7:
        issues.append('dense-replay-or-continuity-failure')
    balance = balances(r)
    if not balance['passed']:
        issues.append('original-balance-or-quadrature-gate-failure')
    return dict(passed=not issues, issues=issues, missing_grid_times=missing,
                dense_grid_samples=grid_samples, dense_grid_error=grid_error,
                event_polynomial_error=poly_error, exact_restart_error=restart_error,
                restarts=restart_records, frozen_I_change=frozen_error,
                independent_force_replay_error_N=force_error, balances=balance,
                accepted_intervals=len(r['accepted_intervals']), accepted_stage_records_retained=True,
                qualified=False)


def render(receipt):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    p = protocol()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout='constrained')
    labels = list(p['windows'])
    for ax, rep in zip(axes, p['representations']):
        for method in p['methods'][:-1]:
            a, b = rep + '/' + method, rep + '/Radau'
            record = receipt['comparisons'].get(a + ' vs ' + b)
            if record is None:
                record = receipt['comparisons'][b + ' vs ' + a]
            ax.plot(range(len(labels)), [max(record['segments'][s].get('max_errors', {}).get('I', float('nan')), 1e-17) for s in labels], 'o-', label=method)
        ax.axhline(1e-9, ls=':', color='#555', label='Original I gate')
        ax.set(yscale='log', xticks=range(len(labels)), xticklabels=['before A', 'A window', 'after A', 'outward', 'frozen', 'inward', 'after inward'], title=rep, ylabel='Max |ΔI| versus combined Radau')
        ax.tick_params(axis='x', rotation=25)
        ax.grid(alpha=.2)
        ax.legend(fontsize=7)
    fig.suptitle('Combined incoming exploration — historical independent raw replay incomplete\nAttracting states held unaccepted; no sliding or anatomical qualification', fontsize=11)
    for ext in ['png', 'svg']:
        fig.savefig(OUT / ('combined-refinement.' + ext), dpi=170)
    svg = OUT / 'combined-refinement.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    plt.close(fig)


def main():
    verify_inputs()
    p = protocol()
    results, inputs, checks, controls, crossings = {}, {}, {}, {}, {}
    for rep, method in itertools.product(p['representations'], p['methods']):
        key = rep + '/' + method
        path = OUT / f'mass-1-{rep}-{method}.json'
        r = json.loads(path.read_text())
        results[key] = r
        inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        checks[key] = audit_run(r)
        for label, control_path in [('ordinary-only', p['ordinary_baselines']['mass-1/' + key]),
                                    ('activation-only', p['activation_baselines']['split/' + key])]:
            path = ROOT / control_path
            old = json.loads(path.read_text())
            inputs[control_path] = hashlib.sha256(path.read_bytes()).hexdigest()
            windows = {'crossing': [0, .003], 'propagation': [.003, .107]} if label == 'activation-only' else None
            controls[key + ' vs ' + label] = compare(r, old, windows)
        if method.startswith('RK4') and r.get('activation_event'):
            for reference in p['methods'][4:]:
                path = ROOT / p['activation_baselines']['split/' + rep + '/' + reference]
                crossings[key + ' vs old split/' + rep + '/' + reference] = crossing_compare(r, json.loads(path.read_text()))
        print('AUDIT', key, checks[key]['passed'], checks[key]['issues'], flush=True)
    comparisons = {a + ' vs ' + b: compare(results[a], results[b]) for a, b in itertools.combinations(results, 2)}
    worst = {name: max(c['max_errors'][name] for c in comparisons.values()) for name in NAMES}
    passing = sum(c['all_windows_passed'] and c['event_gates_passed'] for c in comparisons.values())
    ratios = {}
    for rep in p['representations']:
        ladder = [comparisons[rep + '/' + a + ' vs ' + rep + '/' + b] for a, b in zip(p['methods'][:3], p['methods'][1:4])]
        ratios[rep] = {window: {name: dict(errors=[c['segments'][window].get('max_errors', {}).get(name) for c in ladder],
                                           ratios=[ladder[j]['segments'][window]['max_errors'][name] / ladder[j+1]['segments'][window]['max_errors'][name] if ladder[j+1]['segments'][window]['max_errors'][name] > 0 else None for j in [0, 1]])
                               for name in ['I', 'raw', 'a', 'FT_N']} for window in p['windows']
                      if all(window in c['segments'] and not c['segments'][window].get('missing') for c in ladder)}
    receipt = dict(scope='Exploratory incoming interaction only; authored numerical checks pending independent review',
                   historical_review_limitation=p['historical_review_limitation'], independent_raw_replay_complete=False,
                   protocol_sha256=hashlib.sha256((DATA / 'protocol.json').read_bytes()).hexdigest(), input_sha256=inputs,
                   run_checks=checks, comparisons=comparisons, control_comparisons=controls,
                   activation_crossing_step_comparisons=crossings, adjacent_refinement_ratios=ratios,
                   required_cells=12, executed_cells=len(results), required_pairs=66,
                   pairs_passing_authored_state_and_event_gates=passing, worst_pairwise_maxima=worst,
                   incoming_consistency_authored_checks_passed=all(c['passed'] for c in checks.values()) and passing == 66,
                   accepted_sliding_states=0, qualified_trajectories=0, fourth_order_qualified=False)
    target = OUT / 'analysis.json'
    if target.exists():
        raise ValueError('Refuse to overwrite combined analysis evidence')
    target.write_text(json.dumps(receipt, indent=2) + '\n')
    render(receipt)
    print('PAIRS', passing, '/66', 'worst', worst, 'full qualification false', flush=True)


if __name__ == '__main__':
    main()

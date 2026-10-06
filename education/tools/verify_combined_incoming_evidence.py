#!/usr/bin/env python3
"""Second numerical receipt check: own polynomial and comparison implementation.

This local authored replay does not represent completion of historical independent
review. It neither invokes the combined engine nor reruns a failed trajectory.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path
import numpy as np
from vertical_force_reference import ROOT, output, P

DATA = ROOT / 'education/data/combined-incoming-exploratory-v1'
OUT = DATA / 'review'


def polynomial(d, t):
    u = (t - d['left_s']) / (d['right_s'] - d['left_s'])
    values = []
    for j, old in enumerate(d['y_old']):
        if d['kind'] == 'RK4-cubic':
            v = u * (d['coefficients'][0][j] + u * (d['coefficients'][1][j] + u * d['coefficients'][2][j]))
        elif d['kind'] == 'Radau-power':
            v = 0.
            for q in reversed(d['Q'][j]):
                v = u * (v + q)
        elif d['kind'] == 'DOP853-nested':
            v = 0.
            for k, f in enumerate(reversed(d['F'])):
                v = (v + f[j]) * (u if k % 2 == 0 else 1 - u)
        else:
            raise ValueError('Unknown polynomial')
        values.append(old + v)
    return np.array(values)


def derivative(stage, interval, cfg):
    z = stage['z']
    o = output(z, cfg, {'target': cfg['target']})
    a = min(1., max(.01, z[2]))
    tau = .01 * (.5 + 1.5 * a) if interval['activation_branch'] == 'activation' else .04 / (.5 + 1.5 * a)
    return np.array([z[1], o['acceleration'], (o['u'] - a) / tau, 10 * o['v'],
                     8 * o['e'] if interval['controller_mode'] == 'integrating' else 0.,
                     o['Pactive'], o['D'], o['loadPower'], o['fiberPower'], o['tendonPower'],
                     o['FT'] - cfg['m'] * P['gravity_m_per_s2']])


def verify_run(r):
    previous_t = 0.
    previous_x = np.array(r['history'][0]['z'])
    grid = {round(row['t'], 9): row for row in r['history'] if abs(row['t'] * 1000 - round(row['t'] * 1000)) < 1e-7}
    chain_error = grid_error = stage_coefficient_error = 0.
    reproduced = stages = 0
    frozen_coefficients = 0.
    for interval in r['accepted_intervals']:
        if interval['start'] != previous_t or not interval['end'] > interval['start']:
            raise ValueError('Noncontiguous or nonadvancing accepted chain')
        d = interval['dense']
        chain_error = max(chain_error, float(np.max(np.abs(np.array(d['y_old']) - previous_x))))
        for k in range(math.floor((interval['start'] + 1e-10) * 1000) + 1, math.floor((interval['end'] + 1e-10) * 1000) + 1):
            t = round(k * .001, 9)
            if t not in grid:
                raise ValueError('Missing accepted grid witness')
            grid_error = max(grid_error, float(np.max(np.abs(polynomial(d, t) - grid[t]['z']))))
            reproduced += 1
        if d['kind'] == 'RK4-cubic':
            ss = interval['stages']
            if len(ss) != 4:
                raise ValueError('Actual four RK stages missing')
            h = d['right_s'] - d['left_s']
            if max(abs(s['t'] - t) for s, t in zip(ss, [d['left_s'], d['left_s'] + h/2, d['left_s'] + h/2, d['right_s']])) > 2e-12:
                raise ValueError('Actual RK stage time differs')
            a, b, c, e = [derivative(s, interval, r['cfg']) for s in ss]
            coeff = np.stack([h*a, h*(-1.5*a+b+c-.5*e), h*(2*a/3-2*(b+c)/3+2*e/3)])
            stage_coefficient_error = max(stage_coefficient_error, float(np.max(np.abs(coeff - d['coefficients']))))
            stages += 4
        if interval['controller_mode'] == 'frozen':
            if d['kind'] == 'RK4-cubic':
                values = [c[4] for c in d['coefficients']]
            elif d['kind'] == 'DOP853-nested':
                values = [f[4] for f in d['F']]
            else:
                values = d['Q'][4]
            frozen_coefficients = max(frozen_coefficients, max(map(abs, values)))
        previous_t = interval['end']
        previous_x = polynomial(d, previous_t)
    end_error = float(np.max(np.abs(previous_x - r['history'][-1]['z'])))
    if previous_t != r['acceptedTime'] or chain_error > 1e-12 or grid_error > 1e-12 or stage_coefficient_error > 1e-12 or end_error > 1e-12 or frozen_coefficients != 0:
        raise ValueError('Polynomial chain/stage replay/frozen memory failure')
    return dict(accepted_polynomials=len(r['accepted_intervals']), independently_recomputed_RK_stage_rates=stages,
                RK_coefficients_error=stage_coefficient_error, chain_error=chain_error,
                grid_error=grid_error, reproduced_grid_states=reproduced,
                endpoint_error=end_error, frozen_I_polynomial_coefficients=frozen_coefficients)


def run_replay(path, r, fresh=False):
    """Record each expensive independent replay once, bound to exact bytes.

`--fresh` recomputes it and compares with its retained receipt; nothing is
overwritten. This permits replaying completed cells while the matrix continues.
"""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    verifier = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    dest = OUT / 'run-replays' / path.name
    if dest.exists():
        old = json.loads(dest.read_text())
        if old['result_sha256'] != digest or old['verifier_sha256'] != verifier:
            raise ValueError('Retained replay source identity differs')
        if fresh and verify_run(r) != old['replay']:
            raise ValueError('Fresh replay differs from retained evidence')
        return old['replay']
    checked = verify_run(r)
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(dict(result_sha256=digest, verifier_sha256=verifier,
                                   replay=checked), indent=2) + '\n')
    return checked


def verify_comparison(a, b, record):
    ma = {round(r['t'], 9): r for r in a['history'] if abs(r['t'] * 1000 - round(r['t'] * 1000)) < 1e-7}
    mb = {round(r['t'], 9): r for r in b['history'] if abs(r['t'] * 1000 - round(r['t'] * 1000)) < 1e-7}
    maximum_disagreement = 0.
    tables = 0
    for window, table in record['segments'].items():
        if table.get('missing'):
            continue
        times = [t for t in sorted(ma.keys() & mb.keys()) if table['first_s'] - 1e-12 <= t <= table['last_s'] + 1e-12]
        if len(times) != table['samples']:
            raise ValueError('Comparison samples differ')
        differences = []
        for t in times:
            x, y = ma[t], mb[t]
            differences.append([*[x['z'][j] - y['z'][j] for j in range(4)], x['FT'] - y['FT'], x['z'][4] - y['z'][4], x['uraw'] - y['uraw']])
        values = np.array(differences)
        maxima = np.max(np.abs(values), axis=0)
        names = ['y_m', 'w_m_per_s', 'a', 'q', 'FT_N', 'I', 'raw']
        for j, name in enumerate(names):
            maximum_disagreement = max(maximum_disagreement, abs(float(maxima[j]) - table['max_errors'][name]))
            if record['gates'][name] - float(maxima[j]) != table['margins'][name]:
                raise ValueError('Original margin reproduction differs')
        for name, j in [('I', 5), ('raw', 6), ('FT_N', 4)]:
            k = int(np.argmax(np.abs(values[:, j])))
            witness = table['witnesses'][name]
            if witness['t'] != times[k] or witness['signed_I'] != values[k, 5] or witness['signed_raw'] != values[k, 6] or witness['signed_FT_N'] != values[k, 4]:
                raise ValueError('Signed maximum witness differs')
        tables += 1
    if maximum_disagreement != 0:
        raise ValueError('Comparison maxima differ')
    return tables


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--run-only', help='Replay one completed cell as representation/method')
    parser.add_argument('--fresh', action='store_true', help='Recompute retained per-run replay instead of reusing its bound receipt')
    args = parser.parse_args()
    p = json.loads((DATA / 'protocol.json').read_text())
    if args.run_only:
        rep, method = args.run_only.split('/')
        if rep not in p['representations'] or method not in p['methods']:
            raise ValueError('Undeclared replay cell')
        path = OUT / f'mass-1-{rep}-{method}.json'
        checked = run_replay(path, json.loads(path.read_text()), args.fresh)
        print('REPLAY', args.run_only, checked, flush=True)
        return
    analysis = json.loads((OUT / 'analysis.json').read_text())
    for path, digest in analysis['input_sha256'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise ValueError('Analysis input changed')
    results, runs, tables = {}, {}, 0
    for rep, method in itertools.product(p['representations'], p['methods']):
        key = rep + '/' + method
        path = OUT / f'mass-1-{rep}-{method}.json'
        r = json.loads(path.read_text())
        results[key] = r
        runs[key] = run_replay(path, r, args.fresh)
        print('VERIFY POLYNOMIALS', key, runs[key], flush=True)
    if len(analysis['comparisons']) != 66:
        raise ValueError('All 66 candidate pairs required')
    for pair, record in analysis['comparisons'].items():
        a, b = pair.split(' vs ')
        tables += verify_comparison(results[a], results[b], record)
    for pair, record in analysis['control_comparisons'].items():
        key, control = pair.split(' vs ')
        path = p['ordinary_baselines']['mass-1/' + key] if control == 'ordinary-only' else p['activation_baselines']['split/' + key]
        tables += verify_comparison(results[key], json.loads((ROOT / path).read_text()), record)
    receipt = dict(scope='Local authored second implementation replay; historical independent raw review still incomplete',
                   independent_raw_replay_complete=False, original_gates_changed=False,
                   verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   analysis_sha256=hashlib.sha256((OUT / 'analysis.json').read_bytes()).hexdigest(),
                   runs=runs, comparison_window_tables_reproduced=tables,
                   scalar_maxima_reproduced=7*tables, signed_witnesses_reproduced=3*tables,
                   candidate_pairs_reproduced=66, full_qualification=False)
    path = OUT / 'verification.json'
    if path.exists():
        raise ValueError('Refuse to overwrite second replay')
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print('VERIFIED', tables, 'window tables and', 7*tables, 'maxima; full qualification false', flush=True)


if __name__ == '__main__':
    main()

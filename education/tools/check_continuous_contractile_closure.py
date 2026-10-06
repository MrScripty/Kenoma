"""Reload and check new evidence; no ODE, initialization or historical rerun."""
import hashlib
import json
import math
import subprocess
from pathlib import Path

import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/anatomical-arm-v1/review'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bindings(folder):
    manifest = json.loads((folder/'hash-manifest.json').read_text())
    for row in manifest['files']:
        path = ROOT/row['path']
        assert path.stat().st_size == row['bytes'], row['path']
        assert digest(path) == row['sha256'], row['path']
    return len(manifest['files'])


def moments(n, x, w):
    return np.array([math.fsum(w*n), math.fsum(w*(1+x)*n)/.5,
                     math.fsum(w*.5*(1+x)**2*n)/.5])


def continuous():
    folder = BASE/'continuous-strain-ce'
    count = bindings(folder)
    s = json.loads((folder/'summary.json').read_text())
    z = np.load(folder/'matched-densities.npz', allow_pickle=False)
    assert s['result'] == 'PASS_CONTINUUM_QUADRATURE_TIME_AND_TRANSLATION_GATES'
    assert 'failure' not in s and len(s['runs']) == 96
    assert digest(folder/'matched-densities.npz') == s['matchedDensitiesSHA256']
    assert digest(ROOT/'tools/continuous_strain_ce_reference.py') == s['sourceSHA256']
    assert s['nodeCounts'] == [200, 400, 800] and s['maxStepsSeconds'] == [.001, .0005]
    assert s['solver']['rtol'] == 1e-11 and s['solver']['atol'] == 1e-14
    assert s['edgeNodeCount'] == 32
    assert np.array_equal(z['matchedTimesSeconds'], [0,0,.008,.02,.04,.1,.2,.2,.3,.5,1])
    records = {}
    for r in s['runs']:
        name = r['name']
        x, w, n = (z[name+'_'+key] for key in ['x','weights','matchedDensity'])
        assert n.shape == (11,r['count']) and np.min(n) >= 0 and np.isfinite(n).all()
        m = np.array([moments(row,x,w) for row in n])
        assert np.all(m[:,0] <= r['N'])
        assert np.max(np.abs(m-r['matchedMoments'])) <= 2e-12
        assert r['initialWeightedRHSL1PerSecond'] <= 1e-10
        assert max(r['initialAdaptiveMomentAbsoluteDifferences']) <= 1e-10
        for key, i, j in [('loading',0,1),('reversal',6,7)]:
            q = r[key]
            before, after, h = np.array(q['beforeMoments']), np.array(q['afterMoments']), q['displacement']
            assert np.max(np.abs(before-m[i])) <= 2e-12
            assert np.max(np.abs(after-m[j])) <= 2e-12
            escape = np.array([q['escapedMass'],q['escapedSignedForceMoment'],q['escapedElasticEnergy']])
            expected = [-escape[0], before[0]*h/.5-escape[1],
                        before[1]*h+before[0]*h*h-escape[2]]
            assert np.max(np.abs(after-before-expected)) <= 2e-12
            assert escape[0] >= 0 and escape[2] >= 0 and q['interpolationWork'] == 0
        aux = z[name+'_matchedAuxiliaryDensity']
        assert aux.shape == (6,r['count']+32) and np.isfinite(aux).all() and np.min(aux) >= 0
        for segment, array in zip(r['segments'],['firstAcceptedTimes','secondAcceptedTimes']):
            t = z[name+'_'+array]
            assert t[0] == segment['startSeconds'] and t[-1] == segment['requestedTerminalSeconds']
            assert np.all(np.diff(t) > 0) and len(t) == segment['acceptedNodes']
            assert segment['actualTerminalSeconds'] == segment['requestedTerminalSeconds']
            assert segment['minimumDensity'] >= 0 and segment['mainBRange'][1] <= r['N']
            identity = segment['acceptedStateArray']
            width = (2*r['count']+32) if array == 'firstAcceptedTimes' else r['count']
            assert identity['shape'] == [len(t),width] and identity['nbytes'] == len(t)*width*8
        records[r['R'],r['count'],r['pCa'],r['delta'],r['maxStepSeconds']] = m
    for key, m in records.items():
        R,n,pca,delta,step = key
        if step == .001:
            error = np.max(np.abs(m-records[R,n,pca,delta,.0005]),axis=0)
            assert np.all(error <= [1e-10,2e-10,2e-10])
        if step == .0005 and n in (200,400):
            assert np.max(np.abs(m-records[R,n*2,pca,delta,step])) <= 1e-9
    assert len(s['finiteBinComparisons']) == 144
    for name, h in s['comparisonSourceHashes'].items():
        assert digest(BASE/'conserved-ce-trajectory'/name) == h
    separated = json.loads((folder/'bin-spatial-separation.json').read_text())
    assert separated['referencesCompared'] == len(separated['rows']) == 48
    assert len(separated['groups']) == 16
    assert separated['analysisSourceSHA256'] == digest(ROOT/'tools/analyze_continuous_ce_bin_separation.py')
    for name,h in separated['inputSHA256'].items():
        assert digest(ROOT/name) == h
    bins = np.load(BASE/'conserved-ce-trajectory/independent-reference.npz',allow_pickle=False)
    old = np.load(BASE/'conserved-ce-trajectory/matched-states.npz',allow_pickle=False)
    for q in separated['rows']:
        x = old[f"R{q['R']:g}-dx{q['dx']:g}_x"]
        p = bins[q['name']+'-maxstep0.0005']
        force = np.array([math.fsum(row*(1+x))/.5 for row in p])
        target = records[q['R'],800,q['pCa'],q['delta'],.0005][:,1]
        error = (force-force[0])-(target-target[0])
        assert np.max(np.abs(error-q['signedMatchedForceResponseErrors'])) <= 2e-12
        assert abs(q['ownInitialForceIncrement']-abs(force[1]-force[0])) <= 2e-12
    render = json.loads((folder/'render-receipt.json').read_text())
    for name,h in render['files'].items():
        assert digest(folder/name) == h
    assert render['pngVisuallyInspected'] and render['pdfRasterVisuallyInspected']
    return dict(manifestBindings=count, continuousHistories=96,
                oldMatchedMomentComparisons=144, isolatedBinReferenceComparisons=48, acceptedNodes=sum(
                    q['acceptedNodes'] for r in s['runs'] for q in r['segments']))


def initializer():
    folder = BASE/'source-ce-series-initialization'
    count = bindings(folder)
    s = json.loads((folder/'summary.json').read_text())
    assert s['status'] == 'PASSED' and s['precision_decimal_digits'] == 60
    assert s['initializer_case_count'] == len(s['cases']) == 27
    assert s['invalid_input_rejection_count'] == len(s['invalid_input_rejections']) == 56
    assert s['se_boundary_probe_count'] == len(s['se_boundary_probes']) == 4
    assert s['stationary_condition_count'] == len(s['stationary_conditions']) == 3
    assert digest(ROOT/'tools/source_ce_series_initialization.py') == s['runner_sha256']
    with mp.workdps(60):
        for q in s['stationary_conditions']:
            B,N,M = (mp.mpf(q[k]) for k in ['B','N','M'])
            assert 0 <= B <= N <= 1 and 0 <= M <= 1 and abs(B+M-1) <= mp.mpf('1e-50')
            assert mp.mpf(q['force_moment_variance']) >= 0
            for key in ['population_balance_abs','kinetic_residual_max_abs','attached_integral_abs']:
                assert mp.mpf(q[key]) <= mp.mpf('1e-12')
            assert q['kinetic_residual_sample_count'] == 129
        for q in s['cases']:
            ce,pe,se,total = (mp.mpf(q[k]) for k in ['force_ce','force_pe','force_se','force_total'])
            assert abs(se-ce-pe) <= mp.mpf('1e-12') and abs(total-ce-pe) <= mp.mpf('1e-12')
            assert mp.mpf(q['e_se0']) >= 0
            assert mp.mpf(q['force_balance_abs']) <= mp.mpf('1e-12')
            assert mp.mpf(q['inverse_abs']) <= mp.mpf('1e-12')
            assert all(mp.mpf(v) <= mp.mpf('1e-8') for v in q['tangent_relative_errors'].values())
            assert all(mp.mpf(q[k]) >= 0 for k in ['fast_ce','fast_pe','fast_parallel','fast_se','fast_whole_series'])
        for q in s['se_boundary_probes']:
            assert abs(mp.mpf(q['result_force'])-mp.mpf(q['input_force'])) <= mp.mpf('1e-12')
            assert mp.mpf(q['roundtrip_abs']) <= mp.mpf('1e-12')
    assert s['physical_F0_gamma_area'] == 'symbolic/unselected'
    return dict(manifestBindings=count, initializerCases=27, intendedRejections=56, inverseBoundaryProbes=4)


if __name__ == '__main__':
    result = dict(result='PASS_CONTINUOUS_CONTRACTILE_EVIDENCE_CLOSURE',
                  continuous=continuous(), initializer=initializer(),
                  physicalAndAnatomicalQualification=False)
    changed = subprocess.check_output(['git','diff','--name-status',
        '154d805386bdbe8b2c950af3d883c2ae54c376a8','--'],cwd=ROOT,text=True).splitlines()
    assert all(line.startswith('A\teducation/') for line in changed), changed
    print(json.dumps(result))

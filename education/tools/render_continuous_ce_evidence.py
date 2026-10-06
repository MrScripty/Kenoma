"""Read-only analysis and static render of qualified continuous-CE receipts."""
import hashlib
import json
from pathlib import Path

import fitz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/anatomical-arm-v1/review/continuous-strain-ce'
OLD = ROOT/'data/anatomical-arm-v1/review/conserved-ce-trajectory'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    s = json.loads((OUT/'summary.json').read_text())
    old = json.loads((OLD/'summary.json').read_text())
    assert s['result'] == 'PASS_CONTINUUM_QUADRATURE_TIME_AND_TRANSLATION_GATES'
    times = np.array(s['matchedTimesSeconds'])
    grids = {g['name']:g for g in old['grids']}
    records = {(r['R'],r['count'],r['pCa'],r['delta'],r['maxStepSeconds']):r for r in s['runs']}
    comparisons = {q['name']:q for q in s['finiteBinComparisons']}
    analysis = dict(result='ASSESS_CONTINUOUS_STRAIN_AND_OLD_BIN_MOMENTS',
        histories=len(s['runs']), oldComparisons=len(comparisons),
        maximumInitialWeightedRHSL1PerSecond=max(r['initialWeightedRHSL1PerSecond'] for r in s['runs']),
        maximumJumpIdentityError=max(max(r[key]['identityAbsoluteErrors']) for r in s['runs'] for key in ['loading','reversal']),
        maximumTimePairMomentErrors=np.max([q['momentAbsoluteErrors'] for q in s['timeRefinement']],axis=0).tolist(),
        maximumQuadraturePairMomentErrors=np.max([e for q in s['quadratureRefinement'] for e in q['countPairMomentAbsoluteErrors']],axis=0).tolist(),
        maximumExtentMomentDifferences=np.max([q['momentAbsoluteDifferences'] for q in s['extentDiagnostics']],axis=0).tolist(),
        minimumAcceptedDensity=min(q['minimumDensity'] for r in s['runs'] for q in r['segments']),
        acceptedNodes=sum(q['acceptedNodes'] for r in s['runs'] for q in r['segments']),
        forceErrorNormalization='Own initial force increment |F(0+)-F(0-)|; subtract each model own equilibrium before response comparison',
        physicalAndAnatomicalQualification=False,
        scope='Finite-domain held-N overlap-one source-informed direct CE; no PE/SE dynamics, human/SI calibration or chemical-energy closure')
    rows = []
    for dx in [.04,.02,.01]:
        selected = [comparisons[c['name']] for c in old['cases'] if c['dt']==.001 and grids[c['grid']]['R']==3 and grids[c['grid']]['dx']==dx]
        errors = [q['baselineSubtractedForceErrorOverInitialForceIncrement'] for q in selected]
        rows.append(dict(dx=dx, count=len(errors), relativeForceResponseErrorRange=[min(errors),max(errors)]))
    analysis['oldFinestTimeResponseByBinWidth'] = rows
    for path in [OUT/'continuous-analysis.json',OUT/'continuous-reference.png',OUT/'continuous-reference.pdf',OUT/'continuous-reference-pdf-raster.png']:
        if path.exists():
            raise FileExistsError('preserve existing render/analysis: '+str(path))
    (OUT/'continuous-analysis.json').write_text(json.dumps(analysis,indent=2)+'\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig, axes = plt.subplots(2,2,figsize=(12,8.4))
    colors = ['#9a5a13','#247d82','#65499c']
    for ax,pca in zip(axes[0],[4.5,6.1]):
        reference = np.asarray(records[3.,800,pca,.001,.0005]['matchedMoments'])[:,1]
        ax.plot(times,reference-reference[0],color='#142a3f',lw=2.6,label='Continuous: 800 nodes, max step 0.0005 s')
        for dx,color in zip([.04,.02,.01],colors):
            case = next(c for c in old['cases'] if c['pCa']==pca and c['delta']==.001 and c['dt']==.001 and grids[c['grid']]['R']==3 and grids[c['grid']]['dx']==dx)
            force=np.array(case['matchedForces'])
            ax.plot(times,force-force[0],lw=1.2,ls='--',color=color,label=f'Preserved bins: dx={dx:g}, dt=0.001 s')
        ax.axvline(.2,color='#888',lw=.8,ls=':')
        ax.set(title=f'Matched-time force response · pCa {pca:g}',xlabel='Time (s)',ylabel='Normalized force minus own equilibrium')
        ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        ax.grid(alpha=.16)
    axes[0,0].legend(fontsize=8,loc='upper right')
    ax=axes[1,0]
    worst_time=[max(max(q['momentAbsoluteErrors']) for q in s['timeRefinement'] if q['count']==n) for n in [200,400,800]]
    worst_space=[max(max(q['countPairMomentAbsoluteErrors'][i]) for q in s['quadratureRefinement']) for i in [0,1]]
    ax.semilogy([200,400,800],np.maximum(worst_time,1e-18),'o-',color='#247d82',label='Time pair: max step 0.001 vs 0.0005 s')
    ax.semilogy([400,800],np.maximum(worst_space,1e-18),'s-',color='#65499c',label='Successive quadrature pair')
    ax.axhline(1e-9,color='#65499c',ls=':',lw=1,label='Quadrature gate 1e-9')
    ax.axhline(1e-10,color='#247d82',ls=':',lw=1,label='Strictest time gate 1e-10')
    ax.set(title='New reference refinement receipts',xlabel='Main Gauss nodes',ylabel='Worst absolute moment difference (B, F, E)',xticks=[200,400,800])
    ax.legend(fontsize=8,loc='best');ax.grid(alpha=.16)
    ax=axes[1,1]
    xx=np.array([q['dx'] for q in rows])
    low=np.array([q['relativeForceResponseErrorRange'][0] for q in rows])*100
    high=np.array([q['relativeForceResponseErrorRange'][1] for q in rows])*100
    ax.fill_between(xx,low,high,color='#9a5a13',alpha=.22)
    ax.plot(xx,low,'o-',color='#9a5a13',label='Range over 2 pCa × 4 signed displacements')
    ax.plot(xx,high,'o-',color='#9a5a13')
    ax.set(title='Preserved bins vs continuous reference',xlabel='Bin width dx (dt = 0.001 s, R = 3)',ylabel='Max matched response error (% of own initial jump)',xticks=[.01,.02,.04])
    ax.legend(fontsize=8);ax.grid(alpha=.16)
    fig.suptitle('Continuous-strain CE numerical qualification',fontsize=18,fontweight='bold',y=.98)
    fig.text(.5,.935,'Exact loading at 0 s and reversal at 0.2 s · held capacity · conserved free heads · unchanged gates',ha='center',fontsize=11)
    fig.text(.5,.027,'Dimensionless finite-domain mechanics. Human force/area, PE/SE dynamics, thermodynamics and loaded anatomy remain unqualified.',ha='center',fontsize=9,color='#444')
    fig.tight_layout(rect=[0,.05,1,.915])
    fig.savefig(OUT/'continuous-reference.png',dpi=170)
    fig.savefig(OUT/'continuous-reference.pdf')
    plt.close(fig)
    with fitz.open(OUT/'continuous-reference.pdf') as pdf:
        assert len(pdf)==1
        pdf[0].get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False).save(OUT/'continuous-reference-pdf-raster.png')
    print(json.dumps(analysis))


if __name__=='__main__':
    main()

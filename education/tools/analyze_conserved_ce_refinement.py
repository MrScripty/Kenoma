"""Read-only matched-time response/work analysis and static figure of new evidence."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/anatomical-arm-v1/review/conserved-ce-trajectory'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if (OUT/'refinement-analysis.json').exists():
        raise RuntimeError('refusing to overwrite refinement evidence')
    summary=json.loads((OUT/'summary.json').read_text())
    audit=json.loads((OUT/'independent-audit.json').read_text())
    assert summary['result']=='PASS_CONSERVED_CE_HISTORY_GATES'
    assert audit['result']=='PASS_INDEPENDENT_REFERENCE_AND_STRICT_POPULATION_GATES'
    data=np.load(OUT/'matched-states.npz',allow_pickle=False)
    refs=np.load(OUT/'independent-reference.npz',allow_pickle=False)
    bycase={c['name']:c for c in summary['cases']}
    temporal=[]
    for c in audit['cases']:
        own=data[c['name']]
        ref=refs[c['reference']+'-maxstep0.0005']
        x=data[c['grid']+'_x']
        state_amplitude=float(np.sum(np.abs(ref[1]-ref[0])))
        force_amplitude=float(abs((ref[1]-ref[0])@(1+x)/.5))
        assert min(state_amplitude,force_amplitude)>0
        temporal.append(dict(name=c['name'],grid=c['grid'],pCa=c['pCa'],delta=c['delta'],dt=c['dt'],
                             initialStateL1Perturbation=state_amplitude,initialForcePerturbation=force_amplitude,
                             normalizedStateError=c['maximumMatchedStateL1Error']/state_amplitude,
                             normalizedForceError=c['maximumMatchedForceAbsoluteError']/force_amplitude))
    spatial=[]
    for R in [2.4,3.]:
        for pca in [4.5,6.1]:
            for delta in [.001,-.001,.0005,-.0005]:
                forces=[]
                for dx in [.04,.02,.01]:
                    grid=f'R{R:g}-dx{dx:g}'
                    p=refs[f'{grid}-pCa{pca:g}-delta{delta:g}-maxstep0.0005']
                    forces.append(p@(1+data[grid+'_x'])/.5)
                raw=[float(np.max(np.abs(a-b))) for a,b in zip(forces[:-1],forces[1:])]
                response=[f-f[0] for f in forces]
                increments=[float(np.max(np.abs(a-b))) for a,b in zip(response[:-1],response[1:])]
                spatial.append(dict(R=R,pCa=pca,delta=delta,rawForceDifferences=raw,
                                    rawForceDifferenceRatio=raw[1]/raw[0],
                                    ownBaselineResponseDifferences=increments,
                                    ownBaselineResponseDifferenceRatio=increments[1]/increments[0]))
    work=[]
    for c in summary['cases']:
        dx=next(g['dx'] for g in summary['grids'] if g['name']==c['grid'])
        for event in ['loading','reversal']:
            j=c[event]
            work.append(dict(name=c['name'],dx=dx,event=event,interpolationWork=j['interpolationWork'],
                             percentOfAbsoluteRigidWork=100*j['interpolationWork']/abs(j['rigidTranslationWork'])))
    record=dict(result='ASSESS_MATCHED_TIME_AND_TRANSPORT_WORK',
                inputsSHA256={n:sha(OUT/n) for n in ['summary.json','matched-states.npz','independent-audit.json','independent-reference.npz']},
                analysisSourceSHA256=sha(Path(__file__)),temporal=temporal,finiteBinSpace=spatial,transportWork=work,
                responseNormalization='Error divided by own initial displacement perturbation; not force rescaling or a physiological gate',
                limitations=['Finite-bin references only; no independently continuous-strain transient reference',
                             'Interpolation work is numerical variance, not physical elastic input work',
                             'No PE/SE, SI calibration, anatomical compression/contact or continuum stability qualification'])
    (OUT/'refinement-analysis.json').write_text(json.dumps(record,indent=2)+'\n')
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10})
    fig,axes=plt.subplots(2,2,figsize=(12.7,8.1))
    ax=axes[0,0]
    grid='R3-dx0.01'; x=data[grid+'_x']; t=data['matchedTimesSeconds']
    ref=refs[f'{grid}-pCa4.5-delta0.001-maxstep0.0005']
    f=ref@(1+x)/.5; amp=f[1]-f[0]
    ax.plot(t,(f-f[0])/amp,'k--',lw=1.6,label='Independent bin ODE')
    for dt,color in zip([.004,.002,.001],['#c66c30','#4982a6','#36735c']):
        p=data[f'{grid}-pCa4.5-delta0.001-dt{dt:g}']; ff=p@(1+x)/.5
        ax.plot(t,(ff-ff[0])/amp,'o-',ms=3,lw=.9,color=color,label=f'BE {dt*1000:g} ms')
    ax.set(title='Matched states preserve the reversal history',xlabel='Time (s)',ylabel='Force increment / initial increment',xlim=(0,1))
    ax.axhline(0,color='.8',lw=.6); ax.legend(fontsize=8,loc='upper right')
    ax.text(.99,.02,'pCa 4.5; R=3; dx=.01; delta=+.001',ha='right',va='bottom',transform=ax.transAxes,fontsize=8)
    ax=axes[0,1]
    hs=[.001,.002,.004]
    for pca,color in zip([4.5,6.1],['#36735c','#c66c30']):
        sets=[[r['normalizedStateError'] for r in temporal if r['dt']==h and r['pCa']==pca] for h in hs]
        lo,hi,med=[[func(v) for v in sets] for func in [min,max,np.median]]
        ax.fill_between(np.array(hs)*1000,lo,hi,color=color,alpha=.17)
        ax.loglog(np.array(hs)*1000,med,'o-',color=color,label=f'pCa {pca:g}: median/range')
    guide=np.median([r['normalizedStateError'] for r in temporal if r['dt']==.001])
    ax.loglog([1,4],[guide,4*guide],'k:',lw=1,label='First-order guide')
    ax.set(title='Time error against independent bin dynamics',xlabel='BE timestep (ms)',ylabel='State L1 error / initial perturbation')
    ax.set_xticks([1,2,4],labels=['1','2','4']); ax.legend(fontsize=8)
    ax=axes[1,0]
    for field,color,label,offset in [('rawForceDifferences','#4982a6','Raw force',-.08),
                                     ('ownBaselineResponseDifferences','#c66c30','Own-baseline response',.08)]:
        sets=[[s[field][i] for s in spatial] for i in [0,1]]
        med=np.array([np.median(v) for v in sets]); lo=np.array([min(v) for v in sets]); hi=np.array([max(v) for v in sets])
        ax.errorbar(np.array([0,1])+offset,med,yerr=[med-lo,hi-med],fmt='o-',color=color,capsize=4,label=label)
    ax.set_yscale('log'); ax.set_xticks([0,1],labels=['.04 to .02','.02 to .01'])
    ax.set(title='Bin refinement: baseline can hide response error',xlabel='Adjacent dx pair',ylabel='Maximum matched force difference')
    ax.legend(fontsize=8)
    ax=axes[1,1]
    dxs=[.01,.02,.04]
    sets=[[r['percentOfAbsoluteRigidWork'] for r in work if r['dx']==dx] for dx in dxs]
    ax.fill_between(dxs,[min(v) for v in sets],[max(v) for v in sets],color='#79558d',alpha=.18)
    ax.plot(dxs,[np.median(v) for v in sets],'o-',color='#79558d')
    ax.set(title='Upwind interpolation adds positive work',xlabel='Strain bin width dx',ylabel='Interpolation / |rigid work| (%)')
    ax.set_xticks(dxs,labels=['.01','.02','.04']); ax.set_ylim(bottom=0)
    ax.text(.02,.98,'Both jumps; all cases; median/range',transform=ax.transAxes,va='top',fontsize=8)
    for ax in axes.flat: ax.grid(alpha=.15)
    fig.suptitle('Conserved-head CE prerequisite: step, reversal and refinement',fontsize=16,y=.985)
    fig.text(.5,.02,'144 dimensionless histories; publication medians; M=1-B. No PE/SE, SI scale or anatomical qualification.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.09,right=.98,bottom=.12,top=.90,hspace=.38,wspace=.28)
    fig.savefig(OUT/'conserved-ce-refinement.png',dpi=170)
    fig.savefig(OUT/'conserved-ce-refinement.pdf',metadata={'Title':'Dimensionless conserved-head CE prerequisite','Author':'Kenoma evidence lane'})
    plt.close(fig)
    receipt=dict(analysisSourceSHA256=sha(Path(__file__)),analysisSHA256=sha(OUT/'refinement-analysis.json'),
                 files={n:sha(OUT/n) for n in ['conserved-ce-refinement.png','conserved-ce-refinement.pdf']},
                 figureInches=[12.7,8.1],rasterDPI=170,scope='Static research evidence; no anatomical qualification')
    (OUT/'render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(result=record['result'],cases=len(temporal),spatialGroups=len(spatial),jumpLedgers=len(work))))


if __name__=='__main__': main()

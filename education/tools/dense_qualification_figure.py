"""Render only independently replayed data; record source/output hashes."""
from pathlib import Path
import hashlib,json,os,platform,sys
os.environ.setdefault('MPLCONFIGDIR','/tmp/kenoma-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/kenoma-render-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/anatomical-arm-v1'
OUT=BASE/'review/dense-qualification'
def read(name):return json.loads((BASE/'audit'/name).read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def render():
    coarse_only='--coarse-only' in sys.argv
    out=OUT/'coarse' if coarse_only else OUT
    out.mkdir(parents=True,exist_ok=True)
    coarse=read('anatomical-dense-trajectory-recheck.json')
    pairs=[(coarse,'anatomical-dense-trajectory.json')]
    if not coarse_only:
        fine=read('anatomical-dense-fine-trajectory-recheck.json')
        interpolated=read('anatomical-dense-interpolated-trajectory-recheck.json')
        release=read('anatomical-dense-release-refinement-recheck.json')
        pairs.extend([(fine,'anatomical-dense-fine-trajectory.json'),(interpolated,'anatomical-dense-interpolated-trajectory.json'),(release,'anatomical-dense-release-refinement.json')])
    if any(r['result'] not in ['PASS_DENSE_TRAJECTORY','PASS_PRESERVED_REJECTION','PASS_PRESERVED_BEHAVIOR_REJECTION'] for r,_ in pairs):raise ValueError('Fresh replay required')
    for receipt,source in pairs:
        if receipt['executionReceiptSHA256']!=digest(BASE/'audit'/source):raise ValueError('Stale replay')
    baseline=read('contact-lift-release-recheck.json')
    local=read('anatomical-compression-localization.json')
    integration=read('anatomical-further-integration.json')
    bulk=[read('anatomical-bulk-step-0.5-recheck.json'),read('anatomical-bulk-step-2-recheck.json')]
    enriched=read('anatomical-enriched-step-recheck.json')
    if not coarse_only:
        matched=read('anatomical-dense-matched-times.json')
        if matched['result']!='PASS_ACCEPTED_MATCHED_TIME_COMPARISON':raise ValueError('Fresh matched-time comparison required')
    if enriched['result']!='PASS_ACCEPTED_ENRICHED_COMPARISON':raise ValueError('Fresh enriched comparison required')
    plt.rcParams.update({'font.size':19,'axes.titlesize':20,'svg.hashsalt':'kenoma-dense-qualification-print','axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,axes=plt.subplots(2,2,figsize=(12,9),layout='constrained')
    fig.suptitle('Arm qualification · motion and unresolved compression',fontsize=20)
    held=coarse['held']
    series=[(coarse,'256 points · original\nintervals','#0e7669')]
    if not coarse_only:series.extend([(fine,'256 points · half intervals, target guesses','#ca6234'),(interpolated,'256 points · half intervals, interpolated guesses','#3875b4'),(release,'256 points · release thirds','#72509b')])
    for receipt,label,color in [(baseline,'32 points · original','#758193')]+series:
        rows=receipt['rows'];axes[0,0].plot([0]+[r['timeS'] for r in rows],[held['qRad']*180/np.pi]+[r['qRad']*180/np.pi for r in rows],'.',label=label,color=color,markersize=3,linestyle='--' if 'interpolated' in label else '-')
    axes[0,0].axvline(.13,color='#777',linestyle=':',linewidth=1)
    axes[0,0].text(.135,.18,'effort removed',transform=axes[0,0].get_xaxis_transform(),va='top',fontsize=19)
    axes[0,0].set(title='Accepted angle trajectories',xlabel='Time (s)',ylabel='Joint angle (degrees)')
    if coarse_only:axes[0,0].legend(fontsize=19,loc='upper left')
    else:fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside lower center',ncol=2,fontsize=19)
    for receipt,label,color in series:
        axes[0,1].semilogy([r['timeS'] for r in receipt['rows']],[r['independentResidualN'] for r in receipt['rows']],'.-',label=label,color=color)
    axes[0,1].axhline(1e-4,color='#444',linestyle='--',label='Original gate: 1e-4 N')
    axes[0,1].scatter([integration['timeS']],[integration['frozenResidual2048N']],marker='x',s=65,color='#a3242d',label='Frozen 2048-point\naudit')
    axes[0,1].set(title='Independent reduced\nresiduals',xlabel='Time (s)',ylabel='Maximum residual (N)')
    handles,labels=axes[0,1].get_legend_handles_labels()
    axes[0,1].legend(handles if coarse_only else handles[-2:],labels if coarse_only else labels[-2:],fontsize=19,loc='best')
    bins=next(h for h in local['heads'] if h['elementId']=='FJ1512')['bins'];z=[(b['bin']+.5)/6 for b in bins]
    axes[1,0].plot(z,[b['minimumJ'] for b in bins],'o-',color='#a3242d',label='Minimum sampled J')
    axes[1,0].plot(z,[b['meanJ'] for b in bins],'o-',color='#0e7669',label='Region mean J')
    axes[1,0].axhline(1,color='#888',linestyle=':',linewidth=1);axes[1,0].set(title='Short biceps · proximal\ncompression',xlabel='Longitudinal fraction\n(0 distal, 1 proximal)',ylabel='Volume ratio J',ylim=(.67,1.06));axes[1,0].legend(fontsize=19,loc='lower left')
    labels=['0.5 MPa','1 MPa','2 MPa','1 MPa\n+6 coordinates'];values=[]
    for r in [bulk[0],coarse['rows'][3],bulk[1],enriched]:values.append(min(h['minimumCornerJ'] for h in r['heads']))
    axes[1,1].bar(labels,values,color=['#d5a16f','#0e7669','#8cb8bd','#a3242d'],width=.55)
    for i,v in enumerate(values):axes[1,1].text(i,v+.005,f'{v:.6f}',ha='center',fontsize=19)
    axes[1,1].set(title='Bulk and nodal sensitivity',ylabel='Minimum queried corner J',ylim=(0,1.03))
    fig.supxlabel('Bulk and nodal sensitivity: one increment from the same dense old state.\nThese comparisons do not calibrate trajectories.',fontsize=19)
    for ax in axes.flat:ax.grid(axis='y',alpha=.15)
    inputs=['audit/contact-lift-release-recheck.json','audit/anatomical-dense-trajectory.json','audit/anatomical-dense-trajectory-recheck.json','audit/anatomical-compression-localization.json','audit/anatomical-further-integration.json','audit/anatomical-bulk-step-0.5-recheck.json','audit/anatomical-bulk-step-2-recheck.json','audit/anatomical-enriched-step-recheck.json']
    if not coarse_only:inputs.extend(['audit/anatomical-dense-fine-trajectory.json','audit/anatomical-dense-fine-trajectory-recheck.json','audit/anatomical-dense-interpolated-trajectory.json','audit/anatomical-dense-interpolated-trajectory-recheck.json','audit/anatomical-dense-release-refinement.json','audit/anatomical-dense-release-refinement-recheck.json','audit/anatomical-dense-matched-times.json'])
    for suffix in ['svg','png']:
        fig.savefig(out/f'dense-qualification.{suffix}',dpi=170,metadata={'Date':None} if suffix=='svg' else None)
        if suffix=='svg':
            svg=out/'dense-qualification.svg'
            svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)
    receipt={'schema':1,'coarseOnly':coarse_only,'rendererSHA256':digest(Path(__file__)),'pythonVersion':platform.python_version(),'matplotlibVersion':matplotlib.__version__,'inputs':{p:digest(BASE/p) for p in inputs},'outputs':{f'dense-qualification.{s}':digest(out/f'dense-qualification.{s}') for s in ['svg','png']},'limits':['Accepted prefixes are shown only through their verified times; rejection is not plotted as accepted.','Finite samples and passing reduced residuals do not qualify quadrature, timestep, mesh, full nodal or physiological convergence.']}
    (out/'render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':render()

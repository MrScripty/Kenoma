"""Plot source-bound virtual work in the six excluded displacement directions."""
from pathlib import Path
import hashlib,json,os,platform
os.environ.setdefault('MPLCONFIGDIR','/tmp/kenoma-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/kenoma-render-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from recorded_inputs import recorded_input_matches

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/anatomical-arm-v1'
SOURCE=BASE/'audit/anatomical-nodal-force-components.json'
OUT=BASE/'review/dense-qualification/force-components'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def render():
    data=json.loads(SOURCE.read_text())
    for relative,value in data['sourceHashes'].items():
        assert recorded_input_matches(relative,value),'Changed diagnostic source: '+relative
    rows=data['rows'];assert [(r['node'],r['axis']) for r in rows]==[(n,a) for n in [98,96] for a in range(3)]
    finite=[next(v for v in r['differences'] if v['hM']==5e-8) for r in rows]
    assert all(abs(v['sumDifferenceN'])<1e-6 for v in finite)
    components={
        'Bulk':[r['analyticBodyN']['volume'] for r in rows],
        'Active fibre':[r['analyticBodyN']['active'] for r in rows],
        'Routed tendons':[v['componentsN']['routedTendons'] for v in finite],
        'Other components':[r['analyticBodyN']['matrix']+r['analyticBodyN']['passiveFiber']+sum(v['componentsN'][k] for k in ['embeddedAxialSheets','transverseSheetMatrix','interfaces','contact']) for r,v in zip(rows,finite)],
    }
    totals=np.array([v['totalDerivativeN'] for v in finite])
    assert np.max(np.abs(np.sum(list(components.values()),axis=0)-totals))<2e-6
    plt.rcParams.update({'font.size':19,'svg.hashsalt':'kenoma-nodal-force-print','axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,(ax,legend_panel)=plt.subplots(2,1,figsize=(11,8.5),layout='constrained',gridspec_kw={'height_ratios':[5,1.3]})
    x=np.arange(6);positive=np.zeros(6);negative=np.zeros(6)
    for (name,values),color in zip(components.items(),['#72509b','#ca6234','#0e7669','#a5acb5']):
        values=np.array(values);bottom=np.where(values>=0,positive,negative)
        ax.bar(x,values,bottom=bottom,width=.6,label=name,color=color)
        positive+=np.maximum(values,0);negative+=np.minimum(values,0)
    ax.scatter(x,totals,s=45,color='#172f39',label='Total derivative',zorder=4)
    ax.axhline(0,color='#555',linewidth=.8);ax.grid(axis='y',alpha=.15)
    ax.set_xticks(x,[f'Node {n}\nGlobal {"xyz"[a]}' for n,a in [(r['node'],r['axis']) for r in rows]])
    ax.set(title='Short biceps · forces outside\nthe retained field',ylabel='Potential derivative\nin a unit direction (N)',ylim=(-2.8,.8))
    legend_panel.set_axis_off()
    legend_panel.legend(*ax.get_legend_handles_labels(),ncol=3,loc='center',fontsize=19)
    fig.suptitle('Accepted dense state at 0.10 s\nUnchanged material and contact rule',fontsize=20)
    fig.supxlabel('Unit nodal shapes projected off the 63-coordinate field;\nthese are virtual-work derivatives. No full nodal state is solved\nor advanced. Contact contributes at most 0.000858 N.',fontsize=19)
    OUT.mkdir(parents=True,exist_ok=True)
    for suffix in ['svg','png']:
        fig.savefig(OUT/f'nodal-force-components.{suffix}',dpi=170,metadata={'Date':None} if suffix=='svg' else None)
        if suffix=='svg':
            svg=OUT/'nodal-force-components.svg'
            svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)
    receipt={'schema':1,'inputSHA256':digest(SOURCE),'rendererSHA256':digest(Path(__file__)),'pythonVersion':platform.python_version(),'matplotlibVersion':matplotlib.__version__,'outputs':{f'nodal-force-components.{s}':digest(OUT/f'nodal-force-components.{s}') for s in ['svg','png']},'limits':['Components are scalar virtual-work derivatives in six normalized excluded shapes, not isolated nodal traction vectors.','The unchanged accepted pose is evaluated only; this does not select a material law or establish full nodal equilibrium.']}
    (OUT/'render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':render()

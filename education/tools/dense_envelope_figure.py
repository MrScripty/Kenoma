"""Display accepted P2 node geometry at its true scale, with common view limits."""
from pathlib import Path
import os,hashlib,json,platform
os.environ.setdefault('MPLCONFIGDIR','/tmp/kenoma-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/kenoma-render-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/anatomical-arm-v1'
OUT=BASE/'review/dense-qualification/envelope'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def render():
    source=BASE/'audit/anatomical-dense-envelope.json';r=json.loads(source.read_text())
    assert r['result']=='EXPORTED_ACCEPTED_P2_ENVELOPES'
    for p,h in r['sourceHashes'].items():assert digest(ROOT/p)==h,'Changed envelope input '+p
    OUT.mkdir(parents=True,exist_ok=True)
    faces=np.array(r['surfaceTriangles']);selected=np.array(r['referenceLongitudinalFraction'])>=5/6-1e-10
    cap_faces=faces[np.all(selected[faces],axis=1)]
    poses=[np.array(p['nodesMm']) for p in r['poses']]
    plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'kenoma-dense-envelope-print'})
    fig=plt.figure(figsize=(12,10.5),layout='constrained');fig.suptitle('Short biceps · actual P2 node envelopes at 0.10 s',fontsize=20)
    panels=fig.add_gridspec(5,3,height_ratios=[1,.22,1,.05,.35])
    for row,triangles in enumerate([faces,cap_faces]):
        points=np.concatenate([p if row==0 else p[selected] for p in poses]);low=points.min(axis=0);high=points.max(axis=0);span=high-low;low-=span*.06+.3;high+=span*.06+.3
        for col,(pose,nodes,color) in enumerate(zip(r['poses'],poses,['#a6afb3','#138276','#b34643'])):
            ax=fig.add_subplot(panels[row*2,col],projection='3d');ax.set_proj_type('ortho')
            ax.add_collection3d(Poly3DCollection(nodes[triangles],facecolor=color,edgecolor='#384850',linewidth=.23,alpha=.72))
            for d,limits in enumerate([ax.set_xlim,ax.set_ylim,ax.set_zlim]):limits(low[d],high[d])
            ax.set_box_aspect(high-low);ax.view_init(elev=12,azim=-54);ax.set_axis_off()
            ax.set_title(pose['label'].replace(' · ', '\n') if row==0 else 'Proximal sixth\nSame physical scale',fontsize=19,pad=3)
            if row==0:
                label=fig.add_subplot(panels[1,col]);label.set_axis_off()
                label.text(.5,.5,f"Corner J: {pose['minimumCornerJ']:.6f}\nGlobal volume: {pose['globalVolumeRatio']:.6f}",transform=label.transAxes,ha='center',va='center',fontsize=19)
    caption=fig.add_subplot(panels[4,:]);caption.set_axis_off()
    caption.text(.5,.5,'Stored displacements are not amplified. Common limits within each row;\nthe proximal row is a geometric zoom. Passing force and orientation checks\ndo not qualify compression or a whole tissue envelope.\nBodyParts3D © DBCLS · atlas-derived authored P2 mesh · CC BY 4.0',transform=caption.transAxes,ha='center',va='center',fontsize=19)
    for s in ['png','svg']:
        fig.savefig(OUT/f'dense-envelope.{s}',dpi=170,metadata={'Date':None} if s=='svg' else None)
        if s=='svg':
            svg=OUT/'dense-envelope.svg'
            svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)
    receipt={'schema':1,'rendererSHA256':digest(Path(__file__)),'pythonVersion':platform.python_version(),'matplotlibVersion':matplotlib.__version__,'inputSHA256':digest(source),'outputs':{f'dense-envelope.{s}':digest(OUT/f'dense-envelope.{s}') for s in ['svg','png']},'limits':r['limits']}
    (OUT/'render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':render()

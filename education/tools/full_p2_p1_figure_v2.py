"""Source-bound scientific render of the stationary controlled comparator."""
import hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/anatomical-arm-v1/review/full-p2-p1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
summary=json.loads((OUT/'summary.json').read_text())
verification=json.loads((OUT/'verification.json').read_text())
assert verification['result']=='PASS_FRESH_ORIGINAL_STRESS_GRADIENT_REPLAY'
for name,h in summary['sourceHashes'].items():assert sha(ROOT/name)==h
inputs=[OUT/'summary.json',OUT/'verification.json',OUT/'fine-mesh.json']
records=[]
for c in summary['cases']:
 p=OUT/(c['name']+'.json');inputs.append(p);records.append(json.loads(p.read_text()))
outputs=[OUT/'controlled-mixed-comparator-v2.png',OUT/'controlled-mixed-comparator-v2.pdf',OUT/'render-receipt-v2.json']
assert not any(p.exists() for p in outputs),'Preserve original render'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans'})
fig=plt.figure(figsize=(13,9),layout='constrained')
fig.suptitle('Full P2/P1 controlled specimen: equilibrium passes; descending-limb stability fails',fontsize=15,fontweight='bold')
colors={1.01:'#147881',1.25:'#b93e35'}
ax=fig.add_subplot(2,2,1)
for r in records:
 if r['stretch']==1:continue
 h=r['history'];ax.plot([q['iteration'] for q in h],[q['forceResidualN'] for q in h],
  'o-' if r['name'].startswith('coarse') else 's--',color=colors[r['stretch']],label=f"{r['name'].split('-')[0]}, stretch {r['stretch']}")
ax.axhline(1e-4,color='#333',ls=':',label='unchanged force gate');ax.set_yscale('log');ax.set_xticks([0,1,2,3])
ax.set(xlabel='Newton iteration',ylabel='Full free nodal residual [N]',title='A  Genuine perturbed solves, 256 points/element');ax.legend(fontsize=9)
ax=fig.add_subplot(2,2,2)
for level,marker in [('coarse','o'),('fine','x')]:
 r=[c for c in records if c['name'].startswith(level)]
 ax.plot([c['stretch'] for c in r],[c['replays']['256']['capForceN'] for c in r],marker,ms=9,label=level)
 r0=[c for c in records if c['name'].startswith('coarse')]
ax.plot([c['stretch'] for c in r0],[c['analytic']['capForceN'] for c in r0],color='#999',ls=':',label='analytic affine benchmark')
ax.set(xlabel='Prescribed axial stretch (independent specimens)',ylabel='Axial cap reaction [N]',title='B  Both meshes match the original-law benchmark');ax.legend(fontsize=9)
ax=fig.add_subplot(2,2,3)
smooth=[c for c in summary['cases'] if c['lowestEigenvalueNPerM'] is not None]
values=[c['lowestEigenvalueNPerM'] for c in smooth];labels=[c['name'].replace('-','\n') for c in smooth]
ax.bar(range(4),values,color=['#147881' if v>0 else '#b93e35' for v in values]);ax.axhline(0,color='#333',lw=.8)
ax.set_yscale('symlog',linthresh=2);ax.set_xticks(range(4),labels);ax.set(ylabel='Lowest physical condensed eigenvalue [N/m]',title='C  Spectrum at adequately stationary smooth states')
for i,v in enumerate(values):ax.annotate(f'{v:+.3f}',(i,v),xytext=(0,5),textcoords='offset points',ha='center',fontsize=9)
ax.set_ylim(-20000,1000)
ax.text(.02,.91,'Stretch 1: cutoff; stability unassessed.\nNodal Euclidean normalization; no spectrum-convergence claim.',transform=ax.transAxes,fontsize=8)
ax=fig.add_subplot(2,2,4,projection='3d')
m=json.loads((OUT/'fine-mesh.json').read_text())['mesh'];r=next(c for c in records if c['name']=='fine-1.25')
X=1000*np.array(r['terminalPositionsM']);tri=X[np.array(m['surface'])]
collection=Poly3DCollection(tri,facecolor='#e1b65b',edgecolor='#725b30',linewidth=.2,alpha=.7);ax.add_collection3d(collection)
ax.set(xlim=(0,180),ylim=(0,22),zlim=(0,22),xlabel='x [mm]',ylabel='y [mm]',zlabel='z [mm]',title='D  Actual fine-mesh terminal geometry, stretch 1.25')
ax.set_box_aspect((5,1,1));ax.view_init(elev=21,azim=-65);ax.set_xticks([0,50,100,150]);ax.xaxis.labelpad=10
ax.text2D(.03,.03,'J = 1.000254 (sampled) • strict boundary crossings: 0\nAuthored block; no anatomical claim or motion trajectory.',transform=ax.transAxes,fontsize=9)
fig.savefig(outputs[0],dpi=160);fig.savefig(outputs[1]);plt.close(fig)
receipt=dict(result='PASS_SOURCE_BOUND_CONTROLLED_MIXED_RENDER',rendererSHA256=sha(Path(__file__)),
 inputs={str(p.relative_to(ROOT)):sha(p) for p in inputs},outputs={str(p.relative_to(ROOT)):sha(p) for p in outputs[:2]},
 dimensionsPixels=[2080,1440],limits=['Actual controlled mesh geometry; no skin, atlas, trajectory or continuum spectral convergence claim.','Reference-stretch stability explicitly unassessed.'])
outputs[2].write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))

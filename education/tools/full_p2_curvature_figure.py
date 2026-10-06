"""Plot source-bound frozen diagnostic, with no visual physical advancement."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parents[1]
base = root/'data/anatomical-arm-v1'
review = base/'review/fixed-coefficient-controls'
out = review/'full-p2-render-receipt.json'
if out.exists():
    raise RuntimeError('Preserve render evidence')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = [base/('audit/fixed-coefficient-full-p2-'+suffix+'.json') for suffix in ['operator','spectrum','curvature-recheck','bulk-curvature']]
op,spectrum,replay,bulk = [json.loads(p.read_text()) for p in inputs]
assert replay['result']=='PASS_INDEPENDENT_FROZEN_FULL_P2_CURVATURE'
for run in [spectrum,replay,bulk]:
    for p,h in run['sourceHashes'].items():
        assert sha(root/p)==h
fig,ax = plt.subplots(1,3,figsize=(14.4,5))
values=[spectrum['minimumRestrictedEigenvalueNPerM']]+spectrum['sixSmallestEigenvaluesNPerM']
ax[0].bar(range(7),values,color=['#337a99']+['#ba5548']*6)
ax[0].axhline(0,color='black',lw=1)
ax[0].set_xticks(range(7),['Reduced\nmin','Full 1','2','3','4','5','6'])
ax[0].set(ylabel='Eigenvalue (N/m)',title='Same fixed-cap field, larger space')
source=json.loads((base/'audit/fixed-coefficient-taper.json').read_text())['fixture']['source']
b=source['basis'];X=np.array(op['positionsM'])-np.array(b['origin']);z=1000*(X@np.array(b['axis']));u=1000*(X@np.array(b['u']));direction=np.array(spectrum['direction']);amplitude=np.linalg.norm(direction,axis=1)
scatter=ax[1].scatter(z,u,c=amplitude,s=9,cmap='magma')
held=np.array(op['heldNodes']);ax[1].scatter(z[held],u[held],s=10,facecolors='none',edgecolors='#338999',linewidths=.5)
ax[1].set(xlabel='Axial position (mm)',ylabel='Transverse position (mm)',title='Frozen nodal eigen-direction amplitude')
fig.colorbar(scatter,ax=ax[1],label='Dimensionless component amplitude; norm=1')
groups=bulk['groups'];labels=['Compressed\nJ<1','Expanded\nJ≥1']
x=np.arange(2);ax[2].bar(x-.18,[groups[k]['firstVariationSquaredNPerM'] for k in ['compressed','expanded']],.35,color='#337a99',label='First variation squared')
ax[2].bar(x+.18,[groups[k]['prestressGeometricNPerM'] for k in ['compressed','expanded']],.35,color='#ba5548',label='Prestress geometric')
ax[2].axhline(0,color='black',lw=1);ax[2].set_xticks(x,labels);ax[2].set(ylabel='Volume-term curvature (N/m)',title='Negative bulk prestress contribution');ax[2].legend(fontsize=8)
fig.suptitle('Accepted reduced control at activation 0.01: full P2 forces and curvature remain unqualified',fontsize=12)
fig.text(.5,.015,'Frozen derivative diagnostic, no relaxation/time advancement. Maximum free nodal force 49.09 N; exact cap motion zero; full curvature −1027.02 N/m.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.05,1,.92))
outputs=[review/('full-p2-curvature-comparison.'+ext) for ext in ['png','pdf']]
for p in outputs:
    if p.exists():
        raise RuntimeError('Preserve existing figure')
    fig.savefig(p,dpi=180)
receipt={'result':'PASS_SOURCE_BOUND_FULL_P2_RENDER','inputs':{str(p.relative_to(root)):sha(p) for p in inputs},'rendererSHA256':sha(Path(__file__)),'outputs':{str(p.relative_to(root)):sha(p) for p in outputs}}
out.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

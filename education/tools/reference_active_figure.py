"""Source-bound selected-point diagnostic; no simulated physical advancement."""
import hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root=Path(__file__).resolve().parents[1]
base=root/'data/anatomical-arm-v1'
review=base/'review/mechanical-closure'
receipt=review/'reference-active-render-receipt.json'
if receipt.exists():
    raise RuntimeError('Preserve figure evidence')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[base/('audit/mechanical-closure-reference-active'+s+'.json') for s in ['', '-recheck']]
run,replay=[json.loads(p.read_text()) for p in inputs]
assert replay['result']=='PASS_INDEPENDENT_FROZEN_REFERENCE_CONSTRAINT_REPLAY'
assert replay['executionReceiptSHA256']==sha(inputs[0])
def row(name,normalization='current-authored',iso=False):
    return next(r for r in run['rows'] if r['savedState']==name and r['normalization']==normalization and r['isochoric']==iso)
fig,ax=plt.subplots(1,2,figsize=(13,5.8))
names=['taper-affine-full','quadratic-current-reduced-accepted','FJ1486-step-7','FJ1512-step-7','FJ1478-step-7']
labels=['Affine taper\na=1','Quadratic\na=.01','Brachialis\n.085 s','Short biceps\n.085 s','Long biceps\n.085 s']
x=np.arange(len(names))
for offset,key,color,label in [(-.18,'full','#337a99','Unconstrained'),(.18,'constrained','#ba5548','Exactly incompressible rank one')]:
    ax[0].bar(x+offset,[row(n)[key]['valuePa']/1e6 for n in names],.35,color=color,label=label)
ax[0].set_xticks(x,labels);ax[0].set(title='Current law: negative direction survives constraint',ylabel='Minimum tested curvature (MPa; signed log)')
ax[0].legend(fontsize=8)
names=['quadratic-current-reduced-accepted','FJ1512-step-7','FJ1512-step-10'];x=np.arange(3)
variants=[('current-authored',False,'#ba5548','Current full'),('current-authored',True,'#ce9946','Current isochoric'),('Blemker-reference-benchmark',False,'#788847','1.4 reference benchmark'),('Arm26-centerline-proxy',False,'#337a99','Unqualified length proxy')]
for i,(normalization,iso,color,label) in enumerate(variants):
    ax[1].bar(x+(i-1.5)*.19,[row(n,normalization,iso)['constrained']['valuePa']/1e6 for n in names],.18,color=color,label=label)
ax[1].set_xticks(x,['Quadratic point\na=.01','Short biceps\n.085 s','Short biceps\n.13 s']);ax[1].set(title='Reference sensitivity; no selected replacement',ylabel='Admissible curvature (MPa; signed log)');ax[1].legend(fontsize=8)
for a in ax:
    a.set_yscale('symlog',linthresh=.001);a.axhline(0,color='black',lw=1)
fig.suptitle('Frozen reference/constraint prototype: 84 local diagnostics, no new equilibrium or parameter fit',fontsize=12)
fig.text(.5,.02,'Selected saved points and finite directions only. Benchmark/proxy reference lengths are unqualified for this atlas; a positive local bar is no stability proof.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.07,1,.92))
outputs=[review/('reference-active-comparison.'+s) for s in ['png','pdf']]
for p in outputs:
    if p.exists():
        raise RuntimeError('Preserve existing figure')
    fig.savefig(p,dpi=180)
r={'result':'PASS_SOURCE_BOUND_REFERENCE_ACTIVE_RENDER','inputs':{str(p.relative_to(root)):sha(p) for p in inputs},'rendererSHA256':sha(Path(__file__)),'outputs':{str(p.relative_to(root)):sha(p) for p in outputs}}
receipt.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

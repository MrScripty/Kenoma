"""Plot retained matched-time evidence and the preserved failed Newton trace."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1];base=root/'data/anatomical-arm-v1';out=base/'review/dense-release-rejection'
names=['matched-time-and-rejection.png','matched-time-and-rejection.pdf','render-receipt.json']
assert all(not (out/n).exists() for n in names),'Preserve existing render'
frozen=json.loads((out/'frozen.json').read_text());runpath=base/'audit/anatomical-dense-release-refinement.json';run=json.loads(runpath.read_text());matched=frozen['matched'];trace=[r for r in run['trace'] if r['stage']==len(run['snapshots'])]
fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
axes[0].plot([r['timeS'] for r in matched],[r['angleDifferenceDeg'] for r in matched],'o-',color='#14789d',markersize=4)
axes[0].set(xlabel='Matched accepted time (s)',ylabel='Fine minus coarse angle (degrees)',title='Identical loading prefix; different release steps')
axes[0].grid(alpha=.2);axes[0].annotate('4.4384° at 0.400 s',xy=(matched[-1]['timeS'],matched[-1]['angleDifferenceDeg']),xytext=(.15,3.8),arrowprops={'arrowstyle':'->','color':'#14789d'})
axes[1].semilogy([r['iteration'] for r in trace],[r['residualN'] for r in trace],color='#b95132',linewidth=1.2)
axes[1].axhline(frozen['stationarityToleranceN'],linestyle='--',color='#263b45',label='Unchanged force gate: 10⁻⁴ N')
axes[1].set(xlabel='Newton iteration (fixed 120 limit)',ylabel='Maximum reduced residual (N)',title='Rejected 0.420 → 0.430 s increment')
axes[1].grid(alpha=.2);axes[1].legend(loc='lower left',fontsize=8)
fig.suptitle('Dense reduced trajectory diagnosis · 256 body points per element',fontsize=13)
fig.text(.5,-.04,'Accepted prefixes only; rejected candidate never advances time. No mesh, full-nodal or timestep convergence qualification.',ha='center',fontsize=9)
for name in names[:2]:fig.savefig(out/name,dpi=160,bbox_inches='tight')
plt.close(fig);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt={'result':'PASS_SOURCE_BOUND_DIAGNOSTIC_RENDER','matplotlib':matplotlib.__version__,'sourceHashes':{'tools/dense_release_rejection_figure.py':sha(Path(__file__)),'frozen.json':sha(out/'frozen.json'),'anatomical-dense-release-refinement.json':sha(runpath)},'outputs':{name:sha(out/name) for name in names[:2]},'scope':'Matched retained states and original rejected trace; not convergence acceptance.'}
(out/names[2]).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

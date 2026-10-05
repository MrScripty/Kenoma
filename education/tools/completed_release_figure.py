"""Actual fully replayed coarse/release-refined angles and matched-time error."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1];base=root/'data/anatomical-arm-v1';out=base/'review/dense-release-completed';assert not out.exists(),'Preserve completed render';out.mkdir()
paths={n:base/'audit'/n for n in ['anatomical-dense-trajectory.json','anatomical-dense-release-secant-completed.json','dense-release-secant-matched-times.json']};coarse=json.loads(paths['anatomical-dense-trajectory.json'].read_text());fine=json.loads(paths['anatomical-dense-release-secant-completed.json'].read_text());comparison=json.loads(paths['dense-release-secant-matched-times.json'].read_text());assert comparison['result']=='PASS_COMPLETED_ACCEPTED_RELEASE_MATCHED_TIMES'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['anatomical-dense-trajectory','anatomical-dense-release-secant-completed']:
    p=base/'audit'/(name+'-recheck.json');r=json.loads(p.read_text());assert r['result']=='PASS_DENSE_TRAJECTORY' and r['executionReceiptSHA256']==sha(paths[name+'.json']);paths[p.name]=p
fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
for run,color,label in [(coarse,'#14789d','15 states · release h = 0.03 s'),(fine,'#1c8b66','35 states · release h = 0.01 s')]:
    states=[run['held']['state'],*run['snapshots']];axes[0].plot([s['timeS'] for s in states],[s['qRad']*180/3.141592653589793 for s in states],'o-',color=color,markersize=3,label=label)
axes[0].axvspan(0,.13,color='#e3e9ec',alpha=.5);axes[0].text(.017,32.5,'Same dense\nloading prefix',fontsize=9);axes[0].set(xlabel='Physical time (s)',ylabel='Elbow angle (degrees)',title='Force-checked reduced lift/release');axes[0].legend(fontsize=8);axes[0].grid(alpha=.2)
rows=comparison['rows'];axes[1].plot([r['timeS'] for r in rows],[r['angleDifferenceDeg'] for r in rows],'o-',color='#b95132',markersize=4);axes[1].set(xlabel='Matched accepted time (s)',ylabel='Fine minus coarse angle (degrees)',title='Timestep convergence remains unqualified');axes[1].grid(alpha=.2)
fig.suptitle('Self-consistent dense release refinement · unchanged material and force gate',fontsize=13);fig.text(.5,-.04,'256 body points per element; five identical loading states. Original rejection preserved. No full-nodal or physiological qualification.',ha='center',fontsize=9)
names=['completed-release-matched-times.png','completed-release-matched-times.pdf']
for name in names:fig.savefig(out/name,dpi=160,bbox_inches='tight')
plt.close(fig)
receipt={'result':'PASS_COMPLETED_RELEASE_RENDER','matplotlib':matplotlib.__version__,'sourceHashes':{**{n:sha(p) for n,p in paths.items()},'tools/completed_release_figure.py':sha(Path(__file__))},'outputs':{n:sha(out/n) for n in names},'scope':'Actual fully replayed accepted trajectories and matched-time differences; no convergence acceptance.'};(out/'render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

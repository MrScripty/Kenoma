"""Source-bound controlled active/passive and loading-regime figure."""
from pathlib import Path
import json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/anatomical-arm-v1/review/active-stability-controls'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((OUT/'summary.json').read_text())
for name,h in s['sourceHashes'].items():assert sha(ROOT/name)==h
assert all(c['stationaryAccepted'] and c['derivativeChecksPass'] for c in s['cases'])
paths=[OUT/'summary.json'];r=[]
for c in s['cases']:
 p=OUT/f"case-{c['name']}-a{c['activation']:.2f}.json";paths.append(p);r.append(json.loads(p.read_text()))
files=[OUT/'active-controls.png',OUT/'active-controls.pdf',OUT/'render-receipt.json'];assert not any(p.exists() for p in files)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(3,1,figsize=(11,12),layout='constrained')
fig.suptitle('Declared instantaneous law: isolate active curvature and loading control',fontsize=15,fontweight='bold')
values=[c['fullMinimumNPerM'] for c in s['cases']];weak=[c['weakProjectedMinimumNPerM'] for c in s['cases']]
ax[0].bar(range(8),values,color=['#b63d36' if v<0 else '#1b7780' for v in values]);ax[0].plot(range(8),weak,'ko',mfc='none',ms=6,label='weak P1 constraint')
ax[0].axhline(0,color='#333',lw=.7);ax[0].set_yscale('symlog',linthresh=.1);ax[0].set_ylim(-2e4,100)
ax[0].set_xticks(range(8),[c['name'].replace('-','\n')+'\na='+str(c['activation']) for c in s['cases']])
ax[0].set(ylabel='Minimum physical eigenvalue [N/m]',title='A  Same saved cap geometry; all eight force/pressure/geometry gates pass')
ax[0].legend(loc='upper left',fontsize=9)
for x in r:
 if not x['name'].startswith('coarse'):continue
 rows=x['local']['rows'];label=x['name'].split('-')[1]+'; a='+str(x['activation'])
 ax[1].plot([z['angleRad']*180/np.pi for z in rows],[z['valuePa']/1000 for z in rows],
  '-' if x['activation'] else '--',label=label)
ax[1].axhline(0,color='#333',lw=.7);ax[1].set(xlabel='Rank-one direction angle [degrees]',ylabel='Admissible local curvature [kPa]',title='B  Strict volume-admissible local scan: descending active witness −47.539 kPa')
ax[1].legend(loc='lower left',ncol=2,fontsize=9)
c=[c for c in s['cases'] if c['name'].startswith('coarse')];v=[x['axialDerivativeNPerM'] for x in c]
ax[2].bar(range(4),v,color=['#b63d36' if z<0 else '#1b7780' for z in v]);ax[2].axhline(0,color='#333',lw=.7)
ax[2].set_xticks(range(4),[x['name'].split('-')[1]+'; a='+str(x['activation']) for x in c]);ax[2].set(ylabel='Homogeneous dR/dL [N/m]',title='C  Global axial mode: excluded by length control; allowed by dead-force control')
ax[2].set_ylim(-680,360)
for i,z in enumerate(v):ax[2].annotate(f'{z:+.3f}',(i,z),xytext=(0,5),textcoords='offset points',ha='center')
ax[2].text(.02,.03,'End-separation spring needs k > 484.557 N/m for the active global mode; no stiffness selected.\nSuch a spring does not act on the retained zero-cap interior witnesses.',transform=ax[2].transAxes,fontsize=9)
fig.savefig(files[0],dpi=150);fig.savefig(files[1]);plt.close(fig)
receipt=dict(result='PASS_SOURCE_BOUND_ACTIVE_CONTROL_RENDER',rendererSHA256=sha(Path(__file__)),inputs={str(p.relative_to(ROOT)):sha(p) for p in paths},outputs={str(p.relative_to(ROOT)):sha(p) for p in files[:2]},limits=['No human incremental stiffness, dynamic stability, anatomy or selected replacement law is claimed.'])
files[2].write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

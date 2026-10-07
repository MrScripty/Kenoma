#!/usr/bin/env python3
"""Read immutable JSON forces only; no imports from specimen or quadrature modules."""
import json, pathlib, math, hashlib, csv
ROOT=pathlib.Path('/tmp/Kenoma-fine-window-material-run/education')
OUT=pathlib.Path('/tmp/fine-window-completed-localization-independent')
RAW=ROOT/'review/fine-window-run-20261007/material'
TERMS=['matrix','volume','passiveFiber','activePotential','total']
FOCUS=[197,200,203,206,246,247,248]
STATES=['control45','terminal46']
source=json.loads((ROOT/'data/anatomical-arm-v1/generated/arm-reference.json').read_text())
source=next(m for m in source['muscles'] if m['element_id']=='FJ1486')
ids=source['elements_ten_node']
saved=json.loads((ROOT/'review/fixed-field-integration-run-20261007/saved-arrays.json').read_text())
direction=saved['terminalDirectionM']
inputs={}
def read(path):
 b=path.read_bytes(); inputs[str(path.relative_to(ROOT))]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};return json.loads(b)
def sub(a,b): return [[x-y for x,y in zip(av,bv)] for av,bv in zip(a,b)]
def metric(rows,t):
 signed=[[] for _ in range(1755)];triangle=[[] for _ in range(1755)]; works=[]
 for r in rows:
  e=r['element'];v=r['delta'][t]
  w=math.fsum(v[n][d]*direction[ids[e][n]][d] for n in range(10) for d in range(3));works.append(w)
  for n in range(10):
   for d in range(3):
    i=3*ids[e][n]+d;signed[i].append(v[n][d]);triangle[i].append(abs(v[n][d]))
 S=list(map(math.fsum,signed));A=list(map(math.fsum,triangle));imax=max(range(1755),key=lambda i:abs(S[i]));jmax=max(range(1755),key=lambda i:A[i])
 return dict(signedN=abs(S[imax]),triangleN=A[jmax],signedWorkJ=abs(math.fsum(works)),triangleWorkJ=math.fsum(map(abs,works)),signedMaximum={'node':imax//3,'axis':'xyz'[imax%3],'valueN':S[imax]},triangleMaximum={'node':jmax//3,'axis':'xyz'[jmax%3],'valueN':A[jmax]})
report={};flat=[]
for state in STATES:
 report[state]={}
 for pair in [('I0','I1'),('P8','I1'),('I0','P8')]:
  rows=[]
  for e in FOCUS:
   for shell in ['s'+str(i) for i in range(1,21)]+['core']:
    aa=read(RAW/f'{state}-{e}-{pair[0]}-{shell}-region.json');bb=read(RAW/f'{state}-{e}-{pair[1]}-{shell}-region.json')
    assert aa['element']==bb['element']==e and aa['shell']==bb['shell']==shell
    assert aa['lo']==bb['lo'] and aa['hi']==bb['hi']
    assert aa['evaluationIdentity']==bb['evaluationIdentity']
    row=dict(element=e,shell=shell,lo=aa['lo'],hi=aa['hi'],delta={t:sub(aa['localGradientsN'][t],bb['localGradientsN'][t]) for t in TERMS},energyDifferenceJ={t:aa['energiesJ'][t]-bb['energiesJ'][t] for t in TERMS})
    rows.append(row)
    for t in TERMS:
     v=row['delta'][t];ni,di=max(((n,d) for n in range(10) for d in range(3)),key=lambda z:abs(v[z[0]][z[1]]));flat.append(dict(state=state,pair='/'.join(pair),element=e,shell=shell,component=t,localInfinityN=abs(v[ni][di]),localNode=ni,globalNode=ids[e][ni],axis='xyz'[di],signedAtMaximumN=v[ni][di],directionalDifferenceJ=math.fsum(v[n][d]*direction[ids[e][n]][d] for n in range(10) for d in range(3)),energyDifferenceJ=row['energyDifferenceJ'][t],lo=row['lo'],hi=row['hi']))
  data=dict(focusMetrics={t:metric(rows,t) for t in TERMS},byElement={str(e):{t:metric([r for r in rows if r['element']==e],t) for t in TERMS} for e in FOCUS},byRegion={s:{t:metric([r for r in rows if r['shell']==s],t) for t in TERMS} for s in ['s'+str(i) for i in range(1,21)]+['core']},maximumUnits={t:sorted([x for x in flat if x['state']==state and x['pair']=='/'.join(pair) and x['component']==t],key=lambda x:x['localInfinityN'],reverse=True)[:12] for t in TERMS})
  report[state]['/'.join(pair)]=data
(OUT/'localization.json').write_text(json.dumps({'specimenCalls':0,'quadratureGenerated':False,'readOnlyScalarArithmetic':True,'data':report,'inputs':inputs},indent=2)+'\n')
with (OUT/'localization.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
for state in STATES:
 for pair,data in report[state].items():
  print(state,pair)
  for t,m in data['focusMetrics'].items():print(' ',t,'focus',m)
  if pair=='I0/I1':
   for e,ts in data['byElement'].items():print(' ELEMENT',e,'volume',ts['volume']['signedN'],ts['volume']['triangleN'],'total',ts['total']['signedN'],ts['total']['triangleN'])
   for t in ['volume','total']:print('TOP',t,[(x['element'],x['shell'],x['localInfinityN'],x['globalNode'],x['axis']) for x in data['maximumUnits'][t]])
print('Read immutable files',len(inputs),'local scalar rows',len(flat))

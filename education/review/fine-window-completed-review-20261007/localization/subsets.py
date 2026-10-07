import runpy,json,itertools,pathlib,math
ns=runpy.run_path('/tmp/fine-window-completed-localization-independent/localize.py')
ROOT,RAW,read,sub,metric=map(ns.get,['ROOT','RAW','read','sub','metric'])
rows=[]
for e in ns['FOCUS']:
 for s in ['s'+str(i) for i in range(1,21)]+['core']:
  a=read(RAW/f'terminal46-{e}-I0-{s}-region.json');b=read(RAW/f'terminal46-{e}-I1-{s}-region.json');rows.append(dict(element=e,shell=s,delta={t:sub(a['localGradientsN'][t],b['localGradientsN'][t]) for t in ns['TERMS']}))
sets=[[(247,'s1')],[(247,'s1'),(247,'s2')],[(247,'s1'),(247,'s2'),(247,'s3')],[(247,'s1'),(247,'s2'),(247,'s3'),(206,'s1')],[(247,'s1'),(247,'s2'),(247,'s3'),(247,'s4')]]
out=[]
for chosen in sets:
 rest=[r for r in rows if (r['element'],r['shell']) not in chosen];mets={t:metric(rest,t) for t in ns['TERMS']};out.append({'newDiagnosticSupport':chosen,'oldDiscrepancyOnUnchangedSupport':mets});print('SUBSET',chosen,'remaining volume',mets['volume']['triangleN'],'total',mets['total']['triangleN'])
# Lower bound: all three unit removals leave at node505y more than1.5e-6 by sum of smallest achievable residual there.
term='total';i=505;d=1
pieces=[]
for r in rows:
 for n,node in enumerate(ns['ids'][r['element']]):
  if node==i:pieces.append((abs(r['delta'][term][n][d]),r['element'],r['shell']))
pieces.sort(reverse=True)
print('NODE505y removal lower bound',math.fsum(x[0] for x in pieces[3:]),'top',pieces[:8])
(pathlib.Path('/tmp/fine-window-completed-localization-independent')/'subset-localization.json').write_text(json.dumps({'analyticalOnly':True,'specimenCalls':0,'quadratureGenerated':False,'sets':out,'threeRegionRemovalLowerBoundAtNode505y':math.fsum(x[0] for x in pieces[3:]),'fourRegionCountAtFace16Radial4Gauss5BothFields':4*3*4*16**2*125*2},indent=2)+'\n')

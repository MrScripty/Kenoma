"""Retained-vector arithmetic only; no material imports, quadrature or evaluations."""
import csv,hashlib,json,math,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent
ANCHOR='38ae8a2e2af57cf33254af987b724824b9d84357';RAW='review/selective-fixed-patch-run-20261007/material/';OLD='review/fixed-field-integration-run-20261007/';SHELL='review/element247-shell-run-20261007/material/'
inventory={}
def read(name):
 b=(ROOT/name).read_bytes();frozen=subprocess.check_output(['git','cat-file','blob',f'{ANCHOR}:education/{name}'],cwd=ROOT);assert b==frozen,name;inventory[name]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};return json.loads(b)
source=next(x for x in read('data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if x['element_id']=='FJ1486');arrays=read(OLD+'saved-arrays.json');ids=source['elements_ten_node'];direction=arrays['terminalDirectionM'];patch=arrays['patchElements'];terms=['matrix','volume','passiveFiber','activePotential','total'];quiet=[195,196,198,199,202,237,240,243,244];secondary=[197,200,203,206,246,248]
unit_csv=[];element_csv=[];localized={};sequence={}
def metrics(rows,t):
 local=[[math.fsum(r['localDifferenceN'][i][d] for r in rows) for d in range(3)] for i in range(10)];absolute=[[math.fsum(abs(r['localDifferenceN'][i][d]) for r in rows) for d in range(3)] for i in range(10)]
 return {'signedInfinityN':max(abs(x) for v in local for x in v),'unitTriangleInfinityN':max(x for v in absolute for x in v),'signedWorkJ':abs(math.fsum(r['directionalDifferenceJ'] for r in rows)),'unitTriangleWorkJ':math.fsum(abs(r['directionalDifferenceJ']) for r in rows),'grossUnitAbsoluteL1N':math.fsum(abs(x) for r in rows for v in r['localDifferenceN'] for x in v)}
for state in ['control45','terminal46']:
 c=read(RAW+f'{state}-Q0-Q1-comparison.json');elements={};component_global={}
 for t in terms:
  saved=c['terms'][t];rows=saved['differences'];peak_triangle=max(((v,n,d) for n,X in enumerate(saved['absoluteUnitDifferenceN']) for d,v in enumerate(X)),key=lambda x:x[0]);peak_signed=max(((abs(v),n,d) for n,X in enumerate(saved['aggregateDifferenceN']) for d,v in enumerate(X)),key=lambda x:x[0]);peak_nodes=[]
  for label,(value,n,d) in [('unitTriangle',peak_triangle),('signed',peak_signed)]:
   contributions=[]
   for row in rows:
    nodes=ids[row['element']]
    if n in nodes:
     x=row['localDifferenceN'][nodes.index(n)][d];contributions.append({'element':row['element'],'unit':row['id'],'signedN':x,'absoluteN':abs(x)})
   contributions.sort(key=lambda r:r['absoluteN'],reverse=True)
   peak_nodes.append({'kind':label,'node':n,'componentXYZ':'xyz'[d],'held':n in arrays['heldNodeOrder'],'valueN':value,'signedSumAtEntryN':math.fsum(r['signedN'] for r in contributions),'absoluteSumAtEntryN':math.fsum(r['absoluteN'] for r in contributions),'contributions':contributions})
  component_global[t]={'signedInfinityN':saved['aggregateInfinityN'],'unitTriangleInfinityN':saved['unitTriangleInfinityN'],'signedWorkJ':saved['aggregateDirectionalDifferenceJ'],'unitTriangleWorkJ':saved['unitTriangleDirectionalDifferenceJ'],'pass':saved['pass'],'peaks':peak_nodes}
  for e in patch:
   erows=[r for r in rows if r['element']==e];m=metrics(erows,t);elements.setdefault(str(e),{})[t]={**m,'units':len(erows),'hasShellResolvedDifference':e not in quiet,'shells':[]};element_csv.append({'state':state,'element':e,'term':t,**m})
   for row in erows:
    shell=row['id'].split('-',1)[1];u=metrics([row],t);item={'unit':row['id'],'shell':shell,**u};elements[str(e)][t]['shells'].append(item);unit_csv.append({'state':state,'element':e,'term':t,**item})
   gross=m['grossUnitAbsoluteL1N'];outer=math.fsum(abs(v) for row in erows if row['id']==f'{e}-s1' for X in row['localDifferenceN'] for v in X);elements[str(e)][t]['outerS1GrossL1Share']=outer/gross if gross else 0.
 localized[state]={'components':component_global,'elements':elements,'all16':True,'all585IncludingHeld':True,'unitCount':156}
 # Group-level comparison bounds always retain actual saved comparison units.
 sequence[state]={}
 for pair in ['Q0-Q1','Q1-Q2','Q0-Q2','F44-R44']:
  x=read(RAW+f'{state}-{pair}-comparison.json');groups={}
  for label,es in [('quiet9',quiet),('secondary6',secondary),('element247',[247]),('full16',patch)]:
   g={}
   for t in terms:
    rows=[r for r in x['terms'][t]['differences'] if r['element'] in es];signed=[[0.,0.,0.] for _ in range(585)];absolute=[[0.,0.,0.] for _ in range(585)]
    for row in rows:
     for i,n in enumerate(ids[row['element']]):
      for d in range(3):signed[n][d]+=row['localDifferenceN'][i][d];absolute[n][d]+=abs(row['localDifferenceN'][i][d])
    g[t]={'signedInfinityN':max(abs(v) for X in signed for v in X),'unitTriangleInfinityN':max(v for X in absolute for v in X),'signedWorkJ':abs(math.fsum(r['directionalDifferenceJ'] for r in rows)),'unitTriangleWorkJ':math.fsum(abs(r['directionalDifferenceJ']) for r in rows),'units':len(rows),'emptyOrIdenticalSubsetIsNotQualification':not bool(rows)}
   groups[label]=g
  matched={}
  if pair!='F44-R44':
   wholeA=read(RAW+f"{state}-{x['a']}-hybrid.json")['localElements'];wholeB=read(RAW+f"{state}-{x['b']}-hybrid.json")['localElements']
  else:wholeA=[read(RAW+f'{state}-247-F44-stage.json')];wholeB=[read(RAW+f'{state}-247-R44-stage.json')]
  for t in terms:
   triangle=[[0.,0.,0.] for _ in range(585)];signed=[[0.,0.,0.] for _ in range(585)];whole_works=[]
   for e in patch:
    erows=[z for z in x['terms'][t]['differences'] if z['element']==e]
    if not erows:continue
    ar=next(z for z in wholeA if z['element']==e);br=next(z for z in wholeB if z['element']==e);delta=[[ar['localGradientsN'][t][i][d]-br['localGradientsN'][t][i][d] for d in range(3)] for i in range(10)]
    whole_works.append(math.fsum(delta[i][d]*direction[n][d] for i,n in enumerate(ids[e]) for d in range(3)))
    for i,n in enumerate(ids[e]):
     for d in range(3):v=delta[i][d];signed[n][d]+=v;triangle[n][d]+=abs(v)
   matched[t]={'signedInfinityN':max(abs(v) for X in signed for v in X),'wholeElementTriangleInfinityN':max(v for X in triangle for v in X),'signedWorkJ':abs(math.fsum(whole_works)),'wholeElementTriangleWorkJ':math.fsum(abs(w) for w in whole_works),'partition':'16wholeelements; diagnostic only; doesnotreplace required156/36/21unitgates','representedElements':len(whole_works)}
  sequence[state][pair]={'required':x['required'],'pass':x['pass'],'units':x['units'],'groups':groups,'matchedWholeElementPartition':matched}
 # Old secondary D4/D5 refinement and U5/D5 cross witnesses: whole-element only.
 for a,b in [('D4','D5'),('U5','D5')]:
  rows=[]
  for e in secondary:
   ar,br=read(OLD+f'{a}-{state}-element-{e}-local.json'),read(OLD+f'{b}-{state}-element-{e}-local.json');row={'element':e,'id':f'{e}-whole','terms':{}}
   for t in terms:
    delta=[[ar['localGradientsN'][t][i][d]-br['localGradientsN'][t][i][d] for d in range(3)] for i in range(10)];w=math.fsum(delta[i][d]*direction[ids[e][i]][d] for i in range(10) for d in range(3));row['terms'][t]={'localDifferenceN':delta,'directionalDifferenceJ':w}
   rows.append(row)
  data={}
  for t in terms:
   signed=[[0.,0.,0.] for _ in range(585)];triangle=[[0.,0.,0.] for _ in range(585)]
   for row in rows:
    for i,n in enumerate(ids[row['element']]):
     for d in range(3):v=row['terms'][t]['localDifferenceN'][i][d];signed[n][d]+=v;triangle[n][d]+=abs(v)
   data[t]={'signedInfinityN':max(abs(v) for X in signed for v in X),'elementTriangleInfinityN':max(v for X in triangle for v in X),'signedWorkJ':abs(math.fsum(row['terms'][t]['directionalDifferenceJ'] for row in rows)),'elementTriangleWorkJ':math.fsum(abs(row['terms'][t]['directionalDifferenceJ']) for row in rows),'units':6,'shellPartitionInvented':False}
  sequence[state][f'retained-secondary-{a}-{b}']={'scope':'Six secondary whole-element vectors only; original full-patch failures preserved','terms':data}
for state in ['control45','terminal46']:
 oldc=next(c for c in read(SHELL+'shell-vector-comparisons.json')['comparisons'] if c['state']==state and c['a']=='C55' and c['b']=='A55')
 sequence[state]['retained247-angular1-to2']={'scope':'SameD20/radial1/face123/Gauss5; actual angularparts1to2 at247','pass':oldc['pass'],'terms':{t:{'signedInfinityN':v['aggregateInfinityN'],'shellTriangleInfinityN':v['shellTriangleInfinityN'],'signedWorkJ':v['aggregateDirectionalDifferenceJ'],'shellTriangleWorkJ':v['shellTriangleDirectionalDifferenceJ']} for t,v in oldc['terms'].items()}}
result={'schema':1,'result':'READ_ONLY_LOCALIZATION_AND_FINITE_RESOLUTION_ASSESSMENT','frozenResultCommit':ANCHOR,'originalResult':'UNRESOLVED_FIXED_PATCH_INTEGRATION','newSpecimenCalls':0,'newMaterialLawInvocations':0,'newQuadratureGenerated':False,'gatesChanged':False,'localization':localized,'comparisonGroups':sequence,'inputInventory':inventory,'limitations':['Element/shell triangle metrics are descriptive contributions; fullpatch gate still uses the exact complete shared-node scatter.','GrossL1 shares rank localization; they are not additive shares of globalinfinity norms or analytic error estimates.','Q1/Q2 mixedcrossfamily is not a single globally ordered refinement sequence.','F44/R44 isolates247radial only; X44changesdepthandface jointly.','236outsideU3elements remain unqualified; no anatomicalacceptance.']}
with (HERE/'localization.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
for name,rows in [('element-component-metrics.csv',element_csv),('shell-component-metrics.csv',unit_csv)]:
 with (HERE/name).open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({'result':result['result'],'newSpecimenCalls':0,'inputs':len(inventory),'elementRows':len(element_csv),'shellRows':len(unit_csv),'localizationSha256':hashlib.sha256((HERE/'localization.json').read_bytes()).hexdigest()}))

"""Retained-vector subset arithmetic and symbolic counts only."""
import pathlib,json,math,hashlib,subprocess
ROOT=pathlib.Path('/tmp/Kenoma-fine-window-material-run/education');OUT=pathlib.Path('/tmp/fine-window-completed-localization-independent');RAW=ROOT/'review/fine-window-run-20261007/material'
TERMS=['matrix','volume','passiveFiber','activePotential','total'];FOCUS=[197,200,203,206,246,247,248]
source=next(m for m in json.loads((ROOT/'data/anatomical-arm-v1/generated/arm-reference.json').read_text())['muscles'] if m['element_id']=='FJ1486');ids=source['elements_ten_node'];direction=json.loads((ROOT/'review/fixed-field-integration-run-20261007/saved-arrays.json').read_text())['terminalDirectionM']
loc=json.loads((OUT/'localization.json').read_text());inventory=json.loads((ROOT/'review/fine-window-outcome-20261007/raw-inventory.json').read_text())['files'];pin='5f7612f6c7f6609d8946b3394d7363609d7a30b1';assert subprocess.check_output(['git','-C',str(ROOT.parent),'rev-parse','HEAD'],text=True).strip()==pin
for p,meta in loc['inputs'].items():
 rp=p.removeprefix('review/fine-window-run-20261007/');assert inventory[rp]==meta
for p in ['data/anatomical-arm-v1/generated/arm-reference.json','review/fixed-field-integration-run-20261007/saved-arrays.json']:
 b=(ROOT/p).read_bytes();gitb=subprocess.check_output(['git','-C',str(ROOT.parent),'show',f'{pin}:education/{p}']);assert gitb==b

def metric(rows,t):
 signed=[[] for _ in range(1755)];triangle=[[] for _ in range(1755)];works=[]
 for e,s,dd in rows:
  v=dd[t];works.append(math.fsum(v[n][d]*direction[ids[e][n]][d] for n in range(10) for d in range(3)))
  for n in range(10):
   for d in range(3):i=3*ids[e][n]+d;signed[i].append(v[n][d]);triangle[i].append(abs(v[n][d]))
 return dict(signedN=max(map(abs,map(math.fsum,signed))),triangleN=max(map(math.fsum,triangle)),signedWorkJ=abs(math.fsum(works)),triangleWorkJ=math.fsum(map(abs,works)))
sets={'four':[(247,'s1'),(247,'s2'),(247,'s3'),(206,'s1')],'five':[(247,'s1'),(247,'s2'),(247,'s3'),(247,'s4'),(206,'s1')]};out={}
for name,chosen in sets.items():
 vals={}
 for state in ['control45','terminal46']:
  rows=[]
  for e in FOCUS:
   for s in ['s'+str(i) for i in range(1,21)]+['core']:
    if (e,s) in chosen:continue
    a=json.loads((RAW/f'{state}-{e}-I0-{s}-region.json').read_text());b=json.loads((RAW/f'{state}-{e}-I1-{s}-region.json').read_text());dd={t:[[x-y for x,y in zip(v,w)] for v,w in zip(a['localGradientsN'][t],b['localGradientsN'][t])] for t in TERMS};rows.append((e,s,dd))
  vals[state]={t:metric(rows,t) for t in TERMS}
 maxforce=max(v[k] for ts in vals.values() for v in ts.values() for k in ['signedN','triangleN']);maxwork=max(v[k] for ts in vals.values() for v in ts.values() for k in ['signedWorkJ','triangleWorkJ'])
 n=len(chosen);out[name]=dict(regions=chosen,retainedComplement=vals,retainedComplementMaximumForceN=maxforce,retainedComplementMaximumWorkJ=maxwork,availableFocusForceForNewIncrementN=1.5e-6-maxforce,availableFocusWorkForNewIncrementJ=.15*5.492029235357012e-7-maxwork,face16radial2PointsPerRegionPerField=3*2*16**2*125,newCallsBothFields=n*3*2*16**2*125*2,face16radial4BothFields=n*3*4*16**2*125*2,normalizedPointsAcrossDistinctCornerRegionCharts=n*3*2*16**2*125,normalizedBinaryBytes=n*3*2*16**2*125*48,physicalBinaryBytes=n*3*2*16**2*125*8)
 print(name,json.dumps({k:v for k,v in out[name].items() if k!='retainedComplement'},indent=2))
report={'verdict':'PASS_RETAINED_LOCALIZATION_AND_SYMBOLIC_COST','frozenCompletedHead':pin,'checkedRawRegionHashes':len(loc['inputs']),'specimenCalls':0,'quadratureGenerated':False,'minimumRegionalCountForOldComplementToFitFocusForce':4,'threeRegionComplementLowerBoundN':2.9071825775021348e-6,'options':out,'noAbsoluteGlobalCostMinimalityClaim':True,'outside236Qualified':False,'anatomicalCapstoneQualified':False}
(OUT/'design-check.json').write_text(json.dumps(report,indent=2)+'\n')

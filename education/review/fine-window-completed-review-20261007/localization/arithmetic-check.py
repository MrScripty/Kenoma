import json,pathlib,math
R=pathlib.Path('/tmp/Kenoma-fine-window-material-run/education/review/fine-window-run-20261007/material');O=pathlib.Path('/tmp/fine-window-completed-localization-independent');loc=json.loads((O/'localization.json').read_text())['data'];terms=['matrix','volume','passiveFiber','activePotential','total'];checks=0;maximum=0
for state in ['control45','terminal46']:
 for pair,filename in [('I0/I1','I0-I1'),('P8/I1','S2-I1')]:
  old=json.loads((R/f'{state}-{filename}-comparison.json').read_text())['allocations']['focus']['metrics']
  for t in terms:
   for k in ['signedN','triangleN','signedWorkJ','triangleWorkJ']:
    delta=abs(old[t][k]-loc[state][pair]['focusMetrics'][t][k]);maximum=max(maximum,delta);assert delta<1e-16;checks+=1
for state in ['control45','terminal46']:
 for e in [197,200,203,206,246,247,248]:
  for recipe in ['I0','I1','P8']:
   stage=json.loads((R/f'{state}-{e}-{recipe}-stage.json').read_text());rows=[json.loads((R/f'{state}-{e}-{recipe}-{s}-region.json').read_text()) for s in ['s'+str(i) for i in range(1,21)]+['core']]
   assert sum(r['pointCount'] for r in rows)==stage['pointCount'];checks+=1
   for t in terms:
    assert abs(math.fsum(r['energiesJ'][t] for r in rows)-stage['energiesJ'][t])<=1e-9;checks+=1
    for n in range(10):
     for d in range(3):assert abs(math.fsum(r['localGradientsN'][t][n][d] for r in rows)-stage['localGradientsN'][t][n][d])<=1e-8;checks+=1
# Vertex505y provides a universal minimum-region-count argument without enumerating subsets:
# any three omitted physical-region contributions remove at most the three largest absolute entries there.
assert json.loads((O/'subset-localization.json').read_text())['threeRegionRemovalLowerBoundAtNode505y']>1.5e-6;checks+=1
out={'verdict':'PASS_INDEPENDENT_RETAINED_ARITHMETIC_AND_REGION_COUNT_MINIMUM','assertions':checks,'maxStoredFocusMetricVsIndependentFsumDifference':maximum,'specimenCalls':0,'quadratureGenerated':False}
(O/'arithmetic-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

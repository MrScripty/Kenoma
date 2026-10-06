"""Read-only source/evidence closure; never runs or advances physical solves."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/anatomical-arm-v1/review/full-p2-p1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((OUT/'evidence-manifest.json').read_text())
for name,h in manifest['sha256'].items():assert sha(ROOT/name)==h,name
summary=json.loads((OUT/'summary.json').read_text());v=json.loads((OUT/'verification.json').read_text())
assert v['result']=='PASS_FRESH_ORIGINAL_STRESS_GRADIENT_REPLAY'
assert len(summary['cases'])==6 and len(v['cases'])==6
for c in summary['cases']:
 r=json.loads((OUT/(c['name']+'.json')).read_text())
 for name,h in r['sourceHashes'].items():assert sha(ROOT/name)==h,name
 assert r['stationaryAccepted'] and r['terminal']['forceResidualN']<=1e-4
 q=next(x for x in v['cases'] if x['name']==c['name'])
 if r['stretch']==1:assert not q['stabilityAssessed'] and q['stabilityClassification']=='UNASSESSED_PASSIVE_CUTOFF'
 else:
  assert all(k['independentNodeGradientRelativeError']<=1e-4 for k in q['gradientChecks'])
  if r['stretch']==1.25:assert q['stabilityClassification']=='NEGATIVE_STATIONARY_DIRECTION'
 assert r['coupling']['rank']==r['pressureCount']
 for p in r['replays'].values():
  assert p['freeNodalResidualN']<=1e-4 and p['maximumGradientDifferenceN']<=2e-6
  assert abs(p['capForceN']-p['virtualForceN'])<=1e-3
  assert p['weakPressureRMS']<=1e-6 and p['pointwisePressureRMS']<=1e-6
  assert .98<=p['Jmin']<=p['Jmax']<=1.02 and p['surface']['crossingPairs']==0
assert all(c['matchedStationaryRefinementPass'] and not c['infSupTrendConcern'] for c in summary['refinement'])
for name,renderer in [('render-receipt.json','full_p2_p1_figure.py'),('render-receipt-v2.json','full_p2_p1_figure_v2.py')]:
 r=json.loads((OUT/name).read_text());assert sha(ROOT/'tools'/renderer)==r['rendererSHA256']
 for p,h in {**r['inputs'],**r['outputs']}.items():assert sha(ROOT/p)==h,p
changed=subprocess.check_output(['git','diff','--name-only','e28cb6631a8f4cba0f250786c0c7d3210200d00d'],cwd=ROOT,text=True).splitlines()
assert all(p.startswith(('education/tools/','education/tests/','education/research/','education/data/anatomical-arm-v1/review/')) for p in changed),changed
subprocess.run(['git','merge-base','--is-ancestor','08f5f3b7fd4b987d3f049c13fdf4338bfaa2928e','HEAD'],cwd=ROOT,check=True)
print(json.dumps(dict(result='PASS_CONTROLLED_MIXED_EVIDENCE_CLOSURE',manifestBindings=len(manifest['sha256']),
 sixStationaryCases=True,descendingNegativeWitnessesRetained=True,cutoffClassificationCorrected=True,
 twoMatchedRefinementLevels=True,twoBoundRendersRetained=True,productionBookLeanProtectedFilesUntouched=True,
 limits='Controlled homogeneous comparator only; anatomical closure and dense trajectory remain unqualified.'),indent=2))

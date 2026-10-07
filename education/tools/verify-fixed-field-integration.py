import json,hashlib,pathlib,math,struct
root=pathlib.Path(__file__).resolve().parents[1]
d=root/'review/fixed-field-integration-run-20261007'
r=json.loads((d/'completion-receipt.json').read_text())
assert not (d/'incomplete-receipt.json').exists()
assert r['runtime']['actualConstitutiveCallbacks']==8847360
assert r['runtime']['completedConstitutiveCallbacks']==8847360
assert r['runtime']['reservedCalls']==8847360
assert r['runtime']['elapsedMs']<900000
assert r['runtime']['peakObservedRssBytes']<=8*1024**3
for name,x in r['outputInventory'].items():
 b=(d/name).read_bytes();assert len(b)==x['bytes'];assert hashlib.sha256(b).hexdigest()==x['sha256'],name
for name,h in r['sourceHashes'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h,name
arrays=json.loads((d/'saved-arrays.json').read_text());direction=arrays['terminalDirectionM'];terms=['matrix','volume','passiveFiber','activePotential','total'];comparisons=json.loads((d/'full-vector-comparisons.json').read_text())['comparisons'];rows=[]
for c in comparisons:
 A=json.loads((d/(c['a']+'-'+c['state']+'-assembly.json')).read_text());B=json.loads((d/(c['b']+'-'+c['state']+'-assembly.json')).read_text())
 for t in terms:
  a=A['hybridNodalGradientsN'][t];b=B['hybridNodalGradientsN'][t];entry=c['terms'][t]
  delta=[[b[n][k]-a[n][k] for k in range(3)] for n in range(585)]
  assert delta==entry['differenceVectorN'];maximum=max(abs(x) for X in delta for x in X)
  assert maximum==entry['maximumAllNodalDifferenceN']
  wa=sum(a[n][k]*direction[n][k] for n in range(585) for k in range(3));wb=sum(b[n][k]*direction[n][k] for n in range(585) for k in range(3))
  assert abs(wa-entry['directionalDerivativeAJ'])<1e-12;assert abs(wb-entry['directionalDerivativeBJ'])<1e-12
  expected=maximum<=1e-5 and abs(wb-wa)<=5.492029235357012e-7
  assert expected==entry['pass']
 assert c['pass']==all(c['terms'][t]['pass'] for t in terms)
 rows.append({'state':c['state'],'a':c['a'],'b':c['b'],'required':c['required'],'allNodalTotalDifferenceN':c['terms']['total']['maximumAllNodalDifferenceN'],'freeTotalDifferenceN':c['terms']['total']['maximumFreeDifferenceN'],'totalDirectionalDifferenceJ':c['terms']['total']['directionalDerivativeDifferenceJ'],'failedTerms':[t for t in terms if not c['terms'][t]['pass']]})
required=[c for c in comparisons if c['required']]
expectedResult='PASS_BOUNDED_FIXED_PATCH_AGREEMENT' if all(c['pass'] for c in required) else 'UNRESOLVED_FIXED_PATCH_INTEGRATION'
assert r['result']==expectedResult
# Audit every local contribution against recorded scatter and weighted volume.
for state in ['control45','terminal46']:
 for recipe in ['U3','U4','U5','D4','D5']:
  a=json.loads((d/(recipe+'-'+state+'-assembly.json')).read_text());scatter={t:[[0.,0.,0.] for n in range(585)] for t in terms};energies={t:0. for t in terms}
  mesh=json.loads((root/'data/anatomical-arm-v1/generated/arm-reference.json').read_text())['muscles'];source=next(x for x in mesh if x['element_id']=='FJ1486')
  for name in a['localElements']:
   e=json.loads((d/name).read_text());assert e['pointCount']==a['recipe']['pointsPerElement']
   w=(d/(recipe+'-element-'+str(e['element'])+'-reference-weights.f64le')).read_bytes();assert len(w)==e['pointCount']*8
   assert all(x[0]>0 and math.isfinite(x[0]) for x in struct.iter_unpack('<d',w))
   for t in terms:
    energies[t]+=e['energiesJ'][t]
    for i,n in enumerate(source['elements_ten_node'][e['element']]):
     for k in range(3):scatter[t][n][k]+=e['localGradientsN'][t][i][k]
  if recipe!='U3':
   assert scatter==a['patchNodalGradientsN'];assert energies==a['patchEnergiesJ']
  else:assert scatter==a['hybridNodalGradientsN'];assert energies==a['hybridEnergiesJ']
v={'schema':1,'result':'PASS_OWN_HASH_VECTOR_DIRECTION_SCATTER_ACCOUNTING_VERIFICATION','independentReview':False,'constitutiveCalls':0,'reservedActualCompletedCalls':8847360,'outputHashesChecked':len(r['outputInventory']),'sourceHashesChecked':len(r['sourceHashes']),'runtime':r['runtime'],'diagnosticResult':r['result'],'comparisonSummary':rows,'limits':'Finite patch agreement only; no global integration, equilibrium or displacement qualification'}
print('Verification produces no material calls and preserves all existing evidence.')
print(json.dumps(v,indent=2))

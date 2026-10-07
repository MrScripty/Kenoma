#!/usr/bin/env python3
"""Independent read-only arithmetic/protocol review. No model imports or rule generation."""
import hashlib, json, math, pathlib, subprocess
ROOT=pathlib.Path('/workspace/Kenoma-patch-proposal')
EDU=ROOT/'education'
OUT=pathlib.Path('/tmp')
HEAD='788bbd7c86b23a5bdec18e67a2c70ba1f82cc711'
REC='f7cc2c0f10b536e94557ce978aa1691d6c92246f'
RAW='74054f5c611c57c0b9ddb1fd77a9aaba20ee9c8b'
SHELL='4b83ec5dfebae73b08c3f964aa910f65e02458e0'
FAILED='9c9edbc9f3dd9729f2becc5215054897d139735e'
OLD='review/fixed-field-integration-run-20261007/'
SR='review/element247-shell-run-20261007/material/'
FR='review/element247-two-shell-run-20261007/'
TERMS=['matrix','volume','passiveFiber','activePotential','total']
STATES=['control45','terminal46']
PATCH=[195,196,197,198,199,200,202,203,206,237,240,243,244,246,247,248]
SECOND=[197,200,203,206,246,248]
QUIET=[195,196,198,199,202,237,240,243,244]
GATE=1e-5; WORKGATE=5.492029235357012e-7
reads={}; anchors={}; logs=[]
def sha(b): return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def blob(c,p):return git('cat-file','blob',c+':education/'+p)
def read(p,extra=None):
 b=(EDU/p).read_bytes(); assert b==blob(REC,p),p
 if extra:assert b==blob(extra,p),(extra,p)
 reads[p]={'bytes':len(b),'sha256':sha(b),'recoveryByteExact':True,'rawAnchor':extra}
 return json.loads(b)
def serial(x):return json.dumps(x,separators=(',',':'),allow_nan=False).encode()
def norm(v,nodes=range(585)):return max((abs(v[n][d]) for n in nodes for d in range(3)),default=0.)
def subtract(a,b):return [[a[n][d]-b[n][d] for d in range(3)]for n in range(585)]
def metrics(v,t):
 return {'aggregateInfinityN':norm(v),'elementTriangleInfinityN':norm(t),'freeInfinityN':norm(v,free),'heldReactionInfinityN':norm(v,held),'freeTriangleInfinityN':norm(t,free),'heldTriangleInfinityN':norm(t,held),'aggregateWorkJ':abs(math.fsum(v[n][d]*direction[n][d] for n in range(585) for d in range(3))),'entryWorkAbsoluteBoundJ':math.fsum(t[n][d]*abs(direction[n][d]) for n in range(585) for d in range(3))}
def scatter(elements, records, term):
 bins=[[[] for _ in range(3)] for _ in range(585)]
 for e in elements:
  rec=records[e]
  assert rec['element']==e
  for i,n in enumerate(connect[e]):
   for d in range(3):bins[n][d].append(rec['localGradientsN'][term][i][d])
 return [[math.fsum(q)for q in row]for row in bins]
def compare(st,a,b,elements,records=None):
 records=records or local[st]
 result={}
 for term in TERMS:
  signed=[[[]for _ in range(3)]for _ in range(585)]
  triangles=[[[]for _ in range(3)]for _ in range(585)]
  unit_work=[];unit_energies=[]
  for e in elements:
   ar,br=records[a][e],records[b][e];wd=[]
   for i,n in enumerate(connect[e]):
    for d in range(3):
     delta=ar['localGradientsN'][term][i][d]-br['localGradientsN'][term][i][d]
     signed[n][d].append(delta);triangles[n][d].append(abs(delta));wd.append(delta*direction[n][d])
   unit_work.append(math.fsum(wd));unit_energies.append(ar['energiesJ'][term]-br['energiesJ'][term])
  v=[[math.fsum(q)for q in row]for row in signed];t=[[math.fsum(q)for q in row]for row in triangles]
  m=metrics(v,t);m['aggregateWorkJ']=abs(math.fsum(unit_work));m['elementWorkTriangleJ']=math.fsum(abs(q)for q in unit_work)
  m['signedEnergyDifferenceJ']=math.fsum(unit_energies);m['elementEnergyTriangleJ']=math.fsum(abs(q)for q in unit_energies)
  m['signedForcePass']=m['aggregateInfinityN']<=GATE;m['triangleForcePass']=m['elementTriangleInfinityN']<=GATE
  m['signedWorkPass']=m['aggregateWorkJ']<=WORKGATE;m['triangleWorkPass']=m['elementWorkTriangleJ']<=WORKGATE
  result[term]=m
 return result
assert git('rev-parse','HEAD').decode().strip()==HEAD
assert git('show','-s','--format=%P',HEAD).decode().strip()==REC
assert git('status','--porcelain').decode()==''
proposal_hashes={}
for ext in ['md','py','json']:
 p='research/fixed-patch-selective-proposal-20261007'+ ('-analysis.'+ext if ext!='md' else '.md')
 b=(EDU/p).read_bytes();assert b==blob(HEAD,p);proposal_hashes[p]={'bytes':len(b),'sha256':sha(b)}
producer=json.loads((EDU/'research/fixed-patch-selective-proposal-20261007-analysis.json').read_bytes())
expected=set([OLD+'saved-arrays.json','data/anatomical-arm-v1/generated/arm-reference.json'])
expected|={OLD+f'{r}-{s}-element-{e}-local.json'for r in ['U4','U5','D4','D5']for s in STATES for e in PATCH}
expected|={OLD+f'{r}-{s}-assembly.json'for r in ['U3','U4','U5','D4','D5']for s in STATES}
expected|={OLD+'completion-receipt.json',OLD+'execution-receipt.json','review/element247-shell-run-outcome-20261007/result-summary.json',FR+'material/incomplete-receipt.json','review/element247-two-shell-reconstructed-20261007/reconstructed-diagnostic.json','review/element247-two-shell-reconstructed-20261007/independent-review.json'}
expected|={'tools/element247-two-shell-schema.mjs','tools/element247-shell-protocol.mjs','tools/fixed-field-integration-protocol.mjs','tools/element247_shell_execution.py','tests/element247_two_shell.test.mjs'}
assert len(expected)==151 and expected==set(producer['inputInventory'])
for p in expected:
 b=(EDU/p).read_bytes();assert b==blob(REC,p)
 assert {'bytes':len(b),'sha256':sha(b)}==producer['inputInventory'][p],p
 if p.endswith('.json'):read(p,RAW if p.startswith(OLD) else FAILED if p==FR+'material/incomplete-receipt.json' else SHELL if p.startswith('review/element247-shell-run-outcome') else None)
arrays=read(OLD+'saved-arrays.json',RAW)
assert arrays['patchElements']==PATCH
source=read('data/anatomical-arm-v1/generated/arm-reference.json')
muscle=next(m for m in source['muscles']if m['element_id']=='FJ1486');connect=muscle['elements_ten_node']
assert len(connect)==252
assert [e for e,c in enumerate(connect)if 92 in c]==PATCH
assert all(connect[e].index(92)<4 for e in PATCH)
free=arrays['freeNodeOrder'];held=arrays['heldNodeOrder'];direction=arrays['terminalDirectionM']
assert len(free)==495 and len(held)==90 and set(free).isdisjoint(held) and sorted(free+held)==list(range(585))
assert len(direction)==585 and all(len(v)==3 for v in direction)
assert all(direction[n]==[0,0,0]for n in held)
assert all(len(arrays['positionsM'][s])==585 for s in STATES)
for s in STATES:
 assert all(len(v)==3 and all(math.isfinite(q)for q in v)for v in arrays['positionsM'][s])
local={s:{r:{e:read(OLD+f'{r}-{s}-element-{e}-local.json',RAW)for e in (range(252)if r=='U3'else PATCH)}for r in ['U3','U4','U5','D4','D5']}for s in STATES}
assembly={s:{r:read(OLD+f'{r}-{s}-assembly.json',RAW)for r in local[s]}for s in STATES}
replay={}; replay_vectors={};max_component_force=0.;max_component_energy=0.
for s in STATES:
 replay[s]={};replay_vectors[s]={}
 for r in local[s]:
  records=local[s][r];a=assembly[s][r];elements=list(records)
  assert a['elementOrder']==elements and len(a['localElements'])==len(elements)
  assert all(q['pointCount']==a['recipe']['pointsPerElement']for q in records.values())
  assert all(len(q['localGradientsN'][t])==10 and all(len(v)==3 and all(math.isfinite(x)for x in v)for v in q['localGradientsN'][t])and math.isfinite(q['energiesJ'][t])for q in records.values()for t in TERMS)
  patches={t:scatter(PATCH,records,t)for t in TERMS}
  whole={t:scatter(elements,records,t)for t in TERMS}
  if r!='U3':
   base=replay_vectors[s]['U3']['hybridNodalGradientsN'];oldpatch=replay_vectors[s]['U3']['patchNodalGradientsN']
   whole={t:[[math.fsum([base[t][n][d],-oldpatch[t][n][d],patches[t][n][d]])for d in range(3)]for n in range(585)]for t in TERMS}
  patch_energy={t:math.fsum(records[e]['energiesJ'][t]for e in PATCH)for t in TERMS}
  full_energy={t:math.fsum(records[e]['energiesJ'][t]for e in elements)for t in TERMS}if r=='U3'else {t:math.fsum([replay_vectors[s]['U3']['hybridEnergiesJ'][t],-replay_vectors[s]['U3']['patchEnergiesJ'][t],patch_energy[t]])for t in TERMS}
  work={t:math.fsum(whole[t][n][d]*direction[n][d]for n in range(585)for d in range(3))for t in TERMS}
  err={t:{'patchScatterMaximumErrorN':norm(subtract(patches[t],a['patchNodalGradientsN'][t])),'fullHybridMaximumErrorN':norm(subtract(whole[t],a['hybridNodalGradientsN'][t])),'patchEnergyErrorJ':abs(patch_energy[t]-a['patchEnergiesJ'][t]),'fullEnergyErrorJ':abs(full_energy[t]-a['hybridEnergiesJ'][t]),'directionalWorkErrorJ':abs(work[t]-a['terminalDirectionalDerivativesJ'][t]),'heldReactionMaximumErrorN':norm(subtract(whole[t],a['hybridNodalGradientsN'][t]),held)}for t in TERMS}
  assert all(m['patchScatterMaximumErrorN']<1e-8 and m['fullHybridMaximumErrorN']<1e-8 and m['heldReactionMaximumErrorN']<1e-8 and m['patchEnergyErrorJ']<1e-9 and m['fullEnergyErrorJ']<1e-9 and m['directionalWorkErrorJ']<1e-9 for m in err.values())
  for rec in records.values():
   for i in range(10):
    for d in range(3):max_component_force=max(max_component_force,abs(rec['localGradientsN']['total'][i][d]-math.fsum(rec['localGradientsN'][t][i][d]for t in TERMS[:-1])))
   max_component_energy=max(max_component_energy,abs(rec['energiesJ']['total']-math.fsum(rec['energiesJ'][t]for t in TERMS[:-1])))
  replay[s][r]={'termErrors':err,'totalFullFreeResidualInfinityN':norm(whole['total'],free),'totalFullHeldReactionInfinityN':norm(whole['total'],held),'stationarityGateN':1e-4,'stationarityPass':norm(whole['total'],free)<=1e-4,'totalFullEnergyJ':full_energy['total'],'totalSavedDirectionWorkJ':work['total'],'fullComponentForceErrorN':max(abs(whole['total'][n][d]-math.fsum(whole[t][n][d]for t in TERMS[:-1]))for n in range(585)for d in range(3)),'fullComponentEnergyErrorJ':abs(full_energy['total']-math.fsum(full_energy[t]for t in TERMS[:-1]))}
  replay_vectors[s][r]={'hybridNodalGradientsN':whole,'patchNodalGradientsN':patches,'hybridEnergiesJ':full_energy,'patchEnergiesJ':patch_energy,'terminalDirectionalDerivativesJ':work}
assert max_component_force<1e-8 and max_component_energy<1e-9
pairs=[('U4','U5'),('D4','D5'),('U5','D5')]
subsets={s:{label:{a+'-'+b:compare(s,a,b,es)for a,b in pairs}for label,es in [('quiet9',QUIET),('secondary6',SECOND),('all15Except247',[e for e in PATCH if e!=247]),('full16',PATCH)]}for s in STATES}
per_element={s:{str(e):{'localCornerAtNode92':connect[e].index(92),'minimumRetainedSampleJ':min(local[s][r][e]['minimumSampleJ']for r in ['U4','U5','D4','D5']),'comparisons':{a+'-'+b:compare(s,a,b,[e])for a,b in pairs}}for e in PATCH}for s in STATES}
producer_errors=[]
for s in STATES:
 for label in subsets[s]:
  for pair in subsets[s][label]:
   for t in TERMS:
    for k in ['aggregateInfinityN','elementTriangleInfinityN','aggregateWorkJ','elementWorkTriangleJ']:
     x=subsets[s][label][pair][t][k];y=producer['subsetComparisons'][s][label][pair][t][k]
     assert math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-18),(s,label,pair,t,k,x,y)
     producer_errors.append(abs(x-y))
 for e in per_element[s]:
  assert per_element[s][e]['localCornerAtNode92']==producer['perElement'][s][e]['localCornerAtNode92']
  assert per_element[s][e]['minimumRetainedSampleJ']==producer['perElement'][s][e]['minimumRetainedSampleJ']
  for pair in per_element[s][e]['comparisons']:
   for t in TERMS:
    for k in ['aggregateInfinityN','elementTriangleInfinityN','aggregateWorkJ','elementWorkTriangleJ']:
     x=per_element[s][e]['comparisons'][pair][t][k];y=producer['perElement'][s][e]['comparisons'][pair][t][k]
     assert math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-18),(s,e,pair,t,k,x,y)
for s in STATES:
 for pair in ['D4-D5','U5-D5']:
  assert all(subsets[s]['quiet9'][pair][t]['triangleForcePass']and subsets[s]['quiet9'][pair][t]['triangleWorkPass']for t in TERMS)
assert not subsets['terminal46']['all15Except247']['U5-D5']['total']['triangleForcePass']
# Verify exact source inventories against their executed commit and immutable recovery.
starts=[read(OLD+'execution-start.json',RAW),read(SR+'material-start.json',SHELL),read(FR+'material/material-start.json',FAILED)]
source_verified=[]
for st in starts:
 c=st['sourceCommit'];count=0; historical_differences=[]
 for p,h in st['sourceHashes'].items():
  b=(EDU/p).read_bytes();executed_blob=blob(c,p);assert sha(executed_blob)==h and b==blob(REC,p),(c,p)
  if b!=executed_blob:historical_differences.append({'path':p,'executedSHA256':h,'recoverySHA256':sha(b)})
  count+=1
 source_verified.append({'executedCommit':c,'hashesVerified':count,'historicalVsRecoveryDifferences':historical_differences})
assert starts[0]['sourceCommit']=='ef39f8335486b5cd7c9954361da181f46ea21c80'
assert starts[1]['sourceCommit']=='07aafe8b1c1ef27d212434232f4546feb27449ac'
assert starts[2]['sourceCommit']=='97da4bdea7d0be11fc18222221b8b551b53a8e3b'
assert starts[0]['material']==starts[1]['material']==starts[2]['material']
# Exact field hashes without invoking JS: historical raw JSON.stringify identities compared to bound saved-array JSON.
field_identity={s:{'sha256':next(q['positionsSha256']for q in starts[0]['states']if q['id']==s),'sameAsWholeShell':next(q['positionsSha256']for q in starts[0]['states']if q['id']==s)==next(q['positionsSha256']for q in starts[1]['states']if q['id']==s)}for s in STATES}
assert starts[0]['terminalDirectionSha256']==starts[1]['terminalDirectionSha256']=='bb8bc986540e2e3e098969db2b34b3682f55602d868c9972e35b42464972cdab'
assert (EDU/(FR+'material/saved-arrays.json')).read_bytes()==(EDU/(OLD+'saved-arrays.json')).read_bytes()
recovered_path='review/element247-two-shell-reconstructed-20261007/reconstructed-diagnostic.json'
recovered=read(recovered_path)
review=read('review/element247-two-shell-reconstructed-20261007/independent-review.json')
assert reads[recovered_path]['sha256']=='3efbc3f28b648cf7d5b0f152b865f13aae7ccc89fd752af58d0e35d92da103a6'==review['candidateSha256']
assert review['sourceCommit']=='1671433376014ad148799e1ad7ff3f10219643f7'
assert recovered['originalExitCodes']=={'child':1,'worker':1,'publicEntry':1}and recovered['operationalCompletion']is False
assert recovered['authorizationStatus']=='CONSUMED_BY_ORIGINAL_ONE_SHOT; NO_RETRY_AUTHORIZATION'
assert read(FR+'external-exit.json',FAILED)['childExitCode']==1
assert read(FR+'external-incomplete.json',FAILED)['childExitCode']==1
assert read(FR+'supervisor-incomplete.json',FAILED)['launcherExitCode']==1
for p,m in recovered['provenance']['immutableInputInventory'].items():
 b=(EDU/p).read_bytes();assert sha(b)==m['sha256']and len(b)==m['bytes']and b==blob(REC,p),(p,'recovered inventory')
# Accepted retained changed-region records. No rules generated.
changed=[read(FR+f'material/T24-terminal46-s{i}-shell.json',FAILED)for i in [1,2]]
assert sum(q['pointCount']for q in changed)==4000
assert starts[2]['recipe']['depth']==20 and starts[2]['recipe']['radialParts']==1 and starts[2]['recipe']['angularParts']==4
# The original metadata omission is preserved; no construction is called.
assert all('shell'not in q and q['id']==q['comparisonShell']for q in changed)
for i in range(3,21):
 p=FR+f'material/A55-terminal46-s{i}-shell.json';assert (EDU/p).read_bytes()==(EDU/(SR+f'A55-terminal46-s{i}-shell.json')).read_bytes()
assert (EDU/(FR+'material/A55-terminal46-core-shell.json')).read_bytes()==(EDU/(SR+'A55-terminal46-core-shell.json')).read_bytes()
# Independently replay all complete historical shell records and all comparisons.
shell_local={};shell_replay={};shell_grouped={};shell_vectors={}
for s in STATES:
 shell_local[s]={};shell_replay[s]={};shell_grouped[s]={};shell_vectors[s]={}
 for r in ['C44','C55','R55','A55','X55']:
  asm=read(SR+f'{r}-{s}-assembly.json',SHELL)
  regions={i:read(SR+f'{r}-{s}-{i}-shell.json',SHELL)for i in asm['originalShells']}
  assert len(regions)==(23 if r=='X55'else 21)
  assert sum(q['pointCount']for q in regions.values())==asm['pointCount']
  shell_local[s][r]=regions
  local_sum={t:[[math.fsum(q['localGradientsN'][t][i][d]for q in regions.values())for d in range(3)]for i in range(10)]for t in TERMS}
  energy={t:math.fsum(q['energiesJ'][t]for q in regions.values())for t in TERMS}
  nodal={t:scatter([247],{247:{'element':247,'localGradientsN':{t:local_sum[t]}}},t)for t in TERMS}
  work={t:math.fsum(nodal[t][n][d]*direction[n][d]for n in range(585)for d in range(3))for t in TERMS}
  checks={t:{'localForceErrorN':max(abs(local_sum[t][i][d]-asm['localGradientsN'][t][i][d])for i in range(10)for d in range(3)),'all585ScatterErrorN':norm(subtract(nodal[t],asm['nodalGradientsN'][t])),'energyErrorJ':abs(energy[t]-asm['energiesJ'][t]),'workErrorJ':abs(work[t]-asm['terminalDirectionalDerivativesJ'][t]),'heldReactionErrorN':norm(subtract(nodal[t],asm['nodalGradientsN'][t]),held)}for t in TERMS}
  assert all(m['localForceErrorN']<1e-8 and m['all585ScatterErrorN']<1e-8 and m['heldReactionErrorN']<1e-8 and m['energyErrorJ']<1e-9 and m['workErrorJ']<1e-9 for m in checks.values())
  shell_replay[s][r]=checks;shell_vectors[s][r]={'localGradientsN':local_sum,'nodalGradientsN':nodal,'energiesJ':energy,'terminalDirectionalDerivativesJ':work}
  groups={}
  for unit in [f's{i}'for i in range(1,21)]+['core']:
   members=[q for q in regions.values()if q['comparisonShell']==unit]
   assert members
   groups[unit]={'element':247,'localGradientsN':{t:[[math.fsum(q['localGradientsN'][t][i][d]for q in members)for d in range(3)]for i in range(10)]for t in TERMS},'energiesJ':{t:math.fsum(q['energiesJ'][t]for q in members)for t in TERMS}}
  assert len(groups)==21
  for q in asm['comparisonShells']:
   for t in TERMS:
    assert max(abs(groups[q['shell']]['localGradientsN'][t][i][d]-q['localGradientsN'][t][i][d])for i in range(10)for d in range(3))<1e-8
  shell_grouped[s][r]=groups
old_comparisons=read(SR+'shell-vector-comparisons.json',SHELL)['comparisons']
def compare247units(left,right):
 out={}
 for t in TERMS:
  units=list(left);diff={u:[[left[u]['localGradientsN'][t][i][d]-right[u]['localGradientsN'][t][i][d]for d in range(3)]for i in range(10)]for u in units}
  agg=[[math.fsum(diff[u][i][d]for u in units)for d in range(3)]for i in range(10)]
  tri=[[math.fsum(abs(diff[u][i][d])for u in units)for d in range(3)]for i in range(10)]
  nv=[[0.,0.,0.]for _ in range(585)];nt=[[0.,0.,0.]for _ in range(585)]
  for i,n in enumerate(connect[247]):nv[n]=agg[i];nt[n]=tri[i]
  w=[math.fsum(diff[u][i][d]*direction[n][d]for i,n in enumerate(connect[247])for d in range(3))for u in units]
  out[t]={'aggregateInfinityN':norm(nv),'shellTriangleInfinityN':norm(nt),'aggregateDirectionalDifferenceJ':abs(math.fsum(w)),'shellTriangleDirectionalDifferenceJ':math.fsum(abs(q)for q in w),'entryWorkAbsoluteBoundJ':math.fsum(nt[n][d]*abs(direction[n][d])for n in range(585)for d in range(3)),'signedEnergyDifferenceJ':math.fsum(left[u]['energiesJ'][t]-right[u]['energiesJ'][t]for u in units),'freeInfinityN':norm(nv,free),'heldReactionInfinityN':norm(nv,held),'forcePass':norm(nv)<=GATE and norm(nt)<=GATE,'workPass':abs(math.fsum(w))<=WORKGATE and math.fsum(abs(q)for q in w)<=WORKGATE}
 return out
shell_comparisons={}
for saved in old_comparisons:
 s=saved['state'];a=saved['a'];b=saved['b'];computed=compare247units(shell_grouped[s][a],shell_grouped[s][b])
 for t in TERMS:
  for k in ['aggregateInfinityN','shellTriangleInfinityN','aggregateDirectionalDifferenceJ','shellTriangleDirectionalDifferenceJ']:
   assert math.isclose(computed[t][k],abs(saved['terms'][t][k]),rel_tol=1e-10,abs_tol=1e-13),(s,a,b,t,k)
  assert saved['terms'][t]['forceGateN']==GATE and saved['terms'][t]['derivativeGateJ']==WORKGATE
  assert saved['terms'][t]['pass']==(computed[t]['forcePass']and computed[t]['workPass'])
 shell_comparisons[s+':'+a+'-'+b]=computed
changed_comp=compare247units({q['id']:shell_local['terminal46']['A55'][q['id']]for q in changed},{q['id']:q for q in changed})
for t in TERMS:
 saved=recovered['changedShellComparison']['terms'][t]
 for k in ['aggregateInfinityN','shellTriangleInfinityN','aggregateDirectionalDifferenceJ','shellTriangleDirectionalDifferenceJ']:
  assert math.isclose(changed_comp[t][k],abs(saved[k]),rel_tol=1e-10,abs_tol=1e-13),(t,k)
 # All19 same-tail reconstructed differences are exactly zero by construction.
 same_tail=[q for q in recovered['constructedWholeComparison']['terms'][t]['differences']if q['shell']not in ['s1','s2']]
 assert len(same_tail)==19 and all(all(x==0 for v in q['localDifferenceN']for x in v)for q in same_tail)
# Independent saved field/direction exact JSON.stringify hash identity with Node standard library only.
node_hash_code="const fs=require('node:fs'),c=require('node:crypto');const a=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));const h=x=>c.createHash('sha256').update(JSON.stringify(x)).digest('hex');console.log(JSON.stringify({control45:h(a.positionsM.control45),terminal46:h(a.positionsM.terminal46),direction:h(a.terminalDirectionM)}));"
exact_field_hash=json.loads(subprocess.check_output(['node','-e',node_hash_code,str(EDU/(OLD+'saved-arrays.json'))],cwd=OUT))
for s in STATES:assert exact_field_hash[s]==field_identity[s]['sha256']
assert exact_field_hash['direction']==starts[0]['terminalDirectionSha256']
assert starts[2]['state']['positionsSha256']==exact_field_hash['terminal46']
# Proposed cheaper alternative retained D4/D5 part already passes all15 triangle and signed gates.
assert all(subsets[s]['all15Except247']['D4-D5'][t]['triangleForcePass']and subsets[s]['all15Except247']['D4-D5'][t]['triangleWorkPass']for s in STATES for t in TERMS)

# Rule count and storage arithmetic independently enumerated recipes, no coordinates or quadrature calls.
recipes=[('secondaryC55',6,20,5,1,1,0),('secondaryA55',6,20,5,2,1,0),('247F44',1,20,5,4,1,4000),('247R44',1,20,5,4,2,0),('247X44',1,22,5,4,1,0)]
costs=[]
for name,elements,depth,gauss,angular,radial,reuse in recipes:
 n=(depth+1)*gauss**3*angular**2*radial
 costs.append({'name':name,'elements':elements,'depth':depth,'Gauss':gauss,'angularPartsPerAxis':angular,'radialParts':radial,'pointsPerElementPerField':n,'fields':2,'reusedTerminalMeasurements':reuse,'newCallbacks':elements*n*2-reuse})
new_calls=sum(q['newCallbacks']for q in costs)
physical=8*sum(q['elements']*q['pointsPerElementPerField']for q in costs)
normalized=48*sum((4 if q['elements']==6 else 1)*q['pointsPerElementPerField']for q in costs)
logical=2*sum(q['elements']*(q['depth']+1)for q in costs)
assert(new_calls,physical,normalized,logical)==(497500,2006000,10776000,634)
assert producer['cost']['newCallbacks']==new_calls and producer['cost']['newUniquePhysicalWeightBytes']==physical and producer['cost']['normalizedRuleBytesIncludingFourSecondaryCornerPermutations']==normalized and producer['cost']['logicalShellRecordsBothFields']==logical
fullreceipt=read(OLD+'completion-receipt.json',RAW);exec_receipt=read(OLD+'execution-receipt.json',RAW)
shellsummary=read('review/element247-shell-run-outcome-20261007/result-summary.json',SHELL)
incomplete=read(FR+'material/incomplete-receipt.json',FAILED)
timing={'largeFullPatchSeconds':new_calls*exec_receipt['elapsedSeconds']/fullreceipt['runtime']['completedConstitutiveCallbacks'],'wholeShellSeconds':new_calls*(shellsummary['launcherExit']['elapsedMs']/1000)/shellsummary['finalRuntimeMarker']['completedConstitutiveCallbacks'],'smallChangedBatchSeconds':new_calls*(incomplete['runtime']['elapsedMs']/1000)/incomplete['runtime']['completedConstitutiveCallbacks']}
# Own replay retains all recomputed vectors as scratch supporting evidence.
vec_path=OUT/'independent_selective_patch_replayed_vectors.json'
vec_path.write_text(json.dumps({'fullPatch':replay_vectors,'shell':shell_vectors},separators=(',',':'))+'\n')
report={'schema':1,'verdict':'CONDITIONAL','qualifiedVerdict':'CONDITIONAL_PASS_SCIENTIFIC_PROTOCOL_DESIGN_ONLY','scope':'Independent read-only scientific/protocol review of frozen proposal, retained arithmetic and cost. Not implementation, structural preflight, execution authorization, operational acceptance or integration qualification.','reviewedProposalHead':HEAD,'parentRecoveryAnchor':REC,'proposalHashes':proposal_hashes,'repositoryGuidance':'No AGENTS.md found under /workspace; repository status verified clean; no repository writes.','activity':{'newMaterialCalls':0,'newSpecimenCalls':0,'quadratureGenerated':False,'optimizerOrRefit':False,'producerScriptExecuted':False,'runnerOrConstructorExecuted':False,'repositoryFilesModified':False},'producerInputInventory':{'entries':151,'expectedInventorySetMatches':True,'allByteCountsAndSHA256Match':True,'allRecoveryBlobsByteExact':True},'sourceAnchors':{'fullPatchRaw':RAW,'wholeShellRaw':SHELL,'failedTwoShellRaw':FAILED,'recovery':REC,'reviewedRecoverySource':review['sourceCommit'],'recoveredDiagnosticSHA256':reads[recovered_path]['sha256'],'sourceInventoryVerification':source_verified},'fieldIdentity':field_identity,'terminalDirection':{'unchangedWorkGateJ':WORKGATE,'forceGateTimesDirectionL1J':GATE*math.fsum(abs(x)for v in direction for x in v),'sha256':starts[0]['terminalDirectionSha256'],'heldExactlyZero':True,'L1NormM':math.fsum(abs(x)for v in direction for x in v),'maximumNodalNormM':max(math.sqrt(math.fsum(x*x for x in v))for v in direction)},'retainedReplay':{'states':STATES,'nodes':585,'heldNodes':90,'freeNodes':495,'U3ElementsPerState':252,'patchElementsPerOtherRule':16,'terms':TERMS,'localRecordCount':632,'allLocalScatterFullHybridEnergyWorkErrors':replay,'maximumLocalTotalComponentReconstructionErrorN':max_component_force,'maximumLocalTotalEnergyReconstructionErrorJ':max_component_energy,'producerSubsetArithmeticMaximumAbsoluteDifference':max(producer_errors),'vectorsArtifact':{'path':str(vec_path),'bytes':vec_path.stat().st_size,'sha256':sha(vec_path.read_bytes())}},'shellRetainedReplay':{'originalRecords':214,'allAssemblies':shell_replay,'allEightComparisons':shell_comparisons,'changedTwoShellIndependentArithmetic':changed_comp,'identical19TailZeroDifferencesGiveNoIndependentEvidence':True,'savedArrayExactJSONstringifyHashes':exact_field_hash},'perElement':per_element,'subsetComparisons':subsets,'cost':{'schedule':costs,'newCallbacks':new_calls,'uniquePhysicalWeightBytes':physical,'normalizedRuleBytesFourSecondaryPermutations':normalized,'rawBinaryBytes':physical+normalized,'logicalShellRecordsBothFields':logical,'savedVs8847360Percent':100*(1-new_calls/8847360),'directHistoricalExtrapolationSeconds':timing,'newDeclaredProposedResourceEnvelope':{'wallSeconds':300,'outputBytes':64*1024**2,'nodeHeapMiB':1024,'rssBytes':2*1024**3},'oldShellLimits':{'wallSeconds':180,'outputBytes':64*1024**2},'oldFullPatchLimits':{'wallSeconds':900,'outputBytes':256*1024**2},'budgetInterpretation':'300s/64MiB are NEW DECLARED PROPOSED limits for this schedule; 64MiB numerically matches old shell ceiling, but resource envelope is new and unauthorized. 300s increases old shell wall by 120s and decreases old full-patch wall by 600s. Output ceiling is old-shell-equal, one-quarter old full-patch.','estimationLimits':'14/75/135s are noncomparable historical aggregate-rate extrapolations. They include different setup/output scopes and do not prove a 20-180s interval or guarantee 300s completion. 20-32MiB is plausible planning only; schemas/encoding/metadata/provenance worst-case sizes are not frozen.'},'protocolFindings':[
 'Stationarity at1e-4N remains a separate diagnostic; independently replayed total full free residuals are reported and no equilibrium acceptance follows from agreement.',
 'Both fields, every patch element and all 585 nodes are preserved. U3 baseline minus old complete patch plus proposed patch is arithmetically coherent; shared-node scatters are additive and counted once.',
 'Quiet9 D4/D5 and U5/D5 cover complete tetrahedra independently and pass all five term force and work triangle gates. Reuse is justified only as finite retained method agreement, not analytic error certification.',
 'Terminal all15Except247 U5/D5 total signed maximum passes but element triangle fails. Deleting247 or substituting a signed pass is scientifically invalid.',
 'Q0/Q1/Q2 use distinct complete rules on every element: quiet D4/D5/U5; secondary C55/A55/D5; 247 retained A55/F44/X44. Required Q0-Q1 and Q1-Q2 comparisons do not contain identical full tails. Q0-Q2 remains informational.',
 'Secondary corner permutations are 197/200->3,203->2,206->1,246/248->0; opposite-face ascending indices and moment permutations must be bound at future preflight. A node92-centered chart is full coverage, not evidence of a secondary singularity.',
 '247 F44 samples all21 regions at angular4, including19 newly evaluated terminal tails and all control samples. Reused terminal s1/s2 total4000 are old accepted measurements with original missing shell metadata; future reuse requires explicit normalized schema copies bound to raw hashes, never editing raw data.',
 'F44/R44 angular resolution matches; radial subdivision changes alone. Other15 contributions cancel in this isolated test and cannot gain qualification from it.',
 'X44 depth22 and face231 change together. Its23 original bins must remain durable before aggregating s21/s22/core into the common depth20 core; depth/chart sensitivity remains coupled.',
 'Q0/Q1 units are9 whole elements plus147 shell bins; Q1/Q2 units are15 whole elements plus21 bins. Retained secondary D5 has only whole-element stresses and cannot support invented shell-resolved comparisons. F44/R44 uses21 bins.',
 'At unchanged1e-5N/5.492029235357012e-7J require signed and unit-triangle gates for all five terms and both states, including held reactions; work is algebraic finite-direction agreement, not independent quadrature certification. Unit cancellation remains possible.',
 'All236 unchanged U3 outside elements remain unqualified. Old full-patch and shell failures remain unresolved. Old failed two-shell child/worker/public exit1 and consumed authorization remain preserved.'
 ],'conditionsBeforeImplementationDecision':[
 'Describe heading Smallest defensible first schedule as a proposed first schedule; retained data do not establish minimality or future convergence. A scientifically weaker but cheaper complete-comparison alternative exists.',
 'Explicitly label300s/64MiB as new declared proposed budgets, not unchanged or authorized historical limits. Numeric64MiB equals old shell ceiling, but new wall and call envelope require separate future authorization.',
 'Treat runtime20-180s and artifact20-32MiB as planning estimates only. Future structural preflight must freeze complete encoding schemas and prove worst-case serialized byte counts including all634 records, comparisons, 585-node vectors and receipts.',
 'Future structural preflight must independently validate point/weight/moment/chart/permutation/coverage/cap/J/scatter/hashes and corrected nonzero serialization-constructor fixtures; none of those ungenerated new rule properties are accepted by this review.'
 ],'cheaperScientificallyValidAlternative':{'status':'Design alternative only; weaker secondary comparison-unit granularity; no claim it will pass.','Q0':{'quiet9':'retainedD4','secondary6':'retainedD4','247':'retainedA55'},'Q1':{'quiet9':'retainedD5','secondary6':'retainedD5','247':'F44'},'Q2':{'quiet9':'retainedU5','secondary6':'newA55','247':'X44'},'omittedWork':'Secondary six C55 only','newCallbacks':new_calls-costs[0]['newCallbacks'],'callbacksSaved':costs[0]['newCallbacks'],'uniquePhysicalWeightBytes':physical-8*6*2625,'normalizedRuleBytes':normalized-48*4*2625,'logicalShellRecordsBothFields':logical-2*6*21,'requiredComparisonUnits':'Both Q0/Q1 and Q1/Q2 use15 whole elements plus24721bins; unchanged signed and cancellation-resistant force/work gates, retained D4/D5 and U5/D5 diagnostic failures, full-tail F44/X44 independence and matched F44/R44 remain.','tradeoff':'Saves31500 callbacks (6.33%) and removes six newly generated coarse shell rules. Q0/Q1 reuses retained D4/D5 on all15; Q1/Q2 compares new A55 secondary against retained whole-element D5. Secondary angular-subdivision sensitivity and shell-bin cancellation protection are omitted. Within-secondary-element cancellation can mask shell differences; unacceptable if shell-bin secondary angular evidence is a hard objective.'},'historicalDisposition':{'fullPatchResult':fullreceipt['result'],'wholeShellResult':shellsummary['result'],'twoShellOriginalExitCodes':recovered['originalExitCodes'],'twoShellOperationalCompletion':False,'authorizationStatus':recovered['authorizationStatus'],'noNewQualification':True},'readInventory':reads}
conditions=report.pop('conditionsBeforeImplementationDecision')
report['conditions']={'designWordingAndResourceDeclarations':conditions[:3],'deferredStructuralPreflightEvidence':conditions[3:],'deferredExecutionEvidence':['Separate future authorization, exactly497500 newly reserved/entered/completed callbacks for788 schedule,4000reused separately, accepted child/worker/public exit0, durable terminal/resource receipts and independent finite-agreement disposition. None is provided by this review.']}
report['cheaperScientificallyValidAlternative']['rawBinaryBytes']=report['cheaperScientificallyValidAlternative']['uniquePhysicalWeightBytes']+report['cheaperScientificallyValidAlternative']['normalizedRuleBytes']
report['cheaperScientificallyValidAlternative']['newCallbacksBreakdown']={q['name']:q['newCallbacks']for q in costs if q['name']!='secondaryC55'}
report['historicalRuleCoverageSourceReview']={'D4/D5':'All512depth3cells,positive tensorGauss4/5 covering each whole tetrahedron;32768/64000points per element.','U4/U5':'All eight-child uniform subdivisions at depth4/5 with symmetric4point family;16384/131072points per element.','newShellRules':'Coverage/permutation recipes reviewed mathematically only; no nodes, weights, moments or rules were generated.','newSecondaryCornerMappings':{str(e):{'corner':connect[e].index(92),'ascendingOppositeFace':[i for i in range(4)if i!=connect[e].index(92)]}for e in SECOND}}
report['supportingScript']={'path':str(pathlib.Path(__file__)),'sha256':sha(pathlib.Path(__file__).read_bytes()),'bytes':pathlib.Path(__file__).stat().st_size}
assert git('rev-parse','HEAD').decode().strip()==HEAD and git('status','--porcelain').decode()==''
report_path=OUT/'independent_selective_patch_review.json'
report_path.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({'verdict':report['verdict'],'report':str(report_path),'reportSha256':sha(report_path.read_bytes()),'producerEntries':151,'localRecords':632,'all585ReplayPassed':True,'newCalls':new_calls,'physicalBytes':physical,'normalizedBytes':normalized,'logicalShellRecords':logical,'timing':timing,'terminalAll15U5D5Total':subsets['terminal46']['all15Except247']['U5-D5']['total'],'maxLocalReconstructionN':max_component_force,'reads':len(reads)},indent=2))

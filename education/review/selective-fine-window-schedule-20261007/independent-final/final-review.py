#!/usr/bin/env python3
"""Read frozen blobs, replay retained vector arithmetic, audit scalar plan counts.

No law import, point/geometry construction, quadrature generation or runner.
"""
import hashlib,json,math,pathlib,subprocess,sys
ROOT=pathlib.Path('/tmp/Kenoma-fine-window-schedule')
COMMIT=sys.argv[1] if len(sys.argv)>1 else '3f2f7b96dade17bacf5909dbd602e74b34f6b863'
OUT=pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else pathlib.Path('/tmp/fine-window-independent-review/final-review.json')
def git(*args): return subprocess.check_output(['git','-C',str(ROOT),*args])
def blob(p,c=COMMIT): return git('cat-file','blob',c+':'+p)
def obj(p,c=COMMIT): return json.loads(blob(p,c))
def sha(b):return hashlib.sha256(b).hexdigest()
assertions=0
def check(v,msg):
 global assertions
 assertions+=1
 if not v:raise AssertionError(msg)
paths=['education/research/selective-fine-window-schedule-20261007.md','education/research/selective-fine-window-schedule-20261007.json','education/research/selective-fixed-patch-fine-window-criterion-20261007.md','education/review/selective-fine-window-schedule-20261007/reuse-index.json','education/review/selective-fine-window-schedule-20261007/retained-quiet-witnesses.json']
hashes={p:sha(blob(p)) for p in paths}
plan=obj(paths[1]);index=obj(paths[3]);expect=obj(paths[4]);md=blob(paths[0]).decode()
check(plan['criterionSha256']==hashes[paths[2]],'criterion binding')
check(len(index['files'])==1424,'exact reuse count')
totalreusebytes=0
for p,m in index['files'].items():
 b=blob(p,m['commit']);check(sha(b)==m['sha256'],p+' commit hash');check(len(b)==m['bytes'],p+' bytes')
 check(blob(p)==b,p+' freeze preserves source');totalreusebytes+=len(b)
check(git('merge-base','--is-ancestor',plan['baseReviewCommit'],COMMIT)==b'','base ancestor')
check(plan['newMaterialCallsDuringDesign']==0 and not plan['quadratureGenerated'] and not plan['runnerImplementationAdded'] and not plan['executionAuthorized'],'design-only')
source=obj('education/data/anatomical-arm-v1/generated/arm-reference.json',plan['frozenResultCommit'])
body=next(b for b in source['muscles'] if b['element_id']=='FJ1486')
saved=obj('education/review/fixed-field-integration-run-20261007/saved-arrays.json',plan['frozenResultCommit'])
direction=saved['terminalDirectionM'];check(len(direction)==585,'585 nodes')
check(len(saved['freeNodeOrder'])==495 and len(saved['heldNodeOrder'])==90,'free/held')
for n in saved['heldNodeOrder']:check(direction[n]==[0,0,0],'held direction zero')
oldinputs=obj('education/research/fixed-field-integration-protocol-20261007-inputs.json',plan['frozenResultCommit'])
check(plan['material']==oldinputs['material'] and plan['activation']==oldinputs['activation'],'material preserved')
check(plan['states']==[{'id':s['id'],'positionsSha256':s['positionsSha256']} for s in oldinputs['states']],'frozen field identities')
check(plan['directionSha256']==oldinputs['terminalDirectionSha256'],'frozen direction identity')
check(plan['gateN']==oldinputs['integrationForceGateN']==1e-5 and plan['workGateJ']==oldinputs['integrationDerivativeGateJ']==5.492029235357012e-7,'unchanged global force/work gates')
check(plan['stationarityN']==oldinputs['physicalForceGateN']==1e-4 and plan['reconstructionN']==1e-8 and plan['reconstructionJ']==1e-9,'separate physical/reconstruction gates preserved')
terms=plan['components'];quiet=plan['quiet'];computed={};maxdiff=0
for state in ['control45','terminal46']:
 computed[state]={}
 for pair in ['D4/D5','U4/U5','D5/U5']:
  a,b=pair.split('/');computed[state][pair]={}
  for term in terms:
   perentry=[[] for _ in range(585*3)];work=[]
   for e in quiet:
    pa=f'education/review/fixed-field-integration-run-20261007/{a}-{state}-element-{e}-local.json'
    pb=f'education/review/fixed-field-integration-run-20261007/{b}-{state}-element-{e}-local.json'
    check(pa in index['files'] and pb in index['files'],'quiet provenance closure')
    av=obj(pa,plan['frozenResultCommit'])['localGradientsN'][term];bv=obj(pb,plan['frozenResultCommit'])['localGradientsN'][term]
    products=[]
    for i,n in enumerate(body['elements_ten_node'][e]):
     for d in range(3):
      delta=bv[i][d]-av[i][d];perentry[3*n+d].append(delta);products.append(delta*direction[n][d])
    work.append(math.fsum(products))
   result={'signedN':max(abs(math.fsum(v)) for v in perentry),'triangleN':max(math.fsum(abs(x) for x in v) for v in perentry),'signedWorkJ':abs(math.fsum(work)),'triangleWorkJ':math.fsum(abs(w) for w in work)}
   computed[state][pair][term]=result
   for key,val in result.items():
    diff=abs(val-expect['fields'][state][pair][term][key]);maxdiff=max(maxdiff,diff)
    check(diff<1e-18,f'quiet replay {state}/{pair}/{term}/{key}')
   alloc=plan['subsetAllocations']['I0/I1' if pair=='U4/U5' else 'otherRequiredComparisons']
   check(max(result['signedN'],result['triangleN'])<=alloc['quietForceN'],'quiet force allocation')
   check(max(result['signedWorkJ'],result['triangleWorkJ'])<=alloc['quietWorkJ'],'quiet work allocation')
recipe_rows=[]
for r in plan['recipes']:
 e=len(r['elements']);f=len(r['fields']);p=r['pointsPerElementPerField'];regions=r['originalPhysicalRegionsPerElement'];charts=r['newNormalizedCornerCharts']
 if r['recipe']=='H4':
  calls=e*f*6000;nb=charts*6000*48;wb=e*6000*8;nf=charts*3;wf=e*3;rr=e*f*3
 elif r['recipe']=='C4':
  calls=f*(6*42000+2000);nb=(3*42000+2000)*48;wb=(6*42000+2000)*8;nf=3*21+1;wf=6*21+1;rr=f*(6*21+1)
 else:
  calls=e*f*p;nb=charts*p*48;wb=e*p*8;nf=regions*charts;wf=regions*e;rr=regions*e*f
 check(r['newCalls']==calls,'recipe calls '+r['recipe'])
 check(r['normalizedBytes']==nb,'normalized bytes '+r['recipe'])
 check(r['physicalWeightBytes']==wb,'physical weights once '+r['recipe'])
 check(r['normalizedFiles']==nf,'normalized files '+r['recipe'])
 check(r['physicalWeightFiles']==wf,'physical files '+r['recipe'])
 check(r['regionRecords']==rr,'region records '+r['recipe'])
 check(r['stageRecords']==e*f,'stage records '+r['recipe'])
 recipe_rows.append({'recipe':r['recipe'],'newCalls':calls,'fullRecipePointsPerElementPerField':p,'newRegionRows':rr})
check((3*20+1)*4**2*125==122000,'I0 formula')
check((3*20*2+1)*8**2*125==968000,'I1 formula')
check(sum(r['newCalls'] for r in plan['recipes'])==plan['budget']['plannedAndMaximumNewCalls']==19716000,'complete calls')
sp=plan['storagePlan']
for k,rk in [('normalizedBytes','normalizedBytes'),('physicalWeightBytes','physicalWeightBytes'),('normalizedNewFileCount','normalizedFiles'),('physicalWeightNewFileCount','physicalWeightFiles'),('newRegionRecords','regionRecords'),('newStageRecords','stageRecords')]:check(sp[k]==sum(r[rk] for r in plan['recipes']),'storage aggregate '+k)
check(sp['caps']['binaryPayload']==sp['normalizedBytes']+sp['physicalWeightBytes']==345840000,'binary payload')
check(sp['caps']['regionJson']==1682*8192,'region caps')
check(sp['originalLogicalRegionRecordsIncludingReuse']==2002,'full logical regions preserve support')
check(1682+20*7*2+20*1*2==2002,'all shared rows accounted once')
check(sp['caps']['stageJson']==94*131072,'stage caps')
check(sp['caps']['fullHybridJson']==16*1048576,'16 hybrids cap')
check(sp['caps']['comparisonJson']==24*2097152,'24 comparisons cap')
check(sum(sp['caps'].values())==sp['plannedUpperEnvelopeBytes']==448240000,'full planned envelope')
check(plan['budget']['maximumOutputBytes']-sp['plannedUpperEnvelopeBytes']==88630912,'output headroom')
check(64**1*6*125*8==384000,'largest I1 physical-weight shell')
for alloc in plan['subsetAllocations'].values():
 check(alloc['quietForceN']+alloc['focusForceN']<=plan['gateN']+1e-20,'shared force budget')
 check(alloc['quietWorkJ']+alloc['focusWorkJ']<=plan['workGateJ']+1e-20,'shared work budget')
check(plan['requiredUnitsPerComparison']==9+7*21==156,'actual unit partition')
check(len(plan['requiredComparisons'])*2==14 and len(plan['quietWitnesses'])*2==6,'record slots')
check(len(set(plan['quiet'])|set(plan['focus']))==16 and not set(plan['quiet'])&set(plan['focus']),'16 coverage')
rate=19716000/497500
observed=43.0488345929989*rate;slow=135.02*rate
check(abs(observed-plan['timeEstimates']['observedSelectiveSeconds'])<1e-8,'time extrapolation observed')
check(abs(slow-plan['timeEstimates']['historicSlowBatchSeconds'])<1e-8,'time extrapolation slow')
old=obj('education/review/element247-two-shell-run-20261007/material/incomplete-receipt.json',plan['frozenResultCommit'])
check(old['result'].startswith('INCOMPLETE') and old['runtime']['actualConstitutiveCallbacks']==4000,'failed operation remains incomplete')
for shell in ['s1','s2']:
 oldrow=obj(f'education/review/element247-two-shell-run-20261007/material/T24-terminal46-{shell}-shell.json',plan['frozenResultCommit'])
 newrow=obj(f'education/review/selective-fixed-patch-run-20261007/material/terminal46-247-F44-{shell}-region.json',plan['frozenResultCommit'])
 check(oldrow['pointCount']==newrow['pointCount']==2000,'historical reused row counts')
 check(oldrow['localGradientsN']==newrow['localGradientsN'] and oldrow['energiesJ']==newrow['energiesJ'],'byte-derived value provenance')
correctmax=max(computed[s]['D5/U5'][t]['triangleN'] for s in computed for t in terms)
for m in [4,8]:check(m*(m+1)//2+m*(m-1)//2==m*m,'analytical face triangle count')
for state in ['control45','terminal46']:
 xp=f'education/review/selective-fixed-patch-run-20261007/material/{state}-247-X44-stage.json'
 stage=obj(xp,plan['frozenResultCommit']);recipe=stage['recipe']
 check(recipe['corner']==0 and recipe['faceOrder']==[2,3,1] and recipe['depth']==22 and recipe['radialParts']==1 and recipe['angularParts']==4 and recipe['radialOrder']==recipe['angularOrder']==5,'X44 recipe identity for C4 outer rows')
 for shell in range(1,21):
  rp=f'education/review/selective-fixed-patch-run-20261007/material/{state}-247-X44-s{shell}-region.json'
  wp=f'education/review/selective-fixed-patch-run-20261007/material/247-X44-s{shell}-weights.f64le'
  np=f'education/review/selective-fixed-patch-run-20261007/material/X44-c0-s{shell}-points.f64le'
  check(rp in index['files'] and wp in index['files'] and np in index['files'],'C4 reused row/weights/points explicit closure')
  row=obj(rp,plan['frozenResultCommit'])
  check(row['pointCount']==2000 and row['lo']==2**(-shell) and row['hi']==2**(1-shell),'C4 shared physical-region identity')
  check(index['files'][wp]['bytes']==2000*8 and index['files'][np]['bytes']==2000*6*8,'C4 old point/weight storage counts')
check('require\naccepted prior P4 receipts and refuse mismatch without replacement calls' in md,'same-invocation P4 dependency is fail-closed')
check('Identical C4/X44 outer rows add no depth evidence' in md and 'Shared rows earn no depth evidence' in md,'no identity as resolution evidence')
check('S0/S1 cannot be relabeled post hoc by sliding the window' in md,'fine window preserved prospectively')
quote_error='1.2198439485189283e-6N' in md
report={'verdict':'FAIL_PROSE_QUOTE_ONLY' if quote_error else 'PASS_SCIENTIFIC_COST_DESIGN_CONDITIONAL_ON_FUTURE_STRUCTURAL_REVIEW','sourceCommit':COMMIT,'sourceSha256':hashes,'assertions':assertions,'reusedFilesVerified':1424,'reusedBytesVerified':totalreusebytes,'quietMaximumReplayDifference':maxdiff,'correctQuietD5U5MaximumN':correctmax,'quotedQuietD5U5MaximumWrong':quote_error,'computedQuietWitnesses':computed,'newCallsPlanned':19716000,'storagePlannedUpperEnvelopeBytes':448240000,'outputHeadroomBytes':88630912,'observedTimeExtrapolationSeconds':observed,'slowTimeExtrapolationSeconds':slow,'recipeCallArithmetic':recipe_rows,'historicalFailed4000ValuesRemainIncompleteOperation':True,'noScientificProtocolBlockerBeyondQuotedNumber':True,'conditionalLimitations':['Only bounded finite integration agreement may be reported; no convergence/analytic error claim.','All new primary and independent increments/axes remain unmeasured and must pass without sliding the window.','Shared156unit triangle allows within-shell cancellation; moment reproduction does not certify nonlinear material integration.','Independent graded-tetra decomposition and distinct sampling need structural proof/moments before material calls.','Output/heap/RSS/time numbers are proposed envelopes, not implementation proofs.','Independent work is77.40% of19,716,000calls; no minimal-cost claim justified.','Quiet U4/U5force margin is only1.21491100657e-7N; any identity mismatch refuses reuse.','Outside236U3elements remain unqualified.'],'forbiddenActions':{'newMaterialCalls':0,'specimenCalls':0,'quadratureGeneration':0,'geometryGeneration':0,'runnerLaunches':0,'sourceEdits':0}}
OUT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['computedQuietWitnesses','sourceSha256']},indent=2))

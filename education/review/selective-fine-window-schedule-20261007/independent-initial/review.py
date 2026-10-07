#!/usr/bin/env python3
"""Read frozen blobs, replay retained vector arithmetic, audit scalar plan counts.

No law import, point/geometry construction, quadrature generation or runner.
"""
import hashlib,json,math,pathlib,subprocess,sys
ROOT=pathlib.Path('/tmp/Kenoma-fine-window-schedule')
COMMIT=sys.argv[1] if len(sys.argv)>1 else 'a5d0243b36f99379a61f52a0845a3e01fc6470a0'
OUT=pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else pathlib.Path('/tmp/fine-window-independent-review/initial-review.json')
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
check(len(index['files'])==1342,'exact reuse count')
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
check(plan['material']==obj('education/research/fixed-field-integration-protocol-20261007-inputs.json',plan['frozenResultCommit'])['material'],'material preserved')
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
 check(r['newCalls']==e*f*p,'recipe calls '+r['recipe'])
 check(r['normalizedBytes']==charts*p*6*8,'normalized bytes '+r['recipe'])
 check(r['physicalWeightBytes']==e*p*8,'physical weights once '+r['recipe'])
 check(r['normalizedFiles']==regions*charts,'normalized files '+r['recipe'])
 check(r['physicalWeightFiles']==regions*e,'physical files '+r['recipe'])
 check(r['regionRecords']==regions*e*f,'region records '+r['recipe'])
 check(r['stageRecords']==e*f,'stage records '+r['recipe'])
 recipe_rows.append({'recipe':r['recipe'],'newCalls':e*f*p,'pointsPerElementPerField':p})
check((3*20+1)*4**2*125==122000,'I0 formula')
check((3*20*2+1)*8**2*125==968000,'I1 formula')
check(sum(r['newCalls'] for r in plan['recipes'])==plan['budget']['plannedAndMaximumNewCalls']==20356000,'complete calls')
sp=plan['storagePlan']
for k,rk in [('normalizedBytes','normalizedBytes'),('physicalWeightBytes','physicalWeightBytes'),('normalizedNewFileCount','normalizedFiles'),('physicalWeightNewFileCount','physicalWeightFiles'),('newRegionRecords','regionRecords'),('newStageRecords','stageRecords')]:check(sp[k]==sum(r[rk] for r in plan['recipes']),'storage aggregate '+k)
check(sp['caps']['binaryPayload']==sp['normalizedBytes']+sp['physicalWeightBytes']==358000000,'binary payload')
check(sp['caps']['regionJson']==2002*8192,'region caps')
check(sp['caps']['stageJson']==94*131072,'stage caps')
check(sp['caps']['fullHybridJson']==16*1048576,'16 hybrids cap')
check(sp['caps']['comparisonJson']==24*2097152,'24 comparisons cap')
check(sum(sp['caps'].values())==sp['plannedUpperEnvelopeBytes']==463021440,'full planned envelope')
check(plan['budget']['maximumOutputBytes']-sp['plannedUpperEnvelopeBytes']==73849472,'output headroom')
check(64**1*6*125*8==384000,'largest I1 physical-weight shell')
for alloc in plan['subsetAllocations'].values():
 check(alloc['quietForceN']+alloc['focusForceN']<=plan['gateN']+1e-20,'shared force budget')
 check(alloc['quietWorkJ']+alloc['focusWorkJ']<=plan['workGateJ']+1e-20,'shared work budget')
check(plan['requiredUnitsPerComparison']==9+7*21==156,'actual unit partition')
check(len(plan['requiredComparisons'])*2==14 and len(plan['quietWitnesses'])*2==6,'record slots')
check(len(set(plan['quiet'])|set(plan['focus']))==16 and not set(plan['quiet'])&set(plan['focus']),'16 coverage')
rate=20356000/497500
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
quote_error='1.2198439485189283e-6N' in md
report={'verdict':'FAIL_PROSE_QUOTE_ONLY' if quote_error else 'PASS_SCIENTIFIC_COST_DESIGN_CONDITIONAL_ON_FUTURE_STRUCTURAL_REVIEW','sourceCommit':COMMIT,'sourceSha256':hashes,'assertions':assertions,'reusedFilesVerified':1342,'reusedBytesVerified':totalreusebytes,'quietMaximumReplayDifference':maxdiff,'correctQuietD5U5MaximumN':correctmax,'quotedQuietD5U5MaximumWrong':quote_error,'computedQuietWitnesses':computed,'newCallsPlanned':20356000,'storagePlannedUpperEnvelopeBytes':463021440,'outputHeadroomBytes':73849472,'observedTimeExtrapolationSeconds':observed,'slowTimeExtrapolationSeconds':slow,'recipeCallArithmetic':recipe_rows,'historicalFailed4000ValuesRemainIncompleteOperation':True,'noScientificProtocolBlockerBeyondQuotedNumber':True,'conditionalLimitations':['Only bounded finite integration agreement may be reported; no convergence/analytic error claim.','All new primary and independent increments/axes remain unmeasured and must pass without sliding the window.','Shared156unit triangle allows within-shell cancellation; moment reproduction does not certify nonlinear material integration.','Independent graded-tetra decomposition and distinct sampling need structural proof/moments before material calls.','Output/heap/RSS/time numbers are proposed envelopes, not implementation proofs.','Independent work is74.97% of20,356,000calls; no minimal-cost claim justified.','Quiet U4/U5force margin is only1.21491100657e-7N; any identity mismatch refuses reuse.','Outside236U3elements remain unqualified.'],'forbiddenActions':{'newMaterialCalls':0,'specimenCalls':0,'quadratureGeneration':0,'geometryGeneration':0,'runnerLaunches':0,'sourceEdits':0}}
OUT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['computedQuietWitnesses','sourceSha256']},indent=2))

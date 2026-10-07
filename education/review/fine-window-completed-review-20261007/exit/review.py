"""Independent retained-evidence audit. No repository imports or writes, laws or quadrature."""
import hashlib,json,math,pathlib,subprocess,collections,datetime
REPO=pathlib.Path('/tmp/Kenoma-fine-window-material-run');E=REPO/'education';RUN=E/'review/fine-window-run-20261007';M=RUN/'material';P=E/'review/fine-window-preflight-20261007';OUT=pathlib.Path('/tmp/fine-window-completed-exit-independent')
FROZEN='5f7612f6c7f6609d8946b3394d7363609d7a30b1';EXEC='fe513113cbc336948ae20b0209a5be4b9552b524';SOURCE='9611a4865e9591041fa5253c9df6c0f91da84089';EVIDENCE='b2724db9687fefae09bcf0ae72b5dea8c47f0a35';REVIEW='257b9a255d2a3b9a980ee4716eba064accab15dd';OLD='38ae8a2e2af57cf33254af987b724824b9d84357'
B={'plannedMaterialCalls':19716000,'maximumMaterialCalls':19716000,'maximumWallSeconds':7200,'nodeHeapMiB':1024,'maximumRssBytes':2147483648,'maximumOutputBytes':536870912,'invocations':1};CMD=['node','--max-old-space-size=1024','tools/run-fine-window.mjs','--execute'];assertions=0;cache={};trees={}
def need(v,msg):
 global assertions
 assertions+=1
 if not v:raise AssertionError(msg)
def git(*a):return subprocess.check_output(['git',*a],cwd=REPO)
def read(p):return json.loads(p.read_text())
def hashes(p):
 p=pathlib.Path(p)
 if p not in cache:
  h=hashlib.sha256();g=hashlib.sha1();size=p.stat().st_size;g.update(f'blob {size}\0'.encode())
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b);g.update(b)
  cache[p]=(h.hexdigest(),g.hexdigest(),size)
 return cache[p]
def sha(p):return hashes(p)[0]
def tree(c):
 if c not in trees:
  trees[c]={}
  for item in git('ls-tree','-r','-z',c).split(b'\0'):
   if item:
    meta,path=item.split(b'\t');mode,kind,oid=meta.split();need(kind==b'blob','nonblob tracked file');trees[c][path.decode()]=oid.decode()
 return trees[c]
def bound(p,c):need(tree(c).get(str(p.relative_to(REPO)))==hashes(p)[1],f'commit blob mismatch {c}:{p}')
heads_before=git('for-each-ref','--format=%(refname) %(objectname)');status_before=git('status','--porcelain');need(git('rev-parse','HEAD').decode().strip()==FROZEN,'frozen HEAD');need(status_before==b'','worktree must clean')
for a,b in zip([SOURCE,EVIDENCE,REVIEW,EXEC],[EVIDENCE,REVIEW,EXEC,FROZEN]):need(subprocess.run(['git','merge-base','--is-ancestor',a,b],cwd=REPO).returncode==0,'ancestry')
changed=git('diff','--name-only',REVIEW,EXEC).decode().splitlines();need(changed==['education/research/fine-window-authorization-20261007.json'],'execution commit only adds authorization')
A=E/'research/fine-window-authorization-20261007.json';auth=read(A);pref=read(P/'preflight.json');review=read(P/'independent-review.json');plan=read(P/'storage-plan.json');bound(A,EXEC);bound(A,FROZEN)
need(auth['authorized'] is True and auth['parentAcceptance'] is True and auth['parentThread']=='01a103c3-a2e6-7606-8c1e-06987ac710f1' and auth['scope']=='fine-window-fixed-patch-19716000','one-shot parent auth')
for o in [auth,pref,review]:need(o['budget']==B,'immutable new budgets')
for k,v in [('runnerSourceCommit',SOURCE),('acceptedPreflightEvidenceCommit',EVIDENCE),('acceptedReviewedHead',REVIEW),('preflightSha256','61e25922d9f1d6474d6b1030c1af5491c42cf7468550923d24f79c74bf7388a8'),('independentReviewSha256','64a5ef902aa58fc2e25e84741f233d3e984f33a16ce88f3d97140ead43f89e82')]:need(auth[k]==v,'auth binding '+k)
need(sha(P/'preflight.json')==auth['preflightSha256'] and sha(P/'independent-review.json')==auth['independentReviewSha256'],'accepted evidence hashes');bound(P/'preflight.json',EVIDENCE);bound(P/'independent-review.json',REVIEW)
need(pref['sourceCommit']==SOURCE and pref['specimenCalls']==pref['materialLawInvocations']==0 and pref['tests']['fail']==0,'accepted no-material preflight');need(review['verdict']=='PASS' and review['sourceCommit']==SOURCE and review['preflightSha256']==sha(P/'preflight.json'),'review source')
for path,h in pref['sourceHashes'].items():p=E/path;need(sha(p)==h,'pref source hash');bound(p,SOURCE)
for path,h in pref['artifactHashes'].items():p=P/path;need(sha(p)==h,'pref artifact hash');bound(p,EVIDENCE)
for path,v in review['supportingArtifacts'].items():p=E/path;need(sha(p)==v['sha256'] and hashes(p)[2]==v['bytes'],'supporting review hash');bound(p,REVIEW)
records={n:read(RUN/(n+'.json')) for n in ['execution-start','external-exit','external-final','launcher-exit','launcher-exit.pending','public-entry-exit']};start=records['execution-start'];rid=start['runId'];need(start['sourceCommit']==EXEC and start['authorizationSha256']==sha(A),'execution source auth')
need(len(rid)==32 and all(x in '0123456789abcdef' for x in rid),'run ID')
for n,d in records.items():need(d['sourceCommit']==EXEC and d['runId']==rid and d['budget']==B,'resource receipt identity '+n)
for n in ['execution-start','external-exit']:need(records[n]['command']==CMD and records[n]['invocations']==1,'command heap invocation '+n)
for n in ['external-exit','external-final']:need(records[n]['childExitCode']==0,'child exit')
for n in ['launcher-exit','launcher-exit.pending']:need(records[n]['launcherExitCode']==0 and records[n]['supervisorFailure'] is None,'worker exit')
need(records['external-exit']['watchdogFailure'] is None,'watchdog failure absent');pub=records['public-entry-exit'];need(pub['publicEntryExitCode']==0 and pub['authorizationSha256']==sha(A) and pub['invocations']==1 and pub['retryPerformed'] is False,'public success observed')
need(pub['command'][1:]==['tools/launch-fine-window.py','--execute'],'public command');need(records['launcher-exit']['clockScope']==start['clockScope']=='pre-authorization-and-source-checks','full launch wall scope')
for n in ['external-exit','external-final','launcher-exit','public-entry-exit']:need(0<=records[n]['elapsedMs']<7200000,'wall cap '+n)
need(records['external-exit']['elapsedMs']<=records['external-final']['elapsedMs']<=records['launcher-exit']['elapsedMs']<=pub['elapsedMs'],'external clock order')
need(records['external-exit']['peakObservedChildRssBytes']<=B['maximumRssBytes'] and pub['observedSubprocessTreeRusageMaximumRssBytes']<=B['maximumRssBytes'],'external rss caps')
need(records['external-exit']['logSha256']==records['external-final']['logSha256']==sha(RUN/'execute.log'),'child log hash');need(records['external-final']['externalExitSha256']==sha(RUN/'external-exit.json'),'external exit hash');need(records['launcher-exit']['externalFinalSha256']==sha(RUN/'external-final.json') and records['launcher-exit']['launcherLogSha256']==sha(RUN/'launcher.log'),'worker resource hashes')
for n in ['external-incomplete.json','supervisor-incomplete.json']:need(not (RUN/n).exists(),'no outer failure '+n)
need(not (M/'incomplete-receipt.json').exists(),'no material failure')
completion=read(M/'completion-receipt.json');terminal=read(M/'terminal-completion.json');lines=(RUN/'execute.log').read_text().splitlines();need(len(lines)==1,'sole final stdout receipt');marker=json.loads(lines[-1]);need(marker['kind']==terminal['kind']=='TERMINAL_COMPLETION','terminal kind')
for d in [completion,terminal,marker]:
 need(d['sourceCommit']==EXEC and d['runId']==rid and d['result']=='UNRESOLVED_FIXED_PATCH_INTEGRATION','immutable unresolved result')
 r=d['runtime'];need(all(r[k]==19716000 for k in ['reservedCalls','actualConstitutiveCallbacks','completedConstitutiveCallbacks','plannedCalls','maximumCalls']),'exact callback counters');need(r['activeBatch'] is None,'no active batch');need(r['maximumWallMs']==7200000 and 0<=r['elapsedMs']<7200000,'runtime wall');need(r['maximumRssBytes']==2147483648 and 0<=r['peakObservedRssBytes']<=2147483648,'runtime RSS')
need(completion['runtime']['elapsedMs']<=terminal['runtime']['elapsedMs']<=marker['runtime']['elapsedMs'],'inner clock order');need(marker['runtime']['lastPhase']=='after-terminal-completion-write','post-terminal check');need(terminal['completionSha256']==marker['completionSha256']==sha(M/'completion-receipt.json') and marker['terminalSha256']==sha(M/'terminal-completion.json'),'terminal hashes')
need(completion['runnerSourceCommit']==SOURCE and completion['newCallbacks']==19716000 and completion['logicalRegions']==2002 and completion['newRegions']==1682 and completion['sharedRegions']==320 and completion['sharedLogicalMeasurements']==640000,'completion schedule counts')
need(completion['originalResultCommit']==OLD and completion['originalResult']=='UNRESOLVED_FIXED_PATCH_INTEGRATION' and completion['originalTwoShellExecutionExit']==1,'older failure remains')
for k in ['newNodalFields','nonlinearSolves','optimizerTrials','refits']:need(completion[k]==0,'scope '+k)
need(completion['outsidePatchElements']==236 and completion['outsidePatchQualified'] is False and completion['anatomicalQualification'] is False,'qualification limits')
ms=read(M/'material-start.json');need(ms['sourceCommit']==EXEC and ms['runId']==rid and ms['runnerSourceCommit']==SOURCE and ms['budget']==B and ms['activation']==1,'material-start identity');need(ms['states']==pref['states'] and ms['schedule']==pref['schedule'] and ms['material']==pref['material'] and ms['certificates']==pref['certificates'],'frozen fields laws geometry')
oldstart=read(E/'review/selective-fixed-patch-run-20261007/material/material-start.json');need(ms['states']==oldstart['states'] and ms['material']==oldstart['material'] and ms['activation']==oldstart['activation'],'historical reused fields laws activation unchanged');saved=read(M/'saved-arrays.json');need(saved==read(E/'review/fixed-field-integration-run-20261007/saved-arrays.json')==read(E/'review/selective-fixed-patch-run-20261007/material/saved-arrays.json'),'exact all frozen position direction held free arrays');manifest=read(E/'research/fine-window-runner-20261007-inputs.json');
for path,h in manifest['immutableModuleHashes'].items():need(sha(E/path)==h,'immutable law helper module hash')
expected_sources={**pref['sourceHashes'],**{str((P/n).relative_to(E)):h for n,h in pref['artifactHashes'].items()},str((P/'preflight.json').relative_to(E)):sha(P/'preflight.json'),str((P/'independent-review.json').relative_to(E)):sha(P/'independent-review.json'),str(A.relative_to(E)):sha(A)}
need(completion['sourceHashes']==ms['sourceHashes']==expected_sources,'exact complete input source closure')
for path,h in completion['sourceHashes'].items():need(sha(E/path)==h,'completion immutable source '+path)
inventory=read(E/'review/fine-window-outcome-20261007/raw-inventory.json');paths={str(p.relative_to(RUN)):p for p in RUN.rglob('*') if p.is_file()};need(set(paths)==set(inventory['files']) and len(paths)==inventory['fileCount']==3124,'closed raw inventory all files')
for path,p in paths.items():d=inventory['files'][path];need(hashes(p)[0]==d['sha256'] and hashes(p)[2]==d['bytes'],'raw inventory hash bytes');bound(p,FROZEN)
actualbytes=sum(hashes(p)[2] for p in paths.values());need(actualbytes==inventory['bytes']==378160307 and actualbytes<=B['maximumOutputBytes'],'actual output envelope');need(pub['combinedBytesBeforePublicReceipt']+hashes(RUN/'public-entry-exit.json')[2]==actualbytes,'public final output bytes')
need(terminal['combinedBytesBeforeTerminal']==sum(hashes(p)[2] for p in M.iterdir() if p.name!='terminal-completion.json')+hashes(RUN/'execution-start.json')[2],'actual before-terminal output bytes');need(records['external-final']['combinedBytesBeforeFinal']==sum(hashes(p)[2] for p in M.iterdir())+sum(hashes(RUN/n)[2] for n in ['execution-start.json','execute.log','external-exit.json','launcher.log']),'actual before-external-final output bytes');need(records['launcher-exit']['externalFinalSha256']==sha(RUN/'external-final.json'),'terminal output binding');need(set(p.name for p in M.iterdir())==set(plan['files']),'closed material file inventory')
for name,cap in plan['files'].items():need(hashes(M/name)[2]<=cap,'per-file bytes cap')
need(set(completion['outputInventory'])==set(plan['files'])-{'completion-receipt.json','terminal-completion.json'},'provisional output exact inventory')
for name,v in completion['outputInventory'].items():need(sha(M/name)==v['sha256'] and hashes(M/name)[2]==v['bytes'],'completion output hashes')
for name,h in pref['artifactHashes'].items():
 if name.endswith('.f64le'):need(sha(M/name)==h,'actual point and weight binary immutable')
reuse_index=read(E/'review/selective-fine-window-schedule-20261007/reuse-index.json');provenance=read(M/'provenance-inventory.json');need(provenance['files']==reuse_index['files'] and provenance['reuseIndexSha256']==sha(E/'review/selective-fine-window-schedule-20261007/reuse-index.json'),'retained provenance closure')
for path,v in provenance['files'].items():p=REPO/path;need(sha(p)==v['sha256'] and hashes(p)[2]==v['bytes'],'retained provenance hashes');bound(p,v['commit'])
need(provenance['plannedSameInvocationReuse']==reuse_index['plannedReuseWithinInvocation'],'planned current reuse')
counts=collections.Counter();countregions=collections.Counter();OLDMAT=E/'review/selective-fixed-patch-run-20261007/material'
for state in ['control45','terminal46']:
 for recipe in pref['schedule']:
  e,q=recipe['element'],recipe['id'];s=read(M/f'{state}-{e}-{q}-stage.json');need(s['recipe']==recipe and s['state']==state,'exact stage schedule');new=reused=0
  for i,ref in enumerate(s['rowSources']):
   name='core' if i==recipe['depth'] else f's{i+1}';need(ref['shell']==name,'region order');old=(q=='H4' or (q=='C4' and e==247)) and i<20;current=old and q=='H4' and e!=247;origin=M if not old or current else OLDMAT;row=read(origin/ref['name']);need(sha(origin/ref['name'])==ref['sha256'],'region data hash');category='sameInvocationP4' if current else 'historicalF44' if old and q=='H4' else 'historicalX44' if old else 'new';n=((1 if name=='core' else 3*recipe['radialParts'])*recipe['faceParts']**2*125) if recipe['kind']=='graded-affine-tetra' else 125*recipe['radialParts']*recipe['angularParts']**2
   need(row['pointCount']==n and row['element']==e and row['shell']==name,'actual point row');counts[category]+=n;countregions[category]+=1
   cert=pref['regions'][f'{e}-{q}-{name}'];need(row['minimumSampleJ']==cert['minimumSampleJ'][state],'actual minimum J geometry certificate')
   if old:
    expected=f"{state}-{e}-{'P4' if current else 'F44' if q=='H4' else 'X44'}-{name}-region.json";need(ref['name']==expected and ref['kind']==('same-invocation' if current else 'historical') and ref['identityMatches'] is True and ref['earnsIndependentResolutionCredit'] is False,'exact reuse source no credit');need(ref['normalizedSha256']==cert['normalizedSha256'] and ref['physicalSha256']==cert['physicalSha256'],'reuse exact quadrature hashes');need(sha(origin/ref['stageName'])==ref['stageSha256'],'reuse source stage hash')
    if current:
     prior=read(origin/ref['stageName']);need(prior['newCallbackPoints']==42000 and prior['reusedPoints']==0 and row['evaluationIdentity']==pref['evaluationIdentities'][state],'same invocation full completed source')
    else:need(ref['sha256']==cert['reuseRows'][state]['sha256'],'historical accepted source');bound(origin/ref['name'],OLD);bound(origin/ref['stageName'],OLD)
    reused+=n
   else:
    need(ref['kind']=='new' and row['evaluationIdentity']==pref['evaluationIdentities'][state] and row['recipeId']==q,'new evaluation exact identity');new+=n
  need(s['newCallbackPoints']==new and s['reusedPoints']==reused and s['pointCount']==new+reused,'exact stage count')
need(dict(counts)=={'new':19716000,'sameInvocationP4':480000,'historicalF44':80000,'historicalX44':80000},'independent reuse and new attribution');need(dict(countregions)=={'new':1682,'sameInvocationP4':240,'historicalF44':40,'historicalX44':40},'region attribution')
FAILED=E/'review/element247-two-shell-run-20261007';failedreceipt=read(FAILED/'material/incomplete-receipt.json');failedexit=read(FAILED/'external-exit.json');need(failedexit['childExitCode']==1 and failedreceipt['runtime']['completedConstitutiveCallbacks']==4000 and failedreceipt['result']=='INCOMPLETE_ELEMENT247_SHELL_INTEGRATION','old source failure preserved')
oldcomp=read(OLDMAT/'completion-receipt.json');need(oldcomp['reusedMeasurements']==4000 and oldcomp['originalTwoShellExecutionExit']==1,'retained intermediate old reuse attribution')
for s in ['s1','s2']:
 prior=read(FAILED/f'material/T24-terminal46-{s}-shell.json');current=read(OLDMAT/f'terminal46-247-F44-{s}-region.json');need(prior['pointCount']==current['pointCount']==2000,'old failed point count');
 for k in ['energiesJ','localGradientsN','minimumSampleJ','pointCount']:need(prior[k]==current[k],'exact failed source numerical reuse')
 cert=pref['regions'][f'247-H4-{s}'];need(cert['physicalSha256']==sha(FAILED/f'material/T24-terminal46-{s}-weights.f64le'),'failed source physical weights identity')
need(heads_before==git('for-each-ref','--format=%(refname) %(objectname)') and status_before==git('status','--porcelain'),'all ref heads and worktree unchanged')
report={'schema':1,'verdict':'PASS_INDEPENDENT_COMPLETED_RUN_EXIT_RESOURCE_COUNT_PROVENANCE','reviewedResultCommit':FROZEN,'executionSourceCommit':EXEC,'runnerSourceCommit':SOURCE,'acceptedPreflightEvidenceCommit':EVIDENCE,'acceptedReviewedHead':REVIEW,'runId':rid,'result':completion['result'],'assertions':assertions,'budget':B,'bindings':{'authorizationSha256':sha(A),'preflightSha256':sha(P/'preflight.json'),'reviewSha256':sha(P/'independent-review.json'),'rawInventorySha256':sha(E/'review/fine-window-outcome-20261007/raw-inventory.json'),'completionSha256':sha(M/'completion-receipt.json'),'terminalSha256':sha(M/'terminal-completion.json'),'publicReceiptSha256':sha(RUN/'public-entry-exit.json')},'exitCodes':{'public':pub['publicEntryExitCode'],'worker':records['launcher-exit']['launcherExitCode'],'child':records['external-exit']['childExitCode']},'runtime':{'reservedCalls':19716000,'enteredCallbacks':19716000,'completedCallbacks':19716000,'publicElapsedMs':pub['elapsedMs'],'externalElapsedMs':records['external-exit']['elapsedMs'],'externalPeakObservedRssBytes':records['external-exit']['peakObservedChildRssBytes'],'publicRusageMaximumRssBytes':pub['observedSubprocessTreeRusageMaximumRssBytes'],'childPeakObservedRssBytes':marker['runtime']['peakObservedRssBytes'],'heapMiBCommandLimit':1024,'combinedRawOutputBytes':actualbytes,'rawFiles':len(paths)},'newAndReusePointAttribution':dict(counts),'regionAttribution':dict(countregions),'failedSourceReuse':{'terminal46F44Shells':['s1','s2'],'measurements':4000,'sourceExit':1,'includedInsideHistoricalF44':True,'newCallbacks':0},'checkedSourceFiles':len(pref['sourceHashes']),'checkedPreflightArtifacts':len(pref['artifactHashes']),'checkedRetainedProvenanceFiles':len(provenance['files']),'minimumJRecordsChecked':2002,'specimenCalls':0,'materialLawInvocations':0,'quadratureGenerations':0,'repoImports':0,'repositoryEdits':0,'authorizationConsumed':True,'outside236Qualified':False,'anatomicalQualification':False,'limits':['Configured 1GiB Node old-space cap is bound by exact child command; no independent actual heap-usage measurement exists.','Peak RSS receipts are observed watchdog samples plus process-tree rusage; this review verifies retained receipts, not an external rerun.','Scientific comparison arithmetic is independently reviewed by the separate arithmetic reviewer; this report verifies counts, resources, hashes and provenance.']}
(OUT/'review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

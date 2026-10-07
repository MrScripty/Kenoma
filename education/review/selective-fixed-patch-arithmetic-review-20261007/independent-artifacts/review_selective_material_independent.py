"""Read-only independent fsum arithmetic/resource replay. No material or JS imports."""
import pathlib,json,math,hashlib,subprocess,tempfile,sys,importlib.util
R=pathlib.Path('/workspace/Kenoma-patch-material-run'); E=R/'education'; RAW=E/'review/selective-fixed-patch-run-20261007'; M=RAW/'material'; OLD=E/'review/fixed-field-integration-run-20261007'; SH=E/'review/element247-shell-run-20261007/material'
T=['matrix','volume','passiveFiber','activePotential','total']; PATCH=[195,196,197,198,199,200,202,203,206,237,240,243,244,246,247,248]; QUIET=[195,196,198,199,202,237,240,243,244]; SEC=[197,200,203,206,246,248]
SOURCE='0582de9d86d75ccbb7cc61c74d2c88e320f675af'; PREF='6d3851e7f625baae2e94ebea4261eb852691420d'; ACCEPT='084e830b82f1f53a10ebc39ad23194177e06c42a'; EXEC='5119dad8c882088dee5c73e5d8213acffdc04458'; RESULT='38ae8a2e2af57cf33254af987b724824b9d84357'; F=1e-5; W=5.492029235357012e-7
count=0; err=0.
def need(c,m):
 global count
 count+=1
 if not c:raise AssertionError(m)
def rd(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(c,p):return subprocess.check_output(['git','show',f'{c}:{p}'],cwd=R)
def close(a,b,tol=1e-8):
 global err
 need(math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol,f'finite difference {a} {b} {tol}');err=max(err,abs(a-b))
def nested(a,b,tol=1e-8):
 if isinstance(a,dict):
  need(set(a)==set(b),'dictionary shape')
  for k in a:nested(a[k],b[k],tol)
 elif isinstance(a,list):
  need(len(a)==len(b),'array length')
  for x,y in zip(a,b):nested(x,y,tol)
 else:close(a,b,tol)
ref=next(x for x in rd(E/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if x['element_id']=='FJ1486'); ids=ref['elements_ten_node']; arr=rd(M/'saved-arrays.json'); direction=arr['terminalDirectionM']; held=arr['heldNodes'] if 'heldNodes' in arr else None
# Independent scatter uses lists per output slot and fsum, rather than producer +=.
def assembly(rows):
 bags={t:[[[] for d in range(3)] for n in range(585)] for t in T}; en={t:[] for t in T}
 for row in rows:
  for t in T:
   need(len(row['localGradientsN'][t])==10,'ten local nodes');en[t].append(row['energiesJ'][t])
   for i,n in enumerate(ids[row['element']]):
    for d in range(3):bags[t][n][d].append(row['localGradientsN'][t][i][d])
 return {t:[[math.fsum(b) for b in n] for n in bags[t]] for t in T},{t:math.fsum(en[t]) for t in T}
def component(v,en):
 for n in range(585):
  for d in range(3):close(math.fsum(v[t][n][d] for t in T[:-1]),v['total'][n][d])
 close(math.fsum(en[t] for t in T[:-1]),en['total'],1e-9)
def localtotal(rows,e):
 return {'element':e,'localGradientsN':{t:[[math.fsum(x['localGradientsN'][t][i][d] for x in rows) for d in range(3)] for i in range(10)] for t in T},'energiesJ':{t:math.fsum(x['energiesJ'][t] for x in rows) for t in T}}
pref=rd(E/'review/selective-fixed-patch-preflight-20261007/preflight.json'); review=rd(E/'review/selective-fixed-patch-preflight-20261007/independent-review.json'); auth=rd(E/'research/selective-fixed-patch-authorization-20261007.json'); comp=rd(M/'completion-receipt.json'); term=rd(M/'terminal-completion.json'); start=rd(RAW/'execution-start.json'); ext=rd(RAW/'external-exit.json'); final=rd(RAW/'external-final.json'); launch=rd(RAW/'launcher-exit.json'); public=rd(E/'review/selective-fixed-patch-outcome-20261007/public-entry-exit.json'); inventory=rd(E/'review/selective-fixed-patch-outcome-20261007/raw-execution-inventory.json'); plan=rd(E/'review/selective-fixed-patch-preflight-20261007/storage-plan.json')
need(subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==RESULT,'frozen result HEAD');need(subprocess.check_output(['git','status','--porcelain'],cwd=R,text=True)=='','frozen clean')
for a,b in [(SOURCE,PREF),(PREF,ACCEPT),(ACCEPT,EXEC),(EXEC,RESULT)]:need(subprocess.run(['git','merge-base','--is-ancestor',a,b],cwd=R).returncode==0,'ancestry')
need(auth['runnerSourceCommit']==SOURCE and auth['acceptedPreflightEvidenceCommit']==PREF and auth['acceptedReviewedHead']==ACCEPT,'authorization commits')
for c,p,want in [(PREF,'education/review/selective-fixed-patch-preflight-20261007/preflight.json','2c6a8c69765f57408860f433379b68595b2a4a55aabb2238205ddcb6b86912bb'),(ACCEPT,'education/review/selective-fixed-patch-preflight-20261007/independent-review.json','d617e3c1fd2e8185a234a6a19c0a323c358322f9ce1e274bbf6ec4ce31c3d013')]:need(hashlib.sha256(blob(c,p)).hexdigest()==want==sha(R/p),'accepted byte bindings')
for p,h in pref['sourceHashes'].items():need(hashlib.sha256(blob(SOURCE,'education/'+p)).hexdigest()==h,'source commit blob');need(sha(E/p)==h,'current frozen source')
for p,h in comp['sourceHashes'].items():need(sha(E/p)==h and hashlib.sha256(blob(EXEC,'education/'+p)).hexdigest()==h,'executed source inventory')
need(pref['sourceCommit']==review['sourceCommit']==SOURCE and review['verdict']=='PASS','preflight review source');need(sha(E/'research/selective-fixed-patch-authorization-20261007.json')==start['authorizationSha256']==public['authorizationSha256'],'auth hash')
files={str(p.relative_to(RAW)):p for p in RAW.rglob('*') if p.is_file()};need(set(files)==set(inventory['files']),'raw exact file inventory')
for p,x in inventory['files'].items():need(files[p].stat().st_size==x['bytes'] and sha(files[p])==x['sha256'],'raw bytes/hash')
bytes_total=sum(p.stat().st_size for p in files.values());need(len(files)==1239==inventory['fileCount'] and bytes_total==22302283==inventory['combinedBytes'],'actual output size')
need(set(p.name for p in M.iterdir())==set(plan['files']),'material closed inventory')
for name,cap in plan['files'].items():need((M/name).stat().st_size<=cap,'material enforced file cap')
for name,x in comp['outputInventory'].items():need(sha(M/name)==x['sha256'] and (M/name).stat().st_size==x['bytes'],'completion inventory')
for name in ['external-incomplete.json','supervisor-incomplete.json','material/incomplete-receipt.json']:need(not (RAW/name).exists(),'no failure override')
budget={'plannedMaterialCalls':497500,'maximumMaterialCalls':497500,'maximumWallSeconds':300,'nodeHeapMiB':1024,'maximumRssBytes':2147483648,'maximumOutputBytes':67108864,'invocations':1};need(auth['budget']==budget,'new explicit budget')
for x in [start,ext,final,launch]:need(x['budget']==budget and x['sourceCommit']==EXEC and x['runId']==start['runId'],'receipt source/run/budget')
need(ext['childExitCode']==final['childExitCode']==launch['launcherExitCode']==public['actualPublicEntryExitCode']==0,'child worker public actual zero');need(ext['watchdogFailure'] is None and launch['supervisorFailure'] is None,'no failure')
need(launch['clockScope']==start['clockScope']=='pre-authorization-and-source-checks','fullclock');need(ext['elapsedMs']<=final['elapsedMs']<=launch['elapsedMs']<300000 and public['elapsedSeconds']<300,'wall')
need(ext['peakObservedChildRssBytes']==254705664<=budget['maximumRssBytes'] and bytes_total<budget['maximumOutputBytes'],'rss/output');need('--max-old-space-size=1024' in start['command'],'heapcommand')
for log in ['execute.log','launcher.log']:need((RAW/log).stat().st_size<=65536,'64KiB logs')
for owner,key,p in [(ext,'logSha256','execute.log'),(final,'logSha256','execute.log'),(final,'externalExitSha256','external-exit.json'),(launch,'launcherLogSha256','launcher.log'),(launch,'externalFinalSha256','external-final.json'),(term,'completionSha256','material/completion-receipt.json')]:need(owner[key]==sha(RAW/p),'terminal hash chain')
lines=(RAW/'execute.log').read_text().splitlines();need(len(lines)==1,'one final stdout marker');marker=json.loads(lines[0]);need(marker['terminalSha256']==sha(M/'terminal-completion.json'),'markerhash')
for x in [comp,term,marker]:
 need(x['sourceCommit']==EXEC and x['runId']==start['runId'] and x['result']=='UNRESOLVED_FIXED_PATCH_INTEGRATION','numerical/result identity')
 rt=x['runtime'];need(all(rt[k]==497500 for k in ['reservedCalls','actualConstitutiveCallbacks','completedConstitutiveCallbacks','plannedCalls','maximumCalls']),'new exact counters');need(rt['activeBatch'] is None and rt['maximumWallMs']==300000 and rt['elapsedMs']<300000 and rt['maximumRssBytes']==2147483648 and rt['peakObservedRssBytes']<=2147483648,'runtime resources')
need(comp['runtime']['elapsedMs']<=term['runtime']['elapsedMs']<=marker['runtime']['elapsedMs'] and marker['runtime']['lastPhase']=='after-terminal-completion-write','postwriteclock')
need(comp['reusedMeasurements']==4000 and comp['originalTwoShellExecutionExit']==1 and comp['outsidePatchElements']==236 and comp['outsidePatchQualified'] is False,'historical and outside attribution')
need(sum(r['points']*2 for r in pref['schedule'])-4000==497500,'independent planned cost');need(arr==rd(OLD/'saved-arrays.json'),'unchanged fields/direction')
need(public['publicEntryLogSha256']==sha(E/'review/selective-fixed-patch-outcome-20261007/public-entry.log'),'observed public log hash')
historical=E/'review/element247-two-shell-run-20261007'
need(rd(historical/'external-exit.json')['childExitCode']==rd(historical/'launcher-exit.pending.json')['launcherExitCode']==rd(E/'review/element247-two-shell-outcome-20261007/executor-public-entry-exit.json')['finalToolResult']['exit_code']==1,'historical child/worker/public exit1')
oldrt=rd(historical/'material/incomplete-receipt.json')['runtime'];need(all(oldrt[k]==4000 for k in ['reservedCalls','actualConstitutiveCallbacks','completedConstitutiveCallbacks']),'4000 old completed failures')
need((historical/'supervisor-incomplete.json').exists() and not (historical/'launcher-exit.json').exists() and not (historical/'external-final.json').exists(),'historical incomplete remains authoritative')
results=[]; localized=[]; regions=0; stages_n=0; hybrids_n=0
for state in ['control45','terminal46']:
 old=[rd(OLD/f'U3-{state}-element-{e}-local.json') for e in range(252)];base,baseen=assembly(old);oldpatch,oldpatchen=assembly([x for x in old if x['element'] in PATCH]);stages={}
 for r in pref['schedule']:
  e=r['element'];key=f"{e}-{r['id']}";rows=[rd(M/f"{state}-{key}-{'core' if i==r['depth'] else 's'+str(i+1)}-region.json") for i in range(r['depth']+1)];regions+=len(rows);stages_n+=1
  for i,row in enumerate(rows):
   s='core' if i==r['depth'] else 's'+str(i+1);need(row['id']==row['shell']==s and row['comparisonShell']==('core' if i>=20 else s),'closed serialized region');need(row['pointCount']==125*r['radialParts']*r['angularParts']**2 and row['element']==e and row['minimumSampleJ']>1e-6,'region metadata')
  actual=localtotal(rows,e);stage=rd(M/f'{state}-{key}-stage.json');stages[key]=stage;need(stage['recipe']==r and stage['pointCount']==r['points'] and stage['minimumSampleJ']==min(x['minimumSampleJ'] for x in rows),'stage metadata');nested(actual['localGradientsN'],stage['localGradientsN']);nested(actual['energiesJ'],stage['energiesJ'],1e-9);v,en=assembly(rows);sv,se=assembly([stage]);nested(v,sv);nested(en,se,1e-9);component(v,en)
  need(len(stage['comparisonShells'])==21,'21comparison groups')
  for bin in stage['comparisonShells']:
   selected=[x for x in rows if x['comparisonShell']==bin['shell']];need(bin['originalShells']==[x['shell'] for x in selected],'group originals');actual=localtotal(selected,e);nested(actual['localGradientsN'],bin['localGradientsN']);nested(actual['energiesJ'],bin['energiesJ'],1e-9)
  if state=='terminal46' and r['id']=='F44':
   for row in rows[:2]:
    historical=rd(E/f"review/element247-two-shell-run-20261007/material/T24-terminal46-{row['shell']}-shell.json")
    for k in ['pointCount','localGradientsN','energiesJ','minimumSampleJ','element']:need(row[k]==historical[k],'4000 historical measurements unchanged')
 candidates={}
 for q in ['Q0','Q1','Q2']:
  x=rd(M/f'{state}-{q}-hybrid.json');candidates[q]=x;hybrids_n+=1;need(x['elementOrder']==PATCH and [r['element'] for r in x['localElements']]==PATCH,'all16 composition')
  for row in x['localElements']:
   e=row['element'];rule=({'Q0':'D4','Q1':'D5','Q2':'U5'} if e in QUIET else {'Q0':'C55','Q1':'A55','Q2':'D5'} if e in SEC else {'Q0':'A55','Q1':'F44','Q2':'X44'})[q];expected=rd(SH/f'A55-{state}-assembly.json') if e==247 and q=='Q0' else stages.get(f'{e}-{rule}') or rd(OLD/f'{rule}-{state}-element-{e}-local.json');need(row['localGradientsN']==expected['localGradientsN'] and row['energiesJ']==expected['energiesJ'],'exact candidate local source')
  v,en=assembly(x['localElements']);nested(v,x['patchNodalGradientsN']);nested(base,x['baselineNodalGradientsN']);hy={t:[[math.fsum([base[t][n][d],-oldpatch[t][n][d],v[t][n][d]]) for d in range(3)] for n in range(585)] for t in T};he={t:math.fsum([baseen[t],-oldpatchen[t],en[t]]) for t in T};nested(hy,x['hybridNodalGradientsN']);nested(he,x['hybridEnergiesJ'],1e-9);nested(en,x['patchEnergiesJ'],1e-9);component(hy,he);need(x['outsidePatchElements']==236 and x['outsidePatchQualified'] is False,'outside remains unqualified')
 for a,b in [('Q0','Q1'),('Q1','Q2'),('Q0','Q2'),('F44','R44')]:
  units=[]
  for e in ([247] if a=='F44' else PATCH):
   if e==247 or (a=='Q0' and b=='Q1' and e in SEC):
    def bins(q):
     rule={'Q0':'A55','Q1':'F44','Q2':'X44'}.get(q,q) if e==247 else {'Q0':'C55','Q1':'A55'}[q];return (rd(SH/f'A55-{state}-assembly.json') if e==247 and q=='Q0' else stages[f'{e}-{rule}'])['comparisonShells']
    units.extend((f"{e}-{x['shell']}",e,x,y) for x,y in zip(bins(a),bins(b)))
   else:units.append((f'{e}-whole',e,next(x for x in candidates[a]['localElements'] if x['element']==e),next(x for x in candidates[b]['localElements'] if x['element']==e)))
  saved=rd(M/f'{state}-{a}-{b}-comparison.json');need(saved['units']==len(units) and saved['required']==((a,b)!=('Q0','Q2')),'unit count requiredflag');metrics={};allpass=True
  for t in T:
   bags=[[[] for d in range(3)] for n in range(585)];wb=[];delta_units=[]
   for (name,e,x,y),ds in zip(units,saved['terms'][t]['differences']):
    delta=[[x['localGradientsN'][t][i][d]-y['localGradientsN'][t][i][d] for d in range(3)] for i in range(10)];nested(delta,ds['localDifferenceN'],1e-12);need(ds['id']==name and ds['element']==e,'deltaidentity');work=math.fsum(delta[i][d]*direction[n][d] for i,n in enumerate(ids[e]) for d in range(3));close(work,ds['directionalDifferenceJ'],1e-12);wb.append(work)
    for i,n in enumerate(ids[e]):
     for d in range(3):bags[n][d].append(delta[i][d])
    delta_units.append({'unit':name,'element':e,'infinityN':max(abs(z) for v in delta for z in v),'directionalDifferenceJ':work,'delta':delta})
   signed=[[math.fsum(x) for x in n] for n in bags];tri=[[math.fsum(abs(v) for v in x) for x in n] for n in bags];nested(signed,saved['terms'][t]['aggregateDifferenceN'],1e-12);nested(tri,saved['terms'][t]['absoluteUnitDifferenceN'],1e-12);vals={'aggregateInfinityN':max(abs(z) for n in signed for z in n),'unitTriangleInfinityN':max(z for n in tri for z in n),'aggregateDirectionalDifferenceJ':abs(math.fsum(wb)),'unitTriangleDirectionalDifferenceJ':math.fsum(abs(v) for v in wb)}
   for k,v in vals.items():close(v,saved['terms'][t][k],1e-12)
   passed=vals['aggregateInfinityN']<=F and vals['unitTriangleInfinityN']<=F and vals['aggregateDirectionalDifferenceJ']<=W and vals['unitTriangleDirectionalDifferenceJ']<=W;need(saved['terms'][t]['pass']==passed,'term exact passflag');metrics[t]={**vals,'pass':passed};allpass &= passed
   if a=='Q0' and b=='Q1':
    element=[]
    for e in PATCH:
     us=[z for z in delta_units if z['element']==e];dv=[[math.fsum(z['delta'][i][d] for z in us) for d in range(3)] for i in range(10)];tr=[[math.fsum(abs(z['delta'][i][d]) for z in us) for d in range(3)] for i in range(10)];element.append({'element':e,'signedInfinityN':max(abs(z) for n in dv for z in n),'unitTriangleInfinityN':max(z for n in tr for z in n),'workJ':math.fsum(z['directionalDifferenceJ'] for z in us),'unitTriangleWorkJ':math.fsum(abs(z['directionalDifferenceJ']) for z in us)})
    win=max(((tri[n][d],n,d) for n in range(585) for d in range(3)));contributions=[]
    for z in delta_units:
     if win[1] in ids[z['element']]:
      i=ids[z['element']].index(win[1]);value=z['delta'][i][win[2]]
      if value:contributions.append({'unit':z['unit'],'element':z['element'],'signedN':value,'absoluteN':abs(value)})
    localized.append({'state':state,'component':t,'metrics':vals,'elementContributions':element,'rankedUnits':[{k:v for k,v in z.items() if k!='delta'} for z in sorted(delta_units,key=lambda z:z['infinityN'],reverse=True)],'triangleMaximum':{'node':win[1],'dimension':win[2],'valueN':win[0],'contributions':sorted(contributions,key=lambda z:z['absoluteN'],reverse=True)}})
  need(saved['pass']==allpass,'comparison exact passflag');results.append({'state':state,'a':a,'b':b,'required':saved['required'],'pass':allpass,'terms':metrics})
need(regions==634 and stages_n==30 and hybrids_n==6,'full replay counts');need(not all(x['pass'] for x in results if x['required']),'preserve unresolved')
# Failure priority is exercised with synthetic minimal folders, no actual process launch.
sys.path.insert(0,str(E/'tools'));import element247_shell_execution as supervisor
priority=[]
for name,reason in [('external-incomplete.json','EXTERNAL_INCOMPLETE_TAKES_PRECEDENCE'),('material/incomplete-receipt.json','MATERIAL_INCOMPLETE_TAKES_PRECEDENCE'),('supervisor-incomplete.json','SUPERVISOR_INCOMPLETE_TAKES_PRECEDENCE'),('launcher-exit.pending.json','LAUNCHER_FAILED_EXIT_TAKES_PRECEDENCE'),('launcher-exit.json','LAUNCHER_FAILED_EXIT_TAKES_PRECEDENCE'),('external-exit.json','EXTERNAL_FAILED_EXIT_TAKES_PRECEDENCE')]:
 with tempfile.TemporaryDirectory(prefix='selective-failure-priority-') as d:
  p=pathlib.Path(d)/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'launcherExitCode':1,'childExitCode':1,'supervisorFailure':None,'watchdogFailure':None}))
  try:supervisor.require_terminal_evidence(d,budget,start['command'],results={'UNRESOLVED_FIXED_PATCH_INTEGRATION'});raise AssertionError('refusal expected')
  except supervisor.EvidenceFailure as ex:need(str(ex)==reason,'failure priority before missing hashes');priority.append(reason)
report={'verdict':'PASS_INDEPENDENT_ARITHMETIC_RESOURCE_REVIEW','resultCommit':RESULT,'executedCommit':EXEC,'runnerSourceCommit':SOURCE,'preflightEvidenceCommit':PREF,'acceptedReviewedHead':ACCEPT,'preflightSha256':auth['preflightSha256'],'independentStructuralReviewSha256':auth['independentReviewSha256'],'specimenCallsDuringReview':0,'materialLawInvocationsDuringReview':0,'method':'Independent Python fsum scatter/local-group-hybrid-and-unit-difference replay from retained raw inputs; material law and JS runner are never imported or invoked.','assertions':count,'maximumReplayDifference':err,'regions':regions,'stages':stages_n,'hybrids':hybrids_n,'comparisons':results,'localization':localized,'resource':{'reservedNewCallbacks':497500,'enteredNewCallbacks':497500,'completedNewCallbacks':497500,'historicalReusedMeasurements':4000,'historicalFailedExit':1,'childExit':0,'workerExit':0,'publicExit':0,'wallAcceptanceSeconds':launch['elapsedMs']/1000,'wallObservedPublicSeconds':public['elapsedSeconds'],'peakChildRSSBytes':ext['peakObservedChildRssBytes'],'files':len(files),'bytes':bytes_total,'budget':budget,'failurePriorityTests':priority},'numericalStatus':'UNRESOLVED_FIXED_PATCH_INTEGRATION','outsidePatchElements':236,'outsidePatchQualified':False,'anatomicalQualification':False}
pathlib.Path('/tmp/selective-material-independent-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['comparisons','localization']},indent=2))

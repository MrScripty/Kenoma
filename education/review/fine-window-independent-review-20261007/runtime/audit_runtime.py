"""Independent frozen-source/resource/reuse audit. No geometry generation or laws."""
import argparse,hashlib,json,math,pathlib,subprocess,zipfile
p=argparse.ArgumentParser();p.add_argument('repo');p.add_argument('preflight');p.add_argument('--source',required=True);args=p.parse_args()
repo=pathlib.Path(args.repo);ed=repo/'education';pf=pathlib.Path(args.preflight);checks=0

def need(x,label):
 global checks;checks+=1
 if not x:raise AssertionError(label)
def read(p):return json.loads(pathlib.Path(p).read_bytes())
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def near(a,b,tol=1e-8):need(math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol,f'arithmetic {a} vs {b}')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();need(head==args.source,'source exact')
m=read(ed/'research/fine-window-runner-20261007-inputs.json');accepted=read(ed/'research/selective-fine-window-schedule-20261007.json');pref=read(pf/'preflight.json');plan=read(pf/'storage-plan.json');index=read(ed/'review/selective-fine-window-schedule-20261007/reuse-index.json')
need(pref['sourceCommit']==head,'preflight source');need(pref['specimenCalls']==pref['materialLawInvocations']==0,'zero calls');need(not m['executionAuthorized'] and m['parentPreparationAccepted'],'preparation only');need(not (ed/'research/fine-window-authorization-20261007.json').exists(),'no auth');need(not (ed/'review/fine-window-run-20261007').exists(),'no run')
for name,item in index['files'].items():need(sha(repo/name)==item['sha256'] and (repo/name).stat().st_size==item['bytes'],'reuse hash '+name)
for name,h in pref['sourceHashes'].items():need(sha(ed/name)==h,'source hash '+name)
for name,h in pref['artifactHashes'].items():need(sha(pf/name)==h and (pf/name).stat().st_size==pref['artifactBytes'][name],'artifact '+name)
for name,h in m['immutableModuleHashes'].items():need(sha(ed/name)==h,'immutable law/helper '+name)
need(pref['budget']=={'plannedMaterialCalls':19716000,'maximumMaterialCalls':19716000,'maximumWallSeconds':7200,'nodeHeapMiB':1024,'maximumRssBytes':2147483648,'maximumOutputBytes':536870912,'invocations':1},'new exact budget')
need(pref['states']==accepted['states'] and pref['material']==accepted['material'],'fixed fields/material')
counts={};new=shared=logical=0
for r in pref['schedule']:
 ident=r['id'];e=r['element'];need(e in accepted['focus'],'focus only');need(r['corner']==accepted['corners'][str(e)],'corner');need(r['order']==5,'gauss5');need(r['depth']==(22 if ident=='H4' else 20),'depth axis');need(r['angularParts']==(8 if ident=='P8' else 4),'angular axis');need(r['radialParts']==(2 if ident in ['R4','I1'] else 1),'radial axis');need(r['faceParts']==(8 if ident=='I1' else 4),'independent level');need(r['kind']==('graded-affine-tetra' if ident in ['I0','I1'] else 'tensor-shell'),'family')
 face=[i for i in range(4) if i!=r['corner']];need(r['faceOrder']==(face[1:]+face[:1] if ident=='C4' else face),'isolated chart')
 count=0;shared_count=0
 for i in range(r['depth']+1):
  core=i==r['depth'];n=((1 if core else 3*r['radialParts'])*r['faceParts']**2*125 if ident in ['I0','I1'] else 125*r['radialParts']*r['angularParts']**2)
  reused=i<20 and (ident=='H4' or ident=='C4' and e==247);count+=n;shared_count+=n if reused else 0
  cert=pref['regions'][f"{e}-{ident}-{'core' if core else 's'+str(i+1)}"];need(cert['points']==n and cert['newEvaluation']==(not reused),'region count/reuse');need(cert['physicalBytes']==n*8,'weight cap');need(cert['minimumPhysicalWeightM3']>0 and cert['minimumReferenceJacobian']>0 and min(cert['minimumSampleJ'].values())>1e-6,'finite geometry positivity')
 need(count==r['points'],'logical stage points');counts[ident]=counts.get(ident,0)+2*(count-shared_count);new+=2*(count-shared_count);shared+=2*shared_count;logical+=2*(r['depth']+1)
need(counts=={x['recipe']:x['newCalls'] for x in accepted['recipes']},'exact accepted phase totals');need(new==19716000 and shared==640000 and logical==2002,'callback budget/reuse logical')
need(len(plan['files'])==3116 and sum(v for n,v in plan['files'].items() if n.endswith('.f64le'))==345840000,'binary/closed counts');need(sum(plan['files'].values())+10*65536+4194304==448240000==plan['maximumCombinedBytes']<536870912,'combined envelope');need(plan['maximumRegionPoints']==48000 and plan['partialWeightCapBytes']==524288,'streamed maxima');need(pref['normalizedMomentChecks']==75096 and pref['physicalMomentChecks']==15015 and pref['geometryPointChecks']==20356000,'actual structural inventories');
for n,v in read(pf/'synthetic-worst-serialization.json').items():need(v['encodedBytes']<=v['conservativeBytes']<=v['capBytes'] and v['maximumFiniteNumberChars']==26,'certified finite numeric envelope '+n)
need(pref['tests']['fail']==0,'tests no failure');need(pref['outsidePatchElements']==236 and not pref['outsidePatchQualified'] and not pref['anatomicalQualification'],'outside limit')
need(pref['preflightResourceEvidence']['peakObservedRssBytes']<=2147483648 and pref['preflightResourceEvidence']['elapsedSeconds']<7200,'actual preparation resources')
with zipfile.ZipFile(pf/'synthetic-evidence.zip') as z:
 j={n:json.loads(z.read(n)) for n in z.namelist()};inventory=j['fixture-inventory.json'];need(inventory['fixtureOnly'] and inventory['specimenCalls']==inventory['materialLawInvocations']==0,'fixture provenance')
 for n,v in inventory['completeFileInventory'].items():
  data=(pf/n).read_bytes() if n.endswith('.f64le') else z.read('material/'+n)
  need(len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256'],'fixture closed hash '+n)
 source=next(x for x in read(ed/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if x['element_id']=='FJ1486');ids=source['elements_ten_node'];terms=accepted['components'];states=[x['id'] for x in accepted['states']];allmax=0
 def row(name,origin='material/'):
  return j[origin+name] if origin+name in j else read(ed/'review/selective-fixed-patch-run-20261007/material'/name)
 for state in states:
  for r in pref['schedule']:
   stage=row(f"{state}-{r['element']}-{r['id']}-stage.json");rows=[row(ref['name']) for ref in stage['rowSources']]
   for t in terms:
    near(math.fsum(x['energiesJ'][t] for x in rows),stage['energiesJ'][t],1e-9)
    for i in range(10):
     for d in range(3):near(math.fsum(x['localGradientsN'][t][i][d] for x in rows),stage['localGradientsN'][t][i][d])
   for b in stage['comparisonShells']:
    rr=[x for x in rows if x['comparisonShell']==b['shell']];need(b['originalShells']==[x['shell'] for x in rr],'stable physical bins')
    for t in terms:
     near(math.fsum(x['energiesJ'][t] for x in rr),b['energiesJ'][t],1e-9)
     for i in range(10):
      for d in range(3):near(math.fsum(x['localGradientsN'][t][i][d] for x in rr),b['localGradientsN'][t][i][d])
  for q in ['S0','S1','S2','I0','I1','AR','AH','AC']:
   hybrid=row(f'{state}-{q}-hybrid.json');need(hybrid['elementOrder']==accepted['patch'] and [x['element'] for x in hybrid['localElements']]==accepted['patch'],'all16 coverage')
   for t in terms:
    v=[[[] for _ in range(3)] for _ in range(585)]
    for e in hybrid['localElements']:
     for i,n in enumerate(ids[e['element']]):
      for d in range(3):v[n][d].append(e['localGradientsN'][t][i][d])
    for n in range(585):
     for d in range(3):near(math.fsum(v[n][d]),hybrid['patchNodalGradientsN'][t][n][d])
    near(math.fsum(x['energiesJ'][t] for x in hybrid['localElements']),hybrid['patchEnergiesJ'][t],1e-9)
 comparisons=[x for n,x in j.items() if n.endswith('-comparison.json')];need(len(comparisons)==24 and sum(x['required'] for x in comparisons)==20,'all accepted comparisons')
 direction=j['material/saved-arrays.json']['terminalDirectionM']
 def stage_for(state,e,rule):
  n=f'{state}-{e}-{rule}-stage.json'
  if 'material/'+n in j:return j['material/'+n]
  if e in accepted['quiet']:return read(ed/f'review/fixed-field-integration-run-20261007/{rule}-{state}-element-{e}-local.json')
  if e==247 and rule=='A55':return read(ed/f'review/element247-shell-run-20261007/material/A55-{state}-assembly.json')
  return read(ed/f'review/selective-fixed-patch-run-20261007/material/{n}')
 def rule_for(q,e):
  if e in accepted['quiet']:return 'U4' if q=='I0' else 'U5' if q=='I1' else 'D5'
  return 'A55' if q=='S0' else ('F44' if e==247 else 'P4') if q=='S1' else 'P8' if q=='S2' else q if q in ['I0','I1'] else ('R44' if e==247 else 'R4') if q=='AR' else 'H4' if q=='AH' else 'C4'
 def reduce_units(units,t):
  signed=[[[] for _ in range(3)] for _ in range(585)];works=[]
  for e,a,b in units:
   ws=[]
   for i,n in enumerate(ids[e]):
    for d in range(3):
     delta=a['localGradientsN'][t][i][d]-b['localGradientsN'][t][i][d];signed[n][d].append(delta);ws.append(delta*direction[n][d])
   works.append(math.fsum(ws))
  return [max(abs(math.fsum(v)) for row in signed for v in row),max(math.fsum(abs(x) for x in v) for row in signed for v in row),abs(math.fsum(works)),math.fsum(abs(x) for x in works)]
 for c in comparisons:
  need(set(c['terms'])==set(terms),'all5terms');need(len(c['terms']['total']['aggregateDifferenceN'])==585,'all585inclheld')
  quiet='scope' in c;units=[]
  for e in accepted['quiet'] if quiet else accepted['patch']:
   a=stage_for(c['state'],e,c['a'] if quiet else rule_for(c['a'],e));b=stage_for(c['state'],e,c['b'] if quiet else rule_for(c['b'],e))
   if e in accepted['quiet']:units.append((e,a,b))
   else:
    need([x['shell'] for x in a['comparisonShells']]==[x['shell'] for x in b['comparisonShells']],'stable156 partition')
    units.extend((e,aa,bb) for aa,bb in zip(a['comparisonShells'],b['comparisonShells']))
  need(len(units)==(9 if quiet else 156),'comparison units');passes=[];allocated=[]
  for t in terms:
   x=c['terms'][t];need(x['forceGateN']==1e-5 and x['workGateJ']==5.492029235357012e-7,'frozen gates');vals=reduce_units(units,t)
   for k,v in zip(['aggregateInfinityN','unitTriangleInfinityN','aggregateDirectionalDifferenceJ','unitTriangleDirectionalDifferenceJ'],vals):near(v,x[k],1e-12)
   gp=vals[0]<=1e-5 and vals[1]<=1e-5 and vals[2]<=5.492029235357012e-7 and vals[3]<=5.492029235357012e-7;need(x['pass']==gp,'term pass');passes.append(gp)
   if quiet:
    fraction=.85 if c['a']=='U4' else .2;fp=fraction*1e-5;wp=fraction*5.492029235357012e-7;ap=vals[0]<=fp and vals[1]<=fp and vals[2]<=wp and vals[3]<=wp;need(x['allocatedPass']==ap,'quiet allocation');allocated.append(ap)
   else:
    for name,es,fraction in [('quiet',accepted['quiet'],.85 if c['a']=='I0' and c['b']=='I1' else .2),('focus',accepted['focus'],.15 if c['a']=='I0' and c['b']=='I1' else .8)]:
     vv=reduce_units([u for u in units if u[0] in es],t);fp=fraction*1e-5;wp=fraction*5.492029235357012e-7;rec=c['allocations'][name]['metrics'][t]
     for k,v in zip(['signedN','triangleN','signedWorkJ','triangleWorkJ'],vv):near(v,rec[k],1e-12)
     ap=vv[0]<=fp and vv[1]<=fp and vv[2]<=wp and vv[3]<=wp;need(rec['pass']==ap,'subset pass');allocated.append(ap)
  need(c['globalPass']==all(passes) and c['pass']==(all(passes) and all(allocated)),'global complete comparison pass')
report={'verdict':'PASS_INDEPENDENT_RUNTIME_RESOURCE_ARITHMETIC_REVIEW','sourceCommit':head,'preflightSha256':sha(pf/'preflight.json'),'assertions':checks,'phaseNewCallbackCounts':counts,'newPlannedCallbacks':new,'sharedLogicalMeasurements':shared,'logicalRegions':logical,'reuseFilesVerified':len(index['files']),'sourceFilesVerified':len(pref['sourceHashes']),'artifactFilesVerified':len(pref['artifactHashes']),'closedProductionFileCount':len(plan['files']),'worstCaseCombinedOutputBytes':448240000,'specimenCalls':0,'materialLawInvocations':0,'quadratureGeneratedByReviewer':False,'implementationEditsByReviewer':False,'outside236Qualified':False,'preflightResourceEvidence':pref['preflightResourceEvidence']}
print(json.dumps(report,indent=2))

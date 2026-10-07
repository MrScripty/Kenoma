"""Independent scalar-loop frozen-evidence replay, without law evaluation."""
import json,math,pathlib,sys
from fine_window_execution import ROOT,PREF,AUTH,BUDGET,COMMAND,RESULTS,need,read,digest,require_terminal_evidence,validate_authorization
from importlib import util
_spec=util.spec_from_file_location('old_scalar_verifier',pathlib.Path(__file__).with_name('verify-selective-fixed-patch.py'));_old=util.module_from_spec(_spec);_spec.loader.exec_module(_old)
TERMS=_old.TERMS;PATCH=_old.PATCH;QUIET=_old.QUIET;FOCUS=[197,200,203,206,246,247,248];STATES=['control45','terminal46'];CANDIDATES=['S0','S1','S2','I0','I1','AR','AH','AC'];PAIRS=[('S0','S1',True),('S1','S2',True),('I0','I1',True),('S2','I1',True),('S1','AR',True),('S1','AH',True),('S1','AC',True),('S0','I0',False),('S1','I1',False)];RAW=ROOT/'review/selective-fixed-patch-run-20261007/material';OLD=_old.OLD;SHELL=_old.SHELL
def close(a,b,tol=1e-8):_old.close(a,b,tol)
def rcount(r,s):return (1 if s=='core' else 3*r['radialParts'])*r['faceParts']**2*125 if r['kind']=='graded-affine-tetra' else 125*r['radialParts']*r['angularParts']**2
def shared(r,s):return (r['id']=='H4' or (r['id']=='C4' and r['element']==247)) and s!='core' and int(s[1:])<=20
def expected_rule(q,e):
 if e in QUIET:return 'U4' if q=='I0' else 'U5' if q=='I1' else 'D5'
 return 'A55' if q=='S0' else ('F44' if e==247 else 'P4') if q=='S1' else 'P8' if q=='S2' else q if q in ['I0','I1'] else ('R44' if e==247 else 'R4') if q=='AR' else 'H4' if q=='AH' else 'C4'
def retained(state,e,rule):
 if e in QUIET:return read(OLD/f'{rule}-{state}-element-{e}-local.json')
 if e==247 and rule=='A55':return read(SHELL/f'A55-{state}-assembly.json')
 return read(RAW/f'{state}-{e}-{rule}-stage.json')
def allocations(c,units,ids,direction,a,b):
 independent=a=='I0' and b=='I1';fractions={'quiet':.85 if independent else .2,'focus':.15 if independent else .8};out=[]
 for name,es in [('quiet',QUIET),('focus',FOCUS)]:
  subset=[x for x in units if x[1]['element'] in es];saved=c['allocations'][name];force=fractions[name]*1e-5;work=fractions[name]*5.492029235357012e-7;close(saved['budget']['forceN'],force,1e-18);close(saved['budget']['workJ'],work,1e-20);passed=[]
  for term in TERMS:
   signed=[[[] for _ in range(3)] for _ in range(585)];works=[]
   for _key,A,B in subset:
    ws=[]
    for i,n in enumerate(ids[A['element']]):
     for d in range(3):delta=A['localGradientsN'][term][i][d]-B['localGradientsN'][term][i][d];signed[n][d].append(delta);ws.append(delta*direction[n][d])
    works.append(math.fsum(ws))
   values=[max(abs(math.fsum(v)) for row in signed for v in row),max(math.fsum(abs(x) for x in v) for row in signed for v in row),abs(math.fsum(works)),math.fsum(abs(x) for x in works)];record=saved['metrics'][term]
   for key,value in zip(['signedN','triangleN','signedWorkJ','triangleWorkJ'],values):close(record[key],value,1e-12)
   p=values[0]<=force and values[1]<=force and values[2]<=work and values[3]<=work;need(record['pass'] is p,'FALSE_ALLOCATED_TERM_PASS');passed.append(p)
  need(saved['pass'] is all(passed),'FALSE_ALLOCATED_GROUP_PASS');out.append(all(passed))
 return all(out)
def global_comparison(c,units,ids,direction):
 # Existing independently written scalar reducer uses unchanged global gates.
 value=dict(c);value['pass']=c['globalPass'];return _old.check_comparison(value,units,ids,direction)
def verify_vectors(directory,pref,plan):
 mat=pathlib.Path(directory)/'material';need(set(p.name for p in mat.iterdir())==set(plan['files']),'CLOSED_OUTPUT_FILE_INVENTORY')
 for name,cap in plan['files'].items():need((mat/name).stat().st_size<=cap,'FILE_BYTE_ENVELOPE')
 arrays=read(mat/'saved-arrays.json');need(arrays==read(OLD/'saved-arrays.json'),'FROZEN_ARRAYS');source=next(x for x in read(ROOT/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if x['element_id']=='FJ1486');ids=source['elements_ten_node'];direction=arrays['terminalDirectionM'];stages={};regions=0;new_regions=0;shared_regions=0;callback_points=0;reused_points=0
 for state in STATES:
  identity={'positionsSha256':next(x['positionsSha256'] for x in pref['states'] if x['id']==state),'referenceSha256':pref['evaluationIdentities'][state]['referenceSha256'],'materialSha256':pref['evaluationIdentities'][state]['materialSha256'],'lawModulesSha256':pref['evaluationIdentities'][state]['lawModulesSha256'],'activation':1};need(identity==pref['evaluationIdentities'][state],'EVALUATION_IDENTITY')
  for r in pref['schedule']:
   e,key=r['element'],f"{r['element']}-{r['id']}";stage=read(mat/f'{state}-{key}-stage.json');need(stage['state']==state and stage['recipe']==r,'STAGE_RECIPE');need(len(stage['rowSources'])==r['depth']+1,'ROW_SOURCE_INVENTORY');rows=[]
   for i,ref in enumerate(stage['rowSources']):
    s='core' if i==r['depth'] else f's{i+1}';need(ref['shell']==s,'REGION_ORDER');cert=pref['regions'][f'{key}-{s}'];regions+=1
    if shared(r,s):
     is_current=r['id']=='H4' and e!=247;expected_name=f"{state}-{e}-{'P4' if is_current else 'F44' if r['id']=='H4' else 'X44'}-{s}-region.json";need(ref['name']==expected_name,'EXACT_REUSE_SOURCE');origin=mat if is_current else RAW;row=read(origin/expected_name);need(digest(origin/expected_name)==ref['sha256'],'REUSED_ROW_HASH');need(ref['kind']==('same-invocation' if is_current else 'historical') and ref['earnsIndependentResolutionCredit'] is False,'REUSE_ATTRIBUTION');need(ref['normalizedSha256']==cert['normalizedSha256'] and ref['physicalSha256']==cert['physicalSha256'],'REUSE_POINT_WEIGHT_HASH');
     expected_stage=f"{state}-{e}-{'P4' if is_current else 'F44' if r['id']=='H4' else 'X44'}-stage.json";need(ref['stageName']==expected_stage and digest(origin/expected_stage)==ref['stageSha256'],'REUSE_STAGE_RECEIPT');prior=read(origin/expected_stage)
     if is_current:need(row['evaluationIdentity']==identity and row['state']==state and prior['newCallbackPoints']==42000 and prior['reusedPoints']==0 and any(x['name']==expected_name and x['sha256']==ref['sha256'] for x in prior['rowSources']),'P4_DEPENDENCY_REFUSAL')
     else:need(ref['sha256']==cert['reuseRows'][state]['sha256'],'IMMUTABLE_HISTORICAL_REUSE')
     shared_regions+=1;reused_points+=rcount(r,s)
    else:
     need(ref['kind']=='new' and ref['name']==f'{state}-{key}-{s}-region.json','NEW_ROW_IDENTITY');row=read(mat/ref['name']);need(digest(mat/ref['name'])==ref['sha256'] and (mat/ref['name']).stat().st_size==ref['bytes'],'NEW_ROW_HASH');need(row['evaluationIdentity']==identity and row['state']==state and row['recipeId']==r['id'],'NEW_ROW_EVALUATION_IDENTITY');new_regions+=1;callback_points+=rcount(r,s)
    need(row['element']==e and row['shell']==row['id']==s and row['pointCount']==rcount(r,s),'REGION_IDENTITY_COUNT');need(row['comparisonShell']==('core' if i>=20 else s),'PHYSICAL_COMPARISON_REGION');need(math.isfinite(row['minimumSampleJ']) and row['minimumSampleJ']>1e-6,'J_GUARD');rows.append(row)
   need(stage['pointCount']==r['points'] and stage['minimumSampleJ']==min(x['minimumSampleJ'] for x in rows),'STAGE_POINT_MINIMUM');need(stage['newCallbackPoints']==sum(rcount(r,'core' if i==r['depth'] else f's{i+1}') for i in range(r['depth']+1) if not shared(r,'core' if i==r['depth'] else f's{i+1}')),'STAGE_NEW_CALLBACK_COUNT');need(stage['reusedPoints']==stage['pointCount']-stage['newCallbackPoints'],'STAGE_REUSE_COUNT')
   actual,en=_old.sum_rows(rows,ids);sv,se=_old.sum_rows([stage],ids);_old.same_vectors(actual,sv);_old.components(actual,en)
   for t in TERMS:close(en[t],se[t],1e-9)
   need([x['shell'] for x in stage['comparisonShells']]==[f's{i}' for i in range(1,21)]+['core'],'COMPLETE_PHYSICAL_REGION_BINS')
   for bin in stage['comparisonShells']:
    selected=[x for x in rows if x['comparisonShell']==bin['shell']];need(bin['originalShells']==[x['shell'] for x in selected],'ORIGINAL_REGIONS_PRESERVED');bv,be=_old.sum_rows([bin],ids);rv,re=_old.sum_rows(selected,ids);_old.same_vectors(bv,rv)
    for t in TERMS:close(be[t],re[t],1e-9)
   stages[f'{state}-{key}']=stage
 required=[]
 for state in STATES:
  baserows=[read(OLD/f'U3-{state}-element-{e}-local.json') for e in range(252)];base,be=_old.sum_rows(baserows,ids);old,oe=_old.sum_rows([r for r in baserows if r['element'] in PATCH],ids);candidates={}
  for q in CANDIDATES:
   c=read(mat/f'{state}-{q}-hybrid.json');need(c['state']==state and c['candidate']==q and c['elementOrder']==PATCH and [x['element'] for x in c['localElements']]==PATCH,'COMPLETE_16_CANDIDATE');candidates[q]=c
   for e,row in zip(PATCH,c['localElements']):
    rule=expected_rule(q,e);expected=stages.get(f'{state}-{e}-{rule}') or retained(state,e,rule)
    for k in ['localGradientsN','energiesJ','pointCount']:need(row[k]==expected[k],'CANDIDATE_EXACT_COMPOSITION')
   pv,pe=_old.sum_rows(c['localElements'],ids);_old.same_vectors(pv,c['patchNodalGradientsN']);_old.same_vectors(base,c['baselineNodalGradientsN']);hv={t:[[base[t][n][d]-old[t][n][d]+pv[t][n][d] for d in range(3)] for n in range(585)] for t in TERMS};he={t:be[t]-oe[t]+pe[t] for t in TERMS};_old.same_vectors(hv,c['hybridNodalGradientsN']);_old.components(hv,he)
   for t in TERMS:close(pe[t],c['patchEnergiesJ'][t],1e-9);close(he[t],c['hybridEnergiesJ'][t],1e-9)
   need(c['outsidePatchElements']==236 and c['outsidePatchQualified'] is False,'OUTSIDE236_SCOPE')
  for a,b,is_required in PAIRS:
   units=[]
   for e in PATCH:
    A=stages.get(f'{state}-{e}-{expected_rule(a,e)}') or retained(state,e,expected_rule(a,e));B=stages.get(f'{state}-{e}-{expected_rule(b,e)}') or retained(state,e,expected_rule(b,e))
    if e in QUIET:units.append((f'{e}-whole',A,B))
    else:
     for ar,br in zip(A['comparisonShells'],B['comparisonShells']):units.append((f"{e}-{ar['shell']}",{**ar,'element':e},{**br,'element':e}))
   need(len(units)==156,'ALL_16_PHYSICAL_UNITS');c=read(mat/f'{state}-{a}-{b}-comparison.json');need(c['state']==state and c['a']==a and c['b']==b and c['required'] is is_required,'COMPARISON_IDENTITY');global_pass=global_comparison(c,units,ids,direction);allocated=allocations(c,units,ids,direction,a,b);need(c['pass'] is (global_pass and allocated),'FALSE_FINE_WINDOW_PASS')
   if is_required:required.append(c['pass'])
  for a,b in [('D4','D5'),('U4','U5'),('D5','U5')]:
   c=read(mat/f'{state}-quiet-{a}-{b}-comparison.json');units=[(f'{e}-whole',retained(state,e,a),retained(state,e,b)) for e in QUIET];global_pass=global_comparison(c,units,ids,direction);fraction=.85 if a=='U4' else .2;close(c['allocatedForceN'],fraction*1e-5,1e-18);close(c['allocatedWorkJ'],fraction*5.492029235357012e-7,1e-20);checks=[]
   for t in TERMS:
    x=c['terms'][t];p=x['aggregateInfinityN']<=c['allocatedForceN'] and x['unitTriangleInfinityN']<=c['allocatedForceN'] and x['aggregateDirectionalDifferenceJ']<=c['allocatedWorkJ'] and x['unitTriangleDirectionalDifferenceJ']<=c['allocatedWorkJ'];need(x['allocatedPass'] is p,'FALSE_QUIET_ALLOCATION');checks.append(p)
   need(c['required'] is True and c['pass'] is (global_pass and all(checks)),'QUIET_WITNESS_REQUIRED');required.append(c['pass'])
 need((regions,new_regions,shared_regions,callback_points,reused_points)==(2002,1682,320,19716000,640000),'COMPLETE_SCHEDULE_COUNTS');return {'result':'PASS_BOUNDED_FINE_WINDOW_FIXED_PATCH_AGREEMENT' if all(required) else 'UNRESOLVED_FIXED_PATCH_INTEGRATION','requiredComparisonsIncludingQuiet':20,'replayedLogicalRegions':regions,'newRegions':new_regions,'sharedRegions':shared_regions,'materialLawInvocations':0,'specimenCalls':0,'outside236Qualified':False}
def verify(directory):
 chain=require_terminal_evidence(directory,BUDGET,COMMAND,results=RESULTS);root=pathlib.Path(directory);mat=root/'material';pref=read(PREF/'preflight.json');plan=read(PREF/'storage-plan.json');completion=chain['completion'];auth=read(AUTH);review=read(PREF/'independent-review.json');validate_authorization(auth,pref,review)
 need(auth['preflightSha256']==digest(PREF/'preflight.json') and auth['independentReviewSha256']==digest(PREF/'independent-review.json'),'FROZEN_AUTHORIZATION_CHAIN');need(read(root/'execution-start.json')['authorizationSha256']==digest(AUTH),'NEW_AUTHORIZATION_IDENTITY');need(completion['runnerSourceCommit']==pref['sourceCommit'],'FROZEN_RUNNER_SOURCE');need(completion['newCallbacks']==19716000 and completion['logicalRegions']==2002 and completion['newRegions']==1682 and completion['sharedRegions']==320 and completion['sharedLogicalMeasurements']==640000,'EXACT_NEW_SCHEDULE');need(completion['originalResultCommit']=='38ae8a2e2af57cf33254af987b724824b9d84357' and completion['originalTwoShellExecutionExit']==1 and completion['anatomicalQualification'] is False,'HISTORICAL_FAILURE_SCOPE')
 _old.check_frozen_inventories(completion,pref,plan)
 expected=set(pref['sourceHashes'])|{str((PREF/p).relative_to(ROOT)) for p in ['preflight.json','independent-review.json',*pref['artifactHashes']]}|{str(AUTH.relative_to(ROOT))};need(set(completion['sourceHashes'])==expected,'COMPLETE_SOURCE_HASH_INVENTORY')
 for p,h in completion['sourceHashes'].items():need(digest(ROOT/p)==h,'SOURCE_HASH')
 for name,record in completion['outputInventory'].items():need(digest(mat/name)==record['sha256'] and (mat/name).stat().st_size==record['bytes'],'OUTPUT_HASH')
 for name,h in pref['artifactHashes'].items():
  if name.endswith('.f64le'):need(digest(mat/name)==h,'ACTUAL_BINARY_POINTS_WEIGHTS_HASH')
 result=verify_vectors(root,pref,plan);need(completion['result']==result['result'],'FALSE_NUMERICAL_RESULT');return {'verdict':'PASS_OPERATIONAL_EVIDENCE_AND_REPLAY',**result}
if __name__=='__main__':need(len(sys.argv)==2,'Existing run directory only');print(json.dumps(verify(sys.argv[1]),indent=2))

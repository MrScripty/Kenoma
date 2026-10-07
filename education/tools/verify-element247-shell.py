"""Reusable zero-material verifier. Refuses provisional/incomplete execution.
Run only on an externally completed retained invocation; no output is replaced.
"""
import pathlib,json,math,struct,sys
from element247_shell_execution import BUDGET,COMMAND,need,read,digest,require_terminal_evidence
TERMS=['matrix','volume','passiveFiber','activePotential','total']
RECIPES=[('C44',20,1344),('C55',20,2625),('R55',20,5250),('A55',20,10500),('X55',22,11500)]
PAIRS=[('C44','C55'),('C55','R55'),('C55','A55'),('A55','X55')]
FORCE=1e-5;WORK=5.492029235357012e-7;RECON_FORCE=1e-8;RECON_ENERGY=1e-9
def finite(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def vector(v,n):need(isinstance(v,list) and len(v)==n and all(isinstance(x,list) and len(x)==3 and all(finite(a) for a in x) for x in v),'COMPLETE_FINITE_VECTOR')
def close(a,b,tol=1e-12):need(finite(a) and finite(b) and abs(a-b)<=tol,'ARITHMETIC_MISMATCH')
def zero(n):return [[0.,0.,0.] for _ in range(n)]
def dot(v,u):return sum(v[i][d]*u[i][d] for i in range(len(v)) for d in range(3))
def max_abs(v):return max(abs(x) for row in v for x in row)
def sum_check(vectors,energies,n):
 for t in TERMS:vector(vectors[t],n);need(finite(energies[t]),'FINITE_ENERGY')
 need(max(abs(sum(vectors[t][i][d] for t in TERMS[:-1])-vectors['total'][i][d]) for i in range(n) for d in range(3))<=RECON_FORCE,'INDEPENDENT_TOTAL_RECONSTRUCTION_FORCE')
 need(abs(sum(energies[t] for t in TERMS[:-1])-energies['total'])<=RECON_ENERGY,'INDEPENDENT_TOTAL_RECONSTRUCTION_ENERGY')
def verify(root,directory):
 root=pathlib.Path(root);run=pathlib.Path(directory);d=run/'material';terminal=require_terminal_evidence(run);r=terminal['completion']
 need(r.get('patchQualification') is False and r.get('priorPatchResult')=='UNRESOLVED_FIXED_PATCH_INTEGRATION','OLD_UNRESOLVED_PATCH_REQUIRED');need(r.get('unchangedStates') is True and all(r.get(k)==0 for k in ['newNodalFields','nonlinearSolves','optimizerTrials','refits']),'FROZEN_STATE_SCOPE')
 for p,h in r['sourceHashes'].items():need(not pathlib.Path(p).is_absolute() and '..' not in pathlib.Path(p).parts,'SOURCE_PATH');need(digest(root/p)==h,'SOURCE_HASH:'+p)
 manifest=read(root/'research/element247-shell-runner-20261007-inputs.json');preflight=read(root/'review/element247-shell-runtime-20261007/runtime-preflight.json');expected_sources=set(manifest['inputs'])|set(manifest['newSources'])|{'review/element247-shell-runtime-20261007/runtime-preflight.json','review/element247-shell-runtime-20261007/js-tests.log','review/element247-shell-runtime-20261007/python-tests.log','research/element247-shell-execution-authorization-20261007.json'}
 need(set(r['sourceHashes'])==expected_sources,'COMPLETE_SOURCE_INVENTORY');need(set(preflight['sourceHashes'])==set(manifest['inputs'])|set(manifest['newSources']),'COMPLETE_PREFLIGHT_SOURCE_INVENTORY');need(preflight['sourceCommit']==r['runnerSourceCommit'] and preflight['result']=='PASS_ELEMENT247_SHELL_RUNTIME_PREFLIGHT_NO_MATERIAL_ASSEMBLY' and preflight['specimenConstitutiveCalls']==0 and preflight['tests']['fail']==0,'PINNED_RUNTIME_PREFLIGHT')
 for p,h in preflight['sourceHashes'].items():need(r['sourceHashes'][p]==h,'CHANGED_PREFLIGHT_SOURCE:'+p)
 for name,x in r['outputInventory'].items():need(pathlib.Path(name).name==name,'OUTPUT_PATH');need((d/name).stat().st_size==x['bytes'] and digest(d/name)==x['sha256'],'OUTPUT_HASH:'+name)
 expected={'material-start.json','saved-arrays.json','shell-vector-comparisons.json'}
 for recipe,depth,_ in RECIPES:
  expected.add(recipe+'-normalized-points.f64le')
  for state in ['control45','terminal46']:
   expected.add(f'{recipe}-{state}-assembly.json')
   for shell in [f's{i}' for i in range(1,depth+1)]+['core']:expected.update({f'{recipe}-{state}-{shell}-shell.json',f'{recipe}-{state}-{shell}-weights.f64le'})
 need(set(r['outputInventory'])==expected,'COMPLETE_OUTPUT_INVENTORY');need({p.name for p in d.iterdir()}==expected|{'completion-receipt.json','terminal-completion.json'},'UNEXPECTED_OR_MISSING_MATERIAL_FILE')
 start=read(d/'material-start.json');need(start['sourceCommit']==r['sourceCommit'] and start['runId']==r['runId'] and start['budget']==BUDGET and start['activation']==1,'MATERIAL_START_IDENTITY')
 need(start['sourceHashes']==r['sourceHashes'],'SOURCE_INVENTORY_IDENTITY')
 auth=read(root/'research/element247-shell-execution-authorization-20261007.json');need(auth['authorized'] is True and auth['budget']==BUDGET and auth['runnerSourceCommit']==r['runnerSourceCommit'],'AUTHORIZATION_SCOPE');need(digest(root/'research/element247-shell-execution-authorization-20261007.json')==start['authorizationSha256'],'AUTHORIZATION_HASH')
 need(auth.get('parentThread')=='01a103c3-a2e6-7606-8c1e-06987ac710f1' and auth.get('invocations')==1 and auth.get('runtimePreflightSha256')==digest(root/'review/element247-shell-runtime-20261007/runtime-preflight.json'),'PINNED_ONE_SHOT_AUTHORIZATION')
 prior_protocol=read(root/'research/fixed-field-integration-protocol-20261007-inputs.json');need(start['material']==prior_protocol['material'],'UNCHANGED_MATERIAL')
 arrays=read(d/'saved-arrays.json');need(arrays==read(root/'review/fixed-field-integration-run-20261007/saved-arrays.json'),'UNCHANGED_ARRAYS');direction=arrays['terminalDirectionM'];vector(direction,585);need(all(all(x==0 for x in direction[n]) for n in arrays['heldNodeOrder']),'HELD_DIRECTION_PRESERVATION');close(sum(abs(x) for row in direction for x in row)*FORCE,WORK,1e-20)
 mesh=next(s for s in read(root/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if s['element_id']=='FJ1486');ids=mesh['elements_ten_node'][247];local_direction=[direction[n] for n in ids];stages={};original_receipt=read(root/'review/element247-shell-protocol-20261007/confirmation-preflight.json')
 for recipe,depth,count in RECIPES:
  points=d/(recipe+'-normalized-points.f64le');need(points.stat().st_size==48*count and digest(points)==digest(root/f'review/element247-shell-protocol-20261007/{recipe}-normalized-points.f64le'),'NORMALIZED_RULE_IDENTITY');normative=next(i for i in original_receipt['ruleInventories'] if i['recipe']['id']==recipe);shell_order=[f's{i}' for i in range(1,depth+1)]+['core']
  for state in ['control45','terminal46']:
   stage=read(d/f'{recipe}-{state}-assembly.json');need(stage['state']==state and stage['element']==247 and stage['recipe']==normative['recipe'] and stage['pointCount']==count and stage['originalShells']==shell_order,'COMPLETE_STAGE_SCOPE');need(stage['localShellFiles']==[f'{recipe}-{state}-{s}-shell.json' for s in shell_order],'ORIGINAL_SHELL_INVENTORY')
   locals_={t:zero(10) for t in TERMS};energies={t:0. for t in TERMS};global_={t:zero(585) for t in TERMS};groups=[{'shell':s,'originalShells':[],'localGradientsN':{t:zero(10) for t in TERMS},'energiesJ':{t:0. for t in TERMS}} for s in [f's{i}' for i in range(1,21)]+['core']];all_weights=b'';completed=0
   for shell,geometry in zip(shell_order,normative['perShell']):
    row=read(d/f'{recipe}-{state}-{shell}-shell.json');need(row['shell']==shell and row['element']==247 and row['pointCount']==geometry['points'] and row['lo']==geometry['lo'] and row['hi']==geometry['hi'] and row['comparisonShell']==geometry['comparisonShell'],'SHELL_GEOMETRY_COUNT');need(finite(row['minimumSampleJ']) and row['minimumSampleJ']>1e-6,'SHELL_DOMAIN');sum_check(row['localGradientsN'],row['energiesJ'],10)
    weights=(d/f'{recipe}-{state}-{shell}-weights.f64le').read_bytes();need(len(weights)==8*row['pointCount'] and all(finite(x[0]) and x[0]>0 for x in struct.iter_unpack('<d',weights)),'COMPLETE_POSITIVE_PHYSICAL_WEIGHTS');all_weights+=weights;completed+=row['pointCount'];group=next(g for g in groups if g['shell']==row['comparisonShell']);group['originalShells'].append(shell)
    for t in TERMS:
     close(dot(row['localGradientsN'][t],local_direction),row['terminalDirectionalDerivativesJ'][t]);energies[t]+=row['energiesJ'][t];group['energiesJ'][t]+=row['energiesJ'][t]
     for i,n in enumerate(ids):
      for k in range(3):v=row['localGradientsN'][t][i][k];locals_[t][i][k]+=v;global_[t][n][k]+=v;group['localGradientsN'][t][i][k]+=v
   need(completed==count,'COMPLETE_STAGE_POINT_COUNT');need(all_weights==(root/f'review/element247-shell-protocol-20261007/{recipe}-reference-weights.f64le').read_bytes(),'FROZEN_REFERENCE_WEIGHTS')
   need(stage['comparisonShells']==groups,'COMPLETE_COMPARISON_GROUPS');sum_check(stage['localGradientsN'],stage['energiesJ'],10);sum_check(stage['nodalGradientsN'],stage['energiesJ'],585);need(stage['reconstruction']['gates']=={'forceN':RECON_FORCE,'energyJ':RECON_ENERGY},'FROZEN_RECONSTRUCTION_GATES')
   for t in TERMS:
    vector(stage['nodalGradientsN'][t],585);vector(stage['localGradientsN'][t],10)
    close(stage['energiesJ'][t],energies[t],RECON_ENERGY);close(dot(stage['nodalGradientsN'][t],direction),stage['terminalDirectionalDerivativesJ'][t])
    for i in range(10):
     for k in range(3):close(stage['localGradientsN'][t][i][k],locals_[t][i][k],RECON_FORCE)
    for n in range(585):
     for k in range(3):close(stage['nodalGradientsN'][t][n][k],global_[t][n][k],RECON_FORCE)
   stages[(recipe,state)]=stage
 comparisons=read(d/'shell-vector-comparisons.json')['comparisons'];need([(c['state'],c['a'],c['b']) for c in comparisons]==[(s,a,b) for s in ['control45','terminal46'] for a,b in PAIRS],'COMPLETE_COMPARISON_INVENTORY');failed=[]
 for c in comparisons:
  A,B=stages[(c['a'],c['state'])],stages[(c['b'],c['state'])];need(c['required']==(c['a']!='C44'),'REQUIRED_COMPARISON_SCOPE');passes=[]
  for t in TERMS:
   entry=c['terms'][t];signed=zero(10);absolute=zero(10);work=0.;work_bound=0.;diffs=[]
   for a,b in zip(A['comparisonShells'],B['comparisonShells']):
    delta=[[a['localGradientsN'][t][i][k]-b['localGradientsN'][t][i][k] for k in range(3)] for i in range(10)];w=dot(delta,local_direction);work+=w;work_bound+=abs(w);diffs.append({'shell':a['shell'],'localDifferenceN':delta,'directionalDifferenceJ':w})
    for i in range(10):
     for k in range(3):signed[i][k]+=delta[i][k];absolute[i][k]+=abs(delta[i][k])
   need(entry['differences']==diffs and entry['aggregateDifferenceN']==signed and entry['absoluteShellDifferenceN']==absolute,'RETAINED_SIGNED_ABSOLUTE_DIFFERENCES');scattered=zero(585)
   for i,n in enumerate(ids):scattered[n]=signed[i].copy()
   need(entry['scatteredDifferenceN']==scattered,'ALL585_COMPARISON_SCATTER');maximum=max_abs(signed);triangle=max_abs(absolute)
   close(entry['aggregateInfinityN'],maximum,0);close(entry['shellTriangleInfinityN'],triangle,0);close(entry['aggregateDirectionalDifferenceJ'],abs(work));close(entry['shellTriangleDirectionalDifferenceJ'],work_bound);need(entry['forceGateN']==FORCE and entry['derivativeGateJ']==WORK,'UNCHANGED_COMPARISON_GATES')
   passed=maximum<=FORCE and triangle<=FORCE and abs(work)<=WORK and work_bound<=WORK;need(entry['pass']==passed,'COMPARISON_PASS_FLAG');passes.append(passed)
  need(c['pass']==all(passes),'ALL_COMPONENTS_TOTAL_PASS');
  if c['required'] and not c['pass']:failed.append({'state':c['state'],'a':c['a'],'b':c['b'],'terms':[t for t in TERMS if not c['terms'][t]['pass']]})
 expected_result='UNRESOLVED_ELEMENT247_SHELL_INTEGRATION' if failed else 'PASS_BOUNDED_ELEMENT247_METHOD_AGREEMENT';need(r['result']==expected_result and r['failedComparisons']==failed,'FINAL_NUMERICAL_RESULT')
 return {'result':'PASS_COMPLETE_ELEMENT247_SHELL_EVIDENCE_ARITHMETIC','numericalResult':expected_result,'independentReview':False,'materialCalls':0,'sourceCommit':r['sourceCommit'],'outputHashes':len(expected),'sourceHashes':len(r['sourceHashes']),'patchQualification':False,'limits':['Finite element247 method agreement only.','21-region checks do not exclude within-region/within-shell cancellation.','A55/X55 changes chart and core depth together.','Work consistency bounds are algebraically implied by force triangles.','Moment gate is barycentric degree2, not every quadratic Cartesian function.','Old16-element patch remains unresolved.']}
if __name__=='__main__':
 need(not sys.argv[1:],'Frozen retained invocation only; no alternate paths or budgets');root=pathlib.Path(__file__).resolve().parents[1];print(json.dumps(verify(root,root/'review/element247-shell-run-20261007'),indent=2))

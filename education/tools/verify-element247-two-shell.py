"""Frozen selective diagnostic arithmetic and reuse verification; no material imports."""
import json,pathlib,sys
from element247_shell_execution import need,read,digest,require_terminal_evidence,EvidenceFailure
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader,module_from_spec
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=spec_from_loader('retained_shell_arithmetic',SourceFileLoader('retained_shell_arithmetic',str(ROOT/'tools/verify-element247-shell.py')));base=module_from_spec(spec);spec.loader.exec_module(base)
TERMS=base.TERMS
BUDGET={'plannedMaterialCalls':4000,'maximumMaterialCalls':4000,'maximumWallSeconds':180,'nodeHeapMiB':1024,'maximumRssBytes':2147483648,'maximumOutputBytes':67108864,'invocations':1}
COMMAND=['node','--max-old-space-size=1024','tools/run-element247-two-shell.mjs','--execute']
SHELLS=[f's{i}' for i in range(1,21)]+['core']
OLD='review/element247-shell-run-20261007/material/'
PREF='review/element247-two-shell-preflight-20261007/'
def check_stage(rows,stage,ids,direction):
 need([r['shell'] for r in rows]==SHELLS,'ALL_21_REGIONS')
 local={t:base.zero(10) for t in TERMS};energies={t:0. for t in TERMS};global_={t:base.zero(585) for t in TERMS}
 for row in rows:
  need(row['element']==247 and row['pointCount']==(2000 if row['shell'] in ['s1','s2'] else 500),'EXACT_REGION_POINT_COUNTS');base.sum_check(row['localGradientsN'],row['energiesJ'],10)
  for t in TERMS:
   base.close(row['terminalDirectionalDerivativesJ'][t],base.dot(row['localGradientsN'][t],[direction[n] for n in ids]))
   energies[t]+=row['energiesJ'][t]
   for i,n in enumerate(ids):
    for d in range(3):local[t][i][d]+=row['localGradientsN'][t][i][d];global_[t][n][d]+=row['localGradientsN'][t][i][d]
 need(stage['pointCount']==13500 and stage['evaluatedPoints']==4000 and stage['reusedPoints']==9500,'CONSTRUCTED_VERSUS_EVALUATED_COUNTS')
 need(stage['localGradientsN']==local and stage['nodalGradientsN']==global_ and stage['energiesJ']==energies,'COMPLETE_CONSTRUCTED_RECONSTRUCTION');base.sum_check(global_,energies,585)
 need([r['shell'] for r in stage['comparisonShells']]==SHELLS,'COMPLETE_COMPARISON_REGION_ORDER')
 for old,new in zip(rows,stage['comparisonShells']):need(old['localGradientsN']==new['localGradientsN'] and old['energiesJ']==new['energiesJ'] and new['originalShells']==[old['shell']],'REGION_TO_CONSTRUCTED_IDENTITY')
 for t in TERMS:base.close(stage['terminalDirectionalDerivativesJ'][t],base.dot(global_[t],direction))
 need(stage['reconstruction']['gates']=={'forceN':1e-8,'energyJ':1e-9},'FROZEN_RECONSTRUCTION_GATES')
 component_force=max(abs(base.sequential_sum(global_[t][n][d] for t in TERMS[:-1])-global_['total'][n][d]) for n in range(585) for d in range(3));component_energy=abs(base.sequential_sum(energies[t] for t in TERMS[:-1])-energies['total'])
 base.close(stage['reconstruction']['component']['maximumForceDifferenceN'],component_force,0);base.close(stage['reconstruction']['component']['energyDifferenceJ'],component_energy,0)
 need(stage['reconstruction']['elementToGlobal']=={'maximumForceDifferenceN':0,'maximumEnergyDifferenceJ':0,'all585Nodes':True},'EXACT_ELEMENT_TO_GLOBAL_RECONSTRUCTION')
 return global_
def check_comparison(old_rows,new_rows,record,ids,direction,changed_only):
 wanted=['s1','s2'] if changed_only else SHELLS
 need([r['shell'] for r in old_rows]==[r['shell'] for r in new_rows]==wanted,'COMPARISON_REGION_INVENTORY')
 passes=[]
 for t in TERMS:
  aggregate=base.zero(10);absolute=base.zero(10);work=0.;work_triangle=0.;diffs=[]
  for a,b in zip(old_rows,new_rows):
   delta=[[a['localGradientsN'][t][i][d]-b['localGradientsN'][t][i][d] for d in range(3)] for i in range(10)];w=base.comparison_dot(delta,[direction[n] for n in ids]);work+=w;work_triangle+=abs(w);diffs.append({'shell':a['shell'],'localDifferenceN':delta,'directionalDifferenceJ':w})
   if not changed_only and a['shell'] not in ['s1','s2']:need(all(x==0 for row in delta for x in row),'REUSED_TAIL_DIFFERENCE_MUST_BE_ZERO')
   for i in range(10):
    for d in range(3):aggregate[i][d]+=delta[i][d];absolute[i][d]+=abs(delta[i][d])
  entry=record['terms'][t];scattered=base.zero(585)
  for i,n in enumerate(ids):scattered[n]=aggregate[i].copy()
  need(entry['differences']==diffs and entry['aggregateDifferenceN']==aggregate and entry['absoluteShellDifferenceN']==absolute and entry['scatteredDifferenceN']==scattered,'COMPLETE_SIGNED_TRIANGLE_SCATTER_COMPARISON')
  values={'aggregateInfinityN':base.max_abs(aggregate),'shellTriangleInfinityN':base.max_abs(absolute),'aggregateDirectionalDifferenceJ':abs(work),'shellTriangleDirectionalDifferenceJ':work_triangle}
  for k,v in values.items():base.close(entry[k],v,0)
  need(entry['forceGateN']==1e-5 and entry['derivativeGateJ']==5.492029235357012e-7,'FROZEN_COMPARISON_GATES')
  passed=values['aggregateInfinityN']<=1e-5 and values['shellTriangleInfinityN']<=1e-5 and abs(work)<=5.492029235357012e-7 and work_triangle<=5.492029235357012e-7;need(entry['pass']==passed,'TERM_PASS_FLAG');passes.append(passed)
 need(record['pass']==all(passes) and record['qualification'] is False,'DIAGNOSTIC_PASS_AND_NONQUALIFICATION')
 return all(passes)
def verify(root,directory):
 root=pathlib.Path(root);run=pathlib.Path(directory);d=run/'material';chain=require_terminal_evidence(run,budget=BUDGET,command=COMMAND);r=chain['completion'];m=read(root/'research/element247-two-shell-20261007-inputs.json');p=read(root/(PREF+'preflight.json'));auth=read(root/'research/element247-two-shell-authorization-20261007.json');review=read(root/(PREF+'independent-review.json'))
 need(r['result']=='UNRESOLVED_ELEMENT247_SHELL_INTEGRATION' and r['element247Qualification'] is False and r['patchQualification'] is False and r['priorPatchResult']=='UNRESOLVED_FIXED_PATCH_INTEGRATION','PRESERVE_UNRESOLVED_SCOPE')
 need(r['originalFailureN']==8.611662232570753e-5 and r['tailAgreementIsByConstruction'] is True and all(r[k]==0 for k in ['newNodalFields','nonlinearSolves','optimizerTrials','refits']),'ORIGINAL_FAILURE_AND_ZERO_NEW_FIELD_WORK')
 pref_files=['preflight.json','changed-normalized-points.f64le','changed-reference-weights.f64le','js-tests.log','python-tests.log','independent-review.json'];expected_sources=set(m['inputs'])|set(m['newSources'])|{PREF+n for n in pref_files}|{'research/element247-two-shell-authorization-20261007.json'}
 need(set(r['sourceHashes'])==expected_sources and set(p['sourceHashes'])==set(m['inputs'])|set(m['newSources']),'COMPLETE_SOURCE_INVENTORY')
 for name,h in r['sourceHashes'].items():need(not pathlib.Path(name).is_absolute() and '..' not in pathlib.Path(name).parts and digest(root/name)==h,'SOURCE_HASH:'+name)
 for name,h in p['sourceHashes'].items():need(r['sourceHashes'][name]==h,'PINNED_SOURCE:'+name)
 need(r['runnerSourceCommit']==p['sourceCommit']==auth['runnerSourceCommit']==review['sourceCommit'] and review['verdict']=='PASS','INDEPENDENTLY_REVIEWED_SOURCE');need(auth['authorized'] is True and auth['invocations']==1 and auth['parentThread']=='01a103c3-a2e6-7606-8c1e-06987ac710f1' and auth['budget']==m['budget']==p['budget']==BUDGET,'ONE_EXACT_4000_INVOCATION');need(auth['preflightSha256']==digest(root/(PREF+'preflight.json')) and auth['independentReviewSha256']==digest(root/(PREF+'independent-review.json')),'AUTHORIZATION_BINDINGS')
 names={'material-start.json','saved-arrays.json','changed-normalized-points.f64le','changed-reference-weights.f64le','reuse-manifest.json','constructed-normalized-points.f64le','constructed-reference-weights.f64le','constructed-assembly.json','changed-shell-comparison.json','constructed-whole-comparison.json'}
 for shell in SHELLS:names|={f'{"T24" if shell in ["s1","s2"] else "A55"}-terminal46-{shell}-shell.json',f'{"T24" if shell in ["s1","s2"] else "A55"}-terminal46-{shell}-weights.f64le'}
 need(set(r['outputInventory'])==names and {x.name for x in d.iterdir()}==names|{'completion-receipt.json','terminal-completion.json'},'EXACT_OUTPUT_INVENTORY')
 for name,item in r['outputInventory'].items():need((d/name).stat().st_size==item['bytes'] and digest(d/name)==item['sha256'],'OUTPUT_HASH:'+name)
 start=read(d/'material-start.json');need(start['sourceHashes']==r['sourceHashes'] and start['sourceCommit']==r['sourceCommit'] and start['runId']==r['runId'] and start['budget']==BUDGET and start['recipe']==m['recipe'] and start['material']==m['material'] and start['activation']==1,'MATERIAL_START_BINDING');need(start['authorizationSha256']==digest(root/'research/element247-two-shell-authorization-20261007.json'),'AUTHORIZATION_HASH')
 arrays=read(d/'saved-arrays.json');need(arrays==read(root/(OLD+'saved-arrays.json')),'EXACT_FROZEN_ARRAYS');direction=arrays['terminalDirectionM'];base.vector(direction,585);need(all(all(x==0 for x in direction[n]) for n in arrays['heldNodeOrder']),'HELD_DIRECTION_ZERO')
 source=next(s for s in read(root/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if s['element_id']=='FJ1486');ids=source['elements_ten_node'][247];old_rows=[read(root/(OLD+f'A55-terminal46-{s}-shell.json')) for s in SHELLS];rows=[read(d/f'{"T24" if s in ["s1","s2"] else "A55"}-terminal46-{s}-shell.json') for s in SHELLS]
 need((d/'changed-normalized-points.f64le').read_bytes()==(root/(PREF+'changed-normalized-points.f64le')).read_bytes(),'EXACT_REVIEWED_CHANGED_NODES');weights=(root/(PREF+'changed-reference-weights.f64le')).read_bytes();need((d/'changed-reference-weights.f64le').read_bytes()==weights and len(weights)==32000,'EXACT_REVIEWED_CHANGED_WEIGHTS')
 for i,s in enumerate(['s1','s2']):need((d/f'T24-terminal46-{s}-weights.f64le').read_bytes()==weights[i*16000:(i+1)*16000],'PER_SHELL_WEIGHT_IDENTITY')
 expected_reuse=[]
 for s in SHELLS[2:]:
  for suffix in ['shell.json','weights.f64le']:
   name=f'A55-terminal46-{s}-{suffix}';need((d/name).read_bytes()==(root/(OLD+name)).read_bytes(),'BYTE_EXACT_REUSED_REGION:'+name);expected_reuse.append({'source':OLD+name,'output':name,'sha256':digest(d/name),'bytes':(d/name).stat().st_size})
 need(read(d/'reuse-manifest.json')=={'regions':19,'reusedPoints':9500,'materialCalls':0,'byteExact':True,'files':expected_reuse},'EXACT_19_REGION_REUSE_MANIFEST')
 old_norm=(root/(OLD+'A55-normalized-points.f64le')).read_bytes();need((d/'constructed-normalized-points.f64le').read_bytes()==(d/'changed-normalized-points.f64le').read_bytes()+old_norm[2*500*48:],'EXACT_CONSTRUCTED_NORMALIZED_RULE');need((d/'constructed-reference-weights.f64le').read_bytes()==weights+b''.join((root/(OLD+f'A55-terminal46-{s}-weights.f64le')).read_bytes() for s in SHELLS[2:]),'EXACT_CONSTRUCTED_PHYSICAL_WEIGHTS')
 stage=read(d/'constructed-assembly.json');need(stage['recipe']==m['recipe'] and stage['qualification'] is False and stage['reusedTailAgreementIsByConstruction'] is True,'CONSTRUCTED_STAGE_SCOPE');check_stage(rows,stage,ids,direction)
 changed=read(d/'changed-shell-comparison.json');passed=check_comparison(old_rows[:2],rows[:2],changed,ids,direction,True);whole=read(d/'constructed-whole-comparison.json');check_comparison(old_rows,rows,whole,ids,direction,False);need(whole['reusedTailAgreementIsByConstruction'] is True,'WHOLE_TAIL_LIMIT')
 need(r['changedShellAssessment']==('PASS_CHANGED_SHELL_AGREEMENT' if passed else 'UNRESOLVED_CHANGED_SHELL_AGREEMENT') and r['evaluatedPoints']==4000 and r['reusedPoints']==9500 and r['constructedPoints']==13500 and r['reusedRegions']==19,'DIAGNOSTIC_RESULT')
 original=read(root/(OLD+'shell-vector-comparisons.json'));failure=next(c for c in original['comparisons'] if c['state']=='terminal46' and c['a']=='C55' and c['b']=='A55');need(failure['pass'] is False and failure['terms']['total']['shellTriangleInfinityN']==8.611662232570753e-5,'ORIGINAL_FAILURE_UNCHANGED')
 return {'result':'PASS_TWO_SHELL_RETAINED_EVIDENCE_ARITHMETIC','materialCalls':0,'changedShellAssessment':r['changedShellAssessment'],'element247Result':r['result'],'qualification':False,'sourceCommit':r['sourceCommit'],'sourceHashes':len(expected_sources),'outputHashes':len(names),'reusedRegions':19,'evaluatedCallbacks':4000,'constructedPoints':13500}
if __name__=='__main__':
 need(not sys.argv[1:],'Frozen run only');print(json.dumps(verify(ROOT,ROOT/'review/element247-two-shell-run-20261007'),indent=2))

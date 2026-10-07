"""Independent scalar-loop replay of stored selective vectors; never evaluates a law."""
import json,math,pathlib,sys
from element247_shell_execution import need,read,digest,require_terminal_evidence
from importlib import util
spec=util.spec_from_file_location('selective_launcher',pathlib.Path(__file__).with_name('launch-selective-fixed-patch.py'));launcher=util.module_from_spec(spec);spec.loader.exec_module(launcher)
ROOT=pathlib.Path(__file__).resolve().parents[1]
TERMS=['matrix','volume','passiveFiber','activePotential','total'];PATCH=[195,196,197,198,199,200,202,203,206,237,240,243,244,246,247,248];QUIET=[195,196,198,199,202,237,240,243,244];SECONDARY=[197,200,203,206,246,248];RESULTS={'PASS_BOUNDED_SELECTIVE_FIXED_PATCH_AGREEMENT','UNRESOLVED_FIXED_PATCH_INTEGRATION'}
OLD=ROOT/'review/fixed-field-integration-run-20261007';SHELL=ROOT/'review/element247-shell-run-20261007/material'
def close(a,b,tol=1e-8):
 need(isinstance(a,(int,float)) and isinstance(b,(int,float)) and math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol,'FINITE_REPLAY_DIFFERENCE')
def vectors(n):return {t:[[0.,0.,0.] for _ in range(n)] for t in TERMS}
def sum_rows(rows,ids,n=585):
 out=vectors(n);energy={t:0. for t in TERMS}
 for row in rows:
  need(row['element'] in range(252),'ELEMENT_INDEX')
  for t in TERMS:
   v=row['localGradientsN'][t];need(len(v)==10 and all(len(x)==3 for x in v),'TEN_NODE_VECTOR');close(row['energiesJ'][t],row['energiesJ'][t]);energy[t]+=row['energiesJ'][t]
   for i,node in enumerate(ids[row['element']]):
    for d in range(3):close(v[i][d],v[i][d]);out[t][node][d]+=v[i][d]
 return out,energy
def same_vectors(a,b):
 for t in TERMS:
  need(len(a[t])==len(b[t])==585,'ALL_585_NODES')
  for n in range(585):
   need(len(a[t][n])==len(b[t][n])==3,'THREE_COMPONENTS')
   for d in range(3):close(a[t][n][d],b[t][n][d])
def components(v,e):
 for n in range(585):
  for d in range(3):close(sum(v[t][n][d] for t in TERMS[:-1]),v['total'][n][d])
 close(sum(e[t] for t in TERMS[:-1]),e['total'],1e-9)
def check_comparison(c,units,ids,direction):
 need(c['units']==len(units),'UNIT_INVENTORY');passes=[]
 for t in TERMS:
  signed=[[0.,0.,0.] for _ in range(585)];triangle=[[0.,0.,0.] for _ in range(585)];work=0.;work_triangle=0.;saved=c['terms'][t];need(len(saved['differences'])==len(units),'DIFFERENCE_INVENTORY')
  for (name,a,b),row in zip(units,saved['differences']):
   need(row['id']==name and row['element']==a['element']==b['element'],'UNIT_IDENTITY');w=0.
   for i,node in enumerate(ids[a['element']]):
    for d in range(3):
     x=a['localGradientsN'][t][i][d]-b['localGradientsN'][t][i][d];close(row['localDifferenceN'][i][d],x);signed[node][d]+=x;triangle[node][d]+=abs(x);w+=x*direction[node][d]
   close(row['directionalDifferenceJ'],w,1e-9);work+=w;work_triangle+=abs(w)
  for n in range(585):
   for d in range(3):close(saved['aggregateDifferenceN'][n][d],signed[n][d]);close(saved['absoluteUnitDifferenceN'][n][d],triangle[n][d])
  values=[max(abs(x) for v in signed for x in v),max(x for v in triangle for x in v),abs(work),work_triangle]
  for k,value in zip(['aggregateInfinityN','unitTriangleInfinityN','aggregateDirectionalDifferenceJ','unitTriangleDirectionalDifferenceJ'],values):close(saved[k],value,1e-12)
  passed=values[0]<=1e-5 and values[1]<=1e-5 and values[2]<=5.492029235357012e-7 and values[3]<=5.492029235357012e-7;need(saved['pass'] is passed,'FALSE_TERM_PASS_FLAG');passes.append(passed)
 need(c['pass'] is all(passes),'FALSE_COMPARISON_PASS_FLAG');return all(passes)
def verify(directory):
 chain=require_terminal_evidence(directory,launcher.BUDGET,launcher.COMMAND,results=RESULTS);root=pathlib.Path(directory);mat=root/'material';pref=read(ROOT/'review/selective-fixed-patch-preflight-20261007/preflight.json');plan=read(ROOT/'review/selective-fixed-patch-preflight-20261007/storage-plan.json');completion=chain['completion']
 need(completion['runnerSourceCommit']==pref['sourceCommit'],'PREFLIGHT_SOURCE');need(completion['newCallbacks']==497500 and completion['reusedMeasurements']==4000 and completion['logicalRegions']==634,'EXACT_SCHEDULE');need(completion['originalTwoShellExecutionExit']==1 and completion['anatomicalQualification'] is False,'HISTORICAL_FAILURE_SCOPE')
 need(set(p.name for p in mat.iterdir())==set(plan['files']),'CLOSED_OUTPUT_FILE_INVENTORY')
 for name,cap in plan['files'].items():need((mat/name).stat().st_size<=cap,'FILE_BYTE_ENVELOPE')
 for name,record in completion['outputInventory'].items():need(digest(mat/name)==record['sha256'] and (mat/name).stat().st_size==record['bytes'],'OUTPUT_HASH')
 for p,h in completion['sourceHashes'].items():need(digest(ROOT/p)==h,'SOURCE_HASH')
 for name,h in pref['artifactHashes'].items():
  if name.endswith('.f64le'):need(digest(mat/name)==h,'POINT_OR_WEIGHT_HASH')
 arrays=read(mat/'saved-arrays.json');need(arrays==read(OLD/'saved-arrays.json'),'FROZEN_ARRAYS');source=next(x for x in read(ROOT/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if x['element_id']=='FJ1486');ids=source['elements_ten_node'];direction=arrays['terminalDirectionM'];required=[];regions=0
 for state in ['control45','terminal46']:
  baseline_rows=[read(OLD/f'U3-{state}-element-{e}-local.json') for e in range(252)];baseline,baseline_e=sum_rows(baseline_rows,ids);old_patch,old_e=sum_rows([x for x in baseline_rows if x['element'] in PATCH],ids);stages={}
  for r in pref['schedule']:
   e,key=r['element'],f"{r['element']}-{r['id']}";rows=[]
   for i in range(r['depth']+1):
    s='core' if i==r['depth'] else f's{i+1}';row=read(mat/f'{state}-{key}-{s}-region.json');need(row['shell']==row['id']==s and row['comparisonShell']==('core' if i>=20 else s),'SERIALIZED_REGION_IDENTITY');need(row['element']==e and row['pointCount']==125*r['radialParts']*r['angularParts']**2,'REGION_COUNT');rows.append(row);regions+=1
   stage=read(mat/f'{state}-{key}-stage.json');stages[key]=stage;actual,energy=sum_rows(rows,ids);expected,stage_e=sum_rows([stage],ids);same_vectors(actual,expected);components(actual,energy)
   for t in TERMS:close(energy[t],stage_e[t],1e-9)
   bins=stage['comparisonShells'];need([x['shell'] for x in bins]==[f's{i}' for i in range(1,21)]+['core'],'GROUPED_REGION_INVENTORY')
   for i,bin in enumerate(bins):
    selected=[x for x in rows if x['comparisonShell']==bin['shell']];need(bin['originalShells']==[x['shell'] for x in selected],'ORIGINAL_REGION_INVENTORY');bin['element']=e;v,en=sum_rows(selected,ids);bv,be=sum_rows([bin],ids);same_vectors(v,bv)
    for t in TERMS:close(en[t],be[t],1e-9)
   if state=='terminal46' and r['id']=='F44':
    for row in rows[:2]:
     retained=read(ROOT/f"review/element247-two-shell-run-20261007/material/T24-terminal46-{row['shell']}-shell.json")
     for k in ['element','pointCount','minimumSampleJ','localGradientsN','energiesJ']:need(row[k]==retained[k],'REUSED_MEASUREMENT_CHANGED')
  candidates={}
  for q in ['Q0','Q1','Q2']:
   c=read(mat/f'{state}-{q}-hybrid.json');candidates[q]=c;need(c['elementOrder']==PATCH and [x['element'] for x in c['localElements']]==PATCH,'PATCH_INVENTORY');v,en=sum_rows(c['localElements'],ids);same_vectors(v,c['patchNodalGradientsN']);same_vectors(baseline,c['baselineNodalGradientsN'])
   for e,row in zip(PATCH,c['localElements']):
    rule=({'Q0':'D4','Q1':'D5','Q2':'U5'} if e in QUIET else {'Q0':'C55','Q1':'A55','Q2':'D5'} if e in SECONDARY else {'Q0':'A55','Q1':'F44','Q2':'X44'})[q]
    expected=read(SHELL/f'A55-{state}-assembly.json') if e==247 and q=='Q0' else stages.get(f'{e}-{rule}') or read(OLD/f'{rule}-{state}-element-{e}-local.json')
    need(row['localGradientsN']==expected['localGradientsN'] and row['energiesJ']==expected['energiesJ'],'CANDIDATE_COMPOSITION')
   hybrid={t:[[baseline[t][n][d]-old_patch[t][n][d]+v[t][n][d] for d in range(3)] for n in range(585)] for t in TERMS};same_vectors(hybrid,c['hybridNodalGradientsN']);he={t:baseline_e[t]-old_e[t]+en[t] for t in TERMS};components(hybrid,he)
   for t in TERMS:close(en[t],c['patchEnergiesJ'][t],1e-9);close(he[t],c['hybridEnergiesJ'][t],1e-9)
  for a,b in [('Q0','Q1'),('Q1','Q2'),('Q0','Q2')]:
   units=[]
   for e in PATCH:
    if e==247 or (a=='Q0' and b=='Q1' and e in SECONDARY):
     def bins(q):
      rule={'Q0':'A55','Q1':'F44','Q2':'X44'}[q] if e==247 else {'Q0':'C55','Q1':'A55'}[q]
      value=read(SHELL/f'A55-{state}-assembly.json') if e==247 and q=='Q0' else stages[f'{e}-{rule}'];return value['comparisonShells']
     for ar,br in zip(bins(a),bins(b)):units.append((f"{e}-{ar['shell']}",{**ar,'element':e},{**br,'element':e}))
    else:units.append((f'{e}-whole',next(x for x in candidates[a]['localElements'] if x['element']==e),next(x for x in candidates[b]['localElements'] if x['element']==e)))
   c=read(mat/f'{state}-{a}-{b}-comparison.json');passed=check_comparison(c,units,ids,direction)
   if (a,b)!=('Q0','Q2'):required.append(passed)
  c=read(mat/f'{state}-F44-R44-comparison.json');required.append(check_comparison(c,[(f"247-{ar['shell']}",{**ar,'element':247},{**br,'element':247}) for ar,br in zip(stages['247-F44']['comparisonShells'],stages['247-R44']['comparisonShells'])],ids,direction))
 need(regions==634,'REGION_TOTAL');expected='PASS_BOUNDED_SELECTIVE_FIXED_PATCH_AGREEMENT' if all(required) else 'UNRESOLVED_FIXED_PATCH_INTEGRATION';need(completion['result']==expected,'FALSE_NUMERICAL_RESULT')
 return {'verdict':'PASS_OPERATIONAL_EVIDENCE_AND_REPLAY','result':expected,'specimenCalls':0,'replayedRegions':regions,'requiredComparisons':6,'anatomicalQualification':False}
if __name__=='__main__':need(len(sys.argv)==2,'Existing run directory required');print(json.dumps(verify(sys.argv[1]),indent=2))

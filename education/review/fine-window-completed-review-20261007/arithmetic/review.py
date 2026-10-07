"""Read only, standalone scalar/fsum review. No repository module imports.

This program reads serialized vectors and hashes immutable bytes. It neither
constructs quadrature nor imports or invokes geometry or physical-law code.
"""
import collections, hashlib, json, math, pathlib, subprocess, time

ROOT=pathlib.Path('/tmp/Kenoma-fine-window-material-run')
ED=ROOT/'education'; RUN=ED/'review/fine-window-run-20261007'; MAT=RUN/'material'
PREF=ED/'review/fine-window-preflight-20261007'
RAW=ED/'review/selective-fixed-patch-run-20261007/material'
OLD=ED/'review/fixed-field-integration-run-20261007'
SHELL=ED/'review/element247-shell-run-20261007/material'
OUT=pathlib.Path('/tmp/fine-window-completed-arithmetic-independent')
HEAD='5f7612f6c7f6609d8946b3394d7363609d7a30b1'
SOURCE='9611a4865e9591041fa5253c9df6c0f91da84089'
TERMS=['matrix','volume','passiveFiber','activePotential','total']
PATCH=[195,196,197,198,199,200,202,203,206,237,240,243,244,246,247,248]
QUIET=[195,196,198,199,202,237,240,243,244]
FOCUS=[197,200,203,206,246,247,248]
STATES=['control45','terminal46']
CANDIDATES=['S0','S1','S2','I0','I1','AR','AH','AC']
PAIRS=[('S0','S1',True),('S1','S2',True),('I0','I1',True),('S2','I1',True),('S1','AR',True),('S1','AH',True),('S1','AC',True),('S0','I0',False),('S1','I1',False)]
FORCE=1e-5; WORK=5.492029235357012e-7
checks=collections.Counter(); maximum=collections.defaultdict(float); cache={}; hashed={}

def need(value,label):
    checks[label]+=1
    if not value: raise AssertionError(label)

def close(a,b,tolerance,label):
    need(type(a) in (int,float) and type(b) in (int,float) and math.isfinite(a) and math.isfinite(b),'finite:'+label)
    error=abs(a-b); maximum[label]=max(maximum[label],error)
    need(error<=tolerance,label)

def read(path):
    path=pathlib.Path(path)
    if path not in cache:
        cache[path]=json.loads(path.read_text(),parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    return cache[path]

def digest(path):
    path=pathlib.Path(path)
    if path not in hashed:
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
        hashed[path]=h.hexdigest()
    return hashed[path]

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def validate_row(row):
    need(row['element'] in range(252),'row_element')
    need(set(row['localGradientsN'])==set(TERMS) and set(row['energiesJ'])==set(TERMS),'row_terms')
    for term in TERMS:
        v=row['localGradientsN'][term]
        need(len(v)==10 and all(len(x)==3 for x in v),'ten_by_three')
        for x in v:
            for y in x:need(type(y) in (int,float) and math.isfinite(y),'finite_local_force')
        need(math.isfinite(row['energiesJ'][term]),'finite_local_energy')
    for i in range(10):
        for d in range(3):close(math.fsum(row['localGradientsN'][t][i][d] for t in TERMS[:-1]),row['localGradientsN']['total'][i][d],1e-8,'local_component_force')
    close(math.fsum(row['energiesJ'][t] for t in TERMS[:-1]),row['energiesJ']['total'],1e-9,'local_component_energy')

def sum_rows(rows):
    lists={t:[[[] for d in range(3)] for n in range(585)] for t in TERMS}
    for row in rows:
        for t in TERMS:
            for i,n in enumerate(ids[row['element']]):
                for d in range(3):lists[t][n][d].append(row['localGradientsN'][t][i][d])
    v={t:[[math.fsum(xs) for xs in node] for node in lists[t]] for t in TERMS}
    energy={t:math.fsum(row['energiesJ'][t] for row in rows) for t in TERMS}
    return v,energy

def vector_match(a,b,label):
    need(set(b)==set(TERMS),'global_terms:'+label)
    for t in TERMS:
        need(len(a[t])==len(b[t])==585,'585_nodes:'+label)
        for n in range(585):
            need(len(b[t][n])==3,'three_axes:'+label)
            for d in range(3):close(a[t][n][d],b[t][n][d],1e-8,label)

def component_global(v,e,label):
    for n in range(585):
        for d in range(3):close(math.fsum(v[t][n][d] for t in TERMS[:-1]),v['total'][n][d],1e-8,'global_component_force:'+label)
    close(math.fsum(e[t] for t in TERMS[:-1]),e['total'],1e-9,'global_component_energy:'+label)

def metrics(units,term):
    sums=[[[] for d in range(3)] for n in range(585)]; works=[]; local=[]
    for name,a,b in units:
        dv=[[a['localGradientsN'][term][i][d]-b['localGradientsN'][term][i][d] for d in range(3)] for i in range(10)]
        products=[]
        for i,n in enumerate(ids[a['element']]):
            for d in range(3):sums[n][d].append(dv[i][d]);products.append(dv[i][d]*direction[n][d])
        w=math.fsum(products);works.append(w);local.append((name,a['element'],dv,w))
    signed=[[math.fsum(x) for x in row] for row in sums]
    triangle=[[math.fsum(abs(v) for v in x) for x in row] for row in sums]
    values=[max(abs(x) for row in signed for x in row),max(x for row in triangle for x in row),abs(math.fsum(works)),math.fsum(abs(x) for x in works)]
    return values,signed,triangle,local

def passed(values,force,work):return values[0]<=force and values[1]<=force and values[2]<=work and values[3]<=work

def compare(c,units):
    need(c['units']==len(units),'comparison_unit_count')
    need(c['differenceSign']=='a-minus-b' and c['qualification'] is False,'comparison_scope')
    result={}; passflags=[]
    for t in TERMS:
        values,signed,triangle,locals_=metrics(units,t);s=c['terms'][t]
        need(s['forceGateN']==FORCE and s['workGateJ']==WORK,'global_gates_exact')
        need(len(s['differences'])==len(units),'saved_unit_count')
        for saved,(name,e,dv,w) in zip(s['differences'],locals_):
            need(saved['id']==name and saved['element']==e,'saved_unit_identity')
            need(len(saved['localDifferenceN'])==10 and all(len(x)==3 for x in saved['localDifferenceN']),'saved_unit_shape')
            for i in range(10):
                for d in range(3):close(saved['localDifferenceN'][i][d],dv[i][d],1e-12,'local_difference')
            close(saved['directionalDifferenceJ'],w,1e-12,'local_work')
        for key,actual in [('aggregateDifferenceN',signed),('absoluteUnitDifferenceN',triangle)]:
            need(len(s[key])==585,'comparison_includes_held')
            for n in range(585):
                need(len(s[key][n])==3,'comparison_three_axes')
                for d in range(3):close(s[key][n][d],actual[n][d],1e-12,'comparison_'+key)
        for key,v in zip(['aggregateInfinityN','unitTriangleInfinityN','aggregateDirectionalDifferenceJ','unitTriangleDirectionalDifferenceJ'],values):close(s[key],v,1e-12,'comparison_metric')
        p=passed(values,FORCE,WORK);need(s['pass'] is p,'term_pass');passflags.append(p)
        result[t]={'signedN':values[0],'triangleN':values[1],'signedWorkJ':values[2],'triangleWorkJ':values[3],'globalPass':p}
    return all(passflags),result

def rule(q,e):
    if e in QUIET:return 'U4' if q=='I0' else 'U5' if q=='I1' else 'D5'
    if q=='S0':return 'A55'
    if q=='S1':return 'F44' if e==247 else 'P4'
    if q=='S2':return 'P8'
    if q=='AR':return 'R44' if e==247 else 'R4'
    return q if q in ['I0','I1'] else 'H4' if q=='AH' else 'C4'

def retained(state,e,r):
    if e in QUIET:return read(OLD/f'{r}-{state}-element-{e}-local.json')
    if e==247 and r=='A55':return read(SHELL/f'A55-{state}-assembly.json')
    return read(RAW/f'{state}-{e}-{r}-stage.json')

def stage_for(state,e,r):return stages.get((state,e,r)) or retained(state,e,r)

def pointcount(r,s):
    if r['kind']=='graded-affine-tetra':return 125*r['faceParts']**2*(1 if s=='core' else 3*r['radialParts'])
    return 125*r['radialParts']*r['angularParts']**2

started=time.monotonic()
need(git('rev-parse','HEAD')==HEAD,'frozen_head_start')
need(git('status','--porcelain')=='','clean_worktree_start')
pref=read(PREF/'preflight.json');plan=read(PREF/'storage-plan.json');completion=read(MAT/'completion-receipt.json')
need(pref['sourceCommit']==SOURCE and completion['runnerSourceCommit']==SOURCE,'runner_source')
need(digest(PREF/'preflight.json')=='61e25922d9f1d6474d6b1030c1af5491c42cf7468550923d24f79c74bf7388a8','accepted_preflight')
need(digest(PREF/'independent-review.json')=='64a5ef902aa58fc2e25e84741f233d3e984f33a16ce88f3d97140ead43f89e82','accepted_review')
need(set(p.name for p in MAT.iterdir())==set(plan['files']),'closed_material_inventory')
for name,cap in plan['files'].items():need((MAT/name).stat().st_size<=cap,'bounded_file')
need(set(completion['outputInventory'])==set(plan['files'])-{'completion-receipt.json','terminal-completion.json'},'complete_output_inventory')
for name,record in completion['outputInventory'].items():
    need(digest(MAT/name)==record['sha256'],'output_sha256');need((MAT/name).stat().st_size==record['bytes'],'output_bytes')
authpath=ED/'research/fine-window-authorization-20261007.json'
expected_sources=set(pref['sourceHashes'])|{str((PREF/p).relative_to(ED)) for p in ['preflight.json','independent-review.json',*pref['artifactHashes']]}|{str(authpath.relative_to(ED))}
need(set(completion['sourceHashes'])==expected_sources,'complete_source_inventory')
for name,h in completion['sourceHashes'].items():need(digest(ED/name)==h,'source_sha256')
for name,h in pref['sourceHashes'].items():need(completion['sourceHashes'][name]==h,'preflight_source_binding')
for name,h in pref['artifactHashes'].items():
    need(digest(PREF/name)==h,'preflight_artifact_sha256')
    if name.endswith('.f64le'):need(digest(MAT/name)==h,'actual_binary_sha256')
historical_paths=['education/review/selective-fixed-patch-run-20261007','education/review/selective-fixed-patch-outcome-20261007','education/review/element247-two-shell-run-20261007','education/research/selective-fixed-patch-authorization-20261007.json']
need(git('diff','--name-only','38ae8a2e2af57cf33254af987b724824b9d84357',HEAD,'--',*historical_paths)=='','original_failure_and_authorization_unchanged')
need(completion['originalResultCommit']=='38ae8a2e2af57cf33254af987b724824b9d84357' and completion['originalResult']=='UNRESOLVED_FIXED_PATCH_INTEGRATION' and completion['originalTwoShellExecutionExit']==1,'historical_failure_retained')
arrays=read(MAT/'saved-arrays.json');need(arrays==read(OLD/'saved-arrays.json'),'frozen_nodal_arrays')
need(arrays['patchElements']==PATCH,'patch16')
need(len(arrays['freeNodeOrder'])==495 and len(arrays['heldNodeOrder'])==90 and sorted(arrays['freeNodeOrder']+arrays['heldNodeOrder'])==list(range(585)),'free_and_held_partition')
direction=arrays['terminalDirectionM'];need(len(direction)==585 and all(len(x)==3 for x in direction),'frozen_direction585')
source=next(x for x in read(ED/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if x['element_id']=='FJ1486');ids=source['elements_ten_node']
need(len(ids)==252 and all(len(x)==10 for x in ids),'252_elements_ten_nodes')
stages={}; counts=collections.Counter(); reuse=collections.Counter()
for state in STATES:
    for r in pref['schedule']:
        e=r['element']; key=f'{e}-{r["id"]}';stage=read(MAT/f'{state}-{key}-stage.json')
        need(stage['recipe']==r and stage['state']==state and stage['element']==e,'stage_identity')
        need(len(stage['rowSources'])==r['depth']+1,'stage_complete_original_regions')
        rows=[];newpoints=0;sharedpoints=0
        for i,ref in enumerate(stage['rowSources']):
            s='core' if i==r['depth'] else f's{i+1}';cert=pref['regions'][f'{key}-{s}']
            need(ref['shell']==s,'original_region_order'); counts['logicalRegions']+=1
            sharing=(r['id']=='H4' or (r['id']=='C4' and e==247)) and i<20
            if sharing:
                iscurrent=r['id']=='H4' and e!=247;priorrule='P4' if iscurrent else 'F44' if r['id']=='H4' else 'X44';origin=MAT if iscurrent else RAW
                expected=f'{state}-{e}-{priorrule}-{s}-region.json';expectedstage=f'{state}-{e}-{priorrule}-stage.json'
                need(ref['name']==expected and ref['stageName']==expectedstage,'exact_reuse_name')
                need(ref['kind']==('same-invocation' if iscurrent else 'historical'),'reuse_kind')
                need(ref['earnsIndependentResolutionCredit'] is False and ref['identityMatches'] is True,'explicit_reuse_no_refinement_credit')
                need(digest(origin/expected)==ref['sha256'] and digest(origin/expectedstage)==ref['stageSha256'],'reuse_row_stage_hash')
                need(ref['normalizedSha256']==cert['normalizedSha256'] and ref['physicalSha256']==cert['physicalSha256'],'reuse_quadrature_identity')
                row=read(origin/expected);prior=read(origin/expectedstage)
                if iscurrent:
                    need(row['evaluationIdentity']==pref['evaluationIdentities'][state] and row['state']==state,'same_invocation_frozen_law_state')
                    need(prior['newCallbackPoints']==42000 and prior['reusedPoints']==0 and any(x['name']==expected and x['sha256']==ref['sha256'] for x in prior['rowSources']),'durable_P4_before_H4')
                else:need(ref['sha256']==cert['reuseRows'][state]['sha256'],'historical_certified_hash')
                counts['sharedRegions']+=1;counts['sharedLogicalMeasurements']+=pointcount(r,s);sharedpoints+=pointcount(r,s);reuse[priorrule]+=pointcount(r,s)
            else:
                expected=f'{state}-{key}-{s}-region.json';need(ref['name']==expected and ref['kind']=='new','new_row_identity')
                row=read(MAT/expected);need(digest(MAT/expected)==ref['sha256'] and (MAT/expected).stat().st_size==ref['bytes'],'new_row_hash_size')
                need(row['state']==state and row['recipeId']==r['id'] and row['evaluationIdentity']==pref['evaluationIdentities'][state],'new_state_material_law_identity')
                need(row['origin']=={'kind':'new','normalizedSha256':cert['normalizedSha256'],'physicalSha256':cert['physicalSha256']},'new_exact_quadrature_provenance')
                counts['newRegions']+=1;counts['newCallbacks']+=pointcount(r,s);newpoints+=pointcount(r,s)
            need(row['element']==e and row['id']==row['shell']==s,'row_identity')
            need(row['pointCount']==pointcount(r,s),'row_point_count')
            need(row['lo']==(0 if s=='core' else 2**(-i-1)) and row['hi']==(2**(-r['depth']) if s=='core' else 2**(-i)),'exact_region_bounds')
            need(row['comparisonShell']==('core' if i>=20 else s),'physical_bin_mapping')
            need(row['minimumSampleJ']==cert['minimumSampleJ'][state] and row['minimumSampleJ']>1e-6,'exact_accepted_minimum_J')
            validate_row(row)
            if 'terminalDirectionalDerivativesJ' in row:
                for t in TERMS:
                    actual=math.fsum(row['localGradientsN'][t][j][d]*direction[n][d] for j,n in enumerate(ids[e]) for d in range(3))
                    close(actual,row['terminalDirectionalDerivativesJ'][t],1e-12,'row_directional_derivative')
            rows.append(row)
        need(stage['pointCount']==r['points']==newpoints+sharedpoints and stage['newCallbackPoints']==newpoints and stage['reusedPoints']==sharedpoints,'stage_new_reuse_count')
        need(stage['minimumSampleJ']==min(x['minimumSampleJ'] for x in rows),'stage_minimum_J')
        validate_row(stage);actual,en=sum_rows(rows);sv,se=sum_rows([stage]);vector_match(actual,sv,'region_stage_force');component_global(actual,en,'stage')
        for t in TERMS:close(en[t],se[t],1e-9,'region_stage_energy')
        need([x['shell'] for x in stage['comparisonShells']]==[f's{j}' for j in range(1,21)]+['core'],'complete_21_physical_bins')
        for b in stage['comparisonShells']:
            selected=[x for x in rows if x['comparisonShell']==b['shell']];need(b['originalShells']==[x['shell'] for x in selected],'preserved_original_region_inventory')
            b={**b,'element':e};validate_row(b);v,en=sum_rows(selected);bv,be=sum_rows([b]);vector_match(v,bv,'original_physical_bin_force')
            for t in TERMS:close(en[t],be[t],1e-9,'original_physical_bin_energy')
        stages[state,e,r['id']]=stage
    print('replayed stages and regions',state,flush=True)

comparison_reports=[]; expected_completion=[]
for state in STATES:
    base_rows=[read(OLD/f'U3-{state}-element-{e}-local.json') for e in range(252)]
    for row in base_rows:validate_row(row)
    baseline,be=sum_rows(base_rows);oldpatch,oe=sum_rows([x for x in base_rows if x['element'] in PATCH]);candidates={}
    for q in CANDIDATES:
        c=read(MAT/f'{state}-{q}-hybrid.json');candidates[q]=c
        need(c['state']==state and c['candidate']==q and c['elementOrder']==PATCH and [x['element'] for x in c['localElements']]==PATCH,'exact_patch_candidate_inventory')
        for e,row in zip(PATCH,c['localElements']):
            expected=stage_for(state,e,rule(q,e));validate_row(row)
            for k in ['localGradientsN','energiesJ','pointCount']:need(row[k]==expected[k],'candidate_immutable_composition')
        pv,pe=sum_rows(c['localElements']);vector_match(pv,c['patchNodalGradientsN'],'patch_assembly');vector_match(baseline,c['baselineNodalGradientsN'],'unchanged_baseline')
        hybrid={t:[[baseline[t][n][d]-oldpatch[t][n][d]+pv[t][n][d] for d in range(3)] for n in range(585)] for t in TERMS}
        he={t:be[t]-oe[t]+pe[t] for t in TERMS};vector_match(hybrid,c['hybridNodalGradientsN'],'hybrid_once_only_replacement');component_global(hybrid,he,'hybrid')
        for t in TERMS:close(pe[t],c['patchEnergiesJ'][t],1e-9,'patch_energy');close(he[t],c['hybridEnergiesJ'][t],1e-9,'hybrid_energy')
        need(c['outsidePatchElements']==236 and c['outsidePatchQualified'] is False,'outside236_unqualified')
    for a,b,required in PAIRS:
        units=[]
        for e in PATCH:
            A=stage_for(state,e,rule(a,e));B=stage_for(state,e,rule(b,e))
            if e in QUIET:units.append((f'{e}-whole',A,B))
            else:
                for ar,br in zip(A['comparisonShells'],B['comparisonShells']):
                    need(ar['shell']==br['shell'],'matched_physical_regions');units.append((f'{e}-{ar["shell"]}',{**ar,'element':e},{**br,'element':e}))
        need(len(units)==156,'exact_156_comparison_units')
        c=read(MAT/f'{state}-{a}-{b}-comparison.json');need(c['state']==state and c['a']==a and c['b']==b and c['required'] is required,'comparison_identity')
        global_pass,term_report=compare(c,units);need(c['globalPass'] is global_pass,'global_pass')
        fractions={'quiet':.85 if (a,b)==('I0','I1') else .2,'focus':.15 if (a,b)==('I0','I1') else .8}; allocated=[];groups={}
        for label,es in [('quiet',QUIET),('focus',FOCUS)]:
            subset=[u for u in units if u[1]['element'] in es];saved=c['allocations'][label];force=fractions[label]*FORCE;work=fractions[label]*WORK
            close(saved['budget']['forceN'],force,1e-18,'frozen_allocated_force');close(saved['budget']['workJ'],work,1e-20,'frozen_allocated_work');flags=[];group_terms={}
            for t in TERMS:
                values,_,_,_=metrics(subset,t);p=passed(values,force,work);record=saved['metrics'][t]
                for k,v in zip(['signedN','triangleN','signedWorkJ','triangleWorkJ'],values):close(record[k],v,1e-12,'allocated_metric')
                need(record['pass'] is p,'allocated_term_pass');flags.append(p);group_terms[t]={'values':values,'pass':p}
            need(saved['pass'] is all(flags),'allocated_group_pass');allocated.append(all(flags));groups[label]={'forceN':force,'workJ':work,'terms':group_terms,'pass':all(flags)}
        common=[(f'{e}-whole',A,B) for e,A,B in zip(PATCH,candidates[a]['localElements'],candidates[b]['localElements'])]
        for t in TERMS:
            values,_,_,_=metrics(common,t)
            for k,v in zip(['signedN','triangleN','signedWorkJ','triangleWorkJ'],values):close(c['common16Diagnostic'][t][k],v,1e-12,'supplementary_common16')
        need(c['quietIdenticalReuseEarnsNoRefinementCredit'] is ((a,b) not in [('I0','I1'),('S2','I1')]),'quiet_reuse_does_not_earn_credit')
        overall=global_pass and all(allocated);need(c['pass'] is overall,'comparison_pass');expected_completion.append({'state':state,'a':a,'b':b,'required':required,'pass':overall})
        comparison_reports.append({'state':state,'a':a,'b':b,'required':required,'pass':overall,'globalPass':global_pass,'terms':term_report,'allocations':groups})
    for a,b in [('D4','D5'),('U4','U5'),('D5','U5')]:
        c=read(MAT/f'{state}-quiet-{a}-{b}-comparison.json');units=[(f'{e}-whole',retained(state,e,a),retained(state,e,b)) for e in QUIET]
        need(c['state']==state and c['a']==a and c['b']==b and c['required'] is True,'quiet_comparison_identity')
        g,terms=compare(c,units);fraction=.85 if a=='U4' else .2;force=fraction*FORCE;work=fraction*WORK
        close(c['allocatedForceN'],force,1e-18,'quiet_force_allocation');close(c['allocatedWorkJ'],work,1e-20,'quiet_work_allocation');flags=[]
        for t in TERMS:
            x=terms[t];p=passed([x['signedN'],x['triangleN'],x['signedWorkJ'],x['triangleWorkJ']],force,work);need(c['terms'][t]['allocatedPass'] is p,'quiet_term_allocated_pass');flags.append(p)
        overall=g and all(flags);need(c['pass'] is overall,'quiet_witness_pass');expected_completion.append({'state':state,'a':a,'b':b,'required':True,'pass':overall});comparison_reports.append({'state':state,'a':a,'b':b,'required':True,'pass':overall,'globalPass':g,'terms':terms,'allocatedForceN':force,'allocatedWorkJ':work})
    print('replayed hybrids and all comparisons',state,flush=True)

need(dict(counts)=={'logicalRegions':2002,'newRegions':1682,'newCallbacks':19716000,'sharedRegions':320,'sharedLogicalMeasurements':640000},'exact_new_and_retained_totals')
need(dict(reuse)=={'P4':480000,'F44':80000,'X44':80000},'separate_retained_attribution')
for k,v in counts.items():need(completion[k]==v,'completion_schedule_binding')
need(completion['comparisons']==expected_completion,'completion_all_comparison_bindings')
required=[x for x in comparison_reports if x['required']];informational=[x for x in comparison_reports if not x['required']]
need(len(required)==20 and len(comparison_reports)==24,'24_comparisons_20_required')
need([(x['state'],x['a'],x['b']) for x in required if not x['pass']]==[('terminal46','I0','I1')],'sole_required_failure')
need(completion['result']=='UNRESOLVED_FIXED_PATCH_INTEGRATION','unresolved_result_required')
need(completion['outsidePatchElements']==236 and completion['outsidePatchQualified'] is False and completion['anatomicalQualification'] is False,'unqualified_scope')
need(all(completion[k]==0 for k in ['newNodalFields','nonlinearSolves','optimizerTrials','refits']) and completion['unchangedStates'] is True,'unchanged_physical_scope')
for i,s in enumerate(['s1','s2']):
    original=read(ED/f'review/element247-two-shell-run-20261007/material/T24-terminal46-{s}-shell.json');ret=read(RAW/f'terminal46-247-F44-{s}-region.json')
    for k in ['element','pointCount','minimumSampleJ','localGradientsN','energiesJ']:need(original[k]==ret[k],'4000_failed_two_shell_measurements_preserved')
need(git('rev-parse','HEAD')==HEAD and git('status','--porcelain')=='','frozen_head_and_clean_worktree_end')
report={'verdict':'PASS_INDEPENDENT_RETAINED_ARITHMETIC_AND_PROVENANCE','frozenResultCommit':HEAD,'runnerSourceCommit':SOURCE,'preflightSha256':digest(PREF/'preflight.json'),'independentPreparationReviewSha256':digest(PREF/'independent-review.json'),'consumedAuthorizationSha256':digest(authpath),'completionSha256':digest(MAT/'completion-receipt.json'),'specimenCalls':0,'materialLawInvocations':0,'quadratureGenerationCalls':0,'method':'Standalone scalar loops using math.fsum; no repository imports, no execution or point generation. All global arrays include 585 nodes and all 90 held nodes.','counts':dict(counts),'reusedPointAttribution':dict(reuse),'stageCount':len(stages),'hybridCount':16,'comparisonCount':24,'requiredComparisons':20,'requiredPassed':sum(x['pass'] for x in required),'requiredFailed':sum(not x['pass'] for x in required),'informationalPassed':sum(x['pass'] for x in informational),'informationalFailed':sum(not x['pass'] for x in informational),'result':completion['result'],'outside236Qualified':False,'anatomicalQualified':False,'assertions':dict(checks),'totalAssertions':sum(checks.values()),'maximumReplayErrors':dict(maximum),'verifiedSourceInventoryEntries':len(completion['sourceHashes']),'verifiedOutputInventoryEntries':len(completion['outputInventory']),'uniqueHashedFiles':len(hashed),'elapsedSeconds':time.monotonic()-started,'comparisons':comparison_reports,'qualificationInterpretation':'S2/I1 finite agreement is verified. The failed terminal I0/I1 witness remains failed; it cannot be replaced by the passing cross-family comparison and no convergence or finite-patch qualification follows.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['verdict','totalAssertions','requiredPassed','requiredFailed','elapsedSeconds','counts','reusedPointAttribution','maximumReplayErrors']},indent=2))

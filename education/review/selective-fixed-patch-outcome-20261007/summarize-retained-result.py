"""Read-only outcome/report generation. No law imports or evaluations."""
import csv,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent;RUN=ROOT/'review/selective-fixed-patch-run-20261007';MAT=RUN/'material'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
completion=read(MAT/'completion-receipt.json');terminal=read(MAT/'terminal-completion.json');external=read(RUN/'external-exit.json');launcher=read(RUN/'launcher-exit.json');public=read(HERE/'public-entry-exit.json');verification=read(HERE/'frozen-verifier.log');auth=read(ROOT/'research/selective-fixed-patch-authorization-20261007.json')
assert verification['verdict']=='PASS_OPERATIONAL_EVIDENCE_AND_REPLAY';assert completion['result']==verification['result']=='UNRESOLVED_FIXED_PATCH_INTEGRATION';assert external['childExitCode']==launcher['launcherExitCode']==public['actualPublicEntryExitCode']==0
assert all(completion['runtime'][k]==497500 for k in ['reservedCalls','actualConstitutiveCallbacks','completedConstitutiveCallbacks']);assert completion['reusedMeasurements']==4000
for p in ['external-incomplete.json','supervisor-incomplete.json','material/incomplete-receipt.json']:assert not (RUN/p).exists()
comparisons=[];csvrows=[]
for state in ['control45','terminal46']:
 for pair in ['Q0-Q1','Q1-Q2','Q0-Q2','F44-R44']:
  c=read(MAT/f'{state}-{pair}-comparison.json');terms={}
  for t,v in c['terms'].items():
   values={k:v[k] for k in ['aggregateInfinityN','unitTriangleInfinityN','aggregateDirectionalDifferenceJ','unitTriangleDirectionalDifferenceJ','forceGateN','workGateJ','pass']};terms[t]=values;csvrows.append({'state':state,'comparison':pair,'required':c['required'],'units':c['units'],'term':t,**values})
  ranked=sorted(({'id':r['id'],'maximumLocalVolumeDifferenceN':max(abs(x) for v in r['localDifferenceN'] for x in v)} for r in c['terms']['volume']['differences']),key=lambda v:v['maximumLocalVolumeDifferenceN'],reverse=True)
  comparisons.append({'state':state,'a':c['a'],'b':c['b'],'required':c['required'],'units':c['units'],'pass':c['pass'],'failedTerms':[t for t,v in terms.items() if not v['pass']],'terms':terms,'largestVolumeComparisonUnits':ranked[:8],'source':f'material/{state}-{pair}-comparison.json','sourceSha256':sha(MAT/f'{state}-{pair}-comparison.json')})
bytes_total=sum(p.stat().st_size for p in RUN.rglob('*') if p.is_file());files_total=sum(p.is_file() for p in RUN.rglob('*'))
summary={'schema':1,'result':completion['result'],'acceptedStructuralHead':auth['acceptedReviewedHead'],'frozenRunnerSourceCommit':auth['runnerSourceCommit'],'frozenPreflightEvidenceCommit':auth['acceptedPreflightEvidenceCommit'],'executedSourceCommit':public['sourceCommit'],'runId':external['runId'],'authorizationSha256':sha(ROOT/'research/selective-fixed-patch-authorization-20261007.json'),'preflightSha256':auth['preflightSha256'],'independentStructuralReviewSha256':auth['independentReviewSha256'],'operationalCompletion':{'accepted':True,'invocations':1,'actualNewReservedCallbacks':497500,'actualNewEnteredCallbacks':497500,'actualNewCompletedCallbacks':497500,'reusedHistoricalMeasurements':4000,'historicalFailedRunExit':1,'actualChildExit':0,'actualWorkerExit':0,'observedPublicEntryExit':0,'externalLastAcceptanceElapsedSeconds':launcher['elapsedMs']/1000,'observedPublicEntryElapsedSeconds':public['elapsedSeconds'],'maximumObservedChildRssBytes':external['peakObservedChildRssBytes'],'childRuntimePeakRssBytes':completion['runtime']['peakObservedRssBytes'],'executionOutputBytes':bytes_total,'executionOutputFiles':files_total,'budget':auth['budget'],'incompleteOverrideAbsent':True,'retryAttempted':False},'readOnlyFrozenVerifier':verification,'numericalAssessment':{'requiredComparisons':6,'requiredPassed':sum(c['required'] and c['pass'] for c in comparisons),'requiredFailed':sum(c['required'] and not c['pass'] for c in comparisons),'allWorkGatesPassed':all(v['aggregateDirectionalDifferenceJ']<=v['workGateJ'] and v['unitTriangleDirectionalDifferenceJ']<=v['workGateJ'] for c in comparisons for v in c['terms'].values()),'failingRequiredComparisons':'Q0/Q1 at both fields; volume and total fail signed and unit-triangle force gates','informationOnly':'Q0/Q2 also fails volume/total force gates at both fields','forceGateN':1e-5,'workGateJ':5.492029235357012e-7,'reconstructionForceGateN':1e-8,'reconstructionEnergyGateJ':1e-9,'physicalStationarityGateN':1e-4,'physicalStationarityEstablished':False,'maximumStressComponentReconstructionErrorPa':completion['maximumStressReconstructionErrorPa']},'comparisons':comparisons,'limitations':['All16patch elements and585nodes includingheld are represented at both fixedfields.','236outsideelements keep exact retainedU3 contributions and remain unqualified.','Q1/Q2 and isolated247radial passes do not supersede failing requiredQ0/Q1 or any historical failure.','No analytic quadrature-error,continuum,equilibrium,tangent,displacement or anatomical acceptance.','No new fields,optimizer/refit,additionalquadrature,rescue or retry; no publication/book/main/deployment changes.','Frozen verifier specimenCalls0 describes read-only verification only; actual one-shot execution completed497500new specimen callbacks.']}
with (HERE/'result-summary.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
with (HERE/'comparison-metrics.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(csvrows[0]));w.writeheader();w.writerows(csvrows)
rows=['| Field | Comparison | Required | Total signed force (N) | Total unit triangle (N) | Result |','|---|---|---|---:|---:|---|']
for c in comparisons:
 v=c['terms']['total'];rows.append(f"|{c['state']}|{c['a']}/{c['b']}|{'yes' if c['required'] else 'informational'}|{v['aggregateInfinityN']:.12g}|{v['unitTriangleInfinityN']:.12g}|{'PASS' if c['pass'] else 'FAIL volume/total force'}|")
text=f'''# Selective fixed-patch specimen outcome

**Operational completion verified; numerical status UNRESOLVED_FIXED_PATCH_INTEGRATION.**
Exactly one authorized specimen run completed497500new reserved/entered/completed
callbacks. The4000 reused historical measurements remain separately attributed
to the original incomplete exit1 run, with no reinterpretation as new success.
Child/worker/observed public-entry exits were all0; final terminal hashes,
post-write limits and failure precedence passed the frozen independent scalar
replay. No retry, additional quadrature, optimizer, refit or rescue occurred.

Source/bindings:
- Accepted reviewed head: `{auth['acceptedReviewedHead']}`.
- Frozen runner source: `{auth['runnerSourceCommit']}`.
- Frozen preflight evidence: `{auth['acceptedPreflightEvidenceCommit']}`.
- Authorization commit: `dda7a9a0652b2b3284c0c1a0c0f1cdd6ca4b7166`.
- Executed source/observer commit: `{public['sourceCommit']}`.
- Run ID: `{external['runId']}`.
- Authorization SHA256: `{summary['authorizationSha256']}`.
- Preflight SHA256: `{auth['preflightSha256']}`.
- Independent structural review SHA256: `{auth['independentReviewSha256']}`.

Actual external acceptance time{launcher['elapsedMs']/1000:.6f}s under300s;
observed public entry{public['elapsedSeconds']:.6f}s. Peak externally observed
child RSS{external['peakObservedChildRssBytes']}B under2147483648B; Node heap
limit1024MiB. Execution root contains{files_total}files/{bytes_total}B under
67108864B. These are measurements of this single run, not timing guarantees.

## Every independent comparison

All5terms and all585nodes includingheld were checked at both fields.
Unchanged signed and unit-triangle force limits are1e-5N; work limits
5.492029235357012e-7J. Required Q0/Q1 uses156units, Q1/Q2 uses36units;
isolated247 F44/R44 uses21regions. Q0/Q2 is informational only.

'''+ '\n'.join(rows)+f'''

All work gates passed. Matrix, passiveFiber and activePotential passed every
force/work comparison. Volume and independently assembled total failed both
force checks for required Q0/Q1 at both fields; the informational Q0/Q2 also
failed those terms. Thus4of6required comparisons passed,2failed. Q1/Q2 and
isolated247 F44/R44 pass at both fields, but cannot remove the prescribed
Q0/Q1 failure or qualify the whole patch under this protocol.

The largest volume comparison units in Q0/Q1 are outer secondary-element
shells. Control206-s1/203-s1 differences are1.8428895039335202e-5N/
1.8394080314010353e-5N; terminal206-s1 is1.259785560137061e-4N. This is retained
finite arithmetic localization only; it authorizes no new recipe or evaluation.

[Full all5-term force/work metrics](comparison-metrics.csv) and
[exact result summary](result-summary.json) preserve all comparison values.
[Read-only frozen verifier output](frozen-verifier.log) passes634region,
local/group/full585scatter, candidate composition, hashes, resource envelopes,
held-node and component reconstructions. Its specimenCalls0 means verification
made no law calls; the actual execution made497500new specimen callbacks.

## Evidence and limitations

[Public-entry exit](public-entry-exit.json), [terminal child completion](../selective-fixed-patch-run-20261007/material/terminal-completion.json),
[observed worker acceptance](../selective-fixed-patch-run-20261007/launcher-exit.json)
and [raw file inventory](raw-execution-inventory.json) preserve the actual
process chain and byte identities. The raw invocation is retained separately
in [selective-fixed-patch-run-20261007](../selective-fixed-patch-run-20261007/).
No incomplete override is present; numerical failure remains distinct from
operational failure. Original full-patch/shell failures and consumed prior
authorization remain unchanged.

The236outsideelements retain exact oldU3 contributions and remain unqualified.
No analytic integration-error bound, continuum, equilibrium, tangent,
displacement or anatomical acceptance follows. No book/main/publication,
PR,merge,Pagescancellation,protection,credential or deployment change occurred.
The authorization is consumed; no further specimen execution is authorized.
'''
with (HERE/'README.md').open('x') as f:f.write(text)
inventory={str(p.relative_to(RUN)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(RUN.rglob('*')) if p.is_file()}
with (HERE/'raw-execution-inventory.json').open('x') as f:json.dump({'schema':1,'sourceCommit':public['sourceCommit'],'runId':external['runId'],'files':inventory,'combinedBytes':bytes_total,'fileCount':files_total},f,indent=2);f.write('\n')
print(json.dumps({'result':summary['result'],'operationalCompletion':summary['operationalCompletion'],'requiredPassed':4,'requiredFailed':2,'summarySha256':sha(HERE/'result-summary.json'),'rawInventorySha256':sha(HERE/'raw-execution-inventory.json')}))

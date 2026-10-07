#!/usr/bin/env python3
"""Final source/artifact/reuse closure of independent geometry; zero law or new geometry calls."""
import pathlib,json,subprocess,hashlib,sys,time
ROOT=pathlib.Path('/tmp/Kenoma-fine-window-runner');EDU=ROOT/'education';OUT=pathlib.Path('/tmp/fine-window-geometry-independent');PREF=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('/tmp/kenoma-fine-preflight-final-20261007')
EXPECTED='9611a4865e9591041fa5253c9df6c0f91da84089';HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();assert HEAD==EXPECTED
start=time.monotonic();assertions=0

def check(v,why):
 global assertions
 assertions+=1
 assert v,why

def digest_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()

raw=(PREF/'preflight.json').read_bytes();pref=json.loads(raw);check(pref['sourceCommit']==HEAD,'preflight source');check(pref['result']=='PASS_FINE_WINDOW_STRUCTURAL_PREFLIGHT_NO_SPECIMEN_CALLS','completed preflight');check(pref['specimenCalls']==pref['materialLawInvocations']==0,'zero laws');check(pref['executionAuthorized'] is False,'not execution authorized')
initial_map=json.loads((OUT/'implementation-map-review.json').read_text());initial_physical=json.loads((OUT/'implementation-physical-review.json').read_text())
for name in ['fine-window-maps.mjs','fine-window-protocol.mjs','fine-window-moments.mjs']:
 path='education/tools/'+name;actual=(ROOT/path).read_bytes();check(actual==subprocess.check_output(['git','cat-file','blob',HEAD+':'+path],cwd=ROOT),'finalsource blob');check(hashlib.sha256(actual).hexdigest()==initial_map['sourceHashes'][path],'independently reviewed geometry source unchanged')
for report in [initial_map,initial_physical]:
 for r in report['arrays']:
  p=PREF/r['filename'];check(p.stat().st_size==r['bytes'],'same finalactualarray length');h=digest_file(p);check(h==r['sha256'],'same independently reviewed binaryarray');check(pref['artifactHashes'][r['filename']]==h,'accepted binary closure')
for name,h in pref['artifactHashes'].items():
 p=PREF/name;check(p.is_file(),'preflightartifact exists');check(digest_file(p)==h,'preflightartifact hash');check(p.stat().st_size==pref['artifactBytes'][name],'preflightartifact bytes')
for p,h in pref['sourceHashes'].items():check(digest_file(EDU/p)==h,'preflightsource hash')
for key,r in pref['regions'].items():
 for origin,keysha in [(r['normalizedOrigin'],'normalizedSha256'),(r['weightOrigin'],'physicalSha256')]:
  p=(EDU/'review/selective-fixed-patch-run-20261007/material' if origin['kind']=='historical' else PREF)/origin['name'];check(digest_file(p)==r[keysha],'exact actual normalized/physical alias')
 for state,old in r['reuseRows'].items():check(digest_file(EDU/'review/selective-fixed-patch-run-20261007/material'/old['name'])==old['sha256'],'exact historical regionrow alias')
manifest=json.loads((EDU/'research/fine-window-runner-20261007-inputs.json').read_text());index=json.loads((EDU/'review/selective-fine-window-schedule-20261007/reuse-index.json').read_text())
check(manifest['executionAuthorized'] is False and manifest['parentPreparationAccepted'] is True,'scope authorization');check(len(index['files'])==1424,'retainedfile count');check(index['resultAnchor']=='38ae8a2e2af57cf33254af987b724824b9d84357','frozen result')
proc=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
try:
 for p,v in index['files'].items():
  data=(ROOT/p).read_bytes();check(len(data)==v['bytes'],'retained bytes');check(hashlib.sha256(data).hexdigest()==v['sha256'],'retained hash');proc.stdin.write((v['commit']+':'+p+'\n').encode());proc.stdin.flush();header=proc.stdout.readline().split();check(header[1]==b'blob' and int(header[2])==len(data),'exact immutable blob size');blob=proc.stdout.read(len(data));check(blob==data,'exact immutable retained blob');check(proc.stdout.read(1)==b'\n','git batch delimiter')
finally:proc.stdin.close();proc.stdout.close();proc.wait()
for p,h in manifest['immutableModuleHashes'].items():check(digest_file(EDU/p)==h,'unchanged physical/helpermodule')
check(pref['normalizedMomentChecks']==75096,'all normalized moments');check(pref['physicalMomentChecks']==15015,'all physical moments');check(pref['geometryPointChecks']==20356000,'all logical geometrypoints');check(pref['newPlannedCallbacks']==19716000,'frozencallback schedule');check((pref['logicalRegions'],pref['newRegions'],pref['sharedRegions'],pref['sharedLogicalPoints'])==(2002,1682,320,640000),'exact logical/reusecounts');check(pref['newBinaryBytes']==345840000,'binarypayload');check(pref['worstCaseCombinedOutputBytes']==448240000,'unchanged envelope');check(pref['outsidePatchElements']==236 and pref['outsidePatchQualified'] is False and pref['anatomicalQualification'] is False,'limits');check(pref['minimumSampleJ']>1e-6,'same physical guard');check(pref['tests']['fail']==0,'structural tests');check((EDU/'research/fine-window-authorization-20261007.json').exists() is False,'no executionauthorization');check((EDU/'review/fine-window-run-20261007').exists() is False,'no specimen run')
worst=json.loads((PREF/'synthetic-worst-serialization.json').read_text())
for name,v in worst.items():
 check(v['maximumFiniteNumberChars']==26,'conservative26numberbytes');check(v['conservativeBytes']==v['encodedBytes']+(0 if v['frozenBound'] else v['numericFields']),'26char algebra');check(v['conservativeBytes']<=v['capBytes'],'slot byteenvelope')
check(all(p in worst for p in ['material-start.json','provenance-inventory.json','completion-receipt.json','terminal-completion.json','incomplete-receipt.json']),'complete production/emergency shapes')
result={'schema':1,'status':'PASS_INDEPENDENT_FROZEN_GEOMETRY_PHYSICAL_WEIGHTS_AND_REUSE_CLOSURE','sourceCommit':HEAD,'preflightSha256':hashlib.sha256(raw).hexdigest(),'preflightDirectory':str(PREF),'specimenCalls':0,'materialLawInvocations':0,'newQuadratureGeneratedDuringRebind':False,'sourceEdits':0,'assertions':assertions,'seconds':time.monotonic()-start,'geometrySourceUnchangedFromIndependentInitialReview':True,'exactFinalArraysRebound':len(initial_map['arrays'])+len(initial_physical['arrays']),'exactImmutableReuseFiles':1424,'actualNormalizedPhysicalOriginHashChecks':2*len(pref['regions']),'allPreflightArtifactsVerified':len(pref['artifactHashes']),'independentChecks':{k:initial_map[k] for k in ['tetrahedraExactMetadataChecks','pointChecks','normalizedDegree5Checks','maximumIndependentCoordinateDifference','maximumIndependentRelativeWeightDifference','maximumActualNormalizedMomentRelativeError']},'independentPhysicalChecks':{k:initial_physical[k] for k in ['physicalMomentChecks','geometricStatePointChecks','maximumPhysicalMomentRelativeError','maximumIndependentRelativeWeightDifference','minimumReferenceJacobian','minimumPhysicalWeightM3','minimumSampleJ']},'completePreflightCounts':{k:pref[k] for k in ['normalizedMomentChecks','physicalMomentChecks','geometryPointChecks','newPlannedCallbacks','newBinaryBytes','worstCaseCombinedOutputBytes']},'serializationCorrection':'26 byte universal finite-number bound valid; actual production + emergency constructor shapes certified without changing any cap or physical gate','streamedMaximumRegionPoints':pref['preflightResourceEvidence']['streamedMaximumRegionPoints'],'preflightResourceEvidence':pref['preflightResourceEvidence'],'tests':pref['tests'],'independentArtifactHashes':{n:digest_file(OUT/n) for n in ['implementation-map-review.json','implementation-physical-review.json','implementation-assessment-initial.md']},'qualification':False,'outside236Qualified':False,'limits':['Geometry/structural evidence only, not nonlinear stress integration agreement','All frozen failed comparisons/result unchanged','No execution authorization or material calls','Outside236 U3 elements remain unqualified']}
(OUT/'implementation-final-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

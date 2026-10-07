import copy,hashlib,json,math,pathlib,subprocess,sys,unittest
R=pathlib.Path('/workspace/Kenoma-two-shell-reconstruction/education');RUN=R/'review/element247-two-shell-run-20261007';D=RUN/'material';OLD=R/'review/element247-shell-run-20261007/material';CAND=pathlib.Path('/tmp/kenoma-two-shell-reconstruction-final-candidate.json');HEAD='1671433376014ad148799e1ad7ff3f10219643f7';FAILED='9c9edbc9f3dd9729f2becc5215054897d139735e';SHELLS=[f's{i}' for i in range(1,21)]+['core'];TERMS=['matrix','volume','passiveFiber','activePotential','total'];FORCE=1e-5;WORK=5.492029235357012e-7
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();git=lambda *a:subprocess.check_output(['git',*a],cwd=R)
C=read(CAND);cand_sha=sha(CAND);raw_snapshot={str(p.relative_to(RUN)):sha(p) for p in RUN.rglob('*') if p.is_file()};arrays=read(D/'saved-arrays.json');direction=arrays['terminalDirectionM'];source=next(s for s in read(R/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if s['element_id']=='FJ1486');ids=source['elements_ten_node'][247];old_rows=[read(OLD/f'A55-terminal46-{s}-shell.json') for s in SHELLS];raw_rows=[read(D/f'{"T24" if s in ['s1','s2'] else "A55"}-terminal46-{s}-shell.json') for s in SHELLS];rows=copy.deepcopy(raw_rows)
for r in rows[:2]:r['shell']=r['id']
def zeros(n):return [[0.,0.,0.] for _ in range(n)]
def seqsum(v):
 s=0.
 for x in v:s+=x
 return s
def dot(v,u):return seqsum(seqsum(v[i][d]*u[i][d] for d in range(3)) for i in range(len(v)))
def flatdot(v,u):return seqsum(v[i][d]*u[i][d] for i in range(len(v)) for d in range(3))
def reconstructed(rows):
 local={t:zeros(10) for t in TERMS};global_={t:zeros(585) for t in TERMS};energy={t:0. for t in TERMS}
 for row in rows:
  for t in TERMS:
   energy[t]+=row['energiesJ'][t]
   for i,n in enumerate(ids):
    for d in range(3):local[t][i][d]+=row['localGradientsN'][t][i][d];global_[t][n][d]+=row['localGradientsN'][t][i][d]
 return local,global_,energy
energy_work={}
class IndependentReconstruction(unittest.TestCase):
 def test_exact_final_source_and_all_provenance(self):
  self.assertEqual(git('rev-parse','HEAD').decode().strip(),HEAD);self.assertEqual(git('status','--porcelain').decode().strip(),'');self.assertEqual(C['reconstructionSourceCommit'],HEAD);self.assertEqual(C['failedEvidenceCommit'],FAILED)
  subprocess.run(['git','merge-base','--is-ancestor',FAILED,HEAD],cwd=R,check=True)
  changes=C['provenance']['repairedSourceChanges'];self.assertEqual(set(changes),{'tools/element247-two-shell-runtime.mjs','tests/element247_two_shell.test.mjs'})
  self.assertEqual(len(C['provenance']['originalSourceHashes']),1598)
  for name,h in C['provenance']['originalSourceHashes'].items():
   self.assertEqual(hashlib.sha256(git('cat-file','blob',FAILED+':education/'+name)).hexdigest(),h,name)
   if name not in changes:self.assertEqual(sha(R/name),h,name)
   else:self.assertEqual(changes[name]['originalSha256'],h);self.assertEqual(changes[name]['repairedSha256'],sha(R/name))
  for name,item in C['provenance']['immutableInputInventory'].items():
   self.assertEqual((R/name).stat().st_size,item['bytes']);self.assertEqual(sha(R/name),item['sha256']);self.assertEqual(hashlib.sha256(git('cat-file','blob',FAILED+':education/'+name)).hexdigest(),item['sha256'])
  for name,item in C['provenance']['reconstructionSources'].items():self.assertEqual(sha(R/name),item['sha256']);self.assertEqual((R/name).stat().st_size,item['bytes']);self.assertEqual(hashlib.sha256(git('cat-file','blob',HEAD+':education/'+name)).hexdigest(),item['sha256'])
 def test_all_retained_raw_hashes_and_exact_tail_reuse(self):
  summary=read(R/'review/element247-two-shell-outcome-20261007/failure-summary.json');inc=read(D/'incomplete-receipt.json');self.assertEqual(len(summary['rawOutputInventory']),57);self.assertEqual(set(summary['rawOutputInventory']),set(raw_snapshot));self.assertEqual(len(inc['retainedFiles']),49)
  for name,item in summary['rawOutputInventory'].items():self.assertEqual(sha(RUN/name),item['sha256']);self.assertEqual((RUN/name).stat().st_size,item['bytes'])
  for name,item in inc['retainedFiles'].items():self.assertEqual(sha(D/name),item['sha256']);self.assertEqual((D/name).stat().st_size,item['bytes'])
  for s in SHELLS[2:]:
   for suffix in ['shell.json','weights.f64le']:self.assertEqual((D/f'A55-terminal46-{s}-{suffix}').read_bytes(),(OLD/f'A55-terminal46-{s}-{suffix}').read_bytes())
  reuse=read(D/'reuse-manifest.json');self.assertEqual(reuse['regions'],19);self.assertEqual(reuse['reusedPoints'],9500);self.assertEqual(reuse['materialCalls'],0);self.assertTrue(reuse['byteExact'])
  for item in reuse['files']:self.assertEqual(sha(R/item['source']),item['sha256']);self.assertEqual(sha(D/item['output']),item['sha256'])
 def test_metadata_only_schema_and_all_585_node_reconstruction(self):
  stage=C['constructedWholeValues'];self.assertEqual(stage['originalShells'],SHELLS);self.assertEqual(stage['pointCount'],13500);self.assertEqual(stage['evaluatedPoints'],4000);self.assertEqual(stage['reusedPoints'],9500)
  for i,r in enumerate(raw_rows[:2]):self.assertNotIn('shell',r);self.assertEqual(r['id'],SHELLS[i]);self.assertEqual({k:v for k,v in stage['comparisonShells'][i].items() if k not in ['shell','originalShells']},r)
  for raw,cooked in zip(rows,stage['comparisonShells']):self.assertEqual({k:v for k,v in cooked.items() if k!='originalShells'},raw);self.assertEqual(cooked['originalShells'],[raw['shell']])
  local,global_,energy=reconstructed(rows);self.assertEqual(stage['localGradientsN'],local);self.assertEqual(stage['nodalGradientsN'],global_);self.assertEqual(stage['energiesJ'],energy)
  self.assertEqual(len(arrays['heldNodeOrder']),90);self.assertEqual(len(arrays['freeNodeOrder']),495);self.assertEqual(set(arrays['heldNodeOrder'])|set(arrays['freeNodeOrder']),set(range(585)));self.assertTrue(all(direction[n]==[0,0,0] for n in arrays['heldNodeOrder']))
  local_dir=[direction[n] for n in ids]
  for row in rows:
   for t in TERMS:
    self.assertTrue(math.isfinite(row['energiesJ'][t]));self.assertTrue(all(math.isfinite(x) for v in row['localGradientsN'][t] for x in v));self.assertEqual(row['terminalDirectionalDerivativesJ'][t],dot(row['localGradientsN'][t],local_dir))
   self.assertLessEqual(max(abs(seqsum(row['localGradientsN'][t][i][d] for t in TERMS[:-1])-row['localGradientsN']['total'][i][d]) for i in range(10) for d in range(3)),1e-8);self.assertLessEqual(abs(seqsum(row['energiesJ'][t] for t in TERMS[:-1])-row['energiesJ']['total']),1e-9)
  for t in TERMS:self.assertEqual(stage['terminalDirectionalDerivativesJ'][t],dot(global_[t],direction));self.assertEqual(len(global_[t]),585)
  force=max(abs(seqsum(global_[t][n][d] for t in TERMS[:-1])-global_['total'][n][d]) for n in range(585) for d in range(3));e=abs(seqsum(energy[t] for t in TERMS[:-1])-energy['total']);self.assertEqual(stage['reconstruction']['component'],{'maximumForceDifferenceN':force,'energyDifferenceJ':e});self.assertLessEqual(force,1e-8);self.assertLessEqual(e,1e-9);self.assertEqual(stage['reconstruction']['elementToGlobal'],{'maximumForceDifferenceN':0,'maximumEnergyDifferenceJ':0,'all585Nodes':True})
 def test_independent_signed_absolute_force_and_work_all_terms(self):
  for selection,key in [(slice(0,2),'changedShellComparison'),(slice(None),'constructedWholeComparison')]:
   a=old_rows[selection];b=rows[selection];record=C[key];passed=[]
   for t in TERMS:
    signed=zeros(10);absolute=zeros(10);work=0.;bound=0.;diffs=[]
    for old,new in zip(a,b):
     delta=[[old['localGradientsN'][t][i][d]-new['localGradientsN'][t][i][d] for d in range(3)] for i in range(10)];w=flatdot(delta,[direction[n] for n in ids]);work+=w;bound+=abs(w);diffs.append({'shell':old['shell'],'localDifferenceN':delta,'directionalDifferenceJ':w})
     for i in range(10):
      for d in range(3):signed[i][d]+=delta[i][d];absolute[i][d]+=abs(delta[i][d])
     if old['shell'] not in ['s1','s2']:self.assertTrue(all(x==0 for row in delta for x in row))
    scattered=zeros(585)
    for i,n in enumerate(ids):scattered[n]=signed[i].copy()
    f=max(abs(x) for row in signed for x in row);tri=max(x for row in absolute for x in row);term=record['terms'][t]
    self.assertEqual(term['differences'],diffs);self.assertEqual(term['aggregateDifferenceN'],signed);self.assertEqual(term['absoluteShellDifferenceN'],absolute);self.assertEqual(term['scatteredDifferenceN'],scattered)
    self.assertEqual(term['aggregateInfinityN'],f);self.assertEqual(term['shellTriangleInfinityN'],tri);self.assertEqual(term['aggregateDirectionalDifferenceJ'],abs(work));self.assertEqual(term['shellTriangleDirectionalDifferenceJ'],bound);self.assertEqual(term['forceGateN'],FORCE);self.assertEqual(term['derivativeGateJ'],WORK)
    p=f<=FORCE and tri<=FORCE and abs(work)<=WORK and bound<=WORK;self.assertEqual(term['pass'],p);passed.append(p)
    energy_work.setdefault(key,{})[t]={'aEnergyJ':seqsum(row['energiesJ'][t] for row in a),'bEnergyJ':seqsum(row['energiesJ'][t] for row in b),'aDirectionalDerivativeJ':seqsum(row['terminalDirectionalDerivativesJ'][t] for row in a),'bDirectionalDerivativeJ':seqsum(row['terminalDirectionalDerivativesJ'][t] for row in b),'aggregateForceN':f,'triangleForceN':tri,'aggregateWorkJ':abs(work),'triangleWorkJ':bound}
   self.assertEqual(record['pass'],all(passed));self.assertFalse(record['qualification'])
 def test_original_refusal_authorization_no_qualification_or_new_call(self):
  sys.path.insert(0,str(R/'tools'));from element247_shell_execution import require_terminal_evidence,EvidenceFailure
  self.assertRaisesRegex(EvidenceFailure,'EXTERNAL_INCOMPLETE_TAKES_PRECEDENCE',require_terminal_evidence,RUN)
  for name in ['external-final.json','launcher-exit.json','material/completion-receipt.json','material/terminal-completion.json']:self.assertFalse((RUN/name).exists())
  self.assertFalse(C['operationalCompletion']);self.assertFalse(C['element247Qualification']);self.assertFalse(C['patchQualification']);self.assertEqual(C['authorizationStatus'],'CONSUMED_BY_ORIGINAL_ONE_SHOT; NO_RETRY_AUTHORIZATION');self.assertEqual(C['originalExitCodes'],{'child':1,'worker':1,'publicEntry':1})
  for k in ['newSpecimenCalls','newMaterialCalls','newQuadratureEvaluations','newNonlinearSolves','newFields','refits']:self.assertEqual(C[k],0)
  self.assertEqual(C['originalFailureN'],8.611662232570753e-5);self.assertEqual(C['priorPatchResult'],'UNRESOLVED_FIXED_PATCH_INTEGRATION');self.assertEqual(C['secondaryElementsUnresolved'],[197,200,203,206,246,248]);self.assertTrue(C['comparisonCoverage']['reuseFullyCoversDesiredArithmetic']);self.assertEqual(len(C['comparisonCoverage']['unavailable']),4)
  original=next(c for c in read(OLD/'shell-vector-comparisons.json')['comparisons'] if c['state']=='terminal46' and c['a']=='C55' and c['b']=='A55');self.assertFalse(original['pass']);self.assertEqual(original['terms']['total']['shellTriangleInfinityN'],8.611662232570753e-5)
  self.assertIn('not a cryptographically independent',C['publicExitEvidence']['authority'])
 def test_review_keeps_raw_candidate_and_source_unchanged(self):
  self.assertEqual(cand_sha,sha(CAND));self.assertEqual(raw_snapshot,{str(p.relative_to(RUN)):sha(p) for p in RUN.rglob('*') if p.is_file()});self.assertEqual(git('status','--porcelain').decode().strip(),'')
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IndependentReconstruction));report={'schema':1,'verdict':'PASS_RECONSTRUCTED_OFFLINE_ARITHMETIC_ONLY' if result.wasSuccessful() else 'FAIL','sourceCommit':HEAD,'candidatePath':str(CAND),'candidateSha256':cand_sha,'candidateBytes':CAND.stat().st_size,'failedEvidenceCommit':FAILED,'originalExecutedCommit':C['originalExecutedCommit'],'newSpecimenCalls':0,'newMaterialCalls':0,'newQuadratureEvaluations':0,'tests':{'pass':result.testsRun-len(result.failures)-len(result.errors),'fail':len(result.failures)+len(result.errors)},'originalSourceHashesVerified':1598,'immutableReadInventoryVerified':len(C['provenance']['immutableInputInventory']),'reconstructionModuleHashesVerified':len(C['provenance']['reconstructionSources']),'rawFileHashes':raw_snapshot,'retainedNumericalFilesVerified':49,'reusedRegions':19,'reusedPoints':9500,'arithmeticCoverage':'Complete changed-only and constructed21-region arithmetic for allfive terms, all585held/free nodes, energy/force sums and signed/absolute work; tail agreement is by byte-exact reuse','independentlyComputedEnergyWork':energy_work,'componentReconstruction':C['constructedWholeValues']['reconstruction'],'operationalCompletion':False,'element247Qualification':False,'patchQualification':False,'sourceReview':['Metadata helper adds shell=id, rejects conflicts and preserves numerical fields.','Runtime change applies only metadata helper around existing producer record; original arithmetic/callbacks/resource handling unchanged.','Actual serialized nonzero producer records now cross constructor boundary in synthetic test; deleting shell reproduces original rejection.','Offline reconstruction never invokes changedRule, assembly, RuntimeLimits.invoke or a constitutive evaluator; only retained-vector arithmetic.','Every immutable read equals failed-evidence Git blob and source modifications are separately hash-bound.','Original incomplete receipts/refusal chain and consumed one-shot authorization remain immutable.'],'limits':['PASS accepts offline candidate arithmetic only; original run remains incomplete with exits1.','No independent T24 tail evaluation, radial/chart/depth sensitivity, extra state/element, element/fullpatch or anatomical qualification.','The19-tail differences are zero by construction and give no independent refinement evidence.','Region triangles permit within-region cancellation; work bounds are implied algebraically by force bounds.','Public entry exit remains producer-retained executor tool evidence, not independently authenticated process observation.','Original8.611662232570753e-5N failure, fullpatch and secondary unresolved status persist.','Source/candidate emitted offline only; no retry/new authorization/source/raw mutation/publication by reviewer.']}
 pathlib.Path('/tmp/kenoma-two-shell-reconstruction-independent-review.json').write_text(json.dumps(report,indent=2)+'\n');sys.exit(0 if result.wasSuccessful() else 1)

/** Deterministic source/topology/span checks and labeled historical copies.
 * Does not evaluate constitutive energies/forces or invoke a nonlinear solve.
 */
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {prepareModalBody,modalPositions} from '../web/anatomical-modal.mjs';
import {meshPartition,originalFreeColumns,nestedFamily,projectScalar,projectVector,cartesianColumns,exactDyadicRank,dot,maxAbs} from './isolated-displacement-family.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),read=p=>JSON.parse(fs.readFileSync(root+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex');
const manifestPath='research/isolated-enrichment-protocol-20261006-inputs.json',manifest=read(manifestPath);
assert.equal(manifest.physical_force_gate_N,.0001);assert.equal(manifest.activation,1);assert.equal(manifest.paired_comparison_body_points_per_element,2048);
assert.equal(manifest.nonlinear_solves_authorized,false);assert.equal(manifest.force_rematching_authorized,false);
for(const [p,h] of Object.entries(manifest.inputs))assert.equal(hash(p),h,'Frozen input changed: '+p);
const sourceCommit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
const sources=[manifestPath,'tools/isolated-displacement-family.mjs','tools/check-isolated-enrichment-protocol.mjs','tests/isolated_displacement_family.test.mjs','research/isolated-enrichment-protocol-20261006.md'];
for(const p of sources)execFileSync('git',['ls-files','--error-unmatch',p],{cwd:root,stdio:'pipe'});
execFileSync('git',['diff','--exit-code','HEAD','--',...sources,...Object.keys(manifest.inputs)],{cwd:root,stdio:'pipe'});
const directory=root+'review/isolated-enrichment-protocol-20261006/';fs.mkdirSync(directory,{recursive:true});
if(fs.existsSync(directory+'structural-checks.json'))throw Error('Preserve completed structural evidence');
const diagnosis=read('review/isolated-calibration-resolution-20261006/results.json'),geometry=read('data/anatomical-arm-v1/generated/arm-reference.json'),fits=read('data/anatomical-arm-v1/audit/modal-fixed-end-results.json'),coupled=read('data/anatomical-arm-v1/audit/anatomical-further-integration.json'),prefix=read('data/anatomical-arm-v1/audit/anatomical-dense-loading-prefix.json');
assert.equal(diagnosis.qualifiedSourceCommit,manifest.diagnosis_qualified_source);
for(const [p,h] of Object.entries(diagnosis.sourceHashes))assert.equal(hash(p),h);
const near=(a,b,t)=>assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${a} vs ${b}`),rows=[],directions=[];
for(const fit of fits.records){
 const source=geometry.muscles.find(m=>m.element_id===fit.elementId),body=prepareModalBody(source),partition=meshPartition(source),original=originalFreeColumns(source,body.nodeModes,partition),family=nestedFamily(partition,original.columns),positions=modalPositions(body,Float64Array.from(fit.match.coordinatesM));
 const endpoints=[...fit.match.coordinatesM.slice(0,9),...fit.match.coordinatesM.slice(54)];assert.equal(endpoints.length,18);assert.ok(endpoints.every(v=>v===0));
 assert.equal(partition.free.length,495);assert.equal(partition.held.length,90);assert.equal(partition.capFaceCount,28);
 const vectorColumns=cartesianColumns(original.columns);
 const referenceRow=diagnosis.rows.find(r=>r.elementId===fit.elementId),finer=referenceRow.rules.find(r=>r.pointsPerElement===2048),resolution=finer.resolution;
 assert.deepEqual(resolution.freeNodes,partition.free);
 const g=Float64Array.from(resolution.retained,(v,k)=>v+resolution.omitted[k]),omitted=Float64Array.from(resolution.omitted),norm=Math.sqrt(dot(omitted,omitted)),direction=omitted.map(v=>-v/norm);
 assert.ok(norm>1);near(dot(direction,direction),1,1e-12);
 const maximumDotOriginalColumn=maxAbs(vectorColumns.map(c=>dot(c,direction)));assert.ok(maximumDotOriginalColumn<1e-11);
 const fullDirection=source.nodes_m.map(()=>[0,0,0]);partition.free.forEach((node,i)=>{fullDirection[node]=Array.from(direction.slice(3*i,3*i+3));});
 assert.ok(partition.held.every(n=>fullDirection[n].every(v=>v===0)));
 near(dot(g,direction),-norm,1e-9);
 let previous=null;const stages=[];
 for(const stage of family){
  assert.equal(stage.exactTailRank,stage.numericalTailRank);
  const columnPreservation=maxAbs(original.columns.map(c=>maxAbs(projectScalar(stage,partition,c).map((v,k)=>v-c[k]))));assert.ok(columnPreservation<1e-12);
  const v=Float64Array.from({length:1485},(_,i)=>Math.sin(i*.13)),Pv=projectVector(stage,partition,v),PPv=projectVector(stage,partition,Pv);
  const idempotence=maxAbs(PPv.map((x,k)=>x-Pv[k]));assert.ok(idempotence<1e-12);
  const nesting=previous?maxAbs(projectVector(stage,partition,previous).map((x,k)=>x-previous[k])):0;assert.ok(nesting<1e-12);previous=Pv;
  const selected=new Set(stage.selectedNodes),remaining=partition.free.flatMap((node,i)=>selected.has(node)?[]:[3*i,3*i+1,3*i+2]);
  const withDirection=exactDyadicRank([...vectorColumns,direction],remaining),augmentedDimension=3*stage.selectedNodes.length+withDirection.rank;
  const projectedDirection=projectVector(stage,partition,direction),outside=direction.map((v,k)=>v-projectedDirection[k]),outsideNorm=Math.sqrt(dot(outside,outside));
  assert.equal(augmentedDimension,stage.vectorDimension+(stage.level<4?1:0));
  if(stage.level<4)assert.ok(outsideNorm>1e-8);else near(outsideNorm,0,1e-12);
  stages.push({level:stage.level,name:stage.name,addedNodes:stage.addedNodes,selectedNodes:stage.selectedNodes,unaugmentedVectorDimension:stage.vectorDimension,exactOriginalTailRank:stage.exactTailRank,numericalOriginalTailRank:stage.numericalTailRank,exactOriginalTailPivotNodeRows:stage.exactTailPivotRows.map(i=>partition.free[i]),augmentedFrozenDryDirectionDimension:augmentedDimension,frozenDryDirectionOutsideNorm:outsideNorm,maximumOriginalColumnPreservationError:columnPreservation,maximumProjectorIdempotenceError:idempotence,maximumNestingError:nesting});
 }
 const endpointDifference=maxAbs(partition.held.flatMap(n=>positions[n].map((v,d)=>v-source.nodes_m[n][d])));
 rows.push({elementId:fit.elementId,activation:1,sigma0Pa:fit.match.sigma0Pa,endpointModalCoordinates:endpoints,freeNodes:partition.free.length,heldNodes:partition.held.length,vertices:partition.vertices.length,freeP2Vertices:partition.freeVertices.length,capAdjacentFreeMidpoints:partition.capAdjacentMidpoints.length,lateralFreeMidpoints:partition.lateralMidpoints.length,interiorFreeMidpoints:partition.interiorMidpoints.length,capFaces:partition.capFaceCount,lateralFaces:partition.lateralFaceCount,interiorFaces:partition.interiorFaceCount,rawOriginalCapCoefficients:original.capLeaks,maximumFrozenCapReferenceDifferenceM:endpointDifference,capVariationConvention:'All new admissible variations have exactly zero rows on explicit P2 caps. Original free columns preserved; literal raw cap leakage is disclosed, not silently treated as zero.',frozenDryDirection:{sourceRule:2048,source:'Existing frozen diagnosis only; production direction must be extracted from the reviewed same-quadrature 45-mode control, which has NOT been solved.',omittedGradientL2N:norm,maximumDotOriginalColumn:maximumDotOriginalColumn,energyDirectionalDerivativeN:dot(g,direction),exactFirstAugmentedDimension:stages[0].augmentedFrozenDryDirectionDimension},stages,historicalIsolatedRules:referenceRow.rules.map(r=>({pointsPerElement:r.pointsPerElement,metric:'Infinity norm over 1485 free nodal energy-gradient components, N',fullFreeNodalMaximumN:r.resolution.maximumFreeNodalComponentN,fullFreeNodalPass:r.resolution.passesUnchangedFullNodalGate,original45ModeProjectedMaximumN:r.legacyFreeResidualN,original45ModeProjectedPass:r.legacyPassesUnchangedGate,minimumCornerJ:r.minimumCornerJ,globalVolumeRatio:r.globalVolumeRatio,referenceVolumeSampledBelow09:r.referenceVolumeFractionBelow09,comparisonWithPrevious:r.comparisonWithPrevious,maximumComponentChangeOverForceGate:r.comparisonWithPrevious?r.comparisonWithPrevious.maximumFreeGradientChangeN/.0001:null}))});
 directions.push({elementId:fit.elementId,freeNodeOrder:partition.free,original2048FullFreeGradientN:Array.from(g),original2048NormalizedOmittedDescentDirection:Array.from(direction),scope:'Derived compact copy from frozen diagnosis; NOT a new force evaluation, solve or production 46-mode direction.'});
}
const metricClarification={schema:1,kind:'DOCUMENTED_SUCCESSOR_METRIC_CLARIFICATION',originalDiagnosisCommit:manifest.diagnosis_commit,originalDiagnosisSource:manifest.diagnosis_qualified_source,originalDiagnosisResultsSha256:hash('review/isolated-calibration-resolution-20261006/results.json'),originalCoupledEvidenceSha256:hash('data/anatomical-arm-v1/audit/anatomical-further-integration.json'),coupled2048ResidualN:coupled.frozenResidual2048N,coupled256ResidualN:coupled.baselineResidualN,coupledTimeS:coupled.timeS,coupledGeneralizedCoordinateCount:prefix.snapshots[3].coordinatesM.length,coupledMetric:'Infinity norm of the coupled generalized incremental-gradient vector, with higher-quadrature body contributions substituted into the existing coupled configuration gradient. The scaled joint coordinate includes inertia/gravity/stop/damping; other coupled potential terms remain. Not the 1485-component isolated free nodal maximum.',isolatedMetric:'Infinity norm of 1485 free P2 nodal energy-gradient components of one isolated fixed-cap body plus embedded sheets, at activation1; no coupled joint/contact/inertia.',conclusion:'Both STATE and METRIC differ. These residuals are not a same-metric convergence comparison. Their separate unchanged0.0001N gates remain failed.',noOriginalEvidenceModified:true};
fs.writeFileSync(directory+'metric-clarification.json',JSON.stringify(metricClarification,null,2)+'\n');
fs.writeFileSync(directory+'frozen-response-directions.json',JSON.stringify({sourceResultSha256:metricClarification.originalDiagnosisResultsSha256,directions})+'\n');
const result={schema:1,result:'PASS_DETERMINISTIC_ENRICHMENT_PROTOCOL_STRUCTURAL_CHECKS',qualifiedProtocolSourceCommit:sourceCommit,referenceDiagnosisCommit:manifest.diagnosis_commit,sourceHashes:Object.fromEntries([...Object.keys(manifest.inputs),...sources].map(p=>[p,hash(p)])),nonlinearSolves:0,constitutiveEvaluations:0,forceRematching:false,displacementStateAdvanced:false,pairedComparisonNotYetExecuted:true,bodyQuadratureForProposedPair:2048,unchangedForceGateN:.0001,rows,metricClarificationFile:'metric-clarification.json',frozenDirectionsFile:'frozen-response-directions.json',limits:['Structural rank is exact for the stored binary64 coefficients interpreted as dyadic rational numbers; numerical projectors are separately checked. No formal Lean/numerical equivalence certificate is claimed.','The residual-driven direction here is a structural dry example from an existing failed frozen pose. Future paired45/46 comparison requires a newly reviewed45-mode re-equilibration at the SAME quadrature before selecting and freezing its direction.','Finite nested spaces on one mesh end at fullP2; they do not establish spatial/continuum/quadrature convergence or monotone residual/compression/tangent behavior.','Original diagnosis, historical coupled evidence and all failed physical gates are retained unchanged. Protocol review is required before nonlinear execution.']};
fs.writeFileSync(directory+'structural-checks.json',JSON.stringify(result,null,2)+'\n');
for(const [p,h] of Object.entries(manifest.inputs))assert.equal(hash(p),h);
console.log(JSON.stringify({result:result.result,qualifiedProtocolSourceCommit:sourceCommit,nonlinearSolves:0,constitutiveEvaluations:0,rows:rows.map(r=>({elementId:r.elementId,unaugmentedDimensions:r.stages.map(s=>s.unaugmentedVectorDimension),frozenDryAugmentedDimensions:r.stages.map(s=>s.augmentedFrozenDryDirectionDimension),rawCapLeaks:r.rawOriginalCapCoefficients,maximumCapReferenceDifferenceM:r.maximumFrozenCapReferenceDifferenceM})),metricClarification},null,2));

/** Requested metrics on an already refused run. No optimizer, new trial,
 * force rematch or gate change. Invalid trial: geometry arithmetic only. */
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {prepareModalBody} from '../web/anatomical-modal.mjs';
import {evaluateCompressionBody} from './anatomical-compression-quadrature.mjs';
import {determinant} from '../web/anatomical-material.mjs';
import {exactElementOrientation} from './anatomical-bernstein-orientation.mjs';
import {meshPartition,originalFreeColumns,nestedFamily,projectVector,dot,maxAbs} from './isolated-displacement-family.mjs';
import {prepareResponseBody,addResponseDirection,responsePositions,evaluateResponse,cholesky,solveCholesky} from './isolated-projected-response.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),read=p=>JSON.parse(fs.readFileSync(root+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),directory=root+'review/isolated-brachialis-response-20261006/';
const resultPath='review/isolated-brachialis-response-20261006/results.json',run=read(resultPath),self='tools/summarize-isolated-brachialis-response.mjs';
assert.equal(run.result,'REFUSED_BOUNDED_RESPONSE');assert.equal(run.body,'FJ1486');assert.equal(run.physicalStateAdvanced,false);
execFileSync('git',['ls-files','--error-unmatch',self,resultPath],{cwd:root,stdio:'pipe'});execFileSync('git',['diff','--exit-code','HEAD','--',self,resultPath,...Object.keys(run.sourceHashes)],{cwd:root,stdio:'pipe'});
for(const [p,h] of Object.entries(run.sourceHashes))assert.equal(hash(p),h);
if(fs.existsSync(directory+'response-summary.json'))throw Error('Preserve existing refusal analysis');
const geometry=read('data/anatomical-arm-v1/generated/arm-reference.json'),source=geometry.muscles.find(m=>m.element_id===run.body),modal=prepareModalBody(source),partition=meshPartition(source),original=originalFreeColumns(source,modal.nodeModes,partition),family=nestedFamily(partition,original.columns);
const body=prepareResponseBody(source,modal,run.material,2048);addResponseDirection(body,run.direction.fullNodalVector);
const last=run.trace.filter(r=>r.label==='46-mode-response').at(-1),coordinates=Float64Array.from(last.coordinatesM),positions=responsePositions(body,coordinates),full=evaluateCompressionBody(body.prepared,positions,1,run.material),g=partition.free.flatMap(n=>full.nodalGradientN[n]);
const tangent=evaluateResponse(body,coordinates),H=tangent.hessianNPerM,H45=Float64Array.from({length:2025},(_,i)=>H[46*Math.floor(i/45)+i%45]),cross=Float64Array.from({length:45},(_,i)=>H[46*i+45]),curvature=H[2115],relaxed=curvature-dot(cross,solveCholesky(cholesky(H45,45),cross));
cholesky(H,46);assert.ok(curvature>0&&relaxed>0);
const norm=x=>Math.sqrt(dot(x,x)),retained=projectVector(family[0],partition,g),added=run.direction.freeVector.map(v=>v*dot(g,run.direction.freeVector)),omitted=g.map((v,k)=>v-retained[k]-added[k]);
const capSum=(a,nodes)=>nodes.reduce((s,n)=>s.map((v,d)=>v+a[n][d]),[0,0,0]);
function reactions(a,freeGradient){
 const answer={};
 for(const [name,nodes,base] of [['distal',source.distal_nodes,0],['proximal',source.proximal_nodes,54]]){
  assert.ok(nodes.every(n=>modal.nodeModes[n].filter(m=>m.base===base).reduce((s,m)=>s+m.value,0)===1));
  const nodal=a?capSum(a,nodes):(name==='distal'?run.control45.distalNodalGradientSumN:run.control45.proximalNodalGradientSumN),conjugate=nodal.slice();
  partition.free.forEach((n,i)=>{const weight=modal.nodeModes[n].filter(m=>m.base===base).reduce((s,m)=>s+m.value,0);for(let d=0;d<3;d++)conjugate[d]+=weight*freeGradient[3*i+d];});
  answer[name]={fullCapGradientSumN:nodal,fullCapAxialReactionN:-dot(nodal,source.basis.axis),originalBoundaryTranslationGradientN:conjugate,originalBoundaryTranslationAxialConjugateN:-dot(conjugate,source.basis.axis)};
 }
 return answer;
}
const certificates=source.elements_ten_node.map((ids,element)=>({element,...exactElementOrientation(ids.map(n=>source.nodes_m[n]),ids.map(n=>positions[n]))}));assert.ok(certificates.every(c=>c.orientationCertified));
fs.writeFileSync(directory+'last-valid46-orientation.json',JSON.stringify({label:'Last valid optimization iterate, not46-mode equilibrium',certificates})+'\n');
const partial={status:'LAST_VALID_46_MODE_OPTIMIZATION_ITERATE_NOT_EQUILIBRIUM',iteration:last.iteration,coordinatesM:Array.from(coordinates),positionsM:positions,fullFreeGradientN:g,projectedGradientN:Array.from(tangent.gradientN),projectedMaximumN:maxAbs(tangent.gradientN),fullFreeMaximumN:maxAbs(g),fullFreeL2N:norm(g),passesProjectedGate:maxAbs(tangent.gradientN)<=.0001,passesFullFreeGate:maxAbs(g)<=.0001,energyJ:full.energyJ,energiesJ:full.energies,minimumSampledJ:full.minimumJ,minimumCornerJ:full.minimumCornerJ,globalVolumeRatio:full.globalVolumeRatio,referenceVolumeSampledBelow09:full.referenceVolumeFractionBelow09,retainedOriginalForceL2N:norm(retained),addedDirectionForceN:dot(g,run.direction.freeVector),omitted46ForceL2N:norm(omitted),directCurvatureNPerM:curvature,relaxedCurvatureNPerM:relaxed,projectedTangentPositive:true,reactions:reactions(full.nodalGradientN,g),orientation:{elements:252,certifiedElements:252},additionalCoordinateM:coordinates[45]};
const controlReactions=reactions(null,run.control45.fullFreeGradientN);
const delta=partition.free.flatMap(n=>positions[n].map((v,d)=>v-run.control45.positionsM[n][d]));
const componentChanges=Object.fromEntries(Object.keys(full.energies).map(k=>[k,full.energies[k]-run.control45.energiesJ[k]]));
const comparison={sameRulePointsPerElement:2048,energyDifferenceJ:full.energyJ-run.control45.energyJ,componentEnergyChangesJ:componentChanges,linearVirtualWorkAt45ControlJ:dot(run.control45.fullFreeGradientN,delta),fullFreeMaximumChangeN:partial.fullFreeMaximumN-run.control45.fullFreeMaximumN,minimumCornerJChange:partial.minimumCornerJ-run.control45.minimumCornerJ,distalFullNodalReactionChangeN:partial.reactions.distal.fullCapAxialReactionN-controlReactions.distal.fullCapAxialReactionN,scope:'45-mode projected equilibrium versus the first valid46-mode optimization step. No46-mode equilibrium, physical calibration, integration or spatial convergence achieved.'};
const refused=run.refusals.find(r=>r.kind==='GEOMETRY_OR_DOMAIN_REFUSAL'),trial=responsePositions(body,Float64Array.from(refused.coordinatesM)),tensor=(X,G)=>Array.from({length:9},(_,k)=>X.reduce((s,v,i)=>s+v[Math.floor(k/3)]*G[i][k%3],0)),unqualified=[];
let sampledMinimum=Infinity,cornerMinimum=Infinity,certifiedCount=0;
for(const [element,e] of body.prepared.elements.entries()){
 const ids=e.nodes,X=ids.map(n=>trial[n]),certificate=exactElementOrientation(ids.map(n=>source.nodes_m[n]),X),cornerJs=e.corners.map(p=>determinant(tensor(X,p.gradient))),sampledJs=e.points.map(p=>determinant(tensor(X,p.gradient)));
 const sample=Math.min(...sampledJs),corner=Math.min(...cornerJs);sampledMinimum=Math.min(sampledMinimum,sample);cornerMinimum=Math.min(cornerMinimum,corner);
 if(certificate.orientationCertified)certifiedCount++;
 else unqualified.push({element,cornerJs,minimumSampledJ:sample,certificate,scope:'Negative Bernstein coefficient defeats this sufficient positivity certificate. It is not by itself a negative pointwise determinant witness.'});
}
assert.equal(certifiedCount,249);assert.equal(unqualified.length,3);
const refusedGeometry={kind:'UNCHANGED_EXACT_ORIENTATION_GATE_REFUSAL',trialCoordinatesM:refused.coordinatesM,trialPositionsM:trial,reason:refused.reason,certifiedElements:certifiedCount,unqualifiedElements:unqualified,minimumQueriedSampledJ:sampledMinimum,minimumQueriedCornerJ:cornerMinimum,constitutiveEvaluationOfRefusedTrial:false,nonlinearSolveRestarted:false,gateRelaxed:false,scope:'Geometry arithmetic on the stored refused trial only. Positive queried J cannot replace its failed whole-element sufficient certificate; no newly refined certificate or retry is introduced.'};
fs.writeFileSync(directory+'refused-trial-geometry.json',JSON.stringify(refusedGeometry,null,2)+'\n');
const record={schema:1,result:'PRESERVED_REFUSED_RESPONSE_WITH_REQUESTED_METRICS',analysisSourceCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),analysisSourceSha256:hash(self),runEvidenceCommit:'155dbefd088dbe6c0e3995692b0cec02c6384de2',runSourceCommit:run.sourceCommit,operatorSourceCommit:'0f0b33f68085159c7598e6b9f312c705979c763a',preflightSha256:run.preflightSha256,runResultsSha256:hash(resultPath),physicalStateAdvanced:false,nonlinearSolveRestarted:false,forceRematching:false,forceGateN:.0001,control45:{projectedMaximumN:run.control45.projectedMaximumN,fullFreeMaximumN:run.control45.fullFreeMaximumN,fullFreeL2N:run.control45.fullFreeL2N,energyJ:run.control45.energyJ,minimumCornerJ:run.control45.minimumCornerJ,reactions:controlReactions},partial46:partial,comparison,refusal:{certifiedElements:certifiedCount,unqualifiedElements:unqualified.map(r=>r.element),minimumQueriedSampledJ:sampledMinimum,minimumQueriedCornerJ:cornerMinimum,file:'refused-trial-geometry.json'},limits:['No46-mode equilibrium was completed. The one accepted optimization step and subsequent refusal are retained; no physical state was advanced.','All full free-node force gates remain failed against0.0001N. Lower potential or positive restricted tangent does not qualify the geometry, local compression or full displacement field.','The historical0.0173851553295N coupled460-coordinate incremental-gradient residual differs in both state and metric; it is not a free-nodal comparison.','Known256→2048 gradient changes remain far above the absolute gate. No quadrature, spatial/continuum convergence, physiological calibration or anatomical completion is claimed.']};
fs.writeFileSync(directory+'response-summary.json',JSON.stringify(record,null,2)+'\n');
for(const [p,h] of Object.entries(run.sourceHashes))assert.equal(hash(p),h);
console.log(JSON.stringify({result:record.result,source:record.analysisSourceCommit,control45:record.control45,partial46:{...partial,positionsM:undefined,fullFreeGradientN:undefined,projectedGradientN:undefined,coordinatesM:undefined},comparison,refusal:record.refusal},null,2));

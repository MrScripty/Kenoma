/** Complete paired rerun from original initialization; execute only after independent review.
 * Full-nodal physical failures remain failures regardless of projected solves. */
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {prepareModalBody,modalPositions} from '../web/anatomical-modal.mjs';
import {prepareIntramuscularAponeuroses} from '../web/anatomical-aponeurosis.mjs';
import {MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
import {evaluateCompressionBody} from './anatomical-compression-quadrature.mjs';
import {exactElementOrientation} from './anatomical-bernstein-orientation.mjs';
import {meshPartition,originalFreeColumns,nestedFamily,projectVector,cartesianColumns,exactDyadicRank,dot,maxAbs} from './isolated-displacement-family.mjs';
import {prepareResponseBody,addResponseDirection,responsePositions,responseNodeStep,evaluateResponse as originalEvaluateResponse,cholesky,solveCholesky} from './isolated-projected-response.mjs';
import {certifyState,checkedMaterialEvaluation,geometryBacktracking} from './isolated-geometry-backtracking.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),read=p=>JSON.parse(fs.readFileSync(root+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex');
const manifestPath='research/isolated-geometry-backtracking-20261006-inputs.json',manifest=read(manifestPath),mode=process.argv[2];
assert.equal(mode,'--execute','Only a complete paired rerun is implemented; structural preflight has a separate entry point');assert.equal(manifest.body,'FJ1486');assert.equal(manifest.points_per_element,2048);assert.equal(manifest.activation,1);assert.equal(manifest.physical_force_gate_N,.0001);
assert.equal(manifest.force_rematching,false);assert.equal(manifest.parameter_fitting,false);assert.deepEqual(manifest.only_pair_authorized,[45,46]);
assert.equal(manifest.solver.maximum_iterations,60);assert.equal(manifest.solver.projected_force_gate_N,.0001);assert.equal(manifest.solver.armijo_fraction,.0001);assert.equal(manifest.solver.maximum_nodal_step_m,.0002);assert.equal(manifest.solver.minimum_line_fraction,2**-20);assert.equal(manifest.solver.fractions,21);
const sources=[manifestPath,'tools/run-isolated-geometry-response.mjs','tools/isolated-geometry-backtracking.mjs','tools/preflight-isolated-geometry-backtracking.mjs','tests/isolated_geometry_backtracking.test.mjs','research/isolated-geometry-backtracking-20261006.md'];
for(const p of sources)execFileSync('git',['ls-files','--error-unmatch',p],{cwd:root,stdio:'pipe'});
execFileSync('git',['diff','--exit-code','HEAD','--',...sources,...Object.keys(manifest.inputs)],{cwd:root,stdio:'pipe'});
for(const [p,h] of Object.entries(manifest.inputs))assert.equal(hash(p),h,'Frozen source changed: '+p);
const sourceCommit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),sourceHashes=Object.fromEntries([...Object.keys(manifest.inputs),...sources].map(p=>[p,hash(p)]));
const structuralPath='review/isolated-geometry-backtracking-20261006/structural-preflight.json',structural=read(structuralPath);assert.equal(structural.result,'PASS_STRUCTURAL_ADMISSIBILITY_PREFLIGHT_NO_SOLVE');assert.equal(structural.constitutiveEvaluations,0);assert.equal(structural.nonlinearSolves,0);for(const [p,h] of Object.entries(structural.sourceHashes))assert.equal(hash(p),h,'Frozen structural source: '+p);execFileSync('git',['ls-files','--error-unmatch',structuralPath],{cwd:root,stdio:'pipe'});execFileSync('git',['diff','--exit-code','HEAD','--',structuralPath],{cwd:root,stdio:'pipe'});
const directory=root+'review/isolated-geometry-backtracking-20261006/';fs.mkdirSync(directory,{recursive:true});
const targetFile=directory+'results.json';if(fs.existsSync(targetFile))throw Error('Preserve existing response receipt');
const geometry=read('data/anatomical-arm-v1/generated/arm-reference.json'),fits=read('data/anatomical-arm-v1/audit/modal-fixed-end-results.json'),fit=fits.records.find(r=>r.elementId===manifest.body),source=geometry.muscles.find(m=>m.element_id===manifest.body),modal=prepareModalBody(source),partition=meshPartition(source),original=originalFreeColumns(source,modal.nodeModes,partition),family=nestedFamily(partition,original.columns),columns=cartesianColumns(original.columns),material={...MUSCLE_FIXTURE,sigma0:fit.match.sigma0Pa},initial=Float64Array.from(fit.match.coordinatesM.slice(9,54));
assert.equal(original.capLeaks.length,0);assert.equal(partition.free.length,495);assert.equal(partition.held.length,90);assert.equal(family[0].vectorDimension,45);
const sheets=prepareIntramuscularAponeuroses(modal);assert.equal(sheets.branches.length,0);assert.equal(sheets.matrix.length,0);
const base={schema:1,body:manifest.body,sourceCommit,sourceHashes,protocolPreflightCommit:manifest.protocol_preflight_commit,mode,started:new Date().toISOString(),node:process.version,pointsPerElement:2048,activation:1,material,unchangedForceGateN:.0001,solver:manifest.solver,forceRematching:false,parameterFitting:false,physicalStateAdvanced:false,newMesh:false,newAnatomy:false,sheets:{branches:0,matrix:0},originalFitForceN:fit.match.forceN,originalTargetN:fit.modelReference.value,structuralPreflightSha256:hash(structuralPath),structuralPreflightSourceCommit:structural.sourceCommit,originalInitializationM:Array.from(initial),archivedResponseEvidenceCommit:manifest.archived_response_commit,completePairedRerun:true};
const save=record=>fs.writeFileSync(targetFile,JSON.stringify(record,null,2)+'\n');let record={...base,result:'RUNNING_PREPARATION',trace:[],refusals:[],lineSearchEvents:[],materialGates:[]};save(record);
const near=(a,b,t,label)=>assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${label}: ${a} vs ${b}`);
let body;
function uncheckedMaterial(z,options={}){
 const result=originalEvaluateResponse(body,z,options);
 if(!Number.isFinite(result.energyJ)||!result.gradientN.every(Number.isFinite)||(result.hessianNPerM&&!result.hessianNPerM.every(Number.isFinite)))throw Error('Unexpected nonfinite material result after certification');
 return result;
}
function evaluateResponse(bodyArgument,z,options={}){
 assert.equal(bodyArgument,body);
 return checkedMaterialEvaluation({source,start:options.geometryAnchor??responsePositions(body,z),coordinates:z,positions:q=>responsePositions(body,q),evaluate:q=>uncheckedMaterial(q,options),onCertificate:certificate=>record.materialGates.push({purpose:options.geometryAnchor?'directional-probe':'current-state',certificate})});
}
function orientation(positions,retain=false){
 const certificates=source.elements_ten_node.map((ids,element)=>({element,...exactElementOrientation(ids.map(n=>source.nodes_m[n]),ids.map(n=>positions[n]))}));
 const certified=certificates.filter(c=>c.orientationCertified).length;
 if(certified!==certificates.length)throw Error('Unqualified exact P2 orientation '+certified+'/'+certificates.length);
 return {elements:certificates.length,certifiedElements:certified,...(retain?{certificates}:{})};
}
function audit(z,label,{writeOrientation=true}={}){
 const positions=responsePositions(body,z),geometryCheck=orientation(positions,true),domainPath=certifyState(source,positions);record.materialGates.push({purpose:'independent-full-body-audit',certificate:domainPath});
 const full=evaluateCompressionBody(body.prepared,positions,1,material),g=partition.free.flatMap(n=>full.nodalGradientN[n]),projected=columns.map(c=>dot(c,g));
 const cap=nodes=>nodes.reduce((s,n)=>s.map((v,d)=>v+full.nodalGradientN[n][d]),[0,0,0]);
 const distalGradient=cap(source.distal_nodes),proximalGradient=cap(source.proximal_nodes),reaction=nodes=>-dot(cap(nodes),source.basis.axis);
 const evaluated=evaluateResponse(body,z,{hessian:false});near(full.energyJ,evaluated.energyJ,1e-9,'Independent body energy');
 for(let k=0;k<45;k++)near(projected[k],evaluated.gradientN[k],2e-6,'Independent retained gradient');
 if(z.length===46)near(dot(partition.free.flatMap(n=>body.direction[n]),g),evaluated.gradientN[45],2e-6,'Independent added gradient');
 if(writeOrientation)fs.writeFileSync(directory+label+'-orientation.json',JSON.stringify({label,...geometryCheck})+'\n');
 return {label,coordinatesM:Array.from(z),positionsM:positions,fullFreeGradientN:g,original45GradientN:projected,addedGradientN:z.length===46?evaluated.gradientN[45]:null,original45MaximumN:maxAbs(projected),projectedMaximumN:maxAbs(evaluated.gradientN),fullFreeMaximumN:maxAbs(g),fullFreeL2N:Math.sqrt(dot(g,g)),passesFullFreeGate:maxAbs(g)<=.0001,energyJ:full.energyJ,energiesJ:full.energies,minimumSampledJ:full.minimumJ,minimumCornerJ:full.minimumCornerJ,globalVolumeRatio:full.globalVolumeRatio,referenceVolumeSampledBelow09:full.referenceVolumeFractionBelow09,distalNodalGradientSumN:distalGradient,proximalNodalGradientSumN:proximalGradient,distalAxialNodalReactionN:reaction(source.distal_nodes),proximalAxialNodalReactionN:reaction(source.proximal_nodes),allNodalGradientResultantN:full.nodalGradientN.reduce((s,v)=>s.map((x,d)=>x+v[d]),[0,0,0]),maximumCapReferenceDisplacementM:maxAbs(partition.held.flatMap(n=>positions[n].map((v,d)=>v-source.nodes_m[n][d]))),orientation:{elements:geometryCheck.elements,certifiedElements:geometryCheck.certifiedElements,file:writeOrientation?label+'-orientation.json':null,wholePathDomain:domainPath}};
}
function derivativeChecks(z,direction,exactGradient,exactHessian){
 const checks=[];
 for(const hM of [1e-7,5e-8]){
  const A=z.map((v,k)=>v+hM*direction[k]),B=z.map((v,k)=>v-hM*direction[k]);orientation(responsePositions(body,A));orientation(responsePositions(body,B));
  const plus=evaluateResponse(body,A,{hessian:false,geometryAnchor:responsePositions(body,z)}),minus=evaluateResponse(body,B,{hessian:false,geometryAnchor:responsePositions(body,z)});
  const forceFD=(plus.energyJ-minus.energyJ)/(2*hM),force=dot(exactGradient,direction),tangentFD=plus.gradientN.map((v,k)=>(v-minus.gradientN[k])/(2*hM)),Hv=Float64Array.from({length:z.length},(_,i)=>direction.reduce((s,v,k)=>s+exactHessian[i*z.length+k]*v,0)),tangentError=maxAbs(Hv.map((v,k)=>v-tangentFD[k])),scale=Math.max(1,maxAbs(Hv));
  near(forceFD,force,1e-4,'Potential directional derivative');assert.ok(tangentError<=.001+1e-6*scale,'Analytic tangent directional derivative');
  checks.push({hM,energyDirectionalDerivativeN:force,energyDifferenceDerivativeN:forceFD,errorN:forceFD-force,maximumTangentErrorNPerM:tangentError,relativeTangentError:tangentError/scale});
 }
 return checks;
}
function solve(start,label){
 let z=Float64Array.from(start);const solver=manifest.solver;
 for(let iteration=0;iteration<=solver.maximum_iterations;iteration++){
  console.log('EVALUATE',label,iteration,new Date().toISOString());
  const begin=performance.now(),r=evaluateResponse(body,z),maximum=maxAbs(r.gradientN),row={label,iteration,coordinatesM:Array.from(z),projectedGradientN:Array.from(r.gradientN),energyJ:r.energyJ,projectedMaximumN:maximum,minimumSampledJ:r.minimumSampledJ,minimumCornerJ:r.minimumCornerJ,evaluationSeconds:(performance.now()-begin)/1000};row.fullNodalAudit=audit(z,label+'-iteration-'+iteration,{writeOrientation:false});record.lastValidState=row.fullNodalAudit;record.trace.push(row);save(record);console.log('ITERATION',JSON.stringify({label,iteration,energyJ:row.energyJ,projectedMaximumN:maximum,fullFreeMaximumN:row.fullNodalAudit.fullFreeMaximumN,minimumSampledJ:row.minimumSampledJ,minimumCornerJ:row.minimumCornerJ}));
  const L=cholesky(r.hessianNPerM,z.length);row.projectedTangentPositive=true;save(record);
  if(maximum<=solver.projected_force_gate_N)return {z,r,iterations:iteration};
  if(iteration===solver.maximum_iterations)throw Error('Projected solve iteration ceiling '+label);
  const raw=solveCholesky(L,r.gradientN.map(v=>-v));
  const accepted=geometryBacktracking({source,currentCoordinates:z,currentEnergyJ:r.energyJ,gradientN:r.gradientN,rawNewtonCoordinates:raw,positions:q=>responsePositions(body,q),nodeStep:q=>responseNodeStep(body,q),evaluate:q=>uncheckedMaterial(q,{hessian:false}),onEvent:event=>{record.lineSearchEvents.push({label,iteration,...event});if(event.disposition==='REJECTED'||event.disposition==='FAILURE')record.refusals.push({label,iteration,...event});save(record);}});
  row.acceptedLineFraction=accepted.alpha;row.predictedSlopeJ=accepted.slope;row.acceptedEnergyChangeJ=accepted.state.energyJ-r.energyJ;row.newtonDirection=accepted.direction;z=accepted.coordinates;save(record);
 }
}
try{
 console.log('PREPARE',mode,new Date().toISOString());body=prepareResponseBody(source,modal,material,2048);
 const originalPositions=modalPositions(modal,Float64Array.from(fit.match.coordinatesM));assert.deepEqual(responsePositions(body,initial),originalPositions);
 {
  const preflightPath='review/isolated-brachialis-response-20261006/preflight.json',preflight=read(preflightPath);assert.equal(preflight.result,'PASS_FROZEN_RESPONSE_PREFLIGHT_NO_NONLINEAR_SOLVE');
  execFileSync('git',['ls-files','--error-unmatch',preflightPath],{cwd:root,stdio:'pipe'});execFileSync('git',['diff','--exit-code','HEAD','--',preflightPath],{cwd:root,stdio:'pipe'});
  for(const [p,h] of Object.entries(preflight.sourceHashes))assert.equal(hash(p),h);
  record.preflightSourceCommit=preflight.sourceCommit;record.preflightSha256=hash(preflightPath);record.frozenOriginal=preflight.frozenOriginal;record.result='RUNNING_SAME_RULE_45_MODE_CONTROL';save(record);
  const archived=read('review/isolated-brachialis-response-20261006/results.json');assert.deepEqual(initial,Float64Array.from(archived.frozenOriginal.coordinatesM));
  const control=solve(initial,'45-mode-control');record.control45=audit(control.z,'control45');save(record);assert.deepEqual(Array.from(control.z),archived.control45.coordinatesM,'Control changed: preserve refusal before46 stage');assert.deepEqual(record.control45.positionsM,archived.control45.positionsM,'Control field changed');
  const g=record.control45.fullFreeGradientN,retained=projectVector(family[0],partition,g),omitted=g.map((v,k)=>v-retained[k]),norm=Math.sqrt(dot(omitted,omitted));assert.ok(norm>1e-8,'No omitted direction to add');
  const recomputed=omitted.map(v=>-v/norm),direction=archived.direction.freeVector.slice(),fullDirection=archived.direction.fullNodalVector.map(v=>v.slice());assert.deepEqual(archived.direction.freeNodeOrder,partition.free);assert.ok(maxAbs(direction.map((v,k)=>v-recomputed[k]))<1e-12,'Frozen direction no longer matches same-rule control');
  near(dot(direction,direction),1,1e-12,'Added unit direction');assert.ok(maxAbs(columns.map(c=>dot(c,direction)))<1e-11);assert.equal(exactDyadicRank([...columns,direction],Array.from({length:1485},(_,i)=>i)).rank,46);
  addResponseDirection(body,fullDirection);const start=Float64Array.from([...control.z,0]);assert.deepEqual(responsePositions(body,start),record.control45.positionsM);
  console.log('PRODUCTION_DIRECTION_TANGENT',new Date().toISOString());const augmented=evaluateResponse(body,start),unit=new Float64Array(46);unit[45]=1;
  record.direction={rule:'Exact archived once-selected normalized negative omitted gradient; same-rule45 control required byte-identical before use.',archivedDirectionSha256:hash('review/isolated-brachialis-response-20261006/results.json'),freeNodeOrder:partition.free,freeVector:direction,fullNodalVector:fullDirection,rank:46,maximumOriginalDot:maxAbs(columns.map(c=>dot(c,direction))),norm:Math.sqrt(dot(direction,direction)),omittedGradientNormN:norm,actualEnergyDerivativeN:augmented.gradientN[45],expectedEnergyDerivativeN:dot(g,direction),initialCurvatureNPerM:augmented.hessianNPerM[46*45+45],derivativeChecks:derivativeChecks(start,unit,augmented.gradientN,augmented.hessianNPerM)};near(augmented.gradientN[45],dot(g,direction),2e-6,'Added gradient assembly');save(record);
  const H45=Float64Array.from({length:45*45},(_,i)=>augmented.hessianNPerM[46*Math.floor(i/45)+i%45]),cross=Float64Array.from({length:45},(_,i)=>augmented.hessianNPerM[46*i+45]);
  record.direction.initialRelaxedCurvatureNPerM=record.direction.initialCurvatureNPerM-dot(cross,solveCholesky(cholesky(H45,45),cross));save(record);
  if(!(record.direction.initialCurvatureNPerM>0&&record.direction.initialRelaxedCurvatureNPerM>0))throw Error('Unstable added-direction tangent response');
  record.result='RUNNING_SAME_RULE_46_MODE_RESPONSE';save(record);const enriched=solve(start,'46-mode-response');record.response46=audit(enriched.z,'response46');
  record.direction.finalCurvatureNPerM=enriched.r.hessianNPerM[46*45+45];record.direction.finalDerivativeChecks=derivativeChecks(enriched.z,unit,enriched.r.gradientN,enriched.r.hessianNPerM);
  if(!(record.direction.finalCurvatureNPerM>0))throw Error('Unstable final added-direction curvature');
  record.comparison={sameRulePoints:2048,energyDifferenceJ:record.response46.energyJ-record.control45.energyJ,fullFreeMaximumChangeN:record.response46.fullFreeMaximumN-record.control45.fullFreeMaximumN,minimumCornerJChange:record.response46.minimumCornerJ-record.control45.minimumCornerJ,distalAxialReactionChangeN:record.response46.distalAxialNodalReactionN-record.control45.distalAxialNodalReactionN,additionalCoordinateM:enriched.z[45],scope:'One45/46 response at identical2048-point potential; no spatial, quadrature, stability or physiological convergence claim.'};
  record.result='COMPLETED_PAIRED_PROJECTED_RESPONSE_FULL_PHYSICAL_GATES_RETAINED';record.nonlinearSolves=2;record.fullPhysicalQualification=record.control45.passesFullFreeGate&&record.response46.passesFullFreeGate?'PASS':'FAIL';
 }
 for(const [p,h] of Object.entries(manifest.inputs))assert.equal(hash(p),h);
 record.completed=new Date().toISOString();save(record);console.log('RESULT',record.result);
}catch(error){record.result='REFUSED_BOUNDED_RESPONSE';record.refusals.push({kind:'STOP_ON_FAILURE',reason:error.message});record.completed=new Date().toISOString();record.physicalStateAdvanced=false;save(record);console.error('REFUSAL',error.stack);process.exitCode=1;}

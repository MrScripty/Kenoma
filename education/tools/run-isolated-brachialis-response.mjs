/** One same-rule45/46 response. Source/preflight required before execution.
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
import {prepareResponseBody,addResponseDirection,responsePositions,responseNodeStep,evaluateResponse,cholesky,solveCholesky} from './isolated-projected-response.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),read=p=>JSON.parse(fs.readFileSync(root+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex');
const manifestPath='research/isolated-brachialis-response-20261006-inputs.json',manifest=read(manifestPath),mode=process.argv[2];
assert.ok(['--preflight','--execute'].includes(mode));assert.equal(manifest.body,'FJ1486');assert.equal(manifest.points_per_element,2048);assert.equal(manifest.activation,1);assert.equal(manifest.physical_force_gate_N,.0001);
assert.equal(manifest.force_rematching,false);assert.equal(manifest.parameter_fitting,false);assert.deepEqual(manifest.only_pair_authorized,[45,46]);
const sources=[manifestPath,'tools/isolated-projected-response.mjs','tools/run-isolated-brachialis-response.mjs','tests/isolated_projected_response.test.mjs','research/isolated-brachialis-response-20261006.md'];
for(const p of sources)execFileSync('git',['ls-files','--error-unmatch',p],{cwd:root,stdio:'pipe'});
execFileSync('git',['diff','--exit-code','HEAD','--',...sources,...Object.keys(manifest.inputs)],{cwd:root,stdio:'pipe'});
for(const [p,h] of Object.entries(manifest.inputs))assert.equal(hash(p),h,'Frozen source changed: '+p);
const sourceCommit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),sourceHashes=Object.fromEntries([...Object.keys(manifest.inputs),...sources].map(p=>[p,hash(p)]));
const directory=root+'review/isolated-brachialis-response-20261006/';fs.mkdirSync(directory,{recursive:true});
const targetFile=directory+(mode==='--preflight'?'preflight.json':'results.json');if(fs.existsSync(targetFile))throw Error('Preserve existing response receipt');
const geometry=read('data/anatomical-arm-v1/generated/arm-reference.json'),fits=read('data/anatomical-arm-v1/audit/modal-fixed-end-results.json'),fit=fits.records.find(r=>r.elementId===manifest.body),source=geometry.muscles.find(m=>m.element_id===manifest.body),modal=prepareModalBody(source),partition=meshPartition(source),original=originalFreeColumns(source,modal.nodeModes,partition),family=nestedFamily(partition,original.columns),columns=cartesianColumns(original.columns),material={...MUSCLE_FIXTURE,sigma0:fit.match.sigma0Pa},initial=Float64Array.from(fit.match.coordinatesM.slice(9,54));
assert.equal(original.capLeaks.length,0);assert.equal(partition.free.length,495);assert.equal(partition.held.length,90);assert.equal(family[0].vectorDimension,45);
const sheets=prepareIntramuscularAponeuroses(modal);assert.equal(sheets.branches.length,0);assert.equal(sheets.matrix.length,0);
const base={schema:1,body:manifest.body,sourceCommit,sourceHashes,protocolPreflightCommit:manifest.protocol_preflight_commit,mode,started:new Date().toISOString(),node:process.version,pointsPerElement:2048,activation:1,material,unchangedForceGateN:.0001,solver:manifest.solver,forceRematching:false,parameterFitting:false,physicalStateAdvanced:false,newMesh:false,newAnatomy:false,sheets:{branches:0,matrix:0},originalFitForceN:fit.match.forceN,originalTargetN:fit.modelReference.value};
const save=record=>fs.writeFileSync(targetFile,JSON.stringify(record,null,2)+'\n');let record={...base,result:'RUNNING_PREPARATION',trace:[],refusals:[]};save(record);
const near=(a,b,t,label)=>assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${label}: ${a} vs ${b}`);
let body;
function orientation(positions,retain=false){
 const certificates=source.elements_ten_node.map((ids,element)=>({element,...exactElementOrientation(ids.map(n=>source.nodes_m[n]),ids.map(n=>positions[n]))}));
 const certified=certificates.filter(c=>c.orientationCertified).length;
 if(certified!==certificates.length)throw Error('Unqualified exact P2 orientation '+certified+'/'+certificates.length);
 return {elements:certificates.length,certifiedElements:certified,...(retain?{certificates}:{})};
}
function audit(z,label){
 const positions=responsePositions(body,z),geometryCheck=orientation(positions,true),full=evaluateCompressionBody(body.prepared,positions,1,material),g=partition.free.flatMap(n=>full.nodalGradientN[n]),projected=columns.map(c=>dot(c,g));
 const cap=nodes=>nodes.reduce((s,n)=>s.map((v,d)=>v+full.nodalGradientN[n][d]),[0,0,0]);
 const distalGradient=cap(source.distal_nodes),proximalGradient=cap(source.proximal_nodes),reaction=nodes=>-dot(cap(nodes),source.basis.axis);
 const evaluated=evaluateResponse(body,z,{hessian:false});near(full.energyJ,evaluated.energyJ,1e-9,'Independent body energy');
 for(let k=0;k<45;k++)near(projected[k],evaluated.gradientN[k],2e-6,'Independent retained gradient');
 if(z.length===46)near(dot(partition.free.flatMap(n=>body.direction[n]),g),evaluated.gradientN[45],2e-6,'Independent added gradient');
 fs.writeFileSync(directory+label+'-orientation.json',JSON.stringify({label,...geometryCheck})+'\n');
 return {label,coordinatesM:Array.from(z),positionsM:positions,fullFreeGradientN:g,original45GradientN:projected,addedGradientN:z.length===46?evaluated.gradientN[45]:null,original45MaximumN:maxAbs(projected),projectedMaximumN:maxAbs(evaluated.gradientN),fullFreeMaximumN:maxAbs(g),fullFreeL2N:Math.sqrt(dot(g,g)),passesFullFreeGate:maxAbs(g)<=.0001,energyJ:full.energyJ,energiesJ:full.energies,minimumSampledJ:full.minimumJ,minimumCornerJ:full.minimumCornerJ,globalVolumeRatio:full.globalVolumeRatio,referenceVolumeSampledBelow09:full.referenceVolumeFractionBelow09,distalNodalGradientSumN:distalGradient,proximalNodalGradientSumN:proximalGradient,distalAxialNodalReactionN:reaction(source.distal_nodes),proximalAxialNodalReactionN:reaction(source.proximal_nodes),allNodalGradientResultantN:full.nodalGradientN.reduce((s,v)=>s.map((x,d)=>x+v[d]),[0,0,0]),maximumCapReferenceDisplacementM:maxAbs(partition.held.flatMap(n=>positions[n].map((v,d)=>v-source.nodes_m[n][d]))),orientation:{elements:geometryCheck.elements,certifiedElements:geometryCheck.certifiedElements,file:label+'-orientation.json'}};
}
function derivativeChecks(z,direction,exactGradient,exactHessian){
 const checks=[];
 for(const hM of [1e-7,5e-8]){
  const A=z.map((v,k)=>v+hM*direction[k]),B=z.map((v,k)=>v-hM*direction[k]);orientation(responsePositions(body,A));orientation(responsePositions(body,B));
  const plus=evaluateResponse(body,A,{hessian:false}),minus=evaluateResponse(body,B,{hessian:false});
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
  const begin=performance.now(),r=evaluateResponse(body,z),maximum=maxAbs(r.gradientN),row={label,iteration,coordinatesM:Array.from(z),energyJ:r.energyJ,projectedMaximumN:maximum,minimumSampledJ:r.minimumSampledJ,minimumCornerJ:r.minimumCornerJ,evaluationSeconds:(performance.now()-begin)/1000};record.trace.push(row);save(record);console.log('ITERATION',JSON.stringify(row));
  if(maximum<=solver.projected_force_gate_N)return {z,r,iterations:iteration};
  if(iteration===solver.maximum_iterations)throw Error('Projected solve iteration ceiling '+label);
  const L=cholesky(r.hessianNPerM,z.length),step=solveCholesky(L,r.gradientN.map(v=>-v)),nodeMaximum=Math.max(...responseNodeStep(body,step).map(v=>Math.hypot(...v)));
  const scale=Math.min(1,solver.maximum_nodal_step_m/nodeMaximum);step.forEach((v,k)=>step[k]=scale*v);
  const slope=dot(r.gradientN,step);assert.ok(slope<0,'Newton direction must descend');let accepted=false;
  for(let alpha=1;alpha>=solver.minimum_line_fraction;alpha/=2){
   const trial=z.map((v,k)=>v+alpha*step[k]);
   let state;try{orientation(responsePositions(body,trial));state=evaluateResponse(body,trial,{hessian:false});}catch(error){record.refusals.push({label,iteration,alpha,coordinatesM:Array.from(trial),kind:'GEOMETRY_OR_DOMAIN_REFUSAL',reason:error.message});save(record);throw error;}
   if(state.energyJ<=r.energyJ+solver.armijo_fraction*alpha*slope){row.acceptedLineFraction=alpha;row.predictedSlopeJ=slope;row.acceptedEnergyChangeJ=state.energyJ-r.energyJ;z=trial;accepted=true;save(record);break;}
   record.refusals.push({label,iteration,alpha,coordinatesM:Array.from(trial),kind:'SUFFICIENT_DECREASE_REFUSAL',trialEnergyJ:state.energyJ,requiredMaximumEnergyJ:r.energyJ+solver.armijo_fraction*alpha*slope});save(record);
  }
  if(!accepted)throw Error('Sufficient decrease line-search refusal '+label);
 }
}
try{
 console.log('PREPARE',mode,new Date().toISOString());body=prepareResponseBody(source,modal,material,2048);
 const originalPositions=modalPositions(modal,Float64Array.from(fit.match.coordinatesM));assert.deepEqual(responsePositions(body,initial),originalPositions);
 if(mode==='--preflight'){
  console.log('PRECHECK_HESSIAN',new Date().toISOString());const r=evaluateResponse(body,initial),a=audit(initial,'frozen-original');
  const old=read('review/isolated-calibration-resolution-20261006/results.json').rows.find(r=>r.elementId==='FJ1486').rules.find(r=>r.pointsPerElement===2048);
  near(a.fullFreeMaximumN,old.resolution.maximumFreeNodalComponentN,2e-6,'Historical full-free maximum');near(a.original45MaximumN,old.legacyFreeResidualN,2e-6,'Historical projected maximum');
  const v=Float64Array.from({length:45},(_,i)=>Math.sin(.31*i)),norm=Math.sqrt(dot(v,v));v.forEach((x,k)=>v[k]=x/norm);
  record={...record,result:'PASS_FROZEN_RESPONSE_PREFLIGHT_NO_NONLINEAR_SOLVE',nonlinearSolves:0,frozenOriginal:a,directionalChecks:derivativeChecks(initial,v,r.gradientN,r.hessianNPerM),originalProjectedTangentPositive:true};cholesky(r.hessianNPerM,45);
 }else{
  const preflightPath='review/isolated-brachialis-response-20261006/preflight.json',preflight=read(preflightPath);assert.equal(preflight.result,'PASS_FROZEN_RESPONSE_PREFLIGHT_NO_NONLINEAR_SOLVE');
  execFileSync('git',['ls-files','--error-unmatch',preflightPath],{cwd:root,stdio:'pipe'});execFileSync('git',['diff','--exit-code','HEAD','--',preflightPath],{cwd:root,stdio:'pipe'});
  for(const [p,h] of Object.entries(preflight.sourceHashes))assert.equal(hash(p),h);
  record.preflightSourceCommit=preflight.sourceCommit;record.preflightSha256=hash(preflightPath);record.frozenOriginal=preflight.frozenOriginal;record.result='RUNNING_SAME_RULE_45_MODE_CONTROL';save(record);
  const control=solve(initial,'45-mode-control');record.control45=audit(control.z,'control45');save(record);
  const g=record.control45.fullFreeGradientN,retained=projectVector(family[0],partition,g),omitted=g.map((v,k)=>v-retained[k]),norm=Math.sqrt(dot(omitted,omitted));assert.ok(norm>1e-8,'No omitted direction to add');
  const direction=omitted.map(v=>-v/norm),fullDirection=source.nodes_m.map(()=>[0,0,0]);partition.free.forEach((n,i)=>fullDirection[n]=direction.slice(3*i,3*i+3));
  near(dot(direction,direction),1,1e-12,'Added unit direction');assert.ok(maxAbs(columns.map(c=>dot(c,direction)))<1e-11);assert.equal(exactDyadicRank([...columns,direction],Array.from({length:1485},(_,i)=>i)).rank,46);
  addResponseDirection(body,fullDirection);const start=Float64Array.from([...control.z,0]);assert.deepEqual(responsePositions(body,start),record.control45.positionsM);
  console.log('PRODUCTION_DIRECTION_TANGENT',new Date().toISOString());const augmented=evaluateResponse(body,start),unit=new Float64Array(46);unit[45]=1;
  record.direction={rule:'Normalized negative omitted full-free gradient at the SAME2048-point45-mode re-equilibrated control; selected once.',freeNodeOrder:partition.free,freeVector:direction,fullNodalVector:fullDirection,rank:46,maximumOriginalDot:maxAbs(columns.map(c=>dot(c,direction))),norm:Math.sqrt(dot(direction,direction)),omittedGradientNormN:norm,actualEnergyDerivativeN:augmented.gradientN[45],expectedEnergyDerivativeN:dot(g,direction),initialCurvatureNPerM:augmented.hessianNPerM[46*45+45],derivativeChecks:derivativeChecks(start,unit,augmented.gradientN,augmented.hessianNPerM)};near(augmented.gradientN[45],dot(g,direction),2e-6,'Added gradient assembly');save(record);
  const H45=Float64Array.from({length:45*45},(_,i)=>augmented.hessianNPerM[46*Math.floor(i/45)+i%45]),cross=Float64Array.from({length:45},(_,i)=>augmented.hessianNPerM[46*i+45]);
  record.direction.initialRelaxedCurvatureNPerM=record.direction.initialCurvatureNPerM-dot(cross,solveCholesky(cholesky(H45,45),cross));save(record);
  if(!(record.direction.initialCurvatureNPerM>0&&record.direction.initialRelaxedCurvatureNPerM>0))throw Error('Unstable added-direction tangent response');
  record.result='RUNNING_SAME_RULE_46_MODE_RESPONSE';save(record);const enriched=solve(start,'46-mode-response');record.response46=audit(enriched.z,'response46');
  record.direction.finalCurvatureNPerM=enriched.r.hessianNPerM[46*45+45];record.direction.finalDerivativeChecks=derivativeChecks(enriched.z,unit,enriched.r.gradientN,enriched.r.hessianNPerM);
  if(!(record.direction.finalCurvatureNPerM>0))throw Error('Unstable final added-direction curvature');
  record.comparison={sameRulePoints:2048,energyDifferenceJ:record.response46.energyJ-record.control45.energyJ,fullFreeMaximumChangeN:record.response46.fullFreeMaximumN-record.control45.fullFreeMaximumN,minimumCornerJChange:record.response46.minimumCornerJ-record.control45.minimumCornerJ,distalAxialReactionChangeN:record.response46.distalAxialNodalReactionN-record.control45.distalAxialNodalReactionN,additionalCoordinateM:enriched.z[45],scope:'One45/46 response at identical2048-point potential; no spatial, quadrature, stability or physiological convergence claim.'};
  record.result='COMPLETED_PAIRED_PROJECTED_RESPONSE_FULL_PHYSICAL_GATES_RETAINED';record.nonlinearSolves=2;
 }
 for(const [p,h] of Object.entries(manifest.inputs))assert.equal(hash(p),h);
 record.completed=new Date().toISOString();save(record);console.log('RESULT',record.result);
}catch(error){record.result='REFUSED_BOUNDED_RESPONSE';record.refusals.push({kind:'STOP_ON_FAILURE',reason:error.message});record.completed=new Date().toISOString();record.physicalStateAdvanced=false;save(record);console.error('REFUSAL',error.stack);process.exitCode=1;}

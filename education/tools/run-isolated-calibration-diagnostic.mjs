/** Nine frozen evaluations; no optimizer, refit, state acceptance or downloads. */
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {performance} from 'node:perf_hooks';
import {prepareModalBody,modalPositions,evaluateModalBody} from '../web/anatomical-modal.mjs';
import {prepareIntramuscularAponeuroses,evaluateIntramuscularAponeuroses} from '../web/anatomical-aponeurosis.mjs';
import {MUSCLE_FIXTURE,muscleMaterial,determinant} from '../web/anatomical-material.mjs';
import {prepareCompressionBody,evaluateCompressionBody} from './anatomical-compression-quadrature.mjs';
import {prepareFurtherBody} from './anatomical-integration-refinement.mjs';
import {exactElementOrientation} from './anatomical-bernstein-orientation.mjs';
import {validateFrozenInputs,hashBytes,maxAbs,norm2,projectLegacy,freeResolution,nodalSheets,constitutiveComponents,componentNodalGradients} from './isolated-calibration-diagnostic.mjs';

const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/';
const read=p=>JSON.parse(fs.readFileSync(root+p)),hash=p=>hashBytes(fs.readFileSync(root+p));
const manifestPath='research/isolated-calibration-resolution-20261006-inputs.json',manifest=read(manifestPath);
validateFrozenInputs(root,manifest);
const sourceCommit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
if(execFileSync('git',['rev-parse',manifest.base_commit+'^{tree}'],{cwd:root,encoding:'utf8'}).trim()!==manifest.base_tree)throw Error('Frozen base tree changed');
const sourceFiles=[manifestPath,'tools/isolated-calibration-diagnostic.mjs','tools/run-isolated-calibration-diagnostic.mjs','tests/isolated_calibration_diagnostic.test.mjs'];
execFileSync('git',['diff','--exit-code','HEAD','--',...sourceFiles,...Object.keys(manifest.inputs)],{cwd:root,stdio:'pipe'});
for(const p of sourceFiles)execFileSync('git',['ls-files','--error-unmatch',p],{cwd:root,stdio:'pipe'});
const output=root+'review/isolated-calibration-resolution-20261006/';fs.mkdirSync(output,{recursive:true});
if(fs.existsSync(output+'results.json'))throw Error('Refusing to overwrite completed diagnostic evidence');
const geometry=read('data/anatomical-arm-v1/generated/arm-reference.json'),fits=read('data/anatomical-arm-v1/audit/modal-fixed-end-results.json'),prior=read('data/anatomical-arm-v1/audit/anatomical-calibration-nodal.json');
const tensor=(X,G)=>Array.from({length:9},(_,k)=>X.reduce((s,v,i)=>s+v[Math.floor(k/3)]*G[i][k%3],0));
const add=(a,b)=>a.map((v,i)=>v.map((x,d)=>x+b[i][d]));
const rows=[];const started=new Date().toISOString();
for(const fit of fits.records){
 const headStart=performance.now(),source=geometry.muscles.find(m=>m.element_id===fit.elementId),body=prepareModalBody(source),x=Float64Array.from(fit.match.coordinatesM),positions=modalPositions(body,x),material={...MUSCLE_FIXTURE,sigma0:fit.match.sigma0Pa};
 const sheets=prepareIntramuscularAponeuroses(body),sheet=nodalSheets(source,sheets,positions),canonicalSheets=evaluateIntramuscularAponeuroses(body,sheets,x,{hessian:false}),canonical=evaluateModalBody(body,x,1,{material,hessian:false});
 const sheetProjected=projectLegacy(body,sheet.gradientN),sheetError=maxAbs(sheetProjected.map((v,k)=>v-canonicalSheets.gradient[k]));
 if(sheetError>2e-6||Math.abs(sheet.energyJ-canonicalSheets.energy)>1e-9)throw Error('Independent sheet map mismatch');
 const original=Float64Array.from(canonical.gradient,(v,k)=>v+canonicalSheets.gradient[k]);
 const originalResidual=maxAbs(original.slice(9,54)),originalForce=-source.basis.axis.reduce((s,v,k)=>s+v*original[k],0);
 if(originalResidual>manifest.stationarity_tolerance_N||Math.abs(originalForce-fit.match.forceN)>1e-8)throw Error('Frozen original replay mismatch');
 const held=new Set([...source.distal_nodes,...source.proximal_nodes]);
 const capDisplacement=maxAbs(positions.flatMap((v,n)=>held.has(n)?v.map((z,d)=>z-source.nodes_m[n][d]):[]));
 const traceLeak=maxAbs(body.nodeModes.flatMap((modes,n)=>held.has(n)?modes.filter(m=>m.base>=9&&m.base<54).map(m=>m.value):[]));
 if(capDisplacement>1e-12||traceLeak>1e-12)throw Error('Frozen cap membership/trace mismatch');
 const certificates=source.elements_ten_node.map((ids,element)=>({element,...exactElementOrientation(ids.map(n=>source.nodes_m[n]),ids.map(n=>positions[n]))}));
 fs.writeFileSync(output+fit.elementId+'-orientation.json',JSON.stringify({elementId:fit.elementId,certificates},null,2)+'\n');
 const rules=[];let previous=null;let compressionWitness=null;
 for(const points of manifest.quadrature_points_per_element){
  console.log('START',fit.elementId,points,new Date().toISOString());
  const t=performance.now(),prepared=points===2048?prepareFurtherBody(source,body.nodeModes):prepareCompressionBody(source,body.nodeModes,points===32?1:2);
  const full=evaluateCompressionBody(prepared,positions,1,material),total=add(full.nodalGradientN,sheet.gradientN),projected=projectLegacy(body,total),resolution=freeResolution(body,total);
  const freeVector=resolution.freeNodes.flatMap(n=>total[n]);
  const rule={pointsPerElement:points,referenceVolumeM3:prepared.referenceVolumeM3,energiesJ:full.energies,sheetEnergyJ:sheet.energyJ,minimumSampledJ:full.minimumJ,minimumCornerJ:full.minimumCornerJ,globalVolumeRatio:full.globalVolumeRatio,referenceVolumeFractionBelow09:full.referenceVolumeFractionBelow09,legacyFreeResidualN:maxAbs(projected.slice(9,54)),legacyPassesUnchangedGate:maxAbs(projected.slice(9,54))<=1e-4,resolution,comparisonWithPrevious:previous?{previousPoints:previous.points,freeGradientChangeL2N:norm2(freeVector.map((v,k)=>v-previous.vector[k])),maximumFreeGradientChangeN:maxAbs(freeVector.map((v,k)=>v-previous.vector[k])),relativeChangeToCurrentL2:norm2(freeVector.map((v,k)=>v-previous.vector[k]))/resolution.totalL2N}:null};
  if(points===32){rule.maximumOriginalProjectionDifferenceN=maxAbs(projected.map((v,k)=>v-original[k]));if(rule.maximumOriginalProjectionDifferenceN>2e-6)throw Error('Original32-point force projection mismatch');}
  if(points===256){
   const priorRow=prior.rows.find(r=>r.elementId===fit.elementId);
   rule.prior256DifferenceN=resolution.maximumFreeNodalComponentN-priorRow.maximumFreeNodalComponentN;
   if(Math.abs(rule.prior256DifferenceN)>2e-6)throw Error('Historical256-point full nodal force mismatch');
   const components=componentNodalGradients(prepared,positions,1,material);components.sheet=sheet.gradientN;
   const sums=total.map((_,n)=>[0,1,2].map(d=>Object.values(components).reduce((s,g)=>s+g[n][d],0)));
   rule.maximumComponentSumDifferenceN=maxAbs(sums.flatMap((v,n)=>v.map((f,d)=>f-total[n][d])));
   if(rule.maximumComponentSumDifferenceN>2e-6)throw Error('Independent component force sum mismatch');
   const peak=resolution.largest;
   rule.forceComponents=Object.fromEntries(Object.entries(components).map(([name,g])=>{const free=resolution.freeNodes.flatMap(n=>g[n]),split=freeResolution(body,g);return [name,{freeL2N:norm2(free),maximumFreeComponentN:maxAbs(free),atTotalPeakN:g[peak.node][peak.axis],omittedL2N:split.omittedL2N,retainedL2N:split.retainedL2N}];}));
   rule.derivativeChecks=[];
   for(const hM of [2e-7,1e-7]){
    const energies=[-1,1].map(sign=>{const trial=positions.map(v=>v.slice());trial[peak.node][peak.axis]+=sign*hM;return evaluateCompressionBody(prepared,trial,1,material).energyJ+nodalSheets(source,sheets,trial).energyJ;});
    const differenceN=(energies[1]-energies[0])/(2*hM)-peak.gradientN;
    rule.derivativeChecks.push({hM,analyticGradientN:peak.gradientN,centralDifferenceN:(energies[1]-energies[0])/(2*hM),differenceN});
    if(Math.abs(differenceN)>1e-4)throw Error('Independent frozen nodal energy derivative mismatch');
   }
   let lowest=Infinity;
   for(const [element,e] of prepared.elements.entries())for(const [corner,p] of e.corners.entries()){
    const F=tensor(e.nodes.map(n=>positions[n]),p.gradient),J=determinant(F);
    if(J<lowest){lowest=J;const node=e.nodes[corner];compressionWitness={element,corner,node,referencePositionM:source.nodes_m[node],currentPositionM:positions[node],held:held.has(node),F,fibre:p.fibre,J};}
   }
  }
  rule.durationSeconds=(performance.now()-t)/1000;
  rules.push(rule);previous={points,vector:freeVector};
  console.log('RULE',JSON.stringify({elementId:fit.elementId,points,legacyResidualN:rule.legacyFreeResidualN,fullNodalMaxN:resolution.maximumFreeNodalComponentN,omittedFraction:resolution.omittedSquaredNormFraction,change:rule.comparisonWithPrevious,minimumJ:rule.minimumCornerJ,seconds:rule.durationSeconds}));
 }
 const F=compressionWitness.F,law=muscleMaterial(F,compressionWitness.fibre,1,material),constitutiveChecks=[];
 compressionWitness.lambda=law.lambda;
 compressionWitness.piolaComponentsPa=constitutiveComponents(F,compressionWitness.fibre,1,material).stressesPa;
 compressionWitness.meanCauchyStressPa=Object.fromEntries(Object.entries(compressionWitness.piolaComponentsPa).map(([name,P])=>[name,P.reduce((s,v,i)=>s+v*F[i],0)/(3*law.J)]));
 for(const h of [1e-5,5e-6]){
  const fd=F.map((_,i)=>{const A=F.slice(),B=F.slice();A[i]+=h;B[i]-=h;return (muscleMaterial(A,compressionWitness.fibre,1,material).solvePotential-muscleMaterial(B,compressionWitness.fibre,1,material).solvePotential)/(2*h);});
  const error=maxAbs(fd.map((v,i)=>v-law.P[i])),scale=Math.max(1,maxAbs(law.P));
  constitutiveChecks.push({dimensionlessPerturbation:h,maximumPiolaDerivativeErrorPa:error,maximumPiolaMagnitudePa:scale,relativeMaximumError:error/scale});
  if(error>1e-2+2e-7*scale)throw Error('Frozen compressed-state constitutive derivative mismatch');
 }
 rows.push({elementId:fit.elementId,activation:1,material,originalModelTargetN:fit.modelReference.value,originalFitForceN:fit.match.forceN,originalReplayResidualN:originalResidual,maximumCapDisplacementM:capDisplacement,maximumCapFreeModeCoefficient:traceLeak,sheetProjectionDifferenceN:sheetError,orientation:{elements:certificates.length,certifiedElements:certificates.filter(c=>c.orientationCertified).length,scope:'Exact dyadic signs of stored reference/current P2 Jacobian polynomials; not global injectivity, compression, contact or equilibrium.'},constitutiveWitness:compressionWitness,constitutiveChecks,rules,durationSeconds:(performance.now()-headStart)/1000});
}
validateFrozenInputs(root,manifest);
const contrast=read('data/anatomical-arm-v1/audit/anatomical-further-integration.json');
const result={schema:1,result:'COMPLETED_FROZEN_ISOLATED_CALIBRATION_RESOLUTION_DIAGNOSTIC',qualifiedSourceCommit:sourceCommit,baseCommit:manifest.base_commit,baseTree:manifest.base_tree,started,completed:new Date().toISOString(),node:process.version,sourceHashes:Object.fromEntries([...Object.keys(manifest.inputs),...sourceFiles].map(p=>[p,hash(p)])),unchangedStationarityToleranceN:1e-4,stateAdvanced:false,forceRematch:false,constitutiveChange:false,displacementSolve:false,rows,distinctHistoricalCoupledContext:{timeS:contrast.timeS,baselineResidualN:contrast.baselineResidualN,frozenResidual2048N:contrast.frozenResidual2048N,pointsPerElement:2048,scope:'Different coupled dense0.10s state with inertia/attachment/contact context. Retained historical evidence, not an isolated-fixture outcome or newly solved state.'},limits:manifest.limits.concat(['Euclidean free-node L2 decomposition evaluates force directions available/omitted by the existing45 free modes. It does not solve an enriched field, measure spatial error or establish fullP2/mixed stability.','Rules are frozen-pose reintegration comparisons; no quadrature, mesh, material or physiological convergence is claimed. Positive orientation and derivative controls do not establish anatomical accuracy or constitutive validity.','A failing force gate is a diagnostic result, not accepted equilibrium. The diagnostic itself can execute successfully while every full-nodal equilibrium gate fails.'])};
fs.writeFileSync(output+'results.json',JSON.stringify(result,null,2)+'\n');
console.log('RESULT',result.result,'SOURCE',sourceCommit);

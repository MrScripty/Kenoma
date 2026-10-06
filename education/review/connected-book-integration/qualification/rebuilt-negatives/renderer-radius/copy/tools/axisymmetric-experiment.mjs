/** Bounded numerical evidence only: one uniform cylinder and one passive taper. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {prepareAxisymmetric,solveAxisymmetric,solveAxisymmetricPath,assembleAxisymmetric,createMaterialSampler,fullDisplacement,cutForce,sideTraction,revolvedBoundary,signedBoundaryVolume} from '../web/axisymmetric-specimen.mjs';
const root=path.resolve(import.meta.dirname,'..'),out=path.resolve(process.argv[2]);
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const inputs=Object.fromEntries(['web/axisymmetric-material.mjs','web/axisymmetric-specimen.mjs','tools/axisymmetric-experiment.mjs'].map(p=>[p,sha(p)]));
const zs=[.173,.371,.619,.827],rs=[0,.25,.6,1],cache=new Map();
function solveRecord(axialCells,radialCells,order,epsilon,ratio=1.5){
 const key=[axialCells,radialCells,order,epsilon,ratio].join(':');if(cache.has(key))return cache.get(key);
 const mesh=prepareAxisymmetric({axialCells,radialCells,order,ratio}),start=performance.now(),state=solveAxisymmetricPath(mesh,epsilon,{tolerance:1e-10}),sampler=createMaterialSampler(mesh,state);
 const probes=zs.flatMap(zf=>rs.map(rf=>{const Z=zf*.05,R=rf*.005*(1+(ratio-1)*zf),p=sampler(R,Z);return {zf,rf,R,Z,J:p.J,axialLineStretch:p.axialLineStretch,radialLineStretch:p.radialLineStretch,hoopStretch:p.hoopStretch,v:p.v};}));
 const corners=[0,.0001,.001,.01,.99,.999,.9999,1].flatMap(zf=>[0,1].map(rf=>{const p=sampler(rf*.005*(1+(ratio-1)*zf),zf*.05);return {zf,rf,J:p.J,v:p.v,stressPa:p.cauchy};}));
 const row={key,axialCells,radialCells,order,ratio,epsilon,elapsedMs:performance.now()-start,state,nodes:mesh.nodes,cells:mesh.cells.map(c=>c.nodes),fullDisplacement:Array.from(fullDisplacement(mesh,state.q,epsilon)),referenceVolumeM3:mesh.exactReferenceVolumeM3,integratedReferenceVolumeM3:mesh.referenceVolumeM3,probes,corners,cuts:zs.map(f=>({zf:f,resultantN:cutForce(mesh,state,f*.05)})),sideTractions:zs.map(f=>sideTraction(mesh,state,f*.05))};
 cache.set(key,{mesh,state,sampler,row});console.log('Recorded',key,state.converged,state.failure??'');return cache.get(key);
}
const uniform=[-.1,0,.1].map(e=>solveRecord(4,2,5,e,1));
const meshes=[[4,2],[8,2],[4,4],[8,4],[16,4],[8,8],[16,8]];
const taper=meshes.flatMap(([nx,nr])=>[-.1,.1].map(e=>solveRecord(nx,nr,5,e)));
solveRecord(4,2,5,0);
const quadrature=[];
for(const epsilon of [-.1,.1]){
 const baseline=solveRecord(16,8,5,epsilon),solutions=[3,7].map(order=>solveRecord(16,8,order,epsilon));
 const reevaluations=[3,5,7,9].map(order=>{
  const mesh=prepareAxisymmetric({axialCells:16,radialCells:8,order}),a=assembleAxisymmetric(mesh,baseline.state.q,epsilon,{tangent:false});
  return {order,energyJ:a.energyJ,volumeRatio:a.volumeRatio,rightReactionN:a.rightReactionN,scaledMaxFreeResidual:a.scaledMaxFreeResidual};
 });
 quadrature.push({epsilon,baseline:baseline.row.key,solutions:solutions.map(x=>x.row.key),reevaluations});
}
const spatial=[];
for(const epsilon of [-.1,.1]){
 const finest=solveRecord(16,8,7,epsilon),integration=prepareAxisymmetric({axialCells:16,radialCells:8,order:9});
 for(const [nx,nr] of meshes.slice(0,-1)){
  const row=solveRecord(nx,nr,5,epsilon);let weightedError2=0;
  for(const p of integration.points){const delta=row.sampler(p.R,p.Z).J-finest.sampler(p.R,p.Z).J;weightedError2+=p.weightM3*delta*delta;}
  spatial.push({epsilon,coarse:row.row.key,reference:finest.row.key,volumeWeightedRmsJDifference:Math.sqrt(weightedError2/integration.exactReferenceVolumeM3),maxMaterialProbeJDifference:Math.max(...row.row.probes.map((p,i)=>Math.abs(p.J-finest.row.probes[i].J))),volumeRatioDifference:Math.abs(row.state.diagnostics.volumeRatio-finest.state.diagnostics.volumeRatio),reactionDifferenceN:Math.abs(row.state.diagnostics.rightReactionN-finest.state.diagnostics.rightReactionN),energyDifferenceJ:Math.abs(row.state.diagnostics.energyJ-finest.state.diagnostics.energyJ)});
 }
}
const rendering=[],reactionDerivative=[],conditioning=[];
for(const epsilon of [0,-.1,.1]){
 const solved=solveRecord(16,8,7,epsilon);
 for(const azimuth of [64,128,256])for(const axialSubdivisions of [2,4,8]){
  const b=revolvedBoundary(solved.mesh,solved.state,{azimuth,axialSubdivisions});
  const float=b.vertices.map(v=>Array.from(new Float32Array([v[2],v[0],v[1]])));
  rendering.push({epsilon,azimuth,axialSubdivisions,integratedVolumeM3:solved.state.diagnostics.volumeM3,boundaryVolumeM3:signedBoundaryVolume(b.vertices,b.indices),actualFloat32VolumeM3:signedBoundaryVolume(float,b.indices),referenceBoundaryVolumeM3:signedBoundaryVolume(b.referenceVertices,b.indices),exactReferenceVolumeM3:solved.mesh.exactReferenceVolumeM3});
 }
 for(const h of [2e-5,1e-5]){
  const plus=solveAxisymmetricPath(solved.mesh,epsilon+h,{tolerance:1e-10}),minus=solveAxisymmetricPath(solved.mesh,epsilon-h,{tolerance:1e-10});
  reactionDerivative.push({epsilon,h,plusConverged:plus.converged,minusConverged:minus.converged,energyDerivativeN:(plus.diagnostics.energyJ-minus.diagnostics.energyJ)/(2*h*solved.mesh.parameters.length),assembledReactionN:solved.state.diagnostics.rightReactionN});
 }
 const a=assembleAxisymmetric(solved.mesh,solved.state.q,epsilon);
 conditioning.push({epsilon,n:solved.mesh.freeCount,width:solved.mesh.bandwidth,originalBandTangent:Array.from(a.H),forceScaleN:solved.mesh.forceScaleN});
}
const capMesh=prepareAxisymmetric({axialCells:8,radialCells:4,order:5}),caps=[-.1,.1].map(epsilon=>({epsilon,state:solveAxisymmetric(capMesh,epsilon,{maxIterations:1}),nodes:capMesh.nodes,cells:capMesh.cells.map(c=>c.nodes),fullDisplacement:Array.from(fullDisplacement(capMesh,solveAxisymmetric(capMesh,epsilon,{maxIterations:1}).q,epsilon))}));
if(!Object.entries(inputs).every(([p,h])=>sha(p)===h))throw new Error('Source changed during bounded experiment');
const record={schema:1,inputs,cases:[...cache.values()].map(x=>x.row),uniform:uniform.map(x=>x.row.key),quadrature,spatial,rendering,reactionDerivative,conditioning,caps,scope:'Bounded finite-compliance passive Q2 axisymmetric specimen; only uniform and radius-ratio1.5 taper at K/mu20. Original residual/tangent, no volume correction. Refinement differences are observed errors, not a priori bounds; corner gradients recorded separately.'};
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(record)+'\n');console.log('Saved bounded numerical evidence',out);

import test from 'node:test';
import assert from 'node:assert/strict';
import {uniformCylinderOracle} from '../web/axisymmetric-material.mjs';
import {prepareAxisymmetric,q2Shape,assembleAxisymmetric,solveAxisymmetric,solveAxisymmetricPath,materialPoint,revolvedBoundary,signedBoundaryVolume,bandMultiply,cutForce,sideTraction} from '../web/axisymmetric-specimen.mjs';
const close=(a,b,abs=1e-11,rel=1e-8)=>assert.ok(Math.abs(a-b)<=abs+rel*Math.max(Math.abs(a),Math.abs(b)),`${a} != ${b}`);
test('Q2 partition and derivatives reproduce the exact frustum reference volume',()=>{
 for(const [r,z] of [[0,0],[-1,.6],[.7,1]]){const s=q2Shape(r,z);close(s.N.reduce((a,b)=>a+b,0),1);for(let k=0;k<2;k++)close(s.D.reduce((a,b)=>a+b[k],0),0);}
 for(const ratio of [1,1.5])for(const order of [3,5,7]){
  const m=prepareAxisymmetric({axialCells:3,radialCells:2,order,ratio});close(m.referenceVolumeM3,m.exactReferenceVolumeM3,1e-19,1e-13);
  if(ratio===1.5)close(ratio*ratio,2.25,0,0);
 }
});
test('assembled energy force and ORIGINAL tangent pass directional derivatives',()=>{
 const m=prepareAxisymmetric({axialCells:3,radialCells:2}),epsilon=.03;
 const q=m.freeMetadata.map(({node,component},i)=>component===1?epsilon*m.nodes[node][1]+1e-6*Math.sin(i):1e-6*Math.cos(i));
 const direction=q.map((_,i)=>Math.sin(.7*i+.2)),base=assembleAxisymmetric(m,q,epsilon),hd=bandMultiply(base.H,m.freeCount,m.bandwidth,direction);
 for(const h of [2e-8,1e-8]){
  const plus=assembleAxisymmetric(m,q.map((x,i)=>x+h*direction[i]),epsilon,{tangent:false}),minus=assembleAxisymmetric(m,q.map((x,i)=>x-h*direction[i]),epsilon,{tangent:false});
  close((plus.energyJ-minus.energyJ)/(2*h),base.g.reduce((s,x,i)=>s+x*direction[i],0),2e-8,3e-7);
  for(let i=0;i<m.freeCount;i++)close((plus.g[i]-minus.g[i])/(2*h),hd[i],2e-4,3e-7);
 }
});
test('free-lateral connected cylinder qualifies all nodes and material-point stresses against independent scalar oracle',()=>{
 const m=prepareAxisymmetric({axialCells:4,radialCells:2,ratio:1});
 for(const epsilon of [0,-.1,.1]){
  const s=solveAxisymmetric(m,epsilon,{tolerance:1e-10}),o=uniformCylinderOracle(1+epsilon);
  assert.ok(s.converged&&!s.failure);close(s.diagnostics.volumeRatio,o.J,1e-12);
  close(s.diagnostics.energyJ,o.energyDensityPa*m.exactReferenceVolumeM3,1e-15);
  close(s.diagnostics.rightReactionN,Math.PI*m.parameters.radius**2*o.nominalAxialPa,1e-12);
  for(const Z of [0,.017,m.parameters.length])for(const f of [0,.37,1]){
   const p=materialPoint(m,s,f*m.parameters.radius,Z);close(p.v[0],o.b,1e-12);close(p.v[3],o.lambda,1e-12);close(p.v[4],o.b,1e-12);close(p.v[1],0);close(p.v[2],0);
   close(p.cauchy.rr,0,2e-8);close(p.cauchy.hoop,0,2e-8);
  }
 }
});
test('complete cap axial displacement, free radial end DOFs and regular axis are explicit',()=>{
 const m=prepareAxisymmetric({axialCells:4,radialCells:2}),s=solveAxisymmetric(m,.1,{tolerance:1e-10});
 for(const Z of [0,m.parameters.length])for(const f of [0,.4,1]){
  const R=f*m.parameters.radius*(1+(m.parameters.ratio-1)*Z/m.parameters.length),p=materialPoint(m,s,R,Z);close(p.z,Z*(1+s.epsilon));
  if(f>0)assert.notEqual(p.r,R,'End radial motion must be solved, not clamped');
 }
 for(const Z of [.008,.025,.047]){const p=materialPoint(m,s,0,Z);close(p.r,0);close(p.v[1],0);close(p.v[2],0,1e-12);close(p.v[4],p.v[0],0,0);}
});
test('connected tapered solution develops meridional shear with actual finite local volume compliance',()=>{
 const m=prepareAxisymmetric({axialCells:4,radialCells:2}),s=solveAxisymmetric(m,-.1,{tolerance:1e-10}),p=materialPoint(m,s,.003,.023);
 assert.ok(s.converged);assert.ok(Math.abs(p.v[1])+Math.abs(p.v[2])>1e-4);
 assert.ok(s.diagnostics.maxQuadratureJ-s.diagnostics.minQuadratureJ>1e-3);
 assert.ok(Math.abs(s.diagnostics.volumeRatio-1)>1e-3);
 const traction=sideTraction(m,s,.023);close(traction.normal[1]/traction.normal[0],-.05);
 assert.ok(cutForce(m,s,.023)<0);assert.ok(s.diagnostics.rightReactionN<0);
});
test('watertight renderer follows solved geometry, has one component and exposes tessellation error without correction',()=>{
 const m=prepareAxisymmetric({axialCells:4,radialCells:2}),s=solveAxisymmetric(m,.1,{tolerance:1e-10});
 const b=revolvedBoundary(m,s,{azimuth:64}),edges=new Map(),adj=b.vertices.map(()=>[]);
 for(const face of b.indices)for(let i=0;i<3;i++){const a=face[i],c=face[(i+1)%3],key=[Math.min(a,c),Math.max(a,c)].join(',');edges.set(key,(edges.get(key)||0)+1);adj[a].push(c);adj[c].push(a);}
 assert.ok([...edges.values()].every(n=>n===2));const visited=new Set([0]),queue=[0];while(queue.length){for(const i of adj[queue.pop()])if(!visited.has(i)){visited.add(i);queue.push(i);}}assert.equal(visited.size,b.vertices.length);
 const first=materialPoint(m,s,m.parameters.radius,0);close(b.vertices[0][0],first.r);close(b.vertices[0][2],first.z);
 assert.notDeepEqual(b.vertices,b.referenceVertices);
 const zero=solveAxisymmetric(m,0),coarse=revolvedBoundary(m,zero,{azimuth:32}),fine=revolvedBoundary(m,zero,{azimuth:128});
 const vc=signedBoundaryVolume(coarse.vertices,coarse.indices),vf=signedBoundaryVolume(fine.vertices,fine.indices);
 assert.ok(vc<m.exactReferenceVolumeM3&&vf<m.exactReferenceVolumeM3);assert.ok(Math.abs(vf-m.exactReferenceVolumeM3)<Math.abs(vc-m.exactReferenceVolumeM3)/10);
});
test('finite iteration cap remains an explicit approximation and original tangent linear solves are checked',()=>{
 const m=prepareAxisymmetric({axialCells:4,radialCells:2}),cap=solveAxisymmetric(m,.1,{maxIterations:1}),fine=solveAxisymmetric(m,.1,{tolerance:1e-10});
 assert.ok(!cap.converged&&cap.diagnostics.scaledMaxFreeResidual>cap.tolerance);assert.ok(fine.converged);
 assert.ok(fine.history.every(row=>row.linearRelativeResidual<1e-10&&row.minScaledPivot>0));
});
test('load continuation reaches the fine compressed taper without changing the original Hessian',()=>{
 const m=prepareAxisymmetric({axialCells:16,radialCells:8}),direct=solveAxisymmetric(m,-.1,{tolerance:1e-10});
 assert.ok(!direct.converged&&direct.failure&&direct.diagnostics.scaledMaxFreeResidual>1);
 const path=solveAxisymmetricPath(m,-.1,{tolerance:1e-10});
 assert.ok(path.converged&&path.reachedRequestedPose);close(path.epsilon,-.1,0,0);
 assert.ok(path.continuation.stages.length===5&&path.continuation.stages.every(p=>p.converged&&p.history.every(h=>h.minScaledPivot>0&&h.linearRelativeResidual<1e-9)));
 assert.ok(path.diagnostics.scaledMaxFreeResidual<1e-10);
});

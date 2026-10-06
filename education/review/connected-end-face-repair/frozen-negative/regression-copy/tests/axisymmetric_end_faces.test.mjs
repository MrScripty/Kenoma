import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {prepareAxisymmetric,solveAxisymmetricPath,fullDisplacement,materialPoint,revolvedBoundary} from '../web/axisymmetric-specimen.mjs';
// Frozen, independently derived 60-digit restricted-energy oracle; no production scalar-root reuse.
const oracle=JSON.parse(fs.readFileSync(new URL('../review/connected-passive-specimen/numerical/material-oracle.json',import.meta.url)));
assert.equal(oracle.status,'PASS');
const close=(actual,expected,absolute,relative=0)=>assert.ok(Math.abs(actual-expected)<=absolute+relative*Math.abs(expected),`${actual} != ${expected}`);
test('every accepted axial count assigns every prescribed cap DOF by topology',()=>{
 for(let axialCells=2;axialCells<=32;axialCells++){
  const mesh=prepareAxisymmetric({axialCells,radialCells:1,order:3}),q=Array(mesh.freeCount).fill(0);
  for(const epsilon of [-.1,.1]){
   const u=fullDisplacement(mesh,q,epsilon);
   for(let i=0;i<mesh.nr;i++){
    assert.equal(u[2*i+1],0,`bottom axial DOF ${i}, ${axialCells} cells`);
    assert.equal(u[2*((mesh.nz-1)*mesh.nr+i)+1],epsilon*mesh.parameters.length,`top axial DOF ${i}, ${axialCells} cells`);
    assert.equal(mesh.fixedEnd[2*((mesh.nz-1)*mesh.nr+i)+1],true);
   }
  }
  assert.equal(mesh.nodes.at(-1)[1],mesh.parameters.length,'The top reference row is the exact declared endpoint');
 }
});
for(const epsilon of [-.1,.1])test(`three-cell uniform ${epsilon<0?'compression':'tension'} has oracle reaction and all end-face DOFs`,()=>{
 const mesh=prepareAxisymmetric({axialCells:3,radialCells:2,ratio:1}),state=solveAxisymmetricPath(mesh,epsilon,{tolerance:1e-10}),expected=oracle.cylinders.find(o=>o.lambda===1+epsilon),area=Math.PI*mesh.parameters.radius**2;
 assert.ok(state.converged&&state.reachedRequestedPose);
 const force=state.diagnostics.rightReactionN;assert.ok(Math.sign(force)===Math.sign(epsilon)&&Math.abs(force)>.01,'A loaded cylinder must have a nonzero correctly signed reaction');
 close(force,area*expected.nominal_axial_pa,1e-12);
 close(state.diagnostics.volumeRatio,expected.J,1e-12);
 close(state.diagnostics.energyJ,mesh.exactReferenceVolumeM3*expected.energy_density_pa,1e-15);
 const u=fullDisplacement(mesh,state.q,epsilon);
 for(let i=0;i<mesh.nr;i++){assert.equal(u[2*i+1],0);assert.equal(u[2*((mesh.nz-1)*mesh.nr+i)+1],epsilon*mesh.parameters.length);}
 for(const [R,Z] of mesh.nodes){const p=materialPoint(mesh,state,R,Z);close(p.r,expected.side_stretch*R,2e-12);close(p.z,expected.lambda*Z,2e-12);close(p.J,expected.J,1e-12);close(p.cauchy.rr,0,2e-8);}
});
test('rounded-count reference endpoints and all accepted render subdivisions remain inside the exact domain',()=>{
 // A manufactured admissible axial map isolates endpoint geometry from Newton convergence.
 for(const axialCells of [3,4,6,8,12,16,24])for(const ratio of [1,1.5])for(const epsilon of [-.1,.1]){
  const mesh=prepareAxisymmetric({axialCells,radialCells:2,order:3,ratio}),state={epsilon,q:mesh.freeMetadata.map(({node,component})=>component===1?epsilon*mesh.nodes[node][1]:0)},end=mesh.parameters.length;
  for(let i=0;i<mesh.nr;i++){
   const [R,Z]=mesh.nodes[(mesh.nz-1)*mesh.nr+i];assert.equal(Z,end);const p=materialPoint(mesh,state,R,Z);close(p.z,(1+epsilon)*end,2e-16);
  }
  for(let axialSubdivisions=1;axialSubdivisions<=16;axialSubdivisions++){
   const boundary=revolvedBoundary(mesh,state,{azimuth:8,axialSubdivisions});
   for(const v of boundary.referenceVertices)assert.ok(v[2]>=0&&v[2]<=end);
   for(let i=0;i<boundary.azimuth;i++){const top=(boundary.rings-1)*boundary.azimuth+i;assert.equal(boundary.referenceVertices[top][2],end);close(boundary.vertices[top][2],end*(1+epsilon),2e-16);}
   close(boundary.vertices.at(-1)[2],end*(1+epsilon),2e-16);
  }
 }
});
test('otherwise-delivered axial counts render the top endpoint with subdivision three',()=>{
 for(const axialCells of [4,8,16]){
  const mesh=prepareAxisymmetric({axialCells,radialCells:2,order:3}),state={epsilon:0,q:Array(mesh.freeCount).fill(0)},boundary=revolvedBoundary(mesh,state,{azimuth:8,axialSubdivisions:3});
  assert.equal(boundary.referenceVertices.at(-1)[2],mesh.parameters.length);
  for(let i=0;i<boundary.azimuth;i++)assert.equal(boundary.referenceVertices[(boundary.rings-1)*boundary.azimuth+i][2],mesh.parameters.length);
 }
});

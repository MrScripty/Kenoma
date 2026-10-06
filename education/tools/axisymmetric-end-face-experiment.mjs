/** Additional accepted meshes; exact cap membership, endpoint sampling and real solved states. */
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
import {prepareAxisymmetric,solveAxisymmetricPath,fullDisplacement,createMaterialSampler,revolvedBoundary,signedBoundaryVolume} from '../web/axisymmetric-specimen.mjs';
const root=path.resolve(import.meta.dirname,'..'),out=path.resolve(process.argv[2]);
const sha=n=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,n))).digest('hex');
const names=['web/axisymmetric-specimen.mjs','web/axisymmetric-material.mjs','web/axisymmetric-worker.mjs','tools/axisymmetric-end-face-experiment.mjs'];const inputs=Object.fromEntries(names.map(n=>[n,sha(n)]));
const assignmentAudit=[];
for(let axialCells=2;axialCells<=32;axialCells++){
 const m=prepareAxisymmetric({axialCells,radialCells:1,order:3}),q=Array(m.freeCount).fill(0);
 assignmentAudit.push({axialCells,referenceEndZ:m.nodes.at(-1)[1],upperAxialDofs:m.upperAxialDofs,faces:[-.1,.1].map(epsilon=>{const u=fullDisplacement(m,q,epsilon);return {epsilon,bottom:Array.from({length:m.nr},(_,i)=>u[2*i+1]),top:m.upperAxialDofs.map(id=>u[id])};})});
}
const cases=[];
for(const axialCells of [3,6,12,24])for(const ratio of [1,1.5])for(const epsilon of [-.1,.1]){
 const m=prepareAxisymmetric({axialCells,radialCells:2,ratio,order:7}),state=solveAxisymmetricPath(m,epsilon,{tolerance:1e-10}),u=fullDisplacement(m,state.q,epsilon),sample=createMaterialSampler(m,state);
 const probes=[.173,.371,.619,.827].flatMap(zf=>[0,.25,.6,1].map(rf=>{const Z=zf*.05,R=rf*.005*(1+(ratio-1)*zf);return {zf,rf,...sample(R,Z)};}));
 const endpoints=Array.from({length:m.nr},(_,i)=>({reference:m.nodes[(m.nz-1)*m.nr+i],point:sample(...m.nodes[(m.nz-1)*m.nr+i])}));
 const rendering=[3,4,8].map(axialSubdivisions=>{const b=revolvedBoundary(m,state,{azimuth:256,axialSubdivisions});return {axialSubdivisions,referenceEndZ:b.referenceVertices[(b.rings-1)*b.azimuth][2],referenceMinZ:Math.min(...b.referenceVertices.map(v=>v[2])),referenceMaxZ:Math.max(...b.referenceVertices.map(v=>v[2])),topAxialCoordinates:Array.from({length:b.azimuth},(_,i)=>b.vertices[(b.rings-1)*b.azimuth+i][2]),capCenter:b.vertices.at(-1),boundaryVolumeM3:signedBoundaryVolume(b.vertices,b.indices)};});
 cases.push({key:[axialCells,2,7,epsilon,ratio].join(':'),axialCells,radialCells:2,order:7,ratio,epsilon,state,nodes:m.nodes,cells:m.cells.map(c=>c.nodes),fullDisplacement:Array.from(u),upperAxialDofs:m.upperAxialDofs,probes,endpoints,rendering});console.log('Recorded repaired endpoint case',cases.at(-1).key,state.converged);
}
if(!Object.entries(inputs).every(([n,h])=>sha(n)===h))throw Error('Endpoint experiment inputs changed');
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify({inputs,assignmentAudit,cases,scope:'All accepted axial counts cap assignment; solved formerly affected 3/6/12/24 meshes, both cylinder/taper and compression/tension, strict-domain endpoints and rendering. No material or acceptance changes.'})+'\n');

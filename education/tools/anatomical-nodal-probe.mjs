/** Energy probes in nodal directions orthogonal to the retained Galerkin
 * space. The original potential and fixed material/contact rules are used.
 * Probes are not accepted states or a full nodal optimizer. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {denseModalBody} from './anatomical-dense-quadrature.mjs';
import {prepareCompressionBody} from './anatomical-compression-quadrature.mjs';

export function excludedNodalDirection(body,node,axis){
 const rows=body.nodeModes.map(modes=>{const row=new Float64Array(21);for(const m of modes)row[m.base/3]+=m.value;return row;}),G=Array.from({length:21},()=>new Float64Array(22));
 for(const row of rows)for(let i=0;i<21;i++)for(let j=0;j<21;j++)G[i][j]+=row[i]*row[j];for(let i=0;i<21;i++)G[i][21]=rows[node][i];
 for(let i=0;i<21;i++){
  let pivot=i;for(let k=i+1;k<21;k++)if(Math.abs(G[k][i])>Math.abs(G[pivot][i]))pivot=k;[G[i],G[pivot]]=[G[pivot],G[i]];
  if(Math.abs(G[i][i])<1e-12)throw Error('Rank-deficient nodal projection');const p=G[i][i];for(let j=i;j<=21;j++)G[i][j]/=p;
  for(let k=0;k<21;k++)if(k!==i){const t=G[k][i];for(let j=i;j<=21;j++)G[k][j]-=t*G[i][j];}
 }
 const v=rows.map((row,i)=>(i===node?1:0)-row.reduce((s,c,j)=>s+c*G[j][21],0)),norm=Math.hypot(...v);if(!(norm>1e-8))throw Error('Probe is entirely retained');v.forEach((x,i)=>v[i]=x/norm);
 const maximumModalDot=Math.max(...Array.from({length:21},(_,j)=>Math.abs(rows.reduce((s,row,i)=>s+row[j]*v[i],0))));
 return {direction:v.map(x=>[0,1,2].map(d=>d===axis?x:0)),maximumModalDot,originalExcludedNorm:norm};
}

/** Shift every material-dependent cached position while keeping reference
 * gradients, rest lengths, areas, material law and closest-feature recipe fixed. */
export function nodalProbeConfiguration(arm,body,x,activation,direction,h,prepared){
 const source=body.modal.source,originalNodes=source.nodes_m,originalPoints=body.modal.points,changes=[],seen=new Set();
 const delta=direction.map(v=>v.map(d=>h*d)),extended=Float64Array.from([...x,1]),virtualIndex=x.length;
 // Cached endpoint/reference geometry also determines tendon side areas.
 // An extra evaluation column shifts CURRENT endpoints without changing
 // those reference lengths/areas. Only energy is used by this diagnostic.
 function generic(point){if(point?.sourceElement!==body.id||!point.sourceNodes||seen.has(point))return;seen.add(point);const columns=point.columns;changes.push([point,'columns',columns]);const shift=[0,1,2].map(d=>point.sourceNodes.reduce((s,node,i)=>s+point.sourceWeights[i]*delta[node][d],0));point.columns=[...columns,[virtualIndex,shift]];}
 function internal(point,ids,weights){if(seen.has(point))return;seen.add(point);const reference=point.referenceM;changes.push([point,'referenceM',reference]);point.referenceM=reference.map((v,d)=>v+ids.reduce((s,node,i)=>s+weights[i]*delta[node][d],0));}
 try{
  source.nodes_m=originalNodes.map((X,i)=>X.map((v,d)=>v+delta[i][d]));
  body.modal.points=originalPoints.map((p,index)=>{const e=prepared.elements[p.element],q=e.points[index%prepared.pointsPerElement];return {...p,F0:Float64Array.from(p.F0,(v,k)=>v+e.nodes.reduce((s,node,i)=>s+delta[node][Math.floor(k/3)]*q.gradient[i][k%3],0))};});
  for(const b of arm.model.branches)for(const point of [b.a,b.b,...b.path])generic(point);
  for(const b of arm.model.interfaces)generic(b.a);
  for(const b of arm.model.matrices){generic(b.a);generic(b.b);}
  for(const surface of arm.contact.surfaces)for(const sample of surface.samples)generic(sample.point);
  for(const b of [...body.internalAponeuroses.branches,...body.internalAponeuroses.matrix])for(const point of [b.a,b.b]){
   const ids=Array.from({length:16},(_,i)=>point.sourceRing*16+i),weights=ids.map(node=>(1-point.insetFraction)/16+(node===point.sourcePerimeterNode?point.insetFraction:0));internal(point,ids,weights);
  }
  return anatomicalConfiguration(arm,extended,activation,{hessian:false});
 }finally{source.nodes_m=originalNodes;body.modal.points=originalPoints;for(const [point,key,value] of changes)point[key]=value;}
}

if(process.argv[1]===fileURLToPath(import.meta.url)){
 const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),run=read('audit/anatomical-dense-loading-prefix.json');for(const [p,h] of Object.entries(run.sourceHashes))if(hash(p)!==h)throw Error('Changed dense prefix '+p);
 const state=run.snapshots[3],arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')});for(const b of arm.model.bodies)b.modal=denseModalBody(b.modal);restoreContactRecipe(arm.contact,state.contactRule);
 const body=arm.model.bodies.find(b=>b.id==='FJ1512'),x=Float64Array.from(state.coordinatesM),prepared=prepareCompressionBody(body.modal.source,body.modal.nodeModes,2),baseline=anatomicalConfiguration(arm,x,state.activation,{hessian:false}),rows=[];
 for(const node of [98,96])for(const axis of [0,1,2]){
  const probe=excludedNodalDirection(body.modal,node,axis);if(probe.maximumModalDot>1e-10)throw Error('Probe not orthogonal to retained space');const differences=[];
  for(const hM of [1e-7,5e-8]){const plus=nodalProbeConfiguration(arm,body,x,state.activation,probe.direction,hM,prepared),minus=nodalProbeConfiguration(arm,body,x,state.activation,probe.direction,-hM,prepared);differences.push({hM,energyDerivativeN:(plus.energy-minus.energy)/(2*hM),minimumSampledJ:Math.min(...plus.headResults.map(b=>b.minJ),...minus.headResults.map(b=>b.minJ))});}
  const fresh=anatomicalConfiguration(arm,x,state.activation,{hessian:false});if(Math.abs(fresh.energy-baseline.energy)>1e-14)throw Error('Probe did not restore exact base energy');
  rows.push({node,axis,maximumModalDot:probe.maximumModalDot,originalExcludedNorm:probe.originalExcludedNorm,differences,derivativeDifferenceN:Math.abs(differences[0].energyDerivativeN-differences[1].energyDerivativeN)});console.log('PROBE',JSON.stringify(rows.at(-1)));
 }
 const files=[...Object.keys(run.sourceHashes),'data/anatomical-arm-v1/audit/anatomical-dense-loading-prefix.json','tools/anatomical-nodal-probe.mjs'];
 const result={schema:1,result:'COMPLETED_EXCLUDED_NODAL_DIRECTION_DIAGNOSTIC',sourceHashes:Object.fromEntries(files.map(p=>[p,hash(p)])),timeS:state.timeS,elementId:body.id,rows,limits:['Energy directional differences include body, embedded sheets, apparatus and contact at a frozen accepted dense state. Rigid gravity/inertia are unchanged by these tissue-only probes.','Directions have Euclidean nodal norm 1 and are orthogonal to all 63 retained body displacement columns; derivatives have units N.','This is six selected excluded directions, not a complete full nodal force assembly, equilibrium solve or convergence qualification. Perturbed states are never accepted or advanced.','Finite differences may encounter closest-feature nonsmoothness; two step sizes and positive sampled J are reported, not hidden.']};fs.writeFileSync(base+'audit/anatomical-nodal-probe.json',JSON.stringify(result,null,2)+'\n');
}

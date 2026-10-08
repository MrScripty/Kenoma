import {signedP2VolumeM3} from './p2-volume.mjs';
import {section,dot,sub,cross} from '../anatomical-section-inspector/geometry.mjs';
import {QUANTITY_DEFINITIONS,attachmentQuantityContext} from './quantity-definitions.mjs';
const norm=p=>Math.hypot(...p),check=(ok,msg)=>{if(!ok)throw Error(msg);};
const position=p=>Array.isArray(p)&&p.length===3&&p.every(Number.isFinite);
const key=t=>t.slice().sort((a,b)=>a-b).join(',');
const faceKeys=e=>[[0,1,2],[0,1,3],[0,2,3],[1,2,3]].map(t=>key(t.map(i=>e[i])));
const average=points=>[0,1,2].map(d=>points.reduce((s,p)=>s+p[d],0)/points.length);
export function connectedRegions(m) {
 check(m.centerline_m.length===7,'Existing seven-ring segmentation required');
 const z=m.centerline_m.map(p=>dot(sub(p,m.basis.origin),m.basis.axis));
 check(z.every(Number.isFinite)&&z.slice(1).every((v,i)=>v>z[i]),'Ordered source rings required');
 const groups=Array.from({length:6},(_,i)=>({id:m.element_id+':band'+i,band:i,intervalM:[z[i],z[i+1]],elementIndices:[]}));
 for(const [i,e]of m.elements_ten_node.entries()) {
  const q=e.slice(0,4).map(n=>dot(sub(m.nodes_m[n],m.basis.origin),m.basis.axis));
  const lo=Math.min(...q),hi=Math.max(...q);
  const eligible=groups.filter(g=>lo>=g.intervalM[0]-1e-10&&hi<=g.intervalM[1]+1e-10);
  check(eligible.length===1,'Element must belong to exactly one existing ring band');eligible[0].elementIndices.push(i);
 }
 const owners=new Map();
 for(const [i,e]of m.elements_ten_node.entries())for(const f of faceKeys(e)){const a=owners.get(f)||[];a.push(i);owners.set(f,a);}
 const adjacency=m.elements_ten_node.map(()=>new Set());
 for(const a of owners.values()){check(a.length<=2,'Nonmanifold material face');if(a.length===2){adjacency[a[0]].add(a[1]);adjacency[a[1]].add(a[0]);}}
 for(const group of groups){
  check(group.elementIndices.length>0,'Empty material band');const pending=[group.elementIndices[0]],seen=new Set(),allowed=new Set(group.elementIndices);
  while(pending.length){const n=pending.pop();if(seen.has(n))continue;seen.add(n);for(const a of adjacency[n])if(allowed.has(a)&&!seen.has(a))pending.push(a);}
  check(seen.size===allowed.size,'Disconnected material band');
 }
 const bandByElement=new Map(groups.flatMap(g=>g.elementIndices.map(i=>[i,g.band]))),interfaces=[];
 for(let i=0;i<5;i++){
  const faces=[...owners].filter(([,a])=>a.length===2&&new Set(a.map(n=>bandByElement.get(n))).size===2&&a.some(n=>bandByElement.get(n)===i)&&a.some(n=>bandByElement.get(n)===i+1)).map(([f,a])=>({cornerNodes:f.split(',').map(Number),elementIndices:a}));
  check(faces.length>0,'Adjacent material bands must share faces');interfaces.push({bands:[i,i+1],faces});
 }
 return {groups,interfaces};
}
export function capSamples(m,side) {
 const held=new Set(m[side+'_nodes']),samples=[];
 m.surface_triangles.forEach((nodes,sourceFace)=>{
  if(!nodes.every(n=>held.has(n)))return;
  const X=nodes.map(n=>m.nodes_m[n]),areaM2=norm(cross(sub(X[1],X[0]),sub(X[2],X[0])))/2;
  check(areaM2>0,'Degenerate retained cap face');samples.push({bodyId:m.element_id,side,sourceSurfaceFace:sourceFace,nodes:nodes.slice(),weights:[1/3,1/3,1/3],referencePositionM:average(X),referenceAreaM2:areaM2,areaKind:'authored_belly_cap_mesh_face_area_not_tendon_CSA'});
 });
 check(samples.length>0,'Empty source cap');return samples;
}
export function prepareGeometryContract(model,reference,routing,sourceIdentity) {
 const bodies=model.muscles.map(m=>({id:m.element_id,name:m.name,nodesM:m.nodes_m,elements:m.elements_ten_node,
  basis:m.basis,intervalM:m.belly_interval_m,centerlineM:m.centerline_m,surfaceTriangles:m.surface_triangles,
  regionPartition:connectedRegions(m),caps:{proximal:capSamples(m,'proximal'),distal:capSamples(m,'distal')},
  attachmentOwnership:model.attachments.find(a=>a.element_id===m.element_id),referenceRepairs:m.reference_repair,
  declaredReferenceVolumeM3:m.reference_volume_m3,recordedField:m.frozen?{positionsM:m.frozen.positions_m,maximumFreeNodalComponentN:m.frozen.maximumFreeNodalComponentN,forceGate:m.frozen.passesFullNodalForceGateAtFrozenPose}:null}));
 const caps=bodies.flatMap(b=>[...b.caps.proximal,...b.caps.distal]);
 const patches=Object.entries(model.patches).map(([id,p])=>({id,boneId:p.element_id,referenceAreaM2:p.area_m2,areaKind:'authored_selected_bone_surface_footprint_not_tendon_CSA',quantityContext:{...attachmentQuantityContext(id),declaredAttachmentOwners:model.attachments.flatMap(a=>['proximal','distal'].filter(side=>a[side]?.patch_id===id).map(side=>({bodyId:a.element_id,name:a.name,side,sourceRole:'existing authored ownership declaration; no measured head/tissue footprint partition'})))},sourceReference:'anatomical-arm-v1/config/attachments-apparatus.json',samples:p.anchor_samples.map(s=>({sourceFace:s.triangle_zero_based,boneNodes:s.vertex_indices_zero_based,barycentric:s.barycentric,referencePositionM:s.position_m,weight:s.area_weight,normal:s.outward_normal_unit})),evidenceClass:p.evidence_class,reviewStatus:p.review_status}));
 function binding(p){
  const cap=caps.filter(c=>norm(sub(c.referencePositionM,p))<1e-12);
  const patch=patches.flatMap(q=>q.samples.map((s,i)=>({patchId:q.id,sampleIndex:i,positionM:s.referencePositionM}))).filter(q=>norm(sub(q.positionM,p))<1e-12);
  check(cap.length<=1&&patch.length<=1,'Ambiguous original route endpoint');
  if(cap.length===1&&!patch.length)return {kind:'existing_cap_sample',bodyId:cap[0].bodyId,side:cap[0].side,sourceSurfaceFace:cap[0].sourceSurfaceFace};
  if(patch.length===1&&!cap.length)return {kind:'existing_patch_sample',patchId:patch[0].patchId,sampleIndex:patch[0].sampleIndex};
  return {kind:'retained_literal_endpoint',ownership:'Unresolved shared/estimated endpoint; no mechanical DOF map inferred'};
 }
 const routes=routing.branches.map((r,index)=>{
  for(const p of [r.originalAM,r.originalBM,r.repairedAM,r.repairedBM,...r.guides.map(g=>g.referenceM)])check(position(p),'Invalid retained route position');
  for(const g of r.guides){const b=reference.bones.find(b=>b.element_id===g.sourceElement);check(b&&Number.isInteger(g.sourceVertex)&&g.sourceVertex>=0&&g.sourceVertex<b.vertices_m.length,'Retained guide source vertex');}
  const a=binding(r.originalAM),b=binding(r.originalBM);
  return {sourceIndex:index,group:r.group,a,b,originalEndpointsM:[r.originalAM,r.originalBM],repairedEndpointsM:[r.repairedAM,r.repairedBM],repairOffsetsM:[sub(r.repairedAM,r.originalAM),sub(r.repairedBM,r.originalBM)],guides:r.guides,evidence:r.evidence};
 });
 return {schema:1,sourceIdentity,bodies,patches,routes,routingAssumptions:routing.routing.assumptions,stationarityToleranceN:model.stationarityToleranceN,quantityDefinitions:QUANTITY_DEFINITIONS,
  physicalAssumptions:{scope:'geometry observer only; inherited constitutive law unchanged and not evaluated',regionalVolume:'A near-unity regional/global signed volume ratio does not bound local J or prove valid geometry.',fibreGeometry:'Atlas-derived guides are not measured pennation. This observer does not compute current fibre direction, fibre-normal projected area J/lambda_f or cell packing.',pressure:'No contact traction, solid mean stress, incompressibility multiplier, interstitial fluid pressure or vascular pressure is computed; these are distinct quantities.',transport:'No fluid mass balance, Darcy flux, drainage boundary, perfusion or porosity state is implemented. An elastic bulk penalty and SLS relaxation do not establish fluid transport.',force:'No universal compression-to-force penalty or bulging capacity bonus; no imported animal/human coefficient or retuned capstone constant.',activation:'Inherited capstone force-velocity multiplier one is not velocity validation; no activation or force evaluation occurs here.',researchBacklog:'compression-lab-backlog.md; proposed directional-load and optional sealed/drained transport labs, not implemented mechanisms'},
  quantitySemantics:{regionalVolume:'signed algebraic P2 material volume in m3',materialSliceArea:'tessellated mapped material section area; not tendon CSA or PCSA',bonePatchArea:'authored source-surface enthesis candidate footprint; not measured tendon CSA',bellyCapFaceArea:'reference geometric face area of authored belly cut; not tendon CSA',tendonCSA:'unavailable: no measured specimen-specific tendon cross-section supplied',PCSA:'unavailable: no specimen-specific fascicle/sarcomere-normalized physiological cross-sectional area supplied',existingTendonA0:'not exported: retained apparatus20% patch/cap fractions are authored model inputs, not anatomical measurements',tricepsPatch:'one shared authored olecranon candidate; deep-muscular/superficial-tendinous footprint ownership is unresolved'},
  limits:['Consumable geometry contract; no force/material evaluation or anatomical validation.','Regions are six connected source ring bands per repaired P2 belly.','Volumes are exact polynomial integrals in real arithmetic, evaluated with binary64: signed algebraic material volumes, not no-fold/true-volume certificates.','Cap samples reuse the existing three-node apparatus point maps. Patch weights are geometric source-area weights, not new forces.','Routes retain authored repair/guide coordinates. Shared/estimated endpoint mechanical ownership remains unresolved; no new tendon area, radius, stress or landmark is supplied.','Recorded calibration forces remain failed. No supplied geometry field is accepted as equilibrium.']};
}
function mview(b){return {element_id:b.id,nodes_m:b.nodesM,elements_ten_node:b.elements,basis:b.basis,belly_interval_m:b.intervalM,centerline_m:b.centerlineM};}
/** Consume the existing evaluateApparatus(...).positions record shape without
 * importing or invoking that mechanics function. Require all seven bodies. */
export function observeApparatusPositions(contract,positions,{fieldLabel='supplied apparatus Cartesian positions; geometry only'}={}) {
 check(Array.isArray(positions)&&positions.length===contract.bodies.length,'Complete apparatus position inventory required');
 const fields={};
 for(const row of positions){check(row&&typeof row.elementId==='string'&&!Object.hasOwn(fields,row.elementId)&&Array.isArray(row.nodesM),'Duplicate, missing positions or malformed apparatus body');fields[row.elementId]=row.nodesM;}
 check(contract.bodies.every(b=>Object.hasOwn(fields,b.id)),'Missing apparatus body');
 return evaluateGeometry(contract,{bodyPositionsById:fields,fieldLabel});
}
export function evaluateGeometry(contract,{bodyPositionsById={},patchPositionsById={},fieldLabel='supplied kinematic geometry'}={}) {
 check(contract.schema===1&&contract.stationarityToleranceN===.0001,'Geometry contract version/gate');
 for(const id of Object.keys(bodyPositionsById))check(contract.bodies.some(b=>b.id===id),'Unknown body field');
 for(const id of Object.keys(patchPositionsById))check(contract.patches.some(p=>p.id===id),'Unknown patch field');
 const points=new Map(),bodies=[];
 for(const b of contract.bodies) {
  const current=Object.hasOwn(bodyPositionsById,b.id)?bodyPositionsById[b.id]:b.nodesM;check(Array.isArray(current)&&current.length===b.nodesM.length&&current.every(position),'Full finite nodal position field required');
  const refVolumes=b.elements.map(e=>signedP2VolumeM3(e.map(n=>b.nodesM[n]))),volumes=b.elements.map(e=>signedP2VolumeM3(e.map(n=>current[n])));
  check(refVolumes.every(v=>v>0),'Reference element volume must be positive');
  const membership=b.regionPartition.groups.flatMap(g=>g.elementIndices);check(membership.length===b.elements.length&&new Set(membership).size===b.elements.length&&membership.every(i=>Number.isInteger(i)&&i>=0&&i<b.elements.length),'Complete unique region membership required');
  const regions=b.regionPartition.groups.map(g=>{
   const referenceVolumeM3=g.elementIndices.reduce((s,i)=>s+refVolumes[i],0),signedVolumeM3=g.elementIndices.reduce((s,i)=>s+volumes[i],0);
   const f=((g.intervalM[0]+g.intervalM[1])/2-b.intervalM[0])/(b.intervalM[1]-b.intervalM[0]),m=mview(b);m.frozen={positions_m:current};const s=section(m,f,4);
   return {id:g.id,elementIndices:g.elementIndices,referenceVolumeM3,signedVolumeM3,signedVolumeRatio:signedVolumeM3/referenceVolumeM3,materialStationFraction:f,sectionAreaKind:'mapped_material_slice_not_tendon_CSA_or_PCSA',sectionContext:{quantityType:'muscle_material_slice_area',bodyId:b.id,materialStationM:s.stationM,sourceFrame:b.basis,subdivisions:4,method:QUANTITY_DEFINITIONS.muscle_material_slice_area.method,referenceState:'repaired reference belly',currentState:fieldLabel,anatomicalStatus:'kinematic geometry; no specimen-matched measurement'},referenceSection:s.reference,currentSection:s.current};
  });
  const capMaps={};
  for(const side of ['proximal','distal'])capMaps[side]=b.caps[side].map(c=>{
   const p=[0,1,2].map(d=>c.nodes.reduce((s,n,i)=>s+c.weights[i]*current[n][d],0));points.set('cap:'+b.id+':'+side+':'+c.sourceSurfaceFace,p);
   return {sourceSurfaceFace:c.sourceSurfaceFace,positionM:p,bodyNodes:c.nodes,weights:c.weights,referenceAreaM2:c.referenceAreaM2,areaKind:c.areaKind};
  });
  bodies.push({id:b.id,regions,referenceVolumeM3:refVolumes.reduce((s,v)=>s+v,0),signedVolumeM3:volumes.reduce((s,v)=>s+v,0),caps:capMaps,recordedForceFailure:b.recordedField?{maximumFreeNodalComponentN:b.recordedField.maximumFreeNodalComponentN,unchangedGateN:contract.stationarityToleranceN,forceGate:false}:null,fieldProvided:Object.hasOwn(bodyPositionsById,b.id)});
 }
 for(const patch of contract.patches){const positions=Object.hasOwn(patchPositionsById,patch.id)?patchPositionsById[patch.id]:patch.samples.map(s=>s.referencePositionM);check(Array.isArray(positions)&&positions.length===patch.samples.length&&positions.every(position),'Complete finite patch sample field required');positions.forEach((p,i)=>points.set('patch:'+patch.id+':'+i,p));}
 function endpoint(bind,route,side){
  const mapped=bind.kind==='existing_cap_sample'?points.get('cap:'+bind.bodyId+':'+bind.side+':'+bind.sourceSurfaceFace):bind.kind==='existing_patch_sample'?points.get('patch:'+bind.patchId+':'+bind.sampleIndex):route.originalEndpointsM[side];
  check(position(mapped),'Unresolved bound endpoint');return mapped.map((v,d)=>v+route.repairOffsetsM[side][d]);
 }
 const routes=contract.routes.map(r=>{const path=[endpoint(r.a,r,0),...r.guides.map(g=>g.referenceM),endpoint(r.b,r,1)];const lengthM=path.slice(1).reduce((s,p,i)=>s+norm(sub(p,path[i])),0);return {sourceIndex:r.sourceIndex,group:r.group,pathM:path,lengthM,aBinding:r.a,bBinding:r.b,limits:'Kinematic endpoint following with fixed retained guides/literal endpoints; no sliding wrap, clearance, force, radius or anatomical acceptance.'};});
 return {schema:1,status:'GEOMETRY_ONLY_NO_FORCE_EVALUATION',sourceIdentity:contract.sourceIdentity,quantitySemantics:contract.quantitySemantics,quantityDefinitions:contract.quantityDefinitions,physicalAssumptions:contract.physicalAssumptions,fieldLabel,bodies,routes,limits:contract.limits};
}

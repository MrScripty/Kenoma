/** Reference-area surface penalty, using the actual source bones and the
 * deformed P2 boundary's piecewise-linear render subdivision. Four positive
 * samples per boundary triangle; repeated nodes combined by summed area; finite sampled contact, not global clearance.
 * Active closest-feature derivatives include distance curvature. A declared
 * Gauss-Newton fallback handles distances below 10 nm; feature switches are
 * nonsmooth and are not certified. Reciprocal source-bone sampling is included.
 */
import {triangleTree} from '../../../../web/anatomical-distance.mjs';import {bodyPoint,evaluatePoint,JOINT_SCALE_M} from '../../../../web/anatomical-apparatus.mjs';import {attachmentMap} from '../../../../web/anatomical-transfer.mjs';
import {closestFeatureDifferential,regularizedMinimum} from '../../../../web/anatomical-contact-differential.mjs';
const sub=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
export const CONTACT_ASSUMPTIONS=Object.freeze({pressurePerGapPaPerM:1e9,tissueFeatureWidthM:1e-6,boneGapM:.00015,tissueGapM:.0003,samplesPerTriangle:4,elbowRefinementRadiusM:.07,area:'reference boundary triangle area',useDistanceCurvature:true,boneSampling:'Symmetric tissue-to-bone and bone-to-tissue surface quadrature, half reference area per direction',tendonSampling:'Five material samples per routed axial leg; authored equivalent circular side area from A0, line clearance only, insertion endpoints exempt',tangent:'Active closest-feature second-order differential; below 10 nm distance, Gauss-Newton degeneracy fallback'});
const bounds=vertices=>({lo:[0,1,2].map(d=>Math.min(...vertices.map(v=>v[d]))),hi:[0,1,2].map(d=>Math.max(...vertices.map(v=>v[d])))}),near=(X,b,pad)=>X.every((v,d)=>v>=b.lo[d]-pad&&v<=b.hi[d]+pad);
// A frozen material triangulation is refined only BETWEEN nonlinear solves.
// Positive centroid/vertex weights sum to each original reference face area.
export function rebuildSurfaceSamples(surface){
 const {body}=surface,m=body.modal.source,vertices=new Map(),samples=[];
 for(const [face,children] of surface.materialTriangles.entries()){
  const tri=m.surface_triangles[face],X=tri.map(i=>m.nodes_m[i]);
  for(const child of children){
   const P=child.map(L=>[0,1,2].map(d=>L.reduce((s,w,i)=>s+w*X[i][d],0))),area=Math.hypot(...cross(sub(P[1],P[0]),sub(P[2],P[0])))/2;
   const centroid=[0,1,2].map(d=>child.reduce((s,L)=>s+L[d]/3,0));
   samples.push({point:bodyPoint(body,tri,centroid),referenceAreaM2:area*.5,sourceFace:face});
   for(const L of child){const terms=tri.map((id,i)=>[id,L[i]]).filter(([,w])=>w>0).sort((a,b)=>a[0]-b[0]),key=terms.map(([id,w])=>id+':'+w.toPrecision(15)).join(',');
    if(!vertices.has(key))vertices.set(key,{point:bodyPoint(body,terms.map(t=>t[0]),terms.map(t=>t[1])),referenceAreaM2:0,sourceFaces:[]});
    const sample=vertices.get(key);sample.referenceAreaM2+=area/6;sample.sourceFaces.push(face);
   }
  }
 }
 surface.samples=[...samples,...vertices.values()];return surface;
}
export function prepareContact(model,{parameters=CONTACT_ASSUMPTIONS}={}){
 const surfaces=model.bodies.map(body=>{
  const m=body.modal.source;let refinedFaces=0;
  const materialTriangles=m.surface_triangles.map(tri=>{
   const refined=tri.some(i=>Math.hypot(...sub(m.nodes_m[i],model.frame.origin_m))<parameters.elbowRefinementRadiusM);
   if(refined)refinedFaces++;
   const L=[[1,0,0],[0,1,0],[0,0,1],[.5,.5,0],[0,.5,.5],[.5,0,.5]];
   return (refined?[[0,3,5],[3,1,4],[5,4,2],[3,4,5]]:[[0,1,2]]).map(ids=>ids.map(i=>L[i]));
  });
  return rebuildSurfaceSamples({body,materialTriangles,refinedSourceFaces:refinedFaces,refinement:'Positive reference-area material subdivision; geometric witnesses refine it between solves.'});
 });
 return {surfaces,tendonKnots:new Map(),refinementRounds:0,bones:model.bones.map((bone,i)=>{const samples=[],vertices=new Map();for(const [face,tri] of bone.triangles.entries()){const X=tri.map(j=>bone.vertices_m[j]),area=Math.hypot(...cross(sub(X[1],X[0]),sub(X[2],X[0])))/2;samples.push({referenceM:[0,1,2].map(d=>X.reduce((sum,P)=>sum+P[d]/3,0)),areaM2:area*.5,sourceFace:face});for(const node of tri){if(!vertices.has(node))vertices.set(node,{referenceM:bone.vertices_m[node],areaM2:0,sourceVertex:node});vertices.get(node).areaM2+=area/6;}}samples.push(...vertices.values());return {source:bone,id:bone.element_id,moving:i>0,samples,referenceSamples:samples,tree:triangleTree(bone.vertices_m,bone.triangles),bounds:bounds(bone.vertices_m)};})};
}
export function addContact(model,contact,x,result,{parameters=CONTACT_ASSUMPTIONS}={}){
 const n=model.ndof,gradient=result.gradient,H=result.hessian,q=x[model.jointIndex]/JOINT_SCALE_M,trees=result.positions.map((r,i)=>({tree:triangleTree(r.nodesM,model.bodies[i].modal.source.surface_triangles),bounds:bounds(r.nodesM)}));let energy=0,activeBone=0,activeSoft=0,maxBonePenetrationM=0,maxSoftPenetrationM=0,boneTorqueNm=0,totalBoneForce=[0,0,0],evaluations=0,curvatureFallbacks=0,tendonEvaluations=0,tendonSamples=0,maxTendonPenetrationM=0;
 function penalty(g,clearance,area,columns,kind,normal){const deficit=g-clearance;if(deficit>=0)return;const k=parameters.pressurePerGapPaPerM*area;energy+=.5*k*deficit**2;for(const [i,v] of columns)gradient[i]+=k*deficit*v;if(H)for(const [i,v] of columns)for(const [j,w] of columns)H[i*n+j]+=k*v*w;if(kind.startsWith('bone')){activeBone++;const joint=columns.find(([i])=>i===model.jointIndex);if(joint)boneTorqueNm-=k*deficit*joint[1]*JOINT_SCALE_M;for(let d=0;d<3;d++)totalBoneForce[d]+=(kind==='bone-reverse'?-1:1)*k*deficit*normal[d];maxBonePenetrationM=Math.max(maxBonePenetrationM,-g);}else{activeSoft++;maxSoftPenetrationM=Math.max(maxSoftPenetrationM,-g);}}
 function exactPenalty(query,points,clearance,area,kind,normal){if(!parameters.useDistanceCurvature)return false;if(query.signedDistanceM>=clearance)return true;if(query.distanceM<1e-8){curvatureFallbacks++;return false;}const local=closestFeatureDifferential(points[0].position,points.slice(1).map(p=>p.position),{...query,gradient:normal}),delta=query.signedDistanceM-clearance,k=parameters.pressurePerGapPaPerM*area;if(Math.abs(local.value-query.signedDistanceM)>1e-8)throw new RangeError('Contact feature does not reproduce closest distance');const jacobian=new Map();points.forEach((p,point)=>{for(const [i,v] of p.columns){if(!jacobian.has(i))jacobian.set(i,new Float64Array(12));const row=jacobian.get(i);for(let d=0;d<3;d++)row[point*3+d]+=v[d];}});const columns=[...jacobian].map(([i,v])=>({i,v,entries:Array.from(v).map((c,j)=>[j,c]).filter(([,c])=>c!==0),g:dot(v,local.gradient)}));energy+=.5*k*delta**2;for(const a of columns)gradient[a.i]+=k*delta*a.g;if(H){for(const a of columns)for(const b of columns){let curvature=0;for(const [i,v] of a.entries)for(const [j,w] of b.entries)curvature+=v*local.hessian[i*12+j]*w;H[a.i*n+b.i]+=k*(a.g*b.g+delta*curvature);}points.forEach((p,point)=>{for(const [i,v] of p.second)H[i*n+i]+=k*delta*dot(v,local.gradient.slice(3*point,3*point+3));});}if(kind.startsWith('bone')){activeBone++;const joint=columns.find(a=>a.i===model.jointIndex);if(joint)boneTorqueNm-=k*delta*joint.g*JOINT_SCALE_M;for(let d=0;d<3;d++)totalBoneForce[d]+=(kind==='bone-reverse'?-1:1)*k*delta*normal[d];maxBonePenetrationM=Math.max(maxBonePenetrationM,-query.signedDistanceM);}else{activeSoft++;maxSoftPenetrationM=Math.max(maxSoftPenetrationM,-query.signedDistanceM);}return true;}
 // Quadratic simplex regularization of the MINIMUM unsigned feature distance.
 // It equals the exact closest distance outside a tie band and is <= it.
 // Outside tissue this strengthens the penalty. Inside, u-2*d <= -d also
 // strengthens it. Acceptance always uses the original signed distance.
 function regularizedSoft(query,tree,A,other,clearance,area){
  const width=parameters.tissueFeatureWidthM??CONTACT_ASSUMPTIONS.tissueFeatureWidthM;
  if(!(width>0)||query.distanceM<1e-8)return false;
  // Keep every triangle distance. Merging coincident edges according to the
  // current barycentric feature would change the simplex at an edge transition
  // and introduce an energy jump. Inactive features enter with zero weight.
  const features=tree.closestFeatures(A.position,width,query).map(f=>({...f,tri:other.modal.source.surface_triangles[f.triangle]}));
  if(features.length<2)return false;
  const envelope=regularizedMinimum(features.map(f=>f.distanceM),width),active=envelope.active.map(i=>features[i]),count=active.length;
  if(count<2)return false;
  const weights=envelope.active.map(i=>envelope.weights[i]),gap=envelope.value-(query.inside?2*query.distanceM:0),delta=gap-clearance,k=parameters.pressurePerGapPaPerM*area;
  if(delta>=0)return true;
  const derivatives=active.map(f=>{
   const points=[A,...f.tri.map(node=>evaluatePoint(bodyPoint(other,[node],[1]),x,model))],local=closestFeatureDifferential(A.position,points.slice(1).map(p=>p.position),f),jacobian=new Map();
   if(Math.abs(local.value-f.distanceM)>1e-8)throw new RangeError('Regularized feature distance mismatch');
   points.forEach((p,point)=>{for(const [i,v] of p.columns){if(!jacobian.has(i))jacobian.set(i,new Float64Array(12));const row=jacobian.get(i);for(let d=0;d<3;d++)row[point*3+d]+=v[d];}});
   return {local,columns:[...jacobian].map(([i,v])=>({i,g:dot(v,local.gradient),entries:Array.from(v).map((c,j)=>[j,c]).filter(([,c])=>c!==0)}))};
  });
  const G=new Map(),mean=new Map();
  derivatives.forEach((d,j)=>d.columns.forEach(a=>{G.set(a.i,(G.get(a.i)||0)+(weights[j]-(query.inside&&j===0?2:0))*a.g);mean.set(a.i,(mean.get(a.i)||0)+a.g/count);}));
  energy+=.5*k*delta*delta;for(const [i,g] of G)gradient[i]+=k*delta*g;
  if(H){
   for(const [i,g] of G)for(const [j,h] of G)H[i*n+j]+=k*g*h;
   if(parameters.useDistanceCurvature){
    derivatives.forEach((d,j)=>{const w=weights[j]-(query.inside&&j===0?2:0);for(const a of d.columns)for(const b of d.columns){let curvature=0;for(const [i,v] of a.entries)for(const [l,z] of b.entries)curvature+=v*z*d.local.hessian[i*12+l];H[a.i*n+b.i]+=k*delta*w*curvature;}});
    for(const d of derivatives){const row=new Map(d.columns.map(a=>[a.i,a.g]));for(const [i,g] of mean)for(const [j,h] of mean)H[i*n+j]-=k*delta/width*((row.get(i)||0)-g)*((row.get(j)||0)-h);}
   }
  }
  activeSoft++;maxSoftPenetrationM=Math.max(maxSoftPenetrationM,-query.signedDistanceM);return true;
 }
 // Finite axial-line contact is an explicit approximation, separate from
 // the tissue surface quadrature. Prescribed cortex guides can carry support
 // reactions; source insertion endpoints are deliberately on their source bone.
 result.contactTracePhase='tendon-bone';
 for(const [branchIndex,branch] of model.branches.entries()){const points=branch.path.map(p=>evaluatePoint(p,x,model));for(let leg=0;leg<points.length-1;leg++){const A0=points[leg],B0=points[leg+1],referenceLength=Math.hypot(...sub(branch.path[leg].referenceM,branch.path[leg+1].referenceM)),area=2*Math.sqrt(Math.PI*branch.A0M2)*referenceLength;const knots=contact.tendonKnots?.get(branchIndex+':'+leg),rule=knots?knots.map((t,i)=>[t,((knots[i+1]??t)-(knots[i-1]??t))/2]):[0,.25,.5,.75,1].map(t=>[t,.2]);for(const [t,weight] of rule){const endpoint=t===0?branch.path[leg]:t===1?branch.path[leg+1]:null;if(endpoint?.kind==='bone'&&endpoint.sourceFace!==undefined)continue;const blend=(key)=>[...A0[key].map(([i,v])=>[i,v.map(d=>d*(1-t))]),...B0[key].map(([i,v])=>[i,v.map(d=>d*t)])],A={position:A0.position.map((v,d)=>v*(1-t)+B0.position[d]*t),columns:blend('columns'),second:blend('second')};for(const bone of contact.bones){const local=bone.moving?attachmentMap(A.position,model.frame,2*model.frame.atlas_bind_angle_rad-q).position:A.position;if(!near(local,bone.bounds,parameters.boneGapM))continue;const r=bone.tree.closest(local);evaluations++;tendonEvaluations++;maxTendonPenetrationM=Math.max(maxTendonPenetrationM,-r.signedDistanceM);if(r.signedDistanceM>=parameters.boneGapM)continue;tendonSamples++;const normal=bone.moving?sub(attachmentMap(r.gradient.map((v,d)=>v+model.frame.origin_m[d]),model.frame,q).position,model.frame.origin_m):r.gradient,points=[A,...r.triangleVertices.map(referenceM=>evaluatePoint({kind:'bone',referenceM,moving:bone.moving},x,model))];if(exactPenalty(r,points,parameters.boneGapM,area*weight,'bone-tendon',normal))continue;const columns=A.columns.map(([i,v])=>[i,dot(normal,v)]);if(bone.moving)columns.push([model.jointIndex,-dot(normal,cross(model.frame.axis_unit,sub(A.position,model.frame.origin_m)))/JOINT_SCALE_M]);penalty(r.signedDistanceM,parameters.boneGapM,area*weight,columns,'bone-tendon',normal);}}}}
 for(let a=0;a<contact.surfaces.length;a++){const surface=contact.surfaces[a];for(const sample of surface.samples){const A=evaluatePoint(sample.point,x,model),point=A.position;
  result.contactTracePhase='muscle-bone';
  for(const bone of contact.bones){const local=bone.moving?attachmentMap(point,model.frame,2*model.frame.atlas_bind_angle_rad-q).position:point;if(!near(local,bone.bounds,parameters.boneGapM))continue;const r=bone.tree.closest(local);evaluations++;const normal=bone.moving?sub(attachmentMap(r.gradient.map((v,d)=>v+model.frame.origin_m[d]),model.frame,q).position,model.frame.origin_m):r.gradient;if(parameters.useDistanceCurvature&&r.signedDistanceM<parameters.boneGapM){const points=[A,...r.triangleVertices.map(referenceM=>evaluatePoint({kind:'bone',referenceM,moving:bone.moving},x,model))];if(exactPenalty(r,points,parameters.boneGapM,sample.referenceAreaM2*.5,'bone',normal))continue;}const columns=A.columns.map(([i,v])=>[i,dot(normal,v)]);if(bone.moving){const B=cross(model.frame.axis_unit,sub(point,model.frame.origin_m));columns.push([model.jointIndex,-dot(normal,B)/JOINT_SCALE_M]);}penalty(r.signedDistanceM,parameters.boneGapM,sample.referenceAreaM2*.5,columns,'bone',normal);}
  // Each ordered direction carries half the reference area: a declared
  // symmetric surface potential. It is not an undocumented doubled penalty.
  result.contactTracePhase='muscle-muscle';
  for(let b=0;b<trees.length;b++){if(a===b||!near(point,trees[b].bounds,parameters.tissueGapM+(parameters.tissueFeatureWidthM??CONTACT_ASSUMPTIONS.tissueFeatureWidthM)/2))continue;const r=trees[b].tree.closest(point);evaluations++;if(r.signedDistanceM>=parameters.tissueGapM+(parameters.tissueFeatureWidthM??CONTACT_ASSUMPTIONS.tissueFeatureWidthM)/2)continue;const other=model.bodies[b],tri=other.modal.source.surface_triangles[r.triangle];if(regularizedSoft(r,trees[b].tree,A,other,parameters.tissueGapM,sample.referenceAreaM2*.5))continue;if(parameters.useDistanceCurvature){const points=[A,...tri.map(node=>evaluatePoint(bodyPoint(other,[node],[1]),x,model))];if(exactPenalty(r,points,parameters.tissueGapM,sample.referenceAreaM2*.5,'soft',r.gradient))continue;}const B=bodyPoint(other,tri,r.barycentric),Br=evaluatePoint(B,x,model),columns=[...A.columns.map(([i,v])=>[i,dot(r.gradient,v)]),...Br.columns.map(([i,v])=>[i,-dot(r.gradient,v)])];penalty(r.signedDistanceM,parameters.tissueGapM,sample.referenceAreaM2*.5,columns,'soft',r.gradient);}
 }}
 // Reciprocal source-bone quadrature resolves narrow cortical features that
 // a coarser belly boundary can otherwise cross between its surface samples.
 result.contactTracePhase='bone-muscle-reciprocal';
 for(const bone of contact.bones)for(const sample of bone.samples){const A=evaluatePoint({kind:'bone',referenceM:sample.referenceM,moving:bone.moving},x,model);for(let b=0;b<trees.length;b++){if(!near(A.position,trees[b].bounds,parameters.boneGapM))continue;const r=trees[b].tree.closest(A.position);evaluations++;if(r.signedDistanceM>=parameters.boneGapM)continue;const other=model.bodies[b],tri=other.modal.source.surface_triangles[r.triangle];if(parameters.useDistanceCurvature){const points=[A,...tri.map(node=>evaluatePoint(bodyPoint(other,[node],[1]),x,model))];if(exactPenalty(r,points,parameters.boneGapM,sample.areaM2*.5,'bone-reverse',r.gradient))continue;}const B=evaluatePoint(bodyPoint(other,tri,r.barycentric),x,model),columns=[...A.columns.map(([i,v])=>[i,dot(r.gradient,v)]),...B.columns.map(([i,v])=>[i,-dot(r.gradient,v)])];penalty(r.signedDistanceM,parameters.boneGapM,sample.areaM2*.5,columns,'bone-reverse',r.gradient);}}

 result.energy+=energy;result.contact={tissueFeatureWidthM:parameters.tissueFeatureWidthM??CONTACT_ASSUMPTIONS.tissueFeatureWidthM,refinementRounds:contact.refinementRounds||0,frozenTendonRules:contact.tendonKnots?.size||0,storedEnergyJ:energy,activeBoneSamples:activeBone,activeSoftSamples:activeSoft,maximumSampledBonePenetrationM:maxBonePenetrationM,maximumSampledSoftPenetrationM:maxSoftPenetrationM,boneTorqueNm,boneReactionForceN:totalBoneForce,closestPointEvaluations:evaluations,curvatureFallbacks,tendonClosestPointEvaluations:tendonEvaluations,activeTendonSamples:tendonSamples,maximumSampledTendonPenetrationM:maxTendonPenetrationM,parameters,limits:['Piecewise-linear P2 boundary and finite surface quadrature; full supported-pose crossing audits remain separate.','Pressure is an authored penalty response, not cartilage pressure or measured human tissue pressure.','Closest-feature derivatives apply while the selected feature is fixed; nonsmooth feature changes and degeneracy fallbacks remain explicit.','Repeated boundary-node samples are combined exactly by summed reference area. Active sample counts describe unique evaluation points.']};return result;
}

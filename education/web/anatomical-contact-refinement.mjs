/** Geometric cutting witnesses, frozen during each nonlinear solve.
 * No tolerance relaxation, reference rebasing or routing topology change.
 * This is finite-pose refinement of the PL boundary and axial line, not CCD.
 */
import {triangleTree,closestTriangle} from './anatomical-distance.mjs';
import {triangleRecords,transverseCrossings} from './anatomical-intersections.mjs';
import {attachmentMap} from './anatomical-transfer.mjs';
import {evaluatePoint,JOINT_SCALE_M} from './anatomical-apparatus.mjs';
import {rebuildSurfaceSamples} from './anatomical-contact.mjs';
const mix=(a,b,t)=>a.map((v,d)=>v*(1-t)+b[d]*t);
export function interiorSegmentWitnesses(tree,A,B){
 const hits=tree.segmentHits(A,B),cuts=[0,...hits.map(h=>h.time),1].filter((v,i,a)=>!i||v-a[i-1]>1e-12),witnesses=[];
 for(let i=1;i<cuts.length;i++){
  const t=(cuts[i-1]+cuts[i])/2,query=tree.closest(mix(A,B,t));
  if(query.signedDistanceM<0)witnesses.push({t,pointM:mix(A,B,t),signedDistanceM:query.signedDistanceM,interval:[cuts[i-1],cuts[i]]});
 }
 return witnesses;
}
// Insert a material witness into a conforming local partition. Shared-edge
// witnesses split both adjacent children. Positive weights conserve face area.
export function splitMaterialTriangle(children,L){
 if(children.some(c=>c.some(P=>Math.hypot(...P.map((v,d)=>v-L[d]))<1e-12)))return false;
 let changed=false;const next=[];
 for(const child of children){
  const closest=closestTriangle(L,child);
  if(Math.hypot(...closest.point.map((v,d)=>v-L[d]))>1e-12){next.push(child);continue;}
  const b=closest.barycentric;
  for(let k=0;k<3;k++)if(b[(k+2)%3]>1e-12)next.push([child[k],child[(k+1)%3],L]);
  changed=true;
 }
 if(changed)children.splice(0,children.length,...next);return changed;
}
export function rebuildBoneSamples(bone){
 const samples=[],vertices=new Map();
 for(const [face,children] of bone.materialTriangles.entries()){
  const X=bone.source.triangles[face].map(i=>bone.source.vertices_m[i]);
  for(const child of children){
   const P=child.map(L=>[0,1,2].map(d=>L.reduce((s,w,i)=>s+w*X[i][d],0))),a=P[1].map((v,d)=>v-P[0][d]),b=P[2].map((v,d)=>v-P[0][d]),area=Math.hypot(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])/2;
   samples.push({referenceM:[0,1,2].map(d=>P.reduce((s,p)=>s+p[d]/3,0)),areaM2:area*.5,sourceFace:face});
   for(const referenceM of P){const key=referenceM.map(v=>v.toPrecision(15)).join(',');if(!vertices.has(key))vertices.set(key,{referenceM,areaM2:0});vertices.get(key).areaM2+=area/6;}
  }
 }
 bone.samples=[...samples,...vertices.values()];
}
export function refineContactFromGeometry(model,contact,x,positions){
 const q=x[model.jointIndex]/JOINT_SCALE_M,B=model.bones.map((b,i)=>b.vertices_m.map(P=>i?attachmentMap(P,model.frame,q).position:P)),boneTrees=B.map((v,i)=>triangleTree(v,model.bones[i].triangles)),bodyTrees=positions.map((p,i)=>triangleTree(p.nodesM,model.bodies[i].modal.source.surface_triangles));
 let bodyWitnesses=0,boneWitnesses=0,tendonWitnesses=0,softWitnesses=0;const examples=[];
 for(let i=0;i<model.bodies.length;i++)for(let j=0;j<model.bones.length;j++){
  const surface=contact.surfaces[i],bone=contact.bones[j],ti=model.bodies[i].modal.source.surface_triangles,bj=model.bones[j].triangles;
  const crossings=transverseCrossings(triangleRecords(positions[i].nodesM,ti),triangleRecords(B[j],bj),{maximumExamples:Infinity});
  for(const [face,boneFace] of crossings.examples){
   for(let k=0;k<3;k++){
    const a=k,b=(k+1)%3;
    for(const w of interiorSegmentWitnesses(boneTrees[j],positions[i].nodesM[ti[face][a]],positions[i].nodesM[ti[face][b]])){
     const L=[0,0,0];L[a]=1-w.t;L[b]=w.t;
     if(splitMaterialTriangle(surface.materialTriangles[face],L)){bodyWitnesses++;if(examples.length<12)examples.push({kind:'muscle-bone',body:i,bone:j,face,...w});}
    }
    for(const w of interiorSegmentWitnesses(bodyTrees[i],B[j][bj[boneFace][a]],B[j][bj[boneFace][b]])){
     if(!bone.materialTriangles){bone.source=model.bones[j];bone.materialTriangles=bj.map(()=>[[[1,0,0],[0,1,0],[0,0,1]]]);}
     const L=[0,0,0];L[a]=1-w.t;L[b]=w.t;
     if(splitMaterialTriangle(bone.materialTriangles[boneFace],L)){boneWitnesses++;}
    }
   }
  }
 }
 // The same missed-sample failure can occur between two deforming bellies.
 // Refine both material surfaces, retaining the symmetric half-area law.
 for(let i=0;i<model.bodies.length;i++)for(let j=i+1;j<model.bodies.length;j++){
  const facesI=model.bodies[i].modal.source.surface_triangles,facesJ=model.bodies[j].modal.source.surface_triangles;
  const crossings=transverseCrossings(triangleRecords(positions[i].nodesM,facesI),triangleRecords(positions[j].nodesM,facesJ),{maximumExamples:Infinity});
  for(const [faceI,faceJ] of crossings.examples)for(const [a,b,face,faces] of [[i,j,faceI,facesI],[j,i,faceJ,facesJ]])for(let k=0;k<3;k++){
   const l=(k+1)%3;
   for(const w of interiorSegmentWitnesses(bodyTrees[b],positions[a].nodesM[faces[face][k]],positions[a].nodesM[faces[face][l]])){
    const L=[0,0,0];L[k]=1-w.t;L[l]=w.t;
    if(splitMaterialTriangle(contact.surfaces[a].materialTriangles[face],L)){softWitnesses++;if(examples.length<12)examples.push({kind:'muscle-muscle',body:a,otherBody:b,face,...w});}
   }
  }
 }
 for(const [branchIndex,branch] of model.branches.entries()){
  const points=branch.path.map(p=>evaluatePoint(p,x,model).position);
  for(let leg=0;leg<points.length-1;leg++)for(let bone=0;bone<boneTrees.length;bone++){
   for(const w of interiorSegmentWitnesses(boneTrees[bone],points[leg],points[leg+1])){
    const key=branchIndex+':'+leg,knots=contact.tendonKnots.get(key)||[0,.25,.5,.75,1];
    if(knots.every(t=>Math.abs(t-w.t)>1e-12)){knots.push(w.t);knots.sort((a,b)=>a-b);contact.tendonKnots.set(key,knots);tendonWitnesses++;if(examples.length<12)examples.push({kind:'tendon-bone',branchIndex,leg,bone,...w});}
   }
  }
 }
 const added=bodyWitnesses+boneWitnesses+tendonWitnesses+softWitnesses;
 if(added){for(const s of contact.surfaces)rebuildSurfaceSamples(s);for(const b of contact.bones)if(b.materialTriangles)rebuildBoneSamples(b);contact.refinementRounds++;}
 return {added,bodyWitnesses,boneWitnesses,tendonWitnesses,softWitnesses,examples};
}
// Persist the material rule with the state; processes and workers can replay
// exactly the same potential rather than silently reverting its quadrature.
export function contactRecipe(contact){return structuredClone({schema:1,surfaces:contact.surfaces.map(s=>s.materialTriangles),bones:contact.bones.map(b=>b.materialTriangles||null),tendonKnots:[...contact.tendonKnots],refinementRounds:contact.refinementRounds});}
export function restoreContactRecipe(contact,recipe){
 if(!recipe)return;
 if(recipe.schema!==1||recipe.surfaces.length!==contact.surfaces.length||recipe.bones.length!==contact.bones.length)throw new RangeError('Contact recipe shape');
 recipe.surfaces.forEach((triangles,i)=>{contact.surfaces[i].materialTriangles=structuredClone(triangles);rebuildSurfaceSamples(contact.surfaces[i]);});
 recipe.bones.forEach((triangles,i)=>{const b=contact.bones[i];if(triangles){b.materialTriangles=structuredClone(triangles);rebuildBoneSamples(b);}else{delete b.materialTriangles;b.samples=b.referenceSamples;}});
 contact.tendonKnots=new Map(structuredClone(recipe.tendonKnots));contact.refinementRounds=recipe.refinementRounds;
}

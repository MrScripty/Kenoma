/** Authored radial crown/capitellum regions, evaluated against source triangles.
 * Finite sampled geometry diagnostics, not cartilage/contact validation. */
import {readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {surface,connectedRegion,geodesicRegion,patchRecord,sub,dot} from './anatomical-surface.mjs';
import {triangleTree} from '../web/anatomical-distance.mjs';
import {attachmentMap} from '../web/anatomical-transfer.mjs';
const base=fileURLToPath(new URL('../data/anatomical-arm-v1/',import.meta.url));
const bytes=await readFile(base+'generated/arm-geometry.json'),g=JSON.parse(bytes),picks=JSON.parse(await readFile(base+'config/landmarks.json'));
const h=g.bones[0],r=g.bones[1],H=surface(h),R=surface(r),axis=g.frame.proximal_unit;
const seedPoint=picks.landmarks.capitellum.atlas_position_m;
const seed=H.faces.reduce((best,f)=>Math.hypot(...sub(f.centroid,seedPoint))<Math.hypot(...sub(H.faces[best].centroid,seedPoint))?f.id:best,0);
const capIds=geodesicRegion(H,seed,()=>true,.015);
const maxZ=Math.max(...r.vertices_m.map(X=>dot(X,axis)));
const crown=connectedRegion(R,f=>dot(f.centroid,axis)>maxZ-.016&&dot(f.normal,axis)>.45);
const crownPatch=patchRecord(R,crown.ids.toSorted((a,b)=>a-b),'Radial head proximal crown candidate',{maximum_proximal_depth_m:.016,minimum_proximal_normal_dot:.45,component_sizes:crown.component_sizes});
const capPatch=patchRecord(H,capIds,'Capitellum candidate around retained source pick',{seed_source_face:seed,geodesic_limit_m:.015,seed_evidence:'Original authored capitellum pick; not a measured cartilage border.'});
const restricted=triangleTree(h.vertices_m,capIds.map(i=>h.triangles[i])),whole=triangleTree(h.vertices_m,h.triangles);
function weighted(rows,p){const sorted=rows.toSorted((a,b)=>a.distanceM-b.distanceM);let sum=0;for(const row of sorted){sum+=row.areaWeight;if(sum>=p)return row.distanceM;}return sorted.at(-1).distanceM;}
const poses=[];for(let degrees=0;degrees<=120;degrees+=5){const q=degrees*Math.PI/180,rows=crownPatch.triangle_centroids_m.map((X,i)=>{const P=attachmentMap(X,g.frame,q).position,c=restricted.closest(P,{signed:false}),w=whole.closest(P);return {sourceRadiusFace:crownPatch.triangle_indices_zero_based[i],areaWeight:crownPatch.triangle_area_weights[i],distanceM:c.distanceM,sourceHumerusFace:capIds[c.triangle],closestBarycentric:c.barycentric,wholeHumerusSignedDistanceM:w.signedDistanceM};}),vertices=[...new Set(crownPatch.triangle_indices_zero_based.flatMap(i=>r.triangles[i]))],vd=vertices.map(i=>restricted.closest(attachmentMap(r.vertices_m[i],g.frame,q).position,{signed:false}).distanceM);poses.push({degrees,minimumSourceVertexDistanceM:Math.min(...vd),minimumFaceCentroidDistanceM:Math.min(...rows.map(x=>x.distanceM)),areaWeightedMedianM:weighted(rows,.5),areaWeightedP95M:weighted(rows,.95),maximumFaceCentroidDistanceM:Math.max(...rows.map(x=>x.distanceM)),maximumInsideWholeHumerusM:Math.max(0,...rows.map(x=>-x.wholeHumerusSignedDistanceM)),nearestFacePair:rows.toSorted((a,b)=>a.distanceM-b.distanceM)[0],rows});}
const receipt={schema:1,source_sha256:g.source_sha256,geometry_sha256:createHash('sha256').update(bytes).digest('hex'),frame:g.frame,regions:{radialCrown:crownPatch,capitellum:capPatch},poses,limits:['These authored source regions require anatomical review; the atlas has no cartilage segmentation.','Distances are sampled vertices/area-weighted face centroids to actual continuous capitellum candidate triangles, not a global triangle-to-triangle minimum.','A restricted open patch has no inside/outside interpretation; signed diagnostics query the entire closed humerus separately.','Twenty-five discrete poses do not certify continuous-angle apposition or physiological compression.']};
await writeFile(base+'audit/radial-apposition-results.json',JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({regions:{radiusFaces:crownPatch.triangle_indices_zero_based.length,capitellumFaces:capIds.length},at90:poses.find(x=>x.degrees===90),maximumInsideWholeHumerusM:Math.max(...poses.map(x=>x.maximumInsideWholeHumerusM))}));

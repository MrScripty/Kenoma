/** Exact pure geometry formulas copied from pinned 0b18 operator modules.
 * No quadrature, material, apparatus preparation or force evaluation. */
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),sub=(a,b)=>a.map((v,i)=>v-b[i]),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
export function prepareGeometryBody(m){
 const rings=m.segmentation.rings,sectors=m.segmentation.sectors;if(rings!==7||sectors!==16)throw new RangeError('Explicit seven-ring mode definition');
 const [start,end]=m.belly_interval_m,b=m.basis,length=end-start,radius=Math.sqrt(m.reference_volume_m3/(Math.PI*length)),nodeModes=m.nodes_m.map(X=>{
  const z=dot(sub(X,b.origin),b.axis),t=Math.max(0,Math.min(rings-1,(z-start)/length*(rings-1))),r=Math.min(rings-2,Math.floor(t)),fraction=t-r,center=m.centerline_m[r].map((v,d)=>v+(m.centerline_m[r+1][d]-v)*fraction),rel=sub(X,center),uv=[1,dot(rel,b.u)/radius,dot(rel,b.v)/radius],rows=[];for(const [ring,h] of [[r,1-fraction],[r+1,fraction]])for(let k=0;k<3;k++)if(Math.abs(h*uv[k])>1e-14)rows.push({base:ring*9+k*3,value:h*uv[k]});return rows;
 });
 return {source:m,nodeModes};
}
export function modalPositions(body,x){return body.source.nodes_m.map((X,i)=>X.map((v,d)=>v+body.nodeModes[i].reduce((s,m)=>s+m.value*x[m.base+d],0)));}
export function attachmentMap(referencePoint,frame,q,{moving=true}={}){
 if(![q,...referencePoint,...frame.origin_m,...frame.axis_unit,frame.atlas_bind_angle_rad].every(Number.isFinite)||Math.abs(Math.hypot(...frame.axis_unit)-1)>1e-10)throw new RangeError('Rigid attachment frame');
 if(!moving)return {position:referencePoint.slice(),B:[0,0,0]};
 const r=sub(referencePoint,frame.origin_m),e=frame.axis_unit,c=Math.cos(q-frame.atlas_bind_angle_rad),s=Math.sin(q-frame.atlas_bind_angle_rad),exr=cross(e,r),projection=dot(e,r),rotated=r.map((v,i)=>c*v+s*exr[i]+(1-c)*projection*e[i]);
 return {position:rotated.map((v,i)=>v+frame.origin_m[i]),B:cross(e,rotated)};
}
export function geometryMapper(g){
 if(g.muscles.length!==7||g.bones.length!==3||g.muscles.some(m=>m.nodes_m.length!==585))throw Error('Pinned seven-body geometry required');
 const bodies=g.muscles.map(prepareGeometryBody);
 return coordinates=>{
  if(coordinates.length!==460||!Array.from(coordinates).every(Number.isFinite))throw Error('Geometry coordinates');
  const q=coordinates[459]/.1;
  return {muscles:bodies.map((b,i)=>modalPositions(b,coordinates.slice(i*63,i*63+63))),bones:g.bones.map((b,j)=>b.vertices_m.map(X=>j?attachmentMap(X,g.frame,q).position:X)),omittedCoordinateIndices:Array.from({length:18},(_,i)=>441+i)};
 };
}

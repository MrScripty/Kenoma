/** Read-only material-section geometry; no material, quadrature or solver imports. */
export const EDGES = [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]];
export const dot = (a,b) => a.reduce((s,v,i)=>s+v*b[i],0);
export const sub = (a,b) => a.map((v,i)=>v-b[i]);
export const cross = (a,b) => [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const norm = a => Math.hypot(...a);
const check = (ok,message) => {if(!ok) throw new Error(message);};
const point = p => Array.isArray(p)&&p.length===3&&p.every(Number.isFinite);
export function p2Shape(L) {
  return [...L.map(l=>l*(2*l-1)),...EDGES.map(([i,j])=>4*L[i]*L[j])];
}
export function interpolate(nodes,element,L) {
  const N=p2Shape(L);
  return [0,1,2].map(d=>element.reduce((s,n,i)=>s+N[i]*nodes[n][d],0));
}
export function validateModel(model) {
  check(model.schema===1&&model.bones.length===3&&model.muscles.length===7,'Model inventory');
  check(model.stationarityToleranceN===0.0001,'Original stationarity gate changed');
  for(const bone of model.bones) {
    check(bone.vertices_m.every(point),'Invalid bone position');
    check(bone.triangles.every(t=>t.length===3&&t.every(i=>Number.isInteger(i)&&i>=0&&i<bone.vertices_m.length)),'Invalid bone face');
  }
  for(const [id,patch] of Object.entries(model.patches)) {
    const bone=model.bones.find(b=>b.element_id===patch.element_id);
    check(bone&&patch.triangle_indices_zero_based.length>0,'Missing patch bone '+id);
    check(new Set(patch.triangle_indices_zero_based).size===patch.triangle_indices_zero_based.length,'Repeated patch face');
    check(patch.triangle_area_weights.length===patch.triangle_indices_zero_based.length,'Patch weight inventory');
    check(patch.triangle_area_weights.every(w=>Number.isFinite(w)&&w>0)&&Math.abs(patch.triangle_area_weights.reduce((s,w)=>s+w,0)-1)<1e-10,'Invalid patch weights');
    let area=0;
    patch.triangle_indices_zero_based.forEach((n,i)=>{
      check(Number.isInteger(n)&&n>=0&&n<bone.triangles.length,'Patch source face outside bone');
      const [a,b,c]=bone.triangles[n].map(j=>bone.vertices_m[j]);
      const A=norm(cross(sub(b,a),sub(c,a)))/2;area+=A;
      check(Math.abs(A-patch.triangle_area_m2[i])<1e-12,'Patch area/source face mismatch');
      const centroid=a.map((v,d)=>(v+b[d]+c[d])/3);
      check(norm(sub(centroid,patch.triangle_centroids_m[i]))<1e-10,'Patch centroid/source face mismatch');
      check(Math.abs(A/patch.area_m2-patch.triangle_area_weights[i])<1e-10,'Patch area weight mismatch');
    });
    check(Math.abs(area-patch.area_m2)<1e-12,'Patch total area mismatch');
  }
  for(const m of model.muscles) {
    check(m.nodes_m.every(point)&&m.elements_ten_node.length>0,'Invalid body positions');
    check(point(m.basis.origin)&&m.surface_triangles.every(t=>t.length===3&&t.every(n=>Number.isInteger(n)&&n>=0&&n<m.nodes_m.length)),'Invalid body surface or basis origin');
    check(m.belly_interval_m.length===2&&m.belly_interval_m[1]>m.belly_interval_m[0],'Invalid station interval');
    for(const e of m.elements_ten_node) {
      check(e.length===10&&e.every(n=>Number.isInteger(n)&&n>=0&&n<m.nodes_m.length),'Invalid P2 topology');
      EDGES.forEach(([i,j],k)=>{
        const mid=m.nodes_m[e[i]].map((v,d)=>(v+m.nodes_m[e[j]][d])/2);
        check(norm(sub(mid,m.nodes_m[e[k+4]]))<1e-10,'Curved reference unsupported: straight P2 reference edges required');
      });
    }
    check(Math.abs(dot(m.basis.u,m.basis.v))<1e-10&&Math.abs(dot(m.basis.axis,m.basis.u))<1e-10&&Math.abs(dot(m.basis.axis,m.basis.v))<1e-10,'Invalid section basis');
    check([m.basis.u,m.basis.v,m.basis.axis].every(a=>point(a)&&Math.abs(norm(a)-1)<1e-10),'Nonunit section basis');
    for(const end of ['proximal','distal']) {
      const a=model.attachments.find(a=>a.element_id===m.element_id)?.[end];
      check(a&&((a.kind==='distributed_bone_patch'&&model.patches[a.patch_id])||(a.kind==='fixed_estimated_origin'&&point(a.anchor_m))),'Missing attachment ownership');
    }
    if(m.frozen) {
      const f=m.frozen;
      check(f.positions_m.length===m.nodes_m.length&&f.positions_m.every(point),'Frozen position inventory');
      check(f.held.length===m.nodes_m.length&&f.held.every(x=>typeof x==='boolean'),'Frozen held inventory');
      const held=new Set([...m.proximal_nodes,...m.distal_nodes]);
      check(f.held.every((v,i)=>v===held.has(i)),'Original fixed cap changed');
      check(f.held.every((v,i)=>!v||norm(sub(f.positions_m[i],m.nodes_m[i]))<1e-12),'Frozen cap displacement');
      check(Number.isFinite(f.maximumFreeNodalComponentN)&&f.maximumFreeNodalComponentN>model.stationarityToleranceN&&f.passesFullNodalForceGateAtFrozenPose===false,'Frozen failure must remain visible');
    }
  }
  return true;
}
/** Plane cuts in material/reference space, then evaluate the recorded P2 map.
 * This is a deformed material section, NOT a current-space planar slice or J.
 * Triangular tessellation area is approximate for a curved P2 current map. */
export function section(m,fraction,subdivisions=4) {
  check(Number.isFinite(fraction)&&fraction>0&&fraction<1,'Interior material station required');
  check(Number.isInteger(subdivisions)&&subdivisions>=1&&subdivisions<=12,'Section tessellation bound');
  const {origin,axis,u,v}=m.basis;
  const station=m.belly_interval_m[0]+fraction*(m.belly_interval_m[1]-m.belly_interval_m[0]);
  const triangles=[],seen=new Set();
  for(const [elementIndex,e] of m.elements_ten_node.entries()) {
    const X=e.slice(0,4).map(n=>m.nodes_m[n]);
    const signed=X.map(p=>dot(sub(p,origin),axis)-station);
    if(Math.min(...signed)>1e-11||Math.max(...signed)<-1e-11) continue;
    const points=[];
    const add=L=>{const p=interpolate(m.nodes_m,e,L);if(!points.some(q=>norm(sub(p,q.p))<1e-10))points.push({L,p});};
    signed.forEach((s,i)=>{if(Math.abs(s)<=1e-11)add([0,1,2,3].map(j=>i===j?1:0));});
    for(const [i,j] of EDGES) if(signed[i]*signed[j]<0&&Math.abs(signed[i])>1e-11&&Math.abs(signed[j])>1e-11) {
      const t=signed[i]/(signed[i]-signed[j]);add([0,1,2,3].map(k=>k===i?1-t:k===j?t:0));
    }
    if(points.length<3) continue;
    const center=[0,1,2].map(d=>points.reduce((s,q)=>s+q.p[d],0)/points.length);
    points.sort((a,b)=>Math.atan2(dot(sub(a.p,center),v),dot(sub(a.p,center),u))-Math.atan2(dot(sub(b.p,center),v),dot(sub(b.p,center),u)));
    for(let k=1;k<points.length-1;k++) {
      const base=[points[0],points[k],points[k+1]];
      const key=base.map(q=>q.p.map(x=>Math.round(x*1e10)).join(',')).sort().join(';');
      if(seen.has(key))continue;seen.add(key);
      const at=(i,j)=>{
        const w=[1-(i+j)/subdivisions,i/subdivisions,j/subdivisions];
        const L=[0,1,2,3].map(d=>base.reduce((s,q,k)=>s+w[k]*q.L[d],0));
        return {reference:interpolate(m.nodes_m,e,L),current:interpolate(m.frozen?.positions_m??m.nodes_m,e,L)};
      };
      for(let i=0;i<subdivisions;i++)for(let j=0;j<subdivisions-i;j++) {
        triangles.push({elementIndex,vertices:[at(i,j),at(i+1,j),at(i,j+1)]});
        if(i+j<subdivisions-1)triangles.push({elementIndex,vertices:[at(i+1,j),at(i+1,j+1),at(i,j+1)]});
      }
    }
  }
  check(triangles.length>0,'Empty material section');
  const metrics=which=>{
    let area=0,projectedArea=0;const U=[],V=[];
    for(const t of triangles) {
      const [a,b,c]=t.vertices.map(p=>p[which]);const n=cross(sub(b,a),sub(c,a));
      area+=norm(n)/2;projectedArea+=Math.abs(dot(n,axis))/2;
      for(const p of [a,b,c]){U.push(dot(sub(p,origin),u));V.push(dot(sub(p,origin),v));}
    }
    return {tessellatedAreaMm2:area*1e6,projectedAreaMm2:projectedArea*1e6,widthMm:(Math.max(...U)-Math.min(...U))*1000,depthMm:(Math.max(...V)-Math.min(...V))*1000};
  };
  return {fraction,stationM:station,subdivisions,triangles,reference:metrics('reference'),current:metrics('current'),maximumSampleDisplacementMm:Math.max(...triangles.flatMap(t=>t.vertices.map(p=>norm(sub(p.current,p.reference))*1000)))};
}

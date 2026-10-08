import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {EDGES,p2Shape,interpolate,section,validateModel} from './geometry.mjs';
const near=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)<t,`${a} != ${b}`);
const nodes=c=>[...c,...EDGES.map(([i,j])=>c[i].map((v,d)=>(v+c[j][d])/2))];
const fixture=()=>({basis:{origin:[0,0,0],axis:[0,0,1],u:[1,0,0],v:[0,1,0]},belly_interval_m:[0,1],nodes_m:nodes([[0,0,0],[1,0,0],[0,1,0],[0,0,1]]),elements_ten_node:[[0,1,2,3,4,5,6,7,8,9]]});
test('P2 partition of unity and nodal interpolation, including negative corner shape values',()=>{
  for(const L of [[1,0,0,0],[.1,.2,.3,.4],[.25,.25,.25,.25]])near(p2Shape(L).reduce((s,v)=>s+v,0),1);
  const m=fixture();const values=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],...EDGES.map(([i,j])=>[0,1,2,3].map(k=>k===i||k===j?.5:0))];
  values.forEach((L,i)=>interpolate(m.nodes_m,m.elements_ten_node[0],L).forEach((v,d)=>near(v,m.nodes_m[i][d])));
  assert.ok(p2Shape([.25,.25,.25,.25])[0]<0);
});
test('independent planar tetrahedron area and affine map oracle',()=>{
  const m=fixture();m.frozen={positions_m:m.nodes_m.map(([x,y,z])=>[2*x+.1,3*y-.2,4*z+.3])};
  for(const n of [1,4,8]) {
    const s=section(m,.5,n);near(s.reference.tessellatedAreaMm2,125000,1e-7);near(s.current.tessellatedAreaMm2,750000,1e-6);
    near(s.reference.widthMm,500);near(s.current.widthMm,1000);near(s.current.depthMm,1500);
    for(const t of s.triangles)for(const p of t.vertices){near(p.reference[2],.5);near(p.current[2],2.3);}
  }
});
test('shared coplanar tetrahedron face is counted once',()=>{
  const a=fixture(),other=nodes([[0,0,0],[1,0,0],[0,1,0],[0,0,-1]]);
  a.nodes_m.push(...other);a.elements_ten_node.push([10,11,12,13,14,15,16,17,18,19]);a.belly_interval_m=[-1,1];
  near(section(a,.5,4).reference.tessellatedAreaMm2,500000,1e-6);
});
test('curved P2 material section is not silently flattened to a spatial plane',()=>{
  const m=fixture();m.frozen={positions_m:m.nodes_m.map(p=>p.slice())};m.frozen.positions_m[4][2]+=.3;
  const s=section(m,.5,8),z=s.triangles.flatMap(t=>t.vertices.map(p=>p.current[2]));
  assert.ok(Math.max(...z)-Math.min(...z)>.05);assert.ok(s.current.tessellatedAreaMm2>s.current.projectedAreaMm2);
});
test('station and tessellation domain reject unsupported requests',()=>{
  const m=fixture();for(const f of [0,1,NaN,-.1])assert.throws(()=>section(m,f));
  for(const n of [0,13,3.5])assert.throws(()=>section(m,.5,n));
});
if(process.env.KENOMA_SECTION_MODEL) {
 const m=JSON.parse(fs.readFileSync(process.env.KENOMA_SECTION_MODEL));
 test('actual retained bones, all eight source patches, all seven straight P2 bodies and fixed caps validate',()=>assert.equal(validateModel(m),true));
 test('actual uneven body sections vary by station; saved fields remain separate and nonstationary',()=>{
   for(const body of m.muscles){const areas=[.2,.35,.5,.65,.8].map(f=>section(body,f).reference.tessellatedAreaMm2);assert.ok(Math.max(...areas)-Math.min(...areas)>1);}
   assert.equal(m.muscles.filter(b=>b.frozen).length,3);
   for(const body of m.muscles.filter(b=>b.frozen)){assert.ok(section(body,.5).maximumSampleDisplacementMm>1);assert.equal(body.frozen.passesFullNodalForceGateAtFrozenPose,false);}
 });
 test('damaged source face, centroid, weight, reference edge, cap and hidden force failure are refused',()=>{
   const damage=[x=>x.patches.radial_tuberosity.triangle_indices_zero_based[0]=999999,
     x=>x.patches.radial_tuberosity.triangle_centroids_m[0][0]+=.001,
     x=>x.patches.radial_tuberosity.triangle_area_weights[0]=0,
     x=>x.muscles[0].nodes_m[112][0]+=.001,
     x=>x.muscles[0].frozen.positions_m[0][0]+=.001,
     x=>x.muscles[0].frozen.passesFullNodalForceGateAtFrozenPose=true];
   for(const mutate of damage){const copy=structuredClone(m);mutate(copy);assert.throws(()=>validateModel(copy));}
 });
}

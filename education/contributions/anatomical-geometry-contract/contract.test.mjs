import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';
import {signedP2VolumeM3} from './p2-volume.mjs';import {evaluateGeometry,observeApparatusPositions} from './contract.mjs';
const near=(a,b,t=1e-12)=>assert.ok(Math.abs(a-b)<t,`${a} vs ${b}`);
const pairs=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],corners=[[0,0,0],[1,0,0],[0,1,0],[0,0,1]],X=[...corners,...pairs.map(([i,j])=>corners[i].map((v,d)=>(v+corners[j][d])/2))];
test('reference, translation and general affine determinant volumes match analytic oracle',()=>{
 near(signedP2VolumeM3(X),1/6);
 const F=[[2,.3,.1],[0,3,.2],[0,0,4]],current=X.map(p=>F.map(row=>row.reduce((s,v,i)=>s+v*p[i],0)));
 near(signedP2VolumeM3(current),4);
 near(signedP2VolumeM3(current.map(p=>p.map((v,d)=>v+[100,-200,300][d]))),4,1e-10);
});
test('curved P2 determinant polynomial integrates analytic quadratic map',()=>{
 for(const a of [.3,2,-.2])near(signedP2VolumeM3(X.map(([r,s,t])=>[r+a*r*r,s,t])),1/6+a/12);
});
test('signed volume stays signed and cannot certify no folds',()=>{
 near(signedP2VolumeM3(X.map(([r,s,t])=>[-r,s,t])),-1/6);
 // x=r-1.5r² has local determinant 1-3r, negative near r=1, but positive integral.
 near(signedP2VolumeM3(X.map(([r,s,t])=>[r-1.5*r*r,s,t])),1/24);
});
test('polynomial operator rejects missing/nonfinite nodal fields',()=>{
 assert.throws(()=>signedP2VolumeM3(X.slice(1)));const bad=structuredClone(X);bad[4][2]=NaN;assert.throws(()=>signedP2VolumeM3(bad));
});
if(process.env.KENOMA_GEOMETRY_OUTPUT){
 const root=process.env.KENOMA_GEOMETRY_OUTPUT,contract=JSON.parse(fs.readFileSync(path.join(root,'geometry-contract.json'))),reference=JSON.parse(fs.readFileSync(path.join(root,'reference-observables.json'))),frozen=JSON.parse(fs.readFileSync(path.join(root,'frozen-observables.json')));
 test('42 complete connected retained regions and 35 adjacent face interfaces',()=>{
  for(const b of contract.bodies){assert.equal(b.regionPartition.groups.length,6);assert.equal(b.regionPartition.interfaces.length,5);assert.equal(b.regionPartition.groups.flatMap(g=>g.elementIndices).length,252);assert.equal(new Set(b.regionPartition.groups.flatMap(g=>g.elementIndices)).size,252);assert.ok(b.regionPartition.groups.every(g=>g.elementIndices.length===42));}
 });
 test('all regional reference sums reproduce original body volume; recorded full-force failures remain separate',()=>{
  for(const b of reference.bodies){const source=contract.bodies.find(c=>c.id===b.id);near(b.referenceVolumeM3,source.declaredReferenceVolumeM3,1e-15);near(b.regions.reduce((s,r)=>s+r.referenceVolumeM3,0),b.referenceVolumeM3,1e-15);near(b.regions.reduce((s,r)=>s+r.signedVolumeM3,0),b.signedVolumeM3,1e-15);}
  assert.equal(frozen.bodies.filter(b=>b.fieldProvided).length,3);assert.equal(frozen.status,'GEOMETRY_ONLY_NO_FORCE_EVALUATION');
  for(const b of frozen.bodies.filter(b=>b.fieldProvided)){assert.equal(b.recordedForceFailure.forceGate,false);assert.equal(b.recordedForceFailure.unchangedGateN,.0001);assert.ok(b.recordedForceFailure.maximumFreeNodalComponentN>50);assert.ok(b.regions.some(r=>Math.abs(r.signedVolumeRatio-1)>.001));}
 });
 test('585 retained routes bind exact existing cap/patch samples, with explicit literals for the rest',()=>{
  assert.equal(contract.routes.length,585);const counts=contract.routes.flatMap(r=>[r.a,r.b]).reduce((s,b)=>(s[b.kind]=(s[b.kind]||0)+1,s),{});assert.deepEqual(counts,{existing_cap_sample:560,retained_literal_endpoint:473,existing_patch_sample:137});
  for(const r of contract.routes){const evaluated=reference.routes[r.sourceIndex];near(Math.hypot(...evaluated.pathM[0].map((v,d)=>v-r.repairedEndpointsM[0][d])),0);near(Math.hypot(...evaluated.pathM.at(-1).map((v,d)=>v-r.repairedEndpointsM[1][d])),0);}
 });
 test('actual geometry consumer connects supplied body positions to cap points and tendon endpoint lengths',()=>{
  const body=contract.bodies.find(b=>b.id==='FJ1486'),shift=[.001,-.002,.003],positions=body.nodesM.map(p=>p.map((v,d)=>v+shift[d]));
  const result=evaluateGeometry(contract,{bodyPositionsById:{FJ1486:positions},fieldLabel:'kinematic translation test only'});
  const ref=reference.bodies.find(b=>b.id===body.id),b=result.bodies.find(b=>b.id===body.id);near(b.signedVolumeM3,ref.signedVolumeM3,1e-15);
  const i=contract.routes.findIndex(r=>r.a.kind==='existing_cap_sample'&&r.a.bodyId===body.id);assert.ok(i>=0);
  for(let d=0;d<3;d++)near(result.routes[i].pathM[0][d]-reference.routes[i].pathM[0][d],shift[d]);
  assert.ok(Math.abs(result.routes[i].lengthM-reference.routes[i].lengthM)>1e-5);assert.equal(b.recordedForceFailure.forceGate,false);
 });
 test('original patch sample positions connect to existing route endpoints without moving fixed guides',()=>{
  const p=contract.patches.find(p=>p.id==='radial_tuberosity'),positions=p.samples.map(s=>s.referencePositionM.map((v,d)=>v+(d===0?.001:0))),r=evaluateGeometry(contract,{patchPositionsById:{radial_tuberosity:positions},fieldLabel:'kinematic patch test only'});
  const i=contract.routes.findIndex(r=>r.b.kind==='existing_patch_sample'&&r.b.patchId===p.id);assert.ok(i>=0);near(r.routes[i].pathM.at(-1)[0]-reference.routes[i].pathM.at(-1)[0],.001);assert.deepEqual(r.routes[i].pathM.slice(1,-1),reference.routes[i].pathM.slice(1,-1));
 });
 test('unknown/incomplete/nonfinite supplied fields and damaged regional membership are refused',()=>{
  assert.throws(()=>evaluateGeometry(contract,{bodyPositionsById:{unknown:X}}));assert.throws(()=>evaluateGeometry(contract,{bodyPositionsById:{FJ1486:X}}));
  const bad=structuredClone(contract.bodies[0].nodesM);bad[0][0]=NaN;assert.throws(()=>evaluateGeometry(contract,{bodyPositionsById:{FJ1486:bad}}));
  assert.throws(()=>evaluateGeometry(contract,{patchPositionsById:{radial_tuberosity:[]}}));
  const damaged=structuredClone(contract);damaged.bodies[0].regionPartition.groups[0].elementIndices[0]=damaged.bodies[0].regionPartition.groups[0].elementIndices[1];assert.throws(()=>evaluateGeometry(damaged));
 });
 test('portable artifact executes with the included exact section-geometry dependency',async()=>{
  const module=await import(pathToFileURL(path.join(root,'adapter/anatomical-geometry-contract/contract.mjs')));const r=module.evaluateGeometry(contract);near(r.bodies[0].signedVolumeM3,reference.bodies[0].signedVolumeM3);assert.equal(r.routes.length,585);
 });
 test('direct existing apparatus position-record adapter connects all seven bodies and rejects incomplete/duplicate records',()=>{
  const rows=contract.bodies.map(b=>({elementId:b.id,nodesM:b.recordedField?.positionsM??b.nodesM}));
  const result=observeApparatusPositions(contract,rows,{fieldLabel:'record-shape test; retained nonstationary positions'});
  assert.equal(result.bodies.length,7);for(const b of result.bodies)near(b.signedVolumeM3,frozen.bodies.find(r=>r.id===b.id).signedVolumeM3,1e-15);
  assert.throws(()=>observeApparatusPositions(contract,rows.slice(1)));const duplicate=rows.slice();duplicate[1]=rows[0];assert.throws(()=>observeApparatusPositions(contract,duplicate));
 });
 test('explicit null/undefined body, patch and apparatus fields never silently fall back to reference',()=>{
  for(const value of [null,undefined]){
   assert.throws(()=>evaluateGeometry(contract,{bodyPositionsById:{FJ1486:value}}));assert.throws(()=>evaluateGeometry(contract,{patchPositionsById:{radial_tuberosity:value}}));
   const rows=contract.bodies.map(b=>({elementId:b.id,nodesM:b.nodesM}));rows[0]={elementId:rows[0].elementId,nodesM:value};assert.throws(()=>observeApparatusPositions(contract,rows));
  }
  const rows=contract.bodies.map(b=>({elementId:b.id,nodesM:b.nodesM}));delete rows[0].nodesM;assert.throws(()=>observeApparatusPositions(contract,rows));
 });
 test('machine-readable area kinds prevent footprint, belly slice, tendon CSA and PCSA substitution',()=>{
  assert.ok(contract.patches.every(p=>p.areaKind.includes('not_tendon_CSA')));
  assert.ok(contract.bodies.flatMap(b=>[...b.caps.proximal,...b.caps.distal]).every(c=>c.areaKind.includes('not_tendon_CSA')));
  assert.ok(reference.bodies.flatMap(b=>b.regions).every(r=>r.sectionAreaKind==='mapped_material_slice_not_tendon_CSA_or_PCSA'));
  assert.ok(contract.quantitySemantics.tendonCSA.startsWith('unavailable'));assert.ok(contract.quantitySemantics.PCSA.startsWith('unavailable'));assert.ok(contract.quantitySemantics.existingTendonA0.startsWith('not exported'));
 });
 test('model quantity definitions carry SI conversion, measurement frame/location and unresolved head/tissue ownership',()=>{
  const q=contract.quantityDefinitions;assert.equal(q.muscle_material_slice_area.toSquareMetres,1e-6);assert.equal(q.projected_material_slice_extent.toMetres,1e-3);
  for(const definition of Object.values(q))for(const other of definition.notEquivalentTo??[])assert.ok(Object.hasOwn(q,other),'Quantity reference must resolve: '+other);
  assert.equal(q.tendon_reference_CSA.status,'UNAVAILABLE_SPECIMEN_MATCHED_MEASUREMENT');assert.equal(q.tendon_current_CSA.status,'UNAVAILABLE_SPECIMEN_MATCHED_MEASUREMENT');
  assert.ok(contract.patches.find(p=>p.id==='radial_tuberosity').quantityContext.headOrTissueIdentity.includes('long/short'));
  assert.ok(contract.patches.find(p=>p.id==='olecranon').quantityContext.headOrTissueIdentity.includes('deep muscular/superficial tendinous'));
  for(const r of reference.bodies.flatMap(b=>b.regions)){assert.equal(r.sectionContext.quantityType,'muscle_material_slice_area');assert.equal(r.sectionContext.subdivisions,4);assert.ok(Number.isFinite(r.sectionContext.materialStationM));assert.equal(r.sectionContext.sourceFrame.axis.length,3);}
 });
}

import test from 'node:test';
import assert from 'node:assert/strict';
import {triangleTree} from '../web/anatomical-distance.mjs';
import {interiorSegmentWitnesses,splitMaterialTriangle} from '../web/anatomical-contact-refinement.mjs';
const V=[[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]],F=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]];
const tree=triangleTree(V,F),area=T=>{const a=T[1].map((v,d)=>v-T[0][d]),b=T[2].map((v,d)=>v-T[0][d]);return Math.hypot(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])/2;};
test('exact leg witnesses expose a narrow entry/exit interval missed by all five samples',()=>{
 const A=[-10,.37,.41],B=[90,.37,.41];
 for(const t of [0,.25,.5,.75,1])assert.ok(tree.closest(A.map((v,d)=>v+t*(B[d]-v))).signedDistanceM>0);
 const w=interiorSegmentWitnesses(tree,A,B);assert.equal(w.length,1);assert.ok(w[0].signedDistanceM<0);assert.ok(Math.abs(w[0].t-.105)<1e-12);assert.deepEqual(w[0].interval,[.1,.11]);
 assert.equal(interiorSegmentWitnesses(tree,[-1,2,.41],[2,2,.41]).length,0);
 assert.equal(interiorSegmentWitnesses(tree,[.2,.37,.41],[.8,.37,.41]).length,1);
});
test('interior and shared-edge material cuts conserve area with positive children',()=>{
 const children=[[[1,0,0],[0,1,0],[0,0,1]]],initial=area(children[0]);
 for(const L of [[.2,.3,.5],[.5,.5,0],[.6,.15,.25]]){
  assert.ok(splitMaterialTriangle(children,L));assert.ok(children.every(t=>area(t)>0));
  assert.ok(Math.abs(children.reduce((s,t)=>s+area(t),0)-initial)<1e-14);
  assert.equal(splitMaterialTriangle(children,L),false);
 }
});
import fs from 'node:fs';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {refineContactFromGeometry,contactRecipe,restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {finitePoseAudit} from '../web/anatomical-audit.mjs';
import {finiteRoutingAudit} from '../web/anatomical-routing-audit.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../data/anatomical-arm-v1/'+p,import.meta.url))),rest=read('audit/arm-rest-results.json');
function armFixture(){return prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{quadrature:'four',parameters:rest.parameters,contactParameters:rest.contactParameters,routingRecipe:read('config/apparatus-routing.json')});}
test('archived force-converged rest exposes its 135 micron humeral tendon interval to the new rule',()=>{
 const prefix='audit/rejected-rest-v1/',d=read(prefix+'receipt.json'),input=p=>read(prefix+'snapshot/data/anatomical-arm-v1/'+p);
 const arm=prepareAnatomicalArm(input('generated/arm-reference.json'),input('config/attachments-apparatus.json'),input('audit/modal-fixed-end-results.json'),{quadrature:'four',parameters:d.parameters,contactParameters:d.contactParameters,routingRecipe:input('config/apparatus-routing.json')}),x=Float64Array.from(d.rejectedCoordinatesM),c=anatomicalConfiguration(arm,x,0,{hessian:false});
 const route=finiteRoutingAudit(arm.model,x);assert.equal(route.accepted,false);assert.equal(route.violations[0].branchIndex,461);assert.equal(c.contact.maximumSampledTendonPenetrationM,0);
 const update=refineContactFromGeometry(arm.model,arm.contact,x,c.positions);assert.ok(update.tendonWitnesses>0);
 assert.ok(anatomicalConfiguration(arm,x,0,{hessian:false}).contact.maximumSampledTendonPenetrationM>7e-6);
 assert.equal(arm.parameters.stationarityToleranceN,.0001);
});
test('force-converged loaded muscle/muscle crossings missed by every sample become active witnesses',()=>{
 const d=read('audit/contact-missed-soft-v3/candidate.json'),arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{quadrature:'four',parameters:d.parameters,contactParameters:d.contactParameters,routingRecipe:read('config/apparatus-routing.json'),contactRule:d.contactRule}),x=Float64Array.from(d.coordinatesM),c=anatomicalConfiguration(arm,x,0,{hessian:false}),areas=arm.contact.surfaces.map(s=>s.samples.reduce((a,p)=>a+p.referenceAreaM2,0));
 assert.equal(d.accepted,false);assert.ok(d.residualN<arm.parameters.stationarityToleranceN);assert.equal(c.contact.maximumSampledSoftPenetrationM,0);
 const audit=finitePoseAudit(arm.model,c.positions,x[arm.model.jointIndex]/.1);assert.equal(audit.transverseCrossingPairs,6);assert.equal(audit.boneTissue.reduce((a,p)=>a+p.crossingPairs,0),0);
 const update=refineContactFromGeometry(arm.model,arm.contact,x,c.positions);assert.ok(update.softWitnesses>0);
 assert.ok(anatomicalConfiguration(arm,x,0,{hessian:false}).contact.maximumSampledSoftPenetrationM>0);
 arm.contact.surfaces.forEach((s,i)=>{assert.ok(s.samples.every(p=>p.referenceAreaM2>0));assert.ok(Math.abs(s.samples.reduce((a,p)=>a+p.referenceAreaM2,0)-areas[i])<1e-14);});
});
for(const [label,candidate,expectedCrossings] of [['loaded',read('audit/arm-loaded-rejected-candidate.json'),24],['quarter',read('audit/activation-continuation-results.json').stages[0],32]]){
 test(`${label}: saved sampled-clear muscle/bone and tendon/bone failures become active contact`,()=>{
  const arm=armFixture(),x=Float64Array.from(candidate.coordinatesM),c=anatomicalConfiguration(arm,x,0,{hessian:false}),base=contactRecipe(arm.contact),areas=arm.contact.surfaces.map(s=>s.samples.reduce((t,p)=>t+p.referenceAreaM2,0)),boneAreas=arm.contact.bones.map(b=>b.samples.reduce((t,p)=>t+p.areaM2,0));
  assert.equal(c.contact.maximumSampledBonePenetrationM,0);assert.equal(c.contact.maximumSampledTendonPenetrationM,0);
  assert.equal(finitePoseAudit(arm.model,c.positions,x[arm.model.jointIndex]/.1).transverseCrossingPairs,expectedCrossings);
  const route=finiteRoutingAudit(arm.model,x);assert.equal(route.accepted,false);assert.equal(route.violations.length,1);assert.equal(route.violations[0].branchIndex,112);assert.ok(route.violations[0].minimumSampledSignedDistanceM>0);
  const update=refineContactFromGeometry(arm.model,arm.contact,x,c.positions);assert.ok(update.bodyWitnesses>0);assert.ok(update.boneWitnesses>0);assert.equal(update.tendonWitnesses,1);
  arm.contact.surfaces.forEach((s,i)=>{assert.ok(s.samples.every(p=>p.referenceAreaM2>0));assert.ok(Math.abs(s.samples.reduce((t,p)=>t+p.referenceAreaM2,0)-areas[i])<1e-14);});
  arm.contact.bones.forEach((b,i)=>assert.ok(Math.abs(b.samples.reduce((t,p)=>t+p.areaM2,0)-boneAreas[i])<1e-14));
  const refined=anatomicalConfiguration(arm,x,0,{hessian:false});assert.ok(refined.contact.maximumSampledBonePenetrationM>0);assert.ok(refined.contact.maximumSampledTendonPenetrationM>0);
  assert.equal(arm.parameters.stationarityToleranceN,.0001);assert.equal(arm.contactParameters.boneGapM,.00015);
  const rule=contactRecipe(arm.contact),replay=armFixture();restoreContactRecipe(replay.contact,rule);
  const again=anatomicalConfiguration(replay,x,0,{hessian:false});assert.ok(Math.abs(again.energy-refined.energy)<1e-12);assert.deepEqual(Array.from(again.gradient),Array.from(refined.gradient));
  restoreContactRecipe(arm.contact,base);const restored=anatomicalConfiguration(arm,x,0,{hessian:false});assert.ok(Math.abs(restored.energy-c.energy)<1e-12);assert.equal(restored.contact.maximumSampledBonePenetrationM,0);
 });
}
test('frozen witness quadrature retains analytic gradient and Hessian including moving-bone/tendon contact',()=>{
 const arm=armFixture(),x=Float64Array.from(read('audit/arm-loaded-rejected-candidate.json').coordinatesM),c=anatomicalConfiguration(arm,x,0,{hessian:false});
 refineContactFromGeometry(arm.model,arm.contact,x,c.positions);
 const r=anatomicalConfiguration(arm,x,0),v=x.map((_,i)=>Math.cos(i+1)*.00001),h=1e-4,p=anatomicalConfiguration(arm,x.map((z,i)=>z+h*v[i]),0,{hessian:false}),m=anatomicalConfiguration(arm,x.map((z,i)=>z-h*v[i]),0,{hessian:false}),slope=v.reduce((s,z,i)=>s+z*r.gradient[i],0);
 assert.ok(Math.abs((p.energy-m.energy)/(2*h)-slope)<1e-6);
 for(let i=0;i<arm.model.ndof;i++){
  const hv=v.reduce((s,z,j)=>s+z*r.hessian[i*arm.model.ndof+j],0),fd=(p.gradient[i]-m.gradient[i])/(2*h);
  assert.ok(Math.abs(hv-fd)<Math.max(.003,Math.abs(fd)*2e-4),`${i}: ${hv} versus ${fd}`);
 }
});
test('saved loaded closest-face corner has conservative smooth energy derivatives at the original collision gates',()=>{
 const d=read('audit/contact-gradient-v1/candidate.json'),arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:d.parameters,contactParameters:d.contactParameters,routingRecipe:read('config/apparatus-routing.json'),contactRule:d.old.contactRule}),x=Float64Array.from(d.x),r=anatomicalConfiguration(arm,x,d.activation),h=1e-8;
 assert.equal(arm.parameters.stationarityToleranceN,.0001);assert.equal(arm.contactParameters.tissueGapM,.0003);
 for(const i of [53,47,74,77]){
  const P=x.slice(),M=x.slice();P[i]+=h;M[i]-=h;
  const fd=(anatomicalConfiguration(arm,P,d.activation,{hessian:false}).energy-anatomicalConfiguration(arm,M,d.activation,{hessian:false}).energy)/(2*h);
  assert.ok(Math.abs(fd-r.gradient[i])<1e-5,`${i}: ${fd} versus ${r.gradient[i]}`);
 }
 const v=x.map((_,i)=>Math.sin(i+1)*.00001),eps=1e-5,P=anatomicalConfiguration(arm,x.map((z,i)=>z+eps*v[i]),d.activation,{hessian:false}),M=anatomicalConfiguration(arm,x.map((z,i)=>z-eps*v[i]),d.activation,{hessian:false});
 for(let i=0;i<arm.model.ndof;i++){
  const fd=(P.gradient[i]-M.gradient[i])/(2*eps),hv=v.reduce((s,z,j)=>s+z*r.hessian[i*arm.model.ndof+j],0);
  assert.ok(Math.abs(fd-hv)<Math.max(.003,Math.abs(fd)*2e-4),`${i}: ${fd} versus ${hv}`);
 }
 const legacy=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:d.parameters,contactParameters:{...d.contactParameters,tissueFeatureWidthM:0},routingRecipe:read('config/apparatus-routing.json'),contactRule:d.old.contactRule}),old=anatomicalConfiguration(legacy,x,d.activation,{hessian:false});
 assert.ok(r.energy>=old.energy);assert.ok(Math.abs(r.gradient[53]-old.gradient[53])>.1);
 assert.equal(r.contact.maximumSampledBonePenetrationM,old.contact.maximumSampledBonePenetrationM);
 assert.equal(r.contact.maximumSampledSoftPenetrationM,old.contact.maximumSampledSoftPenetrationM);
});
test('saved cold-load edge transition preserves continuous energy and its gradient',()=>{
 const failed=read('audit/contact-feature-v2/rejected-cold-load.json'),run=read('audit/contact-feature-v2/interrupted-lift.json'),state=failed.state;
 const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json'),contactRule:failed.result.candidateContactRule}),x=Float64Array.from(failed.result.fullCoordinates),a=.04+(state.activation-.04)*Math.exp(-.01/arm.parameters.activationTimeS),r=anatomicalConfiguration(arm,x,a,{hessian:false});
 assert.equal(failed.accepted,false);assert.equal(arm.parameters.stationarityToleranceN,.0001);
 for(const i of [43,73,76]){
  const h=1e-8,P=x.slice(),M=x.slice();P[i]+=h;M[i]-=h;
  const fd=(anatomicalConfiguration(arm,P,a,{hessian:false}).energy-anatomicalConfiguration(arm,M,a,{hessian:false}).energy)/(2*h);
  assert.ok(Math.abs(fd-r.gradient[i])<1e-5,`${i}: ${fd} versus ${r.gradient[i]}`);
 }
});

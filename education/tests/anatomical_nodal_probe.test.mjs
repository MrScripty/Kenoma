import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {prepareCompressionBody} from '../tools/anatomical-compression-quadrature.mjs';
import {excludedNodalDirection,nodalProbeConfiguration} from '../tools/anatomical-nodal-probe.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../data/anatomical-arm-v1/'+p,import.meta.url))),state=read('audit/anatomical-dense-step.json').candidate,arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{quadrature:'four',routingRecipe:read('config/apparatus-routing.json')}),body=arm.model.bodies.find(b=>b.id==='FJ1512'),x=Float64Array.from(state.coordinatesM),prepared=prepareCompressionBody(body.modal.source,body.modal.nodeModes,0);
restoreContactRecipe(arm.contact,state.contactRule);
test('excluded nodal direction has unit norm and is orthogonal to every retained displacement column',()=>{
 const p=excludedNodalDirection(body.modal,98,1);assert.ok(p.maximumModalDot<1e-10);assert.ok(Math.abs(Math.hypot(...p.direction.flat())-1)<1e-12);assert.ok(p.originalExcludedNorm>.5);
});
test('nodal potential probe reproduces actual reduced displacement of body, sheets, apparatus and contact',()=>{
 const baseline=anatomicalConfiguration(arm,x,state.activation,{hessian:false}),originalNodes=body.modal.source.nodes_m,originalPoints=body.modal.points;
 for(const base of [54,57]){
  arm.contactParameters={...arm.contactParameters,boneGapM:.0003};
  const direction=body.modal.nodeModes.map(modes=>[0,1,2].map(d=>d===1?modes.filter(m=>m.base===base).reduce((s,m)=>s+m.value,0):0)),h=1e-5,perturbed=nodalProbeConfiguration(arm,body,x,state.activation,direction,h,prepared),y=x.slice();y[body.offset+base+1]+=h;
  const reduced=anatomicalConfiguration(arm,y,state.activation,{hessian:false});
  for(const key of Object.keys(reduced.energies))assert.ok(Math.abs(perturbed.energies[key]-reduced.energies[key])<1e-10,`${key}: ${perturbed.energies[key]} vs ${reduced.energies[key]}`);
  assert.ok(Math.abs(perturbed.energy-reduced.energy)<1e-10);assert.ok(reduced.contact.activeTendonSamples>0);assert.ok(Math.abs(perturbed.contact.storedEnergyJ-reduced.contact.storedEnergyJ)<1e-10);
 }
 arm.contactParameters={...arm.contactParameters,boneGapM:.00015};
 assert.equal(body.modal.source.nodes_m,originalNodes);assert.equal(body.modal.points,originalPoints);assert.equal(anatomicalConfiguration(arm,x,state.activation,{hessian:false}).energy,baseline.energy);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {prepareAnatomicalArm as original,anatomicalConfiguration as baseConfiguration} from '../web/anatomical-arm.mjs';
import {restoreContactRecipe as baseRestore} from '../web/anatomical-contact-refinement.mjs';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../tools/enriched/anatomical-arm.mjs';
import {restoreContactRecipe} from '../tools/enriched/anatomical-contact-refinement.mjs';
import {evaluateModalBody,modalPositions} from '../web/anatomical-modal.mjs';
import {denseModalBody} from '../tools/anatomical-dense-quadrature.mjs';
import {liftDenseCoordinates,retainedIndex,independentEnrichedBody} from '../tools/enriched-support.mjs';
import {rigidModalRemainder,rotationRemainder} from '../tools/enriched/anatomical-retraction.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../data/anatomical-arm-v1/'+p,import.meta.url))),run=read('audit/anatomical-dense-loading-prefix.json'),state=run.snapshots[3],parameters={parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')},inputs=[read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json')],arm=prepareAnatomicalArm(...inputs,parameters),base=original(...inputs,parameters),x=liftDenseCoordinates(Float64Array.from(state.coordinatesM));for(const b of base.model.bodies)b.modal=denseModalBody(b.modal);restoreContactRecipe(arm.contact,state.contactRule);baseRestore(base.contact,state.contactRule);
const body=arm.model.bodies.find(b=>b.id==='FJ1512'),near=(a,b,t)=>assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${a} vs ${b}`);
test('zero enrichment exactly reproduces the original dense potential, positions and retained gradients',()=>{
 assert.equal(arm.model.ndof,466);assert.equal(arm.model.jointIndex,465);assert.equal(body.modal.ndof,69);
 const A=baseConfiguration(base,Float64Array.from(state.coordinatesM),state.activation,{hessian:false}),B=anatomicalConfiguration(arm,x,state.activation,{hessian:false});near(A.energy,B.energy,2e-10);A.gradient.forEach((v,k)=>near(v,B.gradient[retainedIndex(k)],2e-6));
 for(const [i,head] of A.positions.entries())head.nodesM.flat().forEach((v,k)=>near(v,B.positions[i].nodesM.flat()[k],1e-14));
 const shapes=body.modal.enrichment.scalarShapes;near(Math.hypot(...shapes[0]),1,1e-12);near(Math.hypot(...shapes[1]),1,1e-12);near(shapes[0].reduce((s,v,i)=>s+v*shapes[1][i],0),0,1e-12);
});
test('new apparatus/contact force coefficients agree with independent energy directional differences',()=>{
 const c=anatomicalConfiguration(arm,x,state.activation,{hessian:false});
 for(const k of [126,127,128,130]){const h=1e-7,plus=x.slice(),minus=x.slice();plus[k]+=h;minus[k]-=h;const A=anatomicalConfiguration(arm,plus,state.activation,{hessian:false}),B=anatomicalConfiguration(arm,minus,state.activation,{hessian:false});near((A.energy-B.energy)/(2*h),c.gradient[k],2e-6);}
});
test('enriched body force assembly agrees with independent full P2 nodal gradients',()=>{
 const coordinates=x.slice(body.offset,body.offset+69),A=evaluateModalBody(body.modal,coordinates,state.activation,{material:body.material,hessian:false}),B=independentEnrichedBody(body.modal,coordinates,state.activation,body.material);near(A.energy,B.energyJ,2e-10);A.gradient.forEach((v,k)=>near(v,B.gradientN[k],2e-6));
});
test('enriched analytic body Hessian passes directional differences and symmetry',()=>{
 const modal={...body.modal,points:body.modal.points.filter(p=>p.element===212)},coordinates=x.slice(body.offset,body.offset+69),r=evaluateModalBody(modal,coordinates,state.activation,{material:body.material}),v=Float64Array.from({length:69},(_,i)=>Math.sin(i*.71)),norm=Math.hypot(...v);v.forEach((c,k)=>v[k]=c/norm);
 const h=1e-7,A=evaluateModalBody(modal,coordinates.map((c,k)=>c+h*v[k]),state.activation,{material:body.material,hessian:false}),B=evaluateModalBody(modal,coordinates.map((c,k)=>c-h*v[k]),state.activation,{material:body.material,hessian:false});let error=0,scale=0;
 for(let i=0;i<69;i++){const exact=v.reduce((s,c,k)=>s+r.hessian[i*69+k]*c,0);error=Math.max(error,Math.abs(exact-(A.gradient[i]-B.gradient[i])/(2*h)));scale=Math.max(scale,Math.abs(exact));for(let j=0;j<69;j++)near(r.hessian[i*69+j],r.hessian[j*69+i],1e-8);}
 assert.ok(error<=1e-6*Math.max(1,scale),`Hessian ${error} / ${scale}`);
});
test('rotation search remainder rotates the extra nodal vector modes consistently',()=>{
 const coordinates=x.slice(body.offset,body.offset+69);coordinates.set([.0003,-.0002,.0001,.0001,.0002,-.0003],63);const omega=[.13,-.07,.04],step=.7,center=body.modal.source.centerline_m[3],before=modalPositions(body.modal,coordinates),correction=rigidModalRemainder(body.modal,coordinates,omega,step,center),after=modalPositions(body.modal,coordinates.map((v,k)=>v+correction[k]));
 before.forEach((X,i)=>{const expected=rotationRemainder(X.map((v,d)=>v-center[d]),omega,step);for(let d=0;d<3;d++)near(after[i][d]-X[d],expected[d],1e-12);});
});

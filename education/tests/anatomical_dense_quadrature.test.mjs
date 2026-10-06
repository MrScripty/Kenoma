import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {prepareModalBody,modalPositions,evaluateModalBody} from '../web/anatomical-modal.mjs';
import {prepareCompressionBody,evaluateCompressionBody} from '../tools/anatomical-compression-quadrature.mjs';
import {denseModalBody} from '../tools/anatomical-dense-quadrature.mjs';
import {MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../data/anatomical-arm-v1/'+p,import.meta.url))),geometry=read('generated/arm-reference.json'),source=geometry.muscles[1],original=prepareModalBody(source),single={...source,elements_ten_node:[source.elements_ten_node[31]],reference_fibres:[source.reference_fibres[31]]},body={...original,source:single},dense=denseModalBody(body),state=read('audit/contact-lift-release-results.json').snapshots[3],x=Float64Array.from(state.coordinatesM.slice(63,126)),match=read('audit/modal-fixed-end-results.json').records.find(r=>r.elementId===source.element_id),material={...MUSCLE_FIXTURE,sigma0:match.match.sigma0Pa};
const near=(a,b,t)=>assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${a} versus ${b}`);
test('dense reduced body agrees with independent full P2 assembly at a compressed nonlinear pose',()=>{
 const expected=evaluateCompressionBody(prepareCompressionBody(single,original.nodeModes,2),modalPositions(body,x),state.activation,material),actual=evaluateModalBody(dense,x,state.activation,{material,hessian:false});
 assert.equal(dense.points.length,256);assert.equal(dense.nodeModes,original.nodeModes);
 near(actual.energy,expected.energyJ,2e-10);near(actual.minJ,expected.minimumJ,1e-12);
 actual.gradient.forEach((v,k)=>near(v,expected.gradientN[k],2e-6));
});
test('dense body energy gradient and Hessian pass directional differences at actual compression',()=>{
 const r=evaluateModalBody(dense,x,state.activation,{material}),direction=Float64Array.from(x,(_,i)=>Math.sin(i*.71));
 const norm=Math.hypot(...direction);direction.forEach((v,k)=>direction[k]=v/norm);
 const h=1e-7,plus=x.map((v,k)=>v+h*direction[k]),minus=x.map((v,k)=>v-h*direction[k]),P=evaluateModalBody(dense,plus,state.activation,{material,hessian:false}),M=evaluateModalBody(dense,minus,state.activation,{material,hessian:false});
 near((P.energy-M.energy)/(2*h),r.gradient.reduce((s,v,k)=>s+v*direction[k],0),1e-5);
 let maximumError=0,scale=0;
 for(let k=0;k<63;k++){
  const exact=direction.reduce((s,v,j)=>s+r.hessian[k*63+j]*v,0),fd=(P.gradient[k]-M.gradient[k])/(2*h);
  maximumError=Math.max(maximumError,Math.abs(exact-fd));scale=Math.max(scale,Math.abs(exact));
 }
 assert.ok(maximumError<=1e-6*Math.max(1,scale),`Hessian error ${maximumError}, scale ${scale}`);
 for(let i=0;i<63;i++)for(let j=0;j<63;j++)near(r.hessian[i*63+j],r.hessian[j*63+i],1e-8);
});

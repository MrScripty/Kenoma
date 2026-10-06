import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {compressionQuadrature,prepareCompressionBody,evaluateCompressionBody} from '../tools/anatomical-compression-quadrature.mjs';
import {QUADRATURE} from '../web/anatomical-element.mjs';
import {prepareModalBody,modalPositions,evaluateModalBody} from '../web/anatomical-modal.mjs';
import {muscleMaterial,MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../data/anatomical-arm-v1/'+p,import.meta.url)));
const geometry=read('generated/arm-reference.json'),source=geometry.muscles.find(m=>m.element_id==='FJ1512'),modal=prepareModalBody(source);
const single={...source,elements_ten_node:[source.elements_ten_node[0]],reference_fibres:[source.reference_fibres[0]]};
const near=(a,b,t)=>assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${a} versus ${b}`);
test('nested positive diagnostic rules retain the existing 4/32 rules and reference measure',()=>{
 for(const depth of [0,1,2]){
  const rule=compressionQuadrature(depth);assert.equal(rule.length,4*8**depth);
  near(rule.reduce((s,p)=>s+p.weight,0),1,1e-14);
  for(const p of rule){assert.ok(p.weight>0&&p.L.every(v=>v>=0));near(p.L.reduce((s,v)=>s+v,0),1,1e-14);}
  const body=prepareCompressionBody(single,modal.nodeModes,depth);
  near(body.referenceVolumeM3,prepareCompressionBody(single,modal.nodeModes,0).referenceVolumeM3,1e-15);
 }
 assert.deepEqual(compressionQuadrature(0),QUADRATURE.four);
 const keys=rule=>rule.map(p=>[...p.L,p.weight].map(v=>v.toPrecision(14)).join(',')).sort();
 assert.deepEqual(keys(compressionQuadrature(1)),keys(QUADRATURE.subdivided32));
 assert.throws(()=>compressionQuadrature(3),RangeError);
});
test('independent P2 integration reproduces affine material energy and nodal energy derivatives',()=>{
 const F=[1.03,.012,0,0,.98,.009,0,0,1.01],activation=.02;
 const positions=source.nodes_m.map(X=>[0,1,2].map(d=>F.slice(3*d,3*d+3).reduce((s,v,k)=>s+v*X[k],0)));
 const body=prepareCompressionBody(single,modal.nodeModes,2),r=evaluateCompressionBody(body,positions,activation,MUSCLE_FIXTURE),material=muscleMaterial(F,single.reference_fibres[0],activation);
 near(r.energyJ,material.solvePotential*body.referenceVolumeM3,2e-10);
 near(r.minimumJ,material.J,1e-12);near(r.minimumCornerJ,material.J,1e-12);
 for(const node of [single.elements_ten_node[0][0],single.elements_ten_node[0][4]])for(const d of [0,1,2]){
  const h=1e-7,P=structuredClone(positions),M=structuredClone(positions);P[node][d]+=h;M[node][d]-=h;
  const fd=(evaluateCompressionBody(body,P,activation,MUSCLE_FIXTURE).energyJ-evaluateCompressionBody(body,M,activation,MUSCLE_FIXTURE).energyJ)/(2*h);
  near(fd,r.nodalGradientN[node][d],1e-5);
 }
});
test('half/double bulk diagnostic is exact at fixed geometry and retains the original force gate',()=>{
 const positions=source.nodes_m.map(X=>[X[0]*.99,X[1],X[2]*.96]),body=prepareCompressionBody(single,modal.nodeModes,1),base=evaluateCompressionBody(body,positions,.03,MUSCLE_FIXTURE);
 for(const factor of [.5,2]){
  const changed=evaluateCompressionBody(body,positions,.03,{...MUSCLE_FIXTURE,bulk:MUSCLE_FIXTURE.bulk*factor});
  near(changed.energyJ-base.energyJ,(factor-1)*base.energies.volume,1e-12);
  changed.gradientN.forEach((v,k)=>near(v-base.gradientN[k],(factor-1)*base.bulkGradientN[k],1e-10));
  assert.equal(changed.minimumJ,base.minimumJ);
 }
 assert.equal(read('audit/contact-lift-release-results.json').parameters.stationarityToleranceN,.0001);
});
test('actual compressed loading pose retains the independent original P2 energy, gradient and determinant',()=>{
 const run=read('audit/contact-lift-release-results.json'),state=run.snapshots[3],bi=geometry.muscles.findIndex(m=>m.element_id===source.element_id),x=Float64Array.from(state.coordinatesM.slice(63*bi,63*(bi+1))),positions=modalPositions(modal,x),match=read('audit/modal-fixed-end-results.json').records.find(r=>r.elementId===source.element_id),material={...MUSCLE_FIXTURE,sigma0:match.match.sigma0Pa};
 const independent=evaluateCompressionBody(prepareCompressionBody(source,modal.nodeModes,1),positions,state.activation,material),expected=evaluateModalBody(modal,x,state.activation,{material,hessian:false});
 near(independent.energyJ,expected.energy,2e-10);near(independent.minimumJ,expected.minJ,1e-12);
 expected.gradient.forEach((v,k)=>near(v,independent.gradientN[k],2e-6));
 assert.ok(independent.minimumJ<.9);
});

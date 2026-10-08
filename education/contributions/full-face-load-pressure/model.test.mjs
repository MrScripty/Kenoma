import test from 'node:test';import assert from 'node:assert/strict';import {solveComparison,evaluateAt,DEFAULTS} from './model.mjs';
const close=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);
test('actual inverse roots satisfy both equilibrium and area identities across bounded states',()=>{
 for(const direction of ['Y','Z'])for(const axialStretch of [.8,1,1.2])for(const bulk of [0,50000,250000])for(const breadthFactor of [.5,1,2]){
  const p={...DEFAULTS,direction,axialStretch,bulk,breadthFactor},known=evaluateAt(p,.65);
  for(const mode of ['force','pressure']){const target=mode==='force'?known.compressionResultantN:known.contactPressurePa;assert.ok(target>0);const r=solveComparison({...p,mode,forceN:known.compressionResultantN,pressurePa:known.contactPressurePa});assert.ok(r.solve.converged);close(r.state.stretches[r.loadedAxis],.65);close(r.state.independentVolumeRatio,r.state.J);close(r.state.contactPressurePa*r.state.currentAreaM2,r.state.compressionResultantN);close(r.state.nominalStressPa[0]*r.state.endReferenceAreaM2,r.state.endResultantN);}
 }
});
test('fixed current pressure preserves stresses/stretches while reference area, material volume and energy scale',()=>{
 const one=solveComparison({...DEFAULTS,mode:'pressure'}),two=solveComparison({...DEFAULTS,mode:'pressure',breadthFactor:2});one.state.stretches.forEach((s,i)=>close(s,two.state.stretches[i]));for(const key of ['compressionResultantN','referenceVolumeM3','referenceAreaM2','currentAreaM2','endReferenceAreaM2','endResultantN','energyJ'])close(two.state[key],2*one.state[key]);
});
test('fixed force is actually solved rather than scaling an imposed shape',()=>{const a=solveComparison(),b=solveComparison({...DEFAULTS,breadthFactor:2});close(a.state.compressionResultantN,b.state.compressionResultantN);assert.ok(b.state.stretches[b.loadedAxis]>a.state.stretches[a.loadedAxis]);assert.ok(Math.abs(a.state.contactPressurePa-b.state.contactPressurePa)>100);});
test('low iteration cap honestly fails and unsupported/unbracketed inputs refuse',()=>{assert.equal(solveComparison({...DEFAULTS,outerIterations:8}).solve.converged,false);for(const p of [{forceN:100},{mode:'bad'},{breadthFactor:0},{axialStretch:NaN},{pressurePa:-1},{mu:0},{outerIterations:7}])assert.throws(()=>solveComparison({...DEFAULTS,...p}),RangeError);});

import test from 'node:test';import assert from 'node:assert/strict';
import {DEFAULTS,diagonalResponse,specimen} from './model.mjs';
import {TISSUE,blockEnergy,blockStress} from '../../web/tissue.mjs';
const near=(a,b,t=1e-9)=>assert.ok(Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);
test('general diagonal extension exactly recovers the inherited equal-lateral law',()=>{
 for(const b of [.7,1,1.3])for(const h of [.5,.8,1]){const s=diagonalResponse([b,h,b],TISSUE),old=blockStress(b,h,TISSUE);near(s.energyJ,blockEnergy(b,h,TISSUE));near(s.nominalStressPa[0],old.px);near(s.nominalStressPa[1],old.py);near(s.nominalStressPa[2],old.px);}
});
test('all three stress components agree with independent energy finite differences',()=>{
 for(const x of [[1,.8,1.2],[.9,.7,1.1],[1.2,1,.8]])for(let i=0;i<3;i++){
  const step=1e-6,a=x.slice(),b=x.slice();a[i]-=step;b[i]+=step;const numerical=(diagonalResponse(b,TISSUE).energyJ-diagonalResponse(a,TISSUE).energyJ)/(2*step*TISSUE.width*TISSUE.height*TISSUE.depth);near(numerical,diagonalResponse(x,TISSUE).nominalStressPa[i],1e-7);
 }
});
test('independent transverse equilibrium, boundary volume, force/area and Cauchy conversion across bounded states',()=>{
 for(const direction of ['Y','Z'])for(const axialStretch of [.8,1,1.2])for(const heightStretch of [.5,.8,1])for(const bulk of [0,50000,250000]){
  const r=specimen({...DEFAULTS,direction,axialStretch,heightStretch,bulk});assert.ok(r.state.converged);near(r.state.independentVolumeRatio,r.state.J,1e-13);near(r.state.contactPressurePa*r.state.currentAreaM2,r.state.compressionResultantN,1e-13);near(r.state.contactPressurePa,-r.state.cauchyStressPa[r.loadedAxis],1e-12);
  assert.ok(r.state.stretches[r.freeAxis]>.1&&r.state.stretches[r.freeAxis]<4);assert.equal(r.state.stretches[0],axialStretch);assert.equal(r.state.stretches[r.loadedAxis],heightStretch);
 }
});
test('zero-bulk equilibrium agrees with independent closed form and preserves the law degeneracy',()=>{
 for(const axialStretch of [.8,1,1.2])for(const heightStretch of [.5,.8,1]){const r=specimen({...DEFAULTS,bulk:0,axialStretch,heightStretch});near(r.state.stretches[2],Math.sqrt((axialStretch**2+heightStretch**2)/2),1e-13);}
 const r=specimen({...DEFAULTS,bulk:0,axialStretch:.8,heightStretch:.8});near(r.state.J,.8**3);near(r.state.energyJ,0);near(r.state.compressionResultantN,0);
});
test('direction permutations preserve isotropic response and change full-face load by geometry',()=>{
 const y=specimen(DEFAULTS),z=specimen({...DEFAULTS,direction:'Z'});near(y.state.energyJ,z.state.energyJ,1e-13);near(y.state.contactPressurePa,z.state.contactPressurePa,1e-13);near(y.state.endResultantN,z.state.endResultantN,1e-13);near(z.state.compressionResultantN/y.state.compressionResultantN,TISSUE.height/TISSUE.depth,1e-13);
 assert.notEqual(y.state.stretches[1],y.state.stretches[2]);
});
test('limited iterations fail scalar residual and a tensile grip is exposed rather than hidden',()=>{
 assert.equal(specimen({...DEFAULTS,iterations:8}).state.converged,false);
 const tensile=specimen({...DEFAULTS,axialStretch:1.2,heightStretch:1});assert.ok(tensile.state.compressionResultantN<0);assert.equal(tensile.state.requiresTensileGrip,true);
});
test('invalid/out-of-domain controls fail without invoking any mechanics campaign',()=>{
 for(const change of [{axialStretch:0},{axialStretch:NaN},{direction:'X'},{bulk:-1},{mu:0},{heightStretch:Infinity},{iterations:16}])assert.throws(()=>specimen({...DEFAULTS,...change}));
});

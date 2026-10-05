import test from 'node:test';
import assert from 'node:assert/strict';
import {BAR_DEFAULTS,barState} from '../web/tapered-bar.mjs';
test('linear taper midpoint integration converges to independently integrated log oracle',()=>{
 const errors=[8,16,32,64].map(segments=>Math.abs(barState({...BAR_DEFAULTS,segments}).extensionErrorM));
 for(let i=1;i<errors.length;i++)assert.ok(errors[i]<errors[i-1]/3.8);
 const s=barState({...BAR_DEFAULTS,ratio:1});assert.ok(Math.abs(s.exactExtensionM-.002)<1e-15);assert.ok(Math.abs(s.extensionErrorM)<1e-15);
});
test('equal-length two-area fixed-end active fixture: narrow +1/300, wide -1/300',()=>{
 const s=barState({...BAR_DEFAULTS,shape:'two-segment',mode:'active-fixed',segments:2});
 assert.ok(Math.abs(s.samples[0].strain-1/300)<1e-15);assert.ok(Math.abs(s.samples[1].strain+1/300)<1e-15);
 assert.ok(Math.abs(s.resultantN-(4/3)*BAR_DEFAULTS.area*BAR_DEFAULTS.activeStress)<1e-15);
 assert.ok(Math.abs(s.numericalExtensionM)<1e-15);assert.equal(s.samples[0].resultantN,s.samples[1].resultantN);
});
test('large strain is exposed and invalid area or refinement rejected',()=>{
 assert.equal(barState({...BAR_DEFAULTS,force:20}).smallStrainWarning,true);
 assert.throws(()=>barState({...BAR_DEFAULTS,area:0}),RangeError);assert.throws(()=>barState({...BAR_DEFAULTS,segments:3.5}),RangeError);
});
test('small-strain warning uses true endpoint extrema independently of midpoint display resolution',()=>{
 const fixture={...BAR_DEFAULTS,area:.0001,ratio:4,modulus:110000,force:.6};
 const expectedEndpoint=3/55; // N/(E*A1), independently reduced from the fixture.
 for(const segments of [8,16,64,512]){
  const s=barState({...fixture,segments});
  assert.equal(s.smallStrainWarning,true);assert.ok(Math.abs(s.maxAbsStrain-expectedEndpoint)<1e-15);
  assert.ok(Math.abs(s.maximumStrain-expectedEndpoint)<1e-15);
 }
 assert.ok(Math.max(...barState({...fixture,segments:8}).samples.map(s=>Math.abs(s.strain)))<.05);
 const reverse=barState({...fixture,force:-.6,segments:8});
 assert.equal(reverse.smallStrainWarning,true);assert.ok(Math.abs(reverse.minimumStrain+expectedEndpoint)<1e-15);
});

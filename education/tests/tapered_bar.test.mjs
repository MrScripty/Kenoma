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

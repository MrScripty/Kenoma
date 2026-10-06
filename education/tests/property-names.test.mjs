import test from 'node:test';
import assert from 'node:assert/strict';
import {deformationState,DEFORMATION_DEFAULTS} from '../web/continuum-properties.mjs';
import {barState,BAR_DEFAULTS} from '../web/tapered-bar.mjs';
test('actual Y material-line stretch includes shear and is invariant to rotation/translation',()=>{
 const p={...DEFORMATION_DEFAULTS,sx:1.2,sy:.8,sz:1.1,shear:.6},s=deformationState(p);
 assert.ok(Math.abs(s.materialLineStretches[1]-1)<1e-14);assert.notEqual(s.materialLineStretches[1],p.sy);
 const moved=deformationState({...p,angle:117,tx:30,ty:-20});
 for(let i=0;i<3;i++)assert.ok(Math.abs(s.materialLineStretches[i]-moved.materialLineStretches[i])<1e-14);
 assert.ok(Math.abs(s.J-p.sx*p.sy*p.sz)<1e-14);
});
test('endpoint labels and narrow/wide geometry remain true when taper direction reverses',()=>{
 for(const shape of ['linear','two-segment'])for(const ratio of [.5,1,2]){
  const p={...BAR_DEFAULTS,shape,ratio},r=barState(p);
  assert.deepEqual(r.endpointAreasM2,[p.area,p.area*ratio]);
  assert.equal(r.narrowAreaM2,p.area*Math.min(1,ratio));assert.equal(r.wideAreaM2,p.area*Math.max(1,ratio));
  if(ratio!==1)assert.ok((r.endpointStrains[1]-r.endpointStrains[0])*(ratio-1)<0);
  const active=barState({...p,mode:'active-fixed'});assert.ok(Math.abs(active.exactExtensionM)<1e-17);
 }
});

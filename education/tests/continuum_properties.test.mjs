import test from 'node:test';
import assert from 'node:assert/strict';
import {PROPERTY_DIMENSIONS,DEFORMATION_DEFAULTS,ISOCHORIC_DEFAULTS,deformationState,isochoricState,measureTetrahedron,multiply3,determinant3} from '../web/continuum-properties.mjs';
const close=(a,b,tol=2e-13)=>assert.ok(Math.abs(a-b)<=tol*Math.max(1,Math.abs(a),Math.abs(b)),`${a} versus ${b}`);
test('oriented boundary measurement agrees with an independent affine prediction over translations and rotations',()=>{
 for(const angle of [-81,-17,0,33,89])for(const shear of [-.6,0,.7]){
  const p={...DEFORMATION_DEFAULTS,angle,shear,tx:31,ty:-17,tz:8},r=deformationState(p);
  assert.ok(r.accepted);close(r.volumeRatio,p.sx*p.sy*p.sz);close(r.J,r.volumeRatio);
  for(const v of r.currentBoundary.closureVectorM2)close(v,0);
  close(r.referenceBoundary.signedVolumeM3,PROPERTY_DIMENSIONS.reduce((s,v)=>s*v,1)/6);
 }
});
test('rigid deformation has zero Green strain; volume-preserving shear still has strain',()=>{
 const rigid=deformationState({...DEFORMATION_DEFAULTS,sx:1,sy:1,sz:1,shear:0,angle:53,tx:22,ty:17,tz:-9});
 for(const v of rigid.greenStrain)close(v,0);
 const shear=deformationState({...DEFORMATION_DEFAULTS,sx:1,sy:1,sz:1,shear:.4,angle:0});
 close(shear.J,1);close(shear.greenStrain[1],.2);close(shear.greenStrain[4],.08);
});
test('determinant composition is checked numerically on nontrivial independent matrices',()=>{
 const A=[1.2,.3,-.1,0,.8,.2,.1,0,1.1],B=[.9,0,.2,.1,1.3,0,0,.1,.7];
 close(determinant3(multiply3(A,B)),determinant3(A)*determinant3(B));
});
test('inversion is rejected by signed boundary volume and deformation orientation',()=>{
 const r=deformationState(DEFORMATION_DEFAULTS),inverted=r.current.map(v=>v.slice());
 [inverted[1],inverted[2]]=[inverted[2],inverted[1]];
 const rejected=measureTetrahedron(r.reference,inverted);
 assert.equal(rejected.accepted,false);assert.ok(rejected.J<0&&rejected.currentBoundary.signedVolumeM3<0);
 assert.throws(()=>deformationState({...DEFORMATION_DEFAULTS,sx:0}),RangeError);
});
test('isochoric construction preserves independently triangulated volume while area and length change',()=>{
 for(const axial of [.4,.6,.8,1,1.3,1.7]){
  const r=isochoricState({...ISOCHORIC_DEFAULTS,axial});
  close(r.J,1);close(r.volumeRatio,1);close(r.crossSectionAreaM2,PROPERTY_DIMENSIONS[1]*PROPERTY_DIMENSIONS[2]/axial);
  close(r.areaLengthVolumeM3,r.currentBoundary.signedVolumeM3);
  assert.ok(r.exteriorAreaM2>2*r.crossSectionAreaM2);
 }
 const independent=isochoricState({axial:.8,lateral:1,mode:'independent'});close(independent.volumeRatio,.8);
 assert.throws(()=>isochoricState({axial:-1,lateral:1,mode:'isochoric'}),RangeError);
});

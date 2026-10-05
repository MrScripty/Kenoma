import test from 'node:test';
import assert from 'node:assert/strict';
import {compressionState,COMPRESSION_DEFAULTS as D,COMPRESSION_LIMITS as L} from '../web/compression.mjs';
import {TISSUE,blockStress,tissueAt} from '../web/tissue.mjs';
const close=(a,b,tolerance=1e-9)=>assert.ok(Math.abs(a-b)<=tolerance,`${a} differs from ${b}`);
// Independent full diagonal energy: geometric mean normalization, rather than
// the primary t/h helper and its J**(-2/3) multiplication.
function energy(stretches,mu,bulk){
 const J=stretches.reduce((a,b)=>a*b,1),mean=Math.cbrt(J);
 return TISSUE.width*TISSUE.height*TISSUE.depth*(mu/2*(stretches.reduce((s,x)=>s+(x/mean)**2,0)-3)+bulk/2*(J-1)**2);
}
test('Lab 5 extension retains the same law and independent geometric volume',()=>{
 const s=compressionState(),q=2*Math.asin((TISSUE.gapOpen-TISSUE.height*s.heightStretch)/TISSUE.gapClose),old=tissueAt(q);
 close(s.J,old.volumeRatio);close(s.plateReactionN,old.normal);close(s.energyJ,old.energy);close(s.lateralStretch,old.lateralStretch);
 close(s.volumeRatio,s.J,1e-12);close(s.currentBoundary.signedVolumeM3,s.currentPlateAreaM2*s.heightM,1e-15);
 close(s.energyJ,energy([s.lateralStretch,s.heightStretch,s.lateralStretch],D.mu,D.bulk),1e-14);
 assert.ok(s.J<1&&s.J>.99);assert.ok(s.lateralStretch<s.isochoricComparison.lateralStretch);
});
test('independent diagonal energy derivatives and Cauchy configurations match stress',()=>{
 for(const mu of [100,1500,10000])for(const bulk of [0,1500,50000,1000000])for(const h of [.6,.8,1])for(const boundary of ['free','confined']){
  const s=compressionState({...D,mu,bulk,heightStretch:h,boundary}),x=[s.lateralStretch,h,s.lateralStretch],V0=TISSUE.width*TISSUE.height*TISSUE.depth;
  for(const delta of [2e-6,1e-6])for(const axis of [0,1,2]){
   const plus=[...x],minus=[...x];plus[axis]+=delta;minus[axis]-=delta;
   const numerical=(energy(plus,mu,bulk)-energy(minus,mu,bulk))/(2*delta*V0);
   close(numerical,axis===1?s.axialPiolaStressPa:s.lateralPiolaStressPa,1e-3);
  }
  close(s.meanCompressionPressurePa,s.bulkPressurePa,1e-7);
  close(s.plateReactionN,-s.axialCauchyStressPa*s.currentPlateAreaM2,1e-10);
  if(boundary==='free'){
   close(s.lateralResidualPa,0,L.stressTolerancePa);close(s.volumeEquilibriumJ,s.J,1e-10);close(s.platePressurePa,3*s.bulkPressurePa,1e-7);
  }else close(s.J,h,1e-12);
 }
});
test('confinement changes reactions under imposed height and deformation under imposed force',()=>{
 const free=compressionState(),confined=compressionState({...D,boundary:'confined'});
 assert.ok(confined.plateReactionN>free.plateReactionN*8);assert.ok(confined.sideSupportForceN<0);close(free.sideSupportForceN,0);
 const ff=compressionState({...D,mode:'force'}),cf=compressionState({...D,mode:'force',boundary:'confined'});
 close(ff.plateReactionN,D.force,L.forceToleranceN);close(cf.plateReactionN,D.force,L.forceToleranceN);
 assert.ok(ff.heightStretch<cf.heightStretch);assert.ok(ff.J>cf.J);
 for(const s of [ff,cf])close(compressionState({...D,boundary:s.controls.boundary,heightStretch:s.heightStretch}).plateReactionN,D.force,L.forceToleranceN);
});
test('force branch, relaxed energy derivative and zero-bulk ablation have explicit limits',()=>{
 for(const boundary of ['free','confined'])for(const mu of [100,1500,10000])for(const bulk of [1,100,1500,50000,1000000]){
  const s=compressionState({...D,mu,bulk,boundary}),force=Math.min(2,s.maxSupportedForceN*.7),f=compressionState({...D,mu,bulk,boundary,mode:'force',force});
  close(f.plateReactionN,force,L.forceToleranceN);assert.ok(f.heightStretch>=.8&&f.heightStretch<=1);
 }
 const s=compressionState(),delta=1e-5;
 const relaxed=h=>compressionState({...D,heightStretch:h}).energyJ;
 close((relaxed(.8+delta)-relaxed(.8-delta))/(2*delta),-s.plateReactionN*TISSUE.height,1e-8);
 const ablation=compressionState({...D,bulk:0});close(ablation.lateralStretch,.8);close(ablation.J,.8**3);close(ablation.plateReactionN,0);
 assert.throws(()=>compressionState({...D,bulk:0,mode:'force'}),/no unique/);
 assert.throws(()=>compressionState({...D,mode:'force',force:20}),/supported/);
 assert.throws(()=>compressionState({...D,heightStretch:0}),/domain/);
 assert.throws(()=>compressionState({...D,mu:NaN}),/domain/);
 assert.throws(()=>compressionState({...D,boundary:'unknown'}),/domain/);
});
test('pure dilation separates bulk and simple shear separates shape energy',()=>{
 for(const s of [.7,.9,1.2]){
  const psi=energy([s,s,s],1500,50000)/(TISSUE.width*TISSUE.height*TISSUE.depth);
  close(psi,50000/2*(s**3-1)**2,1e-8);
  const P=blockStress(s,s,TISSUE);close(P.px,50000*(s**3-1)*s*s,1e-8);close(P.py,P.px,1e-8);
 }
 for(const gamma of [-.6,.2,.7]){
  // Independent 3x3 F, cofactor determinant and sum of all squared entries.
  const F=[1,gamma,0,0,1,0,0,0,1],J=F[0]*(F[4]*F[8]-F[5]*F[7])-F[1]*(F[3]*F[8]-F[5]*F[6])+F[2]*(F[3]*F[7]-F[4]*F[6]);
  const I1=F.reduce((sum,x)=>sum+x*x,0);close(J,1);close(1500/2*(J**(-2/3)*I1-3),1500/2*gamma**2,1e-12);
 }
});
test('near-reference free/confined moduli and independent plate-work quadrature',()=>{
 const delta=1e-5,A0=TISSUE.width*TISSUE.depth;
 for(const mu of [100,1500,10000])for(const bulk of [1500,50000,1000000]){
  const free=compressionState({...D,mu,bulk,heightStretch:1-delta}),confined=compressionState({...D,mu,bulk,heightStretch:1-delta,boundary:'confined'});
  const E=9*bulk*mu/(3*bulk+mu),M=bulk+4*mu/3;
  close(free.plateReactionN/(A0*delta),E,E*1e-4);
  close(confined.plateReactionN/(A0*delta),M,M*1e-4);
 }
 for(const boundary of ['free','confined']){
  const s=compressionState({...D,heightStretch:.6,boundary});
  function work(n){
   const step=.4/n;let sum=0;
   for(let i=0;i<=n;i++)sum+=(i===0||i===n?1:i%2?4:2)*compressionState({...D,heightStretch:.6+i*step,boundary}).plateReactionN;
   return TISSUE.height*step*sum/3;
  }
  const e32=Math.abs(work(32)-s.energyJ),e64=Math.abs(work(64)-s.energyJ);
  assert.ok(e64<e32/10,`${boundary}: ${e32} → ${e64}`);assert.ok(e64<1e-7);
 }
});

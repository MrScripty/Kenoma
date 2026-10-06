import test from 'node:test';
import assert from 'node:assert/strict';
import {compressionPair,evaluateCompressionCandidate,MATERIAL_DEFAULTS,MATERIAL_RESIDUAL_PA} from '../web/material-response.mjs';
import {TISSUE,blockEnergy,blockStress} from '../web/tissue.mjs';
const close=(a,b,tol=1e-9)=>assert.ok(Math.abs(a-b)<=tol,`${a} versus ${b}, tolerance ${tol}`);
const state=p=>compressionPair({...MATERIAL_DEFAULTS,...p});
// Independent scalar stationarity equation derived in J, rather than P_x(b).
function oracle(h,mu,K){
 let low=h**3,high=1;
 for(let i=0;i<100;i++){
  const J=(low+high)/2,g=mu*(J-h**3)/(3*h*J**(5/3))+K*(J-1);
  if(g>0)high=J;else low=J;
 }
 return Math.sqrt(((low+high)/2)/h);
}
test('energy derivatives give nominal stress, plate force and two lateral contributions',()=>{
 for(const h of [.55,.8,.97])for(const b of [.7,1,1.25]){
  const p={...TISSUE,bulk:47000,mu:1800},eps=1e-6,V0=p.width*p.height*p.depth,s=blockStress(b,h,p);
  close((blockEnergy(b+eps,h,p)-blockEnergy(b-eps,h,p))/(2*eps),2*V0*s.px,2e-8);
  close((blockEnergy(b,h+eps,p)-blockEnergy(b,h-eps,p))/(2*eps),V0*s.py,2e-8);
 }
 for(const boundary of ['free','confined']){
  const eps=1e-6,p=state(),plus=state({heightStretch:.8+eps})[boundary],minus=state({heightStretch:.8-eps})[boundary];
  close(-(plus.energyJ-minus.energyJ)/(2*eps*TISSUE.height),p[boundary].plateForceN,2e-7);
 }
});
test('bounded parameter sweep: independent equilibrium oracle, energies, SI geometry and wall KKT',()=>{
 for(const h of [.5,.55,.7,.8,.95,.999,1])for(const mu of [500,1500,5000])for(const bulk of [0,10,500,5000,50000,250000]){
  const pair=state({heightStretch:h,mu,bulk}),b=oracle(h,mu,bulk),p={...TISSUE,mu,bulk};
  close(pair.free.b,b,5e-14);close(pair.confined.b,Math.min(b,1),5e-14);
  for(const boundary of ['free','confined']){
   const s=pair[boundary];assert(s.accepted&&s.converged);assert(s.J>0);
   close(s.volumeM3,s.widthM*s.heightM*s.depthM,1e-18);
   close(s.energyJ,s.bulkEnergyJ+s.shearEnergyJ,1e-15);
   close(s.platePressurePa*s.widthM*s.depthM,s.plateForceN,1e-12);
   assert(Math.abs(s.lateralResidualPa)<=MATERIAL_RESIDUAL_PA);
   if(boundary==='confined'){
    assert(s.b<=1&&s.gapXM>=0&&s.gapZM>=0&&s.wallReactionPa>=0);
    close(s.nominalLateralStressPa+s.wallReactionPa,0,MATERIAL_RESIDUAL_PA);
    close(s.complementarityJ,0,1e-15);
    close(s.wallForceXN,s.wallPressurePa*s.heightM*s.depthM,1e-12);
    close(s.wallForceZN,s.wallPressurePa*s.heightM*s.widthM,1e-12);
   }
   // Independent finite grid is evidence within this ansatz, not a global proof.
   const upper=boundary==='free'?1/Math.sqrt(h):1;
   for(let i=0;i<=100;i++)assert(s.energyJ<=blockEnergy(h+(upper-h)*i/100,h,p)+1e-12);
  }
 }
});
test('finite bulk differs from exact J=1 and confinement changes compression work and forces',()=>{
 const low=state({bulk:50000}),high=state({bulk:250000});
 assert(low.free.b>1&&low.free.J<1&&low.free.J>.99);
 assert(high.free.J>low.free.J&&high.free.J<1);
 close(low.confined.J,.8);assert(low.confined.plateForceN>9*low.free.plateForceN);
 assert(high.confined.plateForceN>low.confined.plateForceN);
 const stiff=state({mu:5000});assert(stiff.free.J<low.free.J&&stiff.free.plateForceN>low.free.plateForceN);
 close(low.confined.wallPressurePa,9738.910628109279,1e-8);
});
test('zero bulk isotropic collapse and weak-bulk pull-away are explicit counterexamples',()=>{
 for(const h of [.5,.8,1]){
  const pair=state({heightStretch:h,bulk:0});
  for(const s of [pair.free,pair.confined]){
   close(s.b,h);close(s.J,h**3);close(s.energyJ,0,1e-15);close(s.plateForceN,0,1e-12);
   assert(!s.wallActive);close(s.wallReactionPa,0);
  }
 }
 const pair=state({bulk:500});assert(pair.confined.b<1&&!pair.confined.wallActive&&pair.confined.gapXM>0);
 close(pair.confined.b,pair.free.b,1e-14);close(pair.confined.wallReactionPa,0);
});
test('finite caps retain feasible geometry while exposing unconverged residuals, including near wall transition',()=>{
 const coarse=state({iterations:8}),fine=state({iterations:32});
 assert(coarse.free.accepted&&!coarse.free.converged);assert(fine.free.converged);
 assert(Math.abs(fine.free.lateralResidualPa)<Math.abs(coarse.free.lateralResidualPa));
 assert(coarse.confined.accepted&&coarse.confined.converged);
 // Slightly below onset of wall compression: an unrestricted midpoint can cross b=1.
 for(const h of [.5,.8,.99]){
  const mu=1500,I1=2+h*h,K=mu*h**(-2/3)*(1-I1/3)/((1-h)*h);
  for(const bulk of [K*(1-1e-9),K*(1+1e-9)]){
   const s=state({heightStretch:h,bulk,iterations:8}).confined;
   assert(s.accepted&&s.b<=1&&s.gapXM>=0&&s.wallReactionPa>=0);
  }
 }
});
test('invalid domains, inversion, nonfinite candidates and positive-J wall penetration reject',()=>{
 for(const p of [null,{},...['heightStretch','mu','bulk','iterations'].flatMap(k=>[NaN,Infinity,-1].map(v=>({...MATERIAL_DEFAULTS,[k]:v}))),
  {...MATERIAL_DEFAULTS,heightStretch:0},{...MATERIAL_DEFAULTS,heightStretch:1.01},{...MATERIAL_DEFAULTS,mu:0},
  {...MATERIAL_DEFAULTS,bulk:250001},{...MATERIAL_DEFAULTS,iterations:7}])assert.throws(()=>compressionPair(p),RangeError);
 for(const b of [0,-1,NaN,Infinity,1e200,1e-200])assert(!evaluateCompressionCandidate(MATERIAL_DEFAULTS,b).accepted);
 const infeasible=evaluateCompressionCandidate(MATERIAL_DEFAULTS,1/Math.sqrt(.8),'confined');
 assert(!infeasible.accepted&&infeasible.J>0&&infeasible.penetrationXM>0);
 assert(evaluateCompressionCandidate(MATERIAL_DEFAULTS,1/Math.sqrt(.8),'free').accepted);
 assert.throws(()=>evaluateCompressionCandidate(MATERIAL_DEFAULTS,1,'glued'),RangeError);
});
test('elastic load/unload and explicit default reset are history-free and deterministic',()=>{
 const before=state();state({heightStretch:.5,bulk:250000});
 const restored=state({heightStretch:1});
 for(const s of [restored.free,restored.confined]){close(s.b,1);close(s.J,1);close(s.energyJ,0);close(s.plateForceN,0);}
 assert.deepEqual(state(),before);
});

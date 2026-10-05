/** Lab 5 extension: homogeneous, quasistatic compression under its unchanged
 * split neo-Hookean law. SI, frictionless plates, positive orientation.
 * No anatomical solver, contact search, spatial FEM or pressure field.
 */
import {TISSUE,blockEnergy,blockStress} from './tissue.mjs';
import {boundaryMeasurements,BOX_FACES} from './continuum-properties.mjs';
export const COMPRESSION_DEFAULTS=Object.freeze({mu:1500,bulk:50000,heightStretch:.8,force:2,mode:'displacement',boundary:'free'});
export const COMPRESSION_LIMITS=Object.freeze({minimumHeightStretch:.6,forceMinimumHeightStretch:.8,stressTolerancePa:1e-7,forceToleranceN:1e-8,energyDerivativeTolerancePa:1e-3,rootBisections:52});
const finite=x=>Number.isFinite(x);
const scope='Homogeneous isotropic elastic Lab 5 block; prescribed boundary or stationary compression branch. No biological calibration, spatial stability or anatomical convergence.';
function validate(p){
 if(![p.mu,p.bulk,p.heightStretch,p.force].every(finite)||p.mu<100||p.mu>10000||p.bulk<0||p.bulk>1000000||p.heightStretch<.6||p.heightStretch>1||p.force<0||p.force>20||!['free','confined'].includes(p.boundary)||!['displacement','force'].includes(p.mode))throw new RangeError('Compression controls outside the declared domain');
}
function root(fn,lo,hi){
 let a=fn(lo),b=fn(hi);
 if(!finite(a)||!finite(b)||a*b>0)throw new RangeError('No bracketed equilibrium in the declared domain');
 if(a===0)return lo;if(b===0)return hi;
 for(let i=0;i<COMPRESSION_LIMITS.rootBisections;i++){
  const mid=(lo+hi)/2;if(mid===lo||mid===hi)break;
  const f=fn(mid);if(!finite(f))throw new RangeError('Invalid equilibrium candidate');
  if(f===0)return mid;
  if(f*a>0){lo=mid;a=f;}else{hi=mid;b=f;}
 }
 return (lo+hi)/2;
}
/** Independent lateral equation in the volume variable J, from Cauchy stress.
 * Does not call blockStress or the primary stretch root.
 */
export function volumeEquilibrium(h,mu,bulk){
 if(!(h>0&&h<=1&&mu>0&&bulk>=0))throw new RangeError('Positive compressed state required');
 if(h===1)return 1;if(bulk===0)return h**3;
 return root(J=>mu/3*(J/h-h*h)/J**(5/3)+bulk*(J-1),h**3,1);
}
function stretches(h,p){
 return p.boundary==='confined'?1:p.bulk===0?h:h===1?1:root(t=>blockStress(t,h,p).px,h,1/Math.sqrt(h));
}
function reaction(h,p){const t=stretches(h,p);return -TISSUE.width*TISSUE.depth*blockStress(t,h,p).py;}
export function compressionState(parameters=COMPRESSION_DEFAULTS){
 const controls={...parameters};validate(controls);
 const p={...TISSUE,mu:controls.mu,bulk:controls.bulk,boundary:controls.boundary};
 let h=controls.heightStretch;
 const maxForceN=reaction(COMPRESSION_LIMITS.forceMinimumHeightStretch,p);
 if(controls.mode==='force'){
  if(controls.boundary==='free'&&controls.bulk===0)throw new RangeError('Free block with zero bulk has no unique force-controlled equilibrium; use imposed height');
  if(controls.force>maxForceN+COMPRESSION_LIMITS.forceToleranceN)throw new RangeError(`Force exceeds the supported h ≥ 0.8 branch (${maxForceN.toPrecision(6)} N)`);
  // A bounded check of the actual reduced branch, not a global uniqueness proof.
  let previous=maxForceN;
  for(let i=1;i<=16;i++){
   const next=reaction(.8+.2*i/16,p);
   if(next>previous+COMPRESSION_LIMITS.forceToleranceN)throw new RangeError('Nonmonotone force branch; no accepted force-controlled state');
   previous=next;
  }
  h=root(x=>reaction(x,p)-controls.force,.8,1);
 }
 const t=stretches(h,p),stress=blockStress(t,h,p),{J}=stress,V0=TISSUE.width*TISSUE.height*TISSUE.depth;
 const area0=TISSUE.width*TISSUE.depth,currentPlateAreaM2=area0*t*t,plateReactionN=-area0*stress.py;
 const sigmaLateral=stress.px*t/J,sigmaAxial=stress.py*h/J;
 const bulkPressurePa=controls.bulk*(1-J),meanCompressionPressurePa=-(2*sigmaLateral+sigmaAxial)/3;
 const Joracle=controls.boundary==='free'?volumeEquilibrium(h,p.mu,p.bulk):h;
 if(!(J>0)||Math.abs(J-Joracle)>1e-10||controls.boundary==='free'&&Math.abs(stress.px)>COMPRESSION_LIMITS.stressTolerancePa)throw new Error('Independent lateral equilibrium check failed');
 const forceResidualN=controls.mode==='force'?plateReactionN-controls.force:0;
 if(Math.abs(forceResidualN)>COMPRESSION_LIMITS.forceToleranceN)throw new Error('Plate force residual failed');
 const probes=[2e-6,1e-6].map(delta=>{
  const py=(blockEnergy(t,h+delta,p)-blockEnergy(t,h-delta,p))/(2*delta*V0);
  const px=(blockEnergy(t+delta,h,p)-blockEnergy(t-delta,h,p))/(4*delta*V0);
  return {delta,axialPa:py,lateralPa:px,axialDifferencePa:py-stress.py,lateralDifferencePa:px-stress.px};
 });
 if(probes.some(q=>Math.abs(q.axialDifferencePa)>COMPRESSION_LIMITS.energyDerivativeTolerancePa||Math.abs(q.lateralDifferencePa)>COMPRESSION_LIMITS.energyDerivativeTolerancePa))throw new Error('Energy/stress finite-difference check failed');
 const reference=Array.from({length:8},(_,i)=>[TISSUE.width,TISSUE.height,TISSUE.depth].map((L,d)=>(i>>d&1)*L));
 const current=reference.map(x=>[t*x[0],h*x[1],t*x[2]]),referenceBoundary=boundaryMeasurements(reference,BOX_FACES),currentBoundary=boundaryMeasurements(current,BOX_FACES);
 const volumeRatio=currentBoundary.signedVolumeM3/referenceBoundary.signedVolumeM3,energyJ=blockEnergy(t,h,p);
 const deviatoricEnergyJ=V0*p.mu/2*(J**(-2/3)*(2*t*t+h*h)-3),volumeEnergyJ=V0*p.bulk/2*(J-1)**2;
 const lateralFaceAreaM2=TISSUE.height*TISSUE.depth*h*t;
 // Signed force ON the block at one +x face; the opposing face is opposite.
 const sideSupportForceN=sigmaLateral*lateralFaceAreaM2;
 if(Math.abs(volumeRatio-J)>1e-12||Math.abs(meanCompressionPressurePa-bulkPressurePa)>1e-7||Math.abs(plateReactionN+sigmaAxial*currentPlateAreaM2)>1e-10)throw new Error('Independent volume/configuration check failed');
 return {accepted:true,scope,controls,heightStretch:h,lateralStretch:t,J,volumeRatio,volumeMeasurementDifference:volumeRatio-J,volumeEquilibriumJ:Joracle,volumeEquilibriumDifference:J-Joracle,
  reference,current,referenceBoundary,currentBoundary,heightM:h*TISSUE.height,plateDisplacementM:TISSUE.height*(1-h),currentPlateAreaM2,
  plateReactionN,platePressurePa:plateReactionN/currentPlateAreaM2,bulkPressurePa,meanCompressionPressurePa,lateralPiolaStressPa:stress.px,axialPiolaStressPa:stress.py,lateralCauchyStressPa:sigmaLateral,axialCauchyStressPa:sigmaAxial,sideSupportForceN,
  energyJ,deviatoricEnergyJ,volumeEnergyJ,forceResidualN,lateralResidualPa:controls.boundary==='free'?stress.px:null,energyDerivativeProbes:probes,maxSupportedForceN:maxForceN,
  forceBranch:controls.mode==='force'?'Stationary branch 0.8 ≤ h ≤ 1; monotonicity sampled, no global stability theorem':'Imposed height 0.6 ≤ h ≤ 1; reaction is an output',bulkShearRatio:p.bulk/p.mu,
  isochoricComparison:{lateralStretch:1/Math.sqrt(h),J:1,interpretation:'Prescribed exact-isochoric geometry; not the finite-bulk free-side equilibrium'}};
}

// Homogeneous frictionless compression: one lateral degree of freedom, no mesh.
// Reuse the existing law without altering any older laboratory's calibration.
import {TISSUE,blockEnergy,blockStress} from './tissue.mjs';
export const MATERIAL_DEFAULTS=Object.freeze({heightStretch:.8,mu:1500,bulk:50000,iterations:64});
export const MATERIAL_DOMAIN=Object.freeze({heightStretch:[.5,1],mu:[500,5000],bulk:[0,250000],iterations:[8,32,64]});
export const MATERIAL_RESIDUAL_PA=1e-5; // New lesson's displayed numerical criterion, not a material validity limit.
export function validateMaterial(p){
 for(const key of ['heightStretch','mu','bulk']){
  const [lo,hi]=MATERIAL_DOMAIN[key];
  if(!Number.isFinite(p[key])||p[key]<lo||p[key]>hi)throw new RangeError(`${key} outside declared specimen domain`);
 }
 if(!MATERIAL_DOMAIN.iterations.includes(p.iterations))throw new RangeError('unsupported bisection cap');
 return {...TISSUE,mu:p.mu,bulk:p.bulk};
}
export function compressionPair(parameters=MATERIAL_DEFAULTS){
 const p=validateMaterial(parameters),h=parameters.heightStretch,V0=p.width*p.height*p.depth;
 let lo=h,hi=1/Math.sqrt(h),used=0;
 // Endpoints have P_x <= 0 and >= 0. No iteration count is a convergence badge.
 if(p.bulk===0||h===1)hi=lo;
 else for(;used<parameters.iterations;used++){
  const mid=(lo+hi)/2;
  if(mid===lo||mid===hi)break;
  if(blockStress(mid,h,p).px>0)hi=mid;else lo=mid;
 }
 const freeB=(lo+hi)/2,wallStress=blockStress(1,h,p).px;
 // Decide wall activity at the wall itself, independent of an approximate root.
 // Positive wall stress would require tensile attachment: allow pull-away instead.
 const wallActive=wallStress<0;
 function specimen(boundary){
  const active=boundary==='confined'&&wallActive,b=active?1:freeB;
  const {px,py,J}=blockStress(b,h,p),reaction=active?-px:0;
  const plateForceN=-p.width*p.depth*py,gapX=p.width*(1-b)/2,gapZ=p.depth*(1-b)/2;
  const residualPa=px+reaction,energyJ=blockEnergy(b,h,p);
  const wallForceXN=reaction*p.height*p.depth,wallForceZN=reaction*p.width*p.height;
  const complementarityJ=boundary==='confined'?2*(wallForceXN*gapX+wallForceZN*gapZ):0;
  const values=[b,J,px,py,plateForceN,residualPa,energyJ,reaction,complementarityJ];
  if(!values.every(Number.isFinite)||b<=0||J<=0)throw new RangeError('nonfinite or inverted candidate');
  return {boundary,b,heightStretch:h,J,volumeM3:V0*J,widthM:p.width*b,heightM:p.height*h,depthM:p.depth*b,
   referenceVolumeM3:V0,energyJ,nominalLateralStressPa:px,nominalAxialStressPa:py,
   plateForceN,platePressurePa:plateForceN/(p.width*p.depth*b*b),wallActive:active,
   wallReactionPa:reaction,wallPressurePa:reaction/(b*h),wallForceXN,wallForceZN,
   gapXM:boundary==='confined'?gapX:null,gapZM:boundary==='confined'?gapZ:null,
   lateralResidualPa:residualPa,complementarityJ,accepted:true,
   converged:Math.abs(residualPa)<=MATERIAL_RESIDUAL_PA,
   validity:'Supported homogeneous elastic ansatz; no calibrated material validity or plastic failure prediction'};
 }
 return {parameters:{...parameters},reference:{widthM:p.width,heightM:p.height,depthM:p.depth,volumeM3:V0},
  free:specimen('free'),confined:specimen('confined'),
  solve:{iterations:used,cap:parameters.iterations,bracket:[lo,hi],bracketWidth:hi-lo,residualCriterionPa:MATERIAL_RESIDUAL_PA},
  scope:'Reduced quasistatic homogeneous elastic equilibrium; no spatial muscle, anatomy, friction, dynamics, plasticity or proved global optimum'};
}

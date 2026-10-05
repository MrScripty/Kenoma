/** Small-strain axial bar. No body load, constant E, tensile N and strain positive.
 * Piecewise-constant areas or a linear-area taper, not a fibre-resolved muscle.
 */
export const BAR_DEFAULTS=Object.freeze({length:.2,area:.0003,ratio:2,modulus:100000,force:.3,activeStress:1000,activation:1,segments:16,mode:'passive',shape:'linear'});
function validate(p){
 if(!['passive','active-fixed'].includes(p.mode)||!['linear','two-segment'].includes(p.shape)||!Object.entries(p).filter(([,v])=>typeof v==='number').every(([,v])=>Number.isFinite(v)))throw new RangeError('Finite bar parameters required');
 if(!(p.length>0&&p.area>0&&p.ratio>0&&p.modulus>0&&p.activation>=0&&p.activation<=1&&p.activeStress>=0&&Number.isInteger(p.segments)&&p.segments>=2&&p.segments<=512))throw new RangeError('Positive geometry/modulus and bounded activation/refinement required');
}
export function barState(p=BAR_DEFAULTS){
 validate(p);
 const stress=p.activation*p.activeStress,areaAt=s=>p.area*(p.shape==='linear'?1+(p.ratio-1)*s/p.length:s<p.length/2?1:p.ratio);
 // Independent exact compliance for linear area or two equal-length areas.
 const compliance=p.shape==='linear'?p.length/(p.modulus*p.area)*(Math.abs(p.ratio-1)<1e-10?1:Math.log(p.ratio)/(p.ratio-1)):p.length/(2*p.modulus*p.area)*(1+1/p.ratio);
 // Exact constant resultant satisfying the prescribed fixed-end compatibility.
 const resultantN=p.mode==='active-fixed'?stress*p.length/(p.modulus*compliance):p.force;
 const activeStrain=p.mode==='active-fixed'?stress/p.modulus:0;
 // With positive area, strain is monotone in this linear/step area law.
 // Midpoint samples alone can miss the endpoint that violates small strain.
 const endpointStrains=[p.area,p.area*p.ratio].map(A=>resultantN/(p.modulus*A)-activeStrain);
 const minimumStrain=Math.min(...endpointStrains),maximumStrain=Math.max(...endpointStrains);
 const maxAbsStrain=Math.max(Math.abs(minimumStrain),Math.abs(maximumStrain));
 const exactExtensionM=resultantN*compliance-activeStrain*p.length;
 const dx=p.length/p.segments;
 let displacement=0,elasticEnergyJ=0;
 const samples=Array.from({length:p.segments},(_,i)=>{
  const s=(i+.5)*dx,A=areaAt(s),strain=resultantN/(p.modulus*A)-activeStrain;
  const u0=displacement;displacement+=strain*dx;
  elasticEnergyJ+=.5*p.modulus*strain*strain*A*dx;
  return {sM:s,areaM2:A,strain,resultantN,displacementStartM:u0,displacementEndM:displacement};
 });
 return {accepted:true,resultantN,exactComplianceMPerN:compliance,exactExtensionM,numericalExtensionM:displacement,extensionErrorM:displacement-exactExtensionM,activeStrain,elasticEnergyJ,endpointStrains,minimumStrain,maximumStrain,maxAbsStrain,smallStrainWarning:maxAbsStrain>.05,samples,scope:'Small-strain homogeneous axial bar; prescribed active-stress offset. No active muscle force-length, velocity, transverse equilibrium or calibration.'};
}

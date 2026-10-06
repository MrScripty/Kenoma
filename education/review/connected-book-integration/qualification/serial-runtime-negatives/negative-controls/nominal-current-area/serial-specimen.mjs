/** Two separate homogeneous incompressible neo-Hookean blocks in axial series.
 * Ideal bilateral traction fixtures transmit signed N and allow lateral sliding.
 * A fixed-length massless spacer moves with the block ends; it is not tissue.
 * All dimensions, vertices, stresses and volume measurements use SI units.
 */
import {BOX_FACES,boundaryMeasurements} from './continuum-properties.mjs';
export const SERIAL_DEFAULTS=Object.freeze({length:.025,area:.0003,ratio:2,mu:1500,force:.1,iterations:48});
export const SERIAL_FORCE_CRITERION_N=1e-10;
export const SERIAL_STRETCH_BRACKET=Object.freeze([.6,1.75]);
export const SERIAL_SPACER_LENGTH_M=.012;
export function validateSerialParameters(p){
 const bounds={length:[.01,.04],area:[.0003,.001],ratio:[.5,4],mu:[500,5000],force:[-.1,.1],iterations:[8,64]};
 for(const [key,[lo,hi]] of Object.entries(bounds))if(!Number.isFinite(p[key])||p[key]<lo||p[key]>hi)throw new RangeError(`Out-of-domain ${key}`);
 if(!Number.isInteger(p.iterations))throw new RangeError('Integer bisection cap required');
 return p;
}
// Factored forms avoid cancellation close to the undeformed state.
export const nominalStress=(mu,lambda)=>mu*(lambda-1)*(lambda*lambda+lambda+1)/(lambda*lambda);
export const energyDensity=(mu,lambda)=>mu*(lambda-1)**2*(lambda+2)/(2*lambda);
export function solveStretch(area,mu,force,cap){
 if(![area,mu,force,cap].every(Number.isFinite)||area<=0||mu<=0||!Number.isInteger(cap)||cap<8||cap>64)throw new RangeError('Positive material/area and bounded root cap required');
 let [lo,hi]=SERIAL_STRETCH_BRACKET;
 const residual=lambda=>area/lambda*nominalStress(mu,lambda)-force;
 if(residual(lo)>0||residual(hi)<0)throw new RangeError('Load outside the declared positive-stretch bracket');
 if(force===0)return {stretch:1,iterations:0,cap,bracket:[1,1],bracketWidth:0,residualN:0,converged:true};
 let iterations=0;
 for(;iterations<cap;iterations++){
  const mid=(lo+hi)/2;if(mid===lo||mid===hi)break;
  if(residual(mid)<0)lo=mid;else hi=mid;
 }
 const stretch=(lo+hi)/2,residualN=residual(stretch);
 return {stretch,iterations,cap,bracket:[lo,hi],bracketWidth:hi-lo,residualN,converged:Math.abs(residualN)<=SERIAL_FORCE_CRITERION_N};
}
const subtract=(a,b)=>a.map((v,i)=>v-b[i]);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function vertices(start,length,width,depth){return Array.from({length:8},(_,i)=>[start+(i&1)*length,((i>>1&1)-.5)*width,((i>>2&1)-.5)*depth]);}
function geometryMeasurements(current,reference){
 const currentLengthM=Math.hypot(...subtract(current[1],current[0]));
 const currentAreaM2=Math.hypot(...cross(subtract(current[2],current[0]),subtract(current[4],current[0])));
 const currentBoundary=boundaryMeasurements(current,BOX_FACES),referenceBoundary=boundaryMeasurements(reference,BOX_FACES);
 return {currentLengthM,currentAreaM2,currentBoundaryVolumeM3:currentBoundary.signedVolumeM3,referenceBoundaryVolumeM3:referenceBoundary.signedVolumeM3,volumeRatio:currentBoundary.signedVolumeM3/referenceBoundary.signedVolumeM3,exteriorAreaM2:currentBoundary.surfaceAreaM2};
}
export function serialSpecimen(p=SERIAL_DEFAULTS){
 validateSerialParameters(p);let currentStart=0;
 const cells=[p.area,p.area*p.ratio].map((area,index)=>{
  const solve=solveStretch(area,p.mu,p.force,p.iterations),stretch=solve.stretch,lateralStretch=1/Math.sqrt(stretch),width=Math.sqrt(area);
  const referenceVertices=vertices(index*(p.length+SERIAL_SPACER_LENGTH_M),p.length,width,width);
  const currentVertices=vertices(currentStart,p.length*stretch,width*lateralStretch,width*lateralStretch);
  currentStart+=p.length*stretch+SERIAL_SPACER_LENGTH_M;
  const measured=geometryMeasurements(currentVertices,referenceVertices),nominalStressPa=nominalStress(p.mu,stretch),incompressibilityMultiplierPa=p.mu/stretch;
  const cell={index,referenceAreaM2:area,referenceLengthM:p.length,stretch,lateralStretch,engineeringStrain:stretch-1,referenceVertices,currentVertices,F:[stretch,0,0,0,lateralStretch,0,0,0,lateralStretch],J:stretch*lateralStretch*lateralStretch,referenceVolumeM3:area*p.length,...measured,nominalStressPa,cauchyStressPa:stretch*nominalStressPa,incompressibilityMultiplierPa,lateralStressPa:p.mu*lateralStretch*lateralStretch-incompressibilityMultiplierPa,resultantN:area*nominalStressPa,forceResidualN:solve.residualN,energyJ:area*p.length*energyDensity(p.mu,stretch),solve};
  if(!(measured.currentBoundaryVolumeM3>0)||Math.abs(measured.volumeRatio-1)>1e-12||Math.abs(cell.lateralStressPa)>1e-10)throw new RangeError('Local geometry or free-side stress invariant failed');
  return cell;
 });
 const totalCurrentLengthM=cells.reduce((sum,c)=>sum+c.currentLengthM,0)+SERIAL_SPACER_LENGTH_M,totalReferenceLengthM=2*p.length+SERIAL_SPACER_LENGTH_M;
 return {schema:1,model:'two-block-incompressible-neo-hookean-series-v1',parameters:{...p},cells,spacerLengthM:SERIAL_SPACER_LENGTH_M,totalCurrentLengthM,totalReferenceLengthM,extensionM:totalCurrentLengthM-totalReferenceLengthM,referenceVolumeM3:cells.reduce((sum,c)=>sum+c.referenceVolumeM3,0),currentBoundaryVolumeM3:cells.reduce((sum,c)=>sum+c.currentBoundaryVolumeM3,0),totalEnergyJ:cells.reduce((sum,c)=>sum+c.energyJ,0),forceCriterionN:SERIAL_FORCE_CRITERION_N,converged:cells.every(c=>c.solve.converged),scope:'Two separate homogeneous incompressible neo-Hookean blocks; bilateral ideal axial fixtures allow tangential sliding. No continuous taper/interface solve, unrestricted stability or anatomical calibration.'};
}
export function globalVolumeOnlyCandidate(p,state=serialSpecimen(p)){
 validateSerialParameters(p);
 // Opposite weighted local volume changes conceal each other in the sum.
 const ratios=[1.1,1-.1/p.ratio];
 const candidateCells=state.cells.map((cell,index)=>{
  const b=cell.lateralStretch*Math.sqrt(ratios[index]),width=Math.sqrt(cell.referenceAreaM2);
  const current=vertices(cell.currentVertices[0][0],cell.currentLengthM,width*b,width*b);
  return {index,...geometryMeasurements(current,cell.referenceVertices),J:cell.stretch*b*b,lateralStressPa:p.mu*b*b-cell.incompressibilityMultiplierPa};
 });
 const currentBoundaryVolumeM3=candidateCells.reduce((sum,c)=>sum+c.currentBoundaryVolumeM3,0);
 const accepted=candidateCells.every(c=>c.currentBoundaryVolumeM3>0&&Math.abs(c.J-1)<=1e-12&&Math.abs(c.lateralStressPa)<=1e-10);
 return {accepted,reason:accepted?'Local geometry and lateral traction criteria met.':'Total volume cancels, but each block violates incompressibility and free lateral traction; solved specimen retained.',candidateCells,currentBoundaryVolumeM3,referenceVolumeM3:state.referenceVolumeM3,totalVolumeRatio:currentBoundaryVolumeM3/state.referenceVolumeM3};
}

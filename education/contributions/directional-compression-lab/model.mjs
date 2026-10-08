import {validateMaterial,MATERIAL_DEFAULTS,MATERIAL_RESIDUAL_PA} from '../../web/material-response.mjs';
import {boundaryMeasurements,BOX_FACES} from '../../web/continuum-properties.mjs';
export const DEFAULTS=Object.freeze({...MATERIAL_DEFAULTS,axialStretch:1,direction:'Y'});
export const FORMULAS=Object.freeze({energy:'U = V0 [mu/2 (J^(-2/3) I1 - 3) + K/2 (J - 1)^2]',stress:'Pi = mu J^(-2/3) (li - I1/(3 li)) + K (J - 1) J/li',volume:'J = lx ly lz; I1 = lx^2 + ly^2 + lz^2',force:'Nx = Px H0 D0; C = -Pload A0; q = C/Acurrent = -Pload lload/J',free:'Pfree = 0; solve only the remaining transverse stretch b'});
export const QUANTITIES=Object.freeze({J:{unit:'1',definition:'current/reference volume for this homogeneous positive diagonal map'},stretch:{unit:'1',definition:'current/reference material-edge length'},Nx:{unit:'N',sign:'positive tension',definition:'signed longitudinal end resultant; X length is prescribed'},C:{unit:'N',sign:'positive compression',definition:'signed resultant on one transverse controlled face, not sum over opposite faces'},q:{unit:'Pa',sign:'positive compression',definition:'uniform current-area applied normal traction; not interstitial/vascular pressure'},Pi:{unit:'Pa',sign:'positive tension',definition:'first Piola stress conjugate to stretch per reference face area'},sigma:{unit:'Pa',sign:'positive tension',definition:'Cauchy normal stress Pi li/J'},area:{unit:'m2',definition:'geometric full-face area; not tendon CSA or PCSA'},energy:{unit:'J',definition:'stored elastic energy; no viscous or fluid dissipation'},calibration:{status:'AUTHORED_UNCALIBRATED_PASSIVE_ISOTROPIC',definition:'same existing teaching dimensions/energy/parameter bounds; no biological fitting'}});
export function diagonalResponse(stretches,p){
 if(!Array.isArray(stretches)||stretches.length!==3||!stretches.every(v=>Number.isFinite(v)&&v>0))throw new RangeError('Three finite positive stretches required');
 const J=stretches.reduce((a,b)=>a*b,1),I1=stretches.reduce((s,v)=>s+v*v,0),V0=p.width*p.height*p.depth;
 const energyJ=V0*(p.mu/2*(J**(-2/3)*I1-3)+p.bulk/2*(J-1)**2);
 const nominalStressPa=stretches.map(l=>p.mu*J**(-2/3)*(l-I1/(3*l))+p.bulk*(J-1)*J/l);
 const cauchyStressPa=nominalStressPa.map((P,i)=>P*stretches[i]/J);
 if(![J,I1,energyJ,...nominalStressPa,...cauchyStressPa].every(Number.isFinite))throw new RangeError('Nonfinite response');
 return {J,I1,energyJ,nominalStressPa,cauchyStressPa};
}
export function specimen(parameters=DEFAULTS){
 const p=validateMaterial(parameters);
 if(!Number.isFinite(parameters.axialStretch)||parameters.axialStretch<.8||parameters.axialStretch>1.2||!['Y','Z'].includes(parameters.direction))throw new RangeError('Axial domain0.8..1.2 and direction Y/Z required');
 const loaded=parameters.direction==='Y'?1:2,free=loaded===1?2:1,dimensions=[p.width,p.height,p.depth],reference=Array.from({length:8},(_,i)=>dimensions.map((L,d)=>(i>>d&1)*L));
 function solve(h){
  const stretches=[parameters.axialStretch,1,1];stretches[loaded]=h;
  let lo=.1,hi=4,used=0;
  const at=b=>{stretches[free]=b;return diagonalResponse(stretches,p);};
  if(!(at(lo).nominalStressPa[free]<0&&at(hi).nominalStressPa[free]>0))throw new RangeError('Root not bracketed');
  for(;used<parameters.iterations;used++){
   const mid=(lo+hi)/2;if(mid===lo||mid===hi)break;
   if(at(mid).nominalStressPa[free]>0)hi=mid;else lo=mid;
  }
  const b=(lo+hi)/2,response=at(b),current=reference.map(X=>X.map((v,i)=>v*stretches[i]));
  const measured=boundaryMeasurements(current,BOX_FACES),V0=p.width*p.height*p.depth,referenceAreaM2=dimensions.filter((_,i)=>i!==loaded).reduce((a,v)=>a*v,1),currentAreaM2=referenceAreaM2*stretches[0]*b;
  const compressionResultantN=-response.nominalStressPa[loaded]*referenceAreaM2,contactPressurePa=compressionResultantN/currentAreaM2,endResultantN=response.nominalStressPa[0]*p.height*p.depth,freeResidualPa=response.nominalStressPa[free];
  return {...response,stretches:stretches.slice(),reference,current,dimensionsM:dimensions.map((v,i)=>v*stretches[i]),referenceAreaM2,currentAreaM2,compressionResultantN,contactPressurePa,endResultantN,freeResidualPa,converged:Math.abs(freeResidualPa)<=MATERIAL_RESIDUAL_PA,solve:{bracket:[lo,hi],used,cap:parameters.iterations,residualCriterionPa:MATERIAL_RESIDUAL_PA},boundaryVolumeM3:measured.signedVolumeM3,independentVolumeRatio:measured.signedVolumeM3/V0,volumeDisagreement:measured.signedVolumeM3/V0-response.J,exteriorAreaM2:measured.surfaceAreaM2,requiresTensileGrip:compressionResultantN<0};
 }
 const state=solve(parameters.heightStretch),baseline=solve(1);
 return {schema:1,status:'PASSIVE_REDUCED_ELASTIC_SPECIMEN_NOT_BIOLOGICAL_VALIDATION',parameters:{...parameters},formulas:FORMULAS,quantities:QUANTITIES,referenceDimensionsM:dimensions,loadedAxis:loaded,freeAxis:free,state,baselineEndResultantN:baseline.endResultantN,changeInEndResultantN:state.endResultantN-baseline.endResultantN,scope:'Homogeneous positive diagonal deformation; X and one transverse pair of bilateral grips prescribe displacement, remaining transverse faces have zero normal traction. No activation, fibre architecture, unilateral contact, buckling, spatial bulging, transport or anatomy. Scalar residual is not unrestricted 3D stability.',calibrationStatus:QUANTITIES.calibration.status};
}

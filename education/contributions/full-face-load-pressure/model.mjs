import {specimen,diagonalResponse,DEFAULTS as PASSIVE_DEFAULTS} from '../directional-compression-lab/model.mjs';
import {validateMaterial,MATERIAL_RESIDUAL_PA} from '../../web/material-response.mjs';
import {boundaryMeasurements,BOX_FACES} from '../../web/continuum-properties.mjs';
export const DEFAULTS=Object.freeze({...PASSIVE_DEFAULTS,mode:'force',forceN:6.65,pressurePa:1350,breadthFactor:1,outerIterations:64});
export const SCOPE='Passive homogeneous positive diagonal full-face loading; fixed X length, traction-free remaining transverse faces. Different reference breadths change specimen volume/material amount. No localized contact patch, activation, biological calibration, fluid pressure, transport or unrestricted stability.';
export function evaluateAt(p,h){
 if(!p||!Number.isFinite(p.breadthFactor)||p.breadthFactor<.5||p.breadthFactor>2)throw new RangeError('Reference breadth factor outside 0.5..2');
 const base=specimen({...p,heightStretch:h,iterations:64}),s=base.state,loaded=base.loadedAxis,free=base.freeAxis;
 if(!s.converged)throw new RangeError('Inherited free-face residual failed');
 const material=validateMaterial({...p,heightStretch:h,iterations:64}),dimensions=[material.width,material.height,material.depth];dimensions[free]*=p.breadthFactor;
 [material.width,material.height,material.depth]=dimensions;
 const response=diagonalResponse(s.stretches,material),reference=Array.from({length:8},(_,i)=>dimensions.map((L,d)=>(i>>d&1)*L)),current=reference.map(X=>X.map((v,i)=>v*s.stretches[i]));
 const referenceAreaM2=dimensions.filter((_,i)=>i!==loaded).reduce((a,b)=>a*b,1),currentAreaM2=referenceAreaM2*s.stretches[0]*s.stretches[free],V0=dimensions.reduce((a,b)=>a*b,1),measured=boundaryMeasurements(current,BOX_FACES);
 const compressionResultantN=-response.nominalStressPa[loaded]*referenceAreaM2,contactPressurePa=compressionResultantN/currentAreaM2;
 return {...s,...response,reference,current,referenceDimensionsM:dimensions,dimensionsM:dimensions.map((v,i)=>v*s.stretches[i]),referenceVolumeM3:V0,referenceAreaM2,currentAreaM2,compressionResultantN,contactPressurePa,nominalCompressionPa:compressionResultantN/referenceAreaM2,endReferenceAreaM2:dimensions[1]*dimensions[2],endResultantN:response.nominalStressPa[0]*dimensions[1]*dimensions[2],boundaryVolumeM3:measured.signedVolumeM3,independentVolumeRatio:measured.signedVolumeM3/V0,volumeDisagreement:measured.signedVolumeM3/V0-response.J,exteriorAreaM2:measured.surfaceAreaM2,requiresTensileGrip:compressionResultantN<0};
}
export function solveComparison(p=DEFAULTS){
 if(!p||!['force','pressure'].includes(p.mode)||!['Y','Z'].includes(p.direction))throw new RangeError('Force/pressure mode and Y/Z direction required');
 for(const [key,lo,hi] of [['axialStretch',.8,1.2],['breadthFactor',.5,2],['forceN',0,100],['pressurePa',0,100000]])if(!Number.isFinite(p[key])||p[key]<lo||p[key]>hi)throw new RangeError(key+' outside declared domain');
 if(![8,32,64].includes(p.outerIterations))throw new RangeError('Unsupported outer bisection cap');
 const target=p.mode==='force'?p.forceN:p.pressurePa,tolerance=p.mode==='force'?1e-8:1e-5,key=p.mode==='force'?'compressionResultantN':'contactPressurePa';
 const residual=s=>s[key]-target;let lo=.5,hi=1,left=evaluateAt(p,lo),right=evaluateAt(p,hi),fl=residual(left),fr=residual(right),used=0,state;
 const endpointRange=[Math.min(left[key],right[key]),Math.max(left[key],right[key])];
 if(Math.abs(fl)<=tolerance)state=left;else if(Math.abs(fr)<=tolerance)state=right;else {
  if((fl>0)===(fr>0))throw new RangeError('Target not bracketed on h=0.5..1. Endpoint range '+endpointRange.map(v=>v.toPrecision(7)).join('..')+' '+(p.mode==='force'?'N':'Pa')+'; previous state retained.');
  for(;used<p.outerIterations;used++){
   const h=(lo+hi)/2;if(h===lo||h===hi)break;
   const mid=evaluateAt(p,h),fm=residual(mid);
   if((fm>0)===(fl>0)){lo=h;fl=fm;}else{hi=h;fr=fm;}
  }
  state=evaluateAt(p,(lo+hi)/2);
 }
 const outerResidual=residual(state),converged=Math.abs(outerResidual)<=tolerance&&Math.abs(state.freeResidualPa)<=MATERIAL_RESIDUAL_PA;
 return {schema:1,status:'AUTHORED_UNCALIBRATED_PASSIVE_FULL_FACE_COMPARISON',parameters:{...p},state,loadedAxis:p.direction==='Y'?1:2,freeAxis:p.direction==='Y'?2:1,solve:{mode:p.mode,target,unit:p.mode==='force'?'N':'Pa',outerResidual,outerCriterion:tolerance,freeCriterionPa:MATERIAL_RESIDUAL_PA,converged,used,cap:p.outerIterations,bracket:[lo,hi],endpointRange,endpointRangeIsNotProofOfGlobalRange:true},scope:SCOPE,geometryPolicy:{fullFaceOnly:true,changesReferenceVolumeAndMaterialAmount:true,referenceBreadthFactor:p.breadthFactor},pressureConvention:'q=C/Acurrent=-sigma_loaded; nominal compression=C/A0. Both positive compression; no interstitial or vascular pressure.',proofScope:'Inherited three conditional Std product identities only; no Real instantiation, constitutive law or inverse solver theorem.'};
}

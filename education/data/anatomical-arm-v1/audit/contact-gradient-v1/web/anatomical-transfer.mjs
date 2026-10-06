/** Actual one-DOF rigid attachment Jacobian and tension-only transfer. SI. */
import {tendonSegment} from './anatomical-material.mjs';
const sub=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
export function attachmentMap(referencePoint,frame,q,{moving=true}={}){
 if(![q,...referencePoint,...frame.origin_m,...frame.axis_unit,frame.atlas_bind_angle_rad].every(Number.isFinite)||Math.abs(Math.hypot(...frame.axis_unit)-1)>1e-10)throw new RangeError('Rigid attachment frame');
 if(!moving)return {position:referencePoint.slice(),B:[0,0,0]};
 const r=sub(referencePoint,frame.origin_m),e=frame.axis_unit,c=Math.cos(q-frame.atlas_bind_angle_rad),s=Math.sin(q-frame.atlas_bind_angle_rad),exr=cross(e,r),projection=dot(e,r),rotated=r.map((v,i)=>c*v+s*exr[i]+(1-c)*projection*e[i]);
 return {position:rotated.map((v,i)=>v+frame.origin_m[i]),B:cross(e,rotated)};
}
export function tendonTransfer(node,referenceAnchor,frame,q,{L0,A0,moving=true,material}={}){
 const anchor=attachmentMap(referenceAnchor,frame,q,{moving}),d=sub(node,anchor.position),length=Math.hypot(...d),r=tendonSegment(length,L0,A0,material),direction=length>1e-12?d.map(v=>v/length):[0,0,0],boneForce=direction.map(v=>r.forceN*v),nodeForce=boneForce.map(v=>-v),Q=dot(anchor.B,boneForce);
 return {...r,lengthM:length,anchorPosition:anchor.position,B:anchor.B,nodeForce,boneForce,QNm:Q,nodeGradient:boneForce,qGradient:-Q};
}

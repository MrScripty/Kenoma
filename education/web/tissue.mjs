// A single homogeneous affine hyperelastic block between ideal frictionless plates.
// This is a reduced continuum ansatz, not a tetrahedron or mesh FEM implementation.
export const TISSUE=Object.freeze({height:0.06,width:0.08,depth:0.05,mu:1500,bulk:50000,gapOpen:0.085,gapClose:0.055});
export function lbsPoint([x,y,z],q){return [(x+x*Math.cos(q)-y*Math.sin(q))/2,(y+x*Math.sin(q)+y*Math.cos(q))/2,z];}
export function blockEnergy(t,h,p=TISSUE){
 const J=t*t*h,I1=2*t*t+h*h;
 if(J<=0||![t,h,J].every(Number.isFinite))throw new RangeError('positive tissue stretches required');
 return p.width*p.height*p.depth*(p.mu/2*(J**(-2/3)*I1-3)+p.bulk/2*(J-1)**2);
}
export function blockStress(t,h,p=TISSUE){
 const J=t*t*h,I1=2*t*t+h*h,factor=p.mu*J**(-2/3),vol=p.bulk*(J-1)*J;
 return {px:factor*(t-I1/(3*t))+vol/t,py:factor*(h-I1/(3*h))+vol/h,J};
}
export function tissueAt(q,p=TISSUE,contact=true){
 if(!Number.isFinite(q)||q<0||q>135*Math.PI/180||p.mu<=0||p.bulk<0)throw new RangeError('tissue model domain');
 const gap=p.gapOpen-p.gapClose*Math.sin(q/2),gapDerivative=-p.gapClose/2*Math.cos(q/2);
 const h=contact?Math.min(1,gap/p.height):1;
 let t=1;
 if(h<1){
  if(p.bulk===0)t=h;
  else {let lo=h,hi=1/Math.sqrt(h);for(let i=0;i<52;i++){const mid=(lo+hi)/2;if(blockStress(mid,h,p).px>0)hi=mid;else lo=mid;}t=(lo+hi)/2;}
 }
 const stress=blockStress(t,h,p),energy=blockEnergy(t,h,p),normal=contact?Math.max(0,-p.width*p.depth*stress.py):0;
 const currentArea=p.width*p.depth*t*t;
 const clearance=gap-h*p.height,torque=normal*gapDerivative;
 // Uniform 50/50 shared-pivot LBS: diag(cos(q/2),cos(q/2),1), rotated by q/2.
 const skinScale=Math.cos(q/2),skinJ=skinScale*skinScale;
 return {gap,gapDerivative,height:h*p.height,lateralStretch:t,heightStretch:h,volumeRatio:stress.J,volume:stress.J*p.width*p.height*p.depth,
  energy,normal,pressure:normal/currentArea,lateralStressResidual:Math.abs(stress.px),clearance,
  penetration:Math.max(0,-clearance),complementarity:normal*clearance,torque,
  skinScale,skinVolumeRatio:skinJ,skinHeight:p.height*skinScale,skinClearance:gap-p.height*skinScale};
}

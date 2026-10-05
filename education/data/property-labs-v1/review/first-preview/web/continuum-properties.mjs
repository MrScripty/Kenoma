/** Additive prescribed-kinematics lessons. SI; no muscle force or equilibrium.
 * Boundary-triangle volume does not call the deformation-gradient determinant.
 */
export const PROPERTY_DIMENSIONS=Object.freeze([.08,.06,.05]);
export const DEFORMATION_DEFAULTS=Object.freeze({sx:1.2,sy:.85,sz:1.03,shear:.25,angle:20,tx:0,ty:0,tz:0});
export const ISOCHORIC_DEFAULTS=Object.freeze({axial:.8,lateral:1,mode:'isochoric'});
const subtract=(a,b)=>a.map((v,i)=>v-b[i]);
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const norm=a=>Math.hypot(...a);
export const determinant3=A=>A[0]*(A[4]*A[8]-A[5]*A[7])-A[1]*(A[3]*A[8]-A[5]*A[6])+A[2]*(A[3]*A[7]-A[4]*A[6]);
export const multiply3=(A,B)=>Array.from({length:9},(_,i)=>{const r=Math.floor(i/3),c=i%3;return [0,1,2].reduce((s,k)=>s+A[r*3+k]*B[k*3+c],0);});
const transform=(A,x,t=[0,0,0])=>[0,1,2].map(r=>t[r]+dot(A.slice(r*3,r*3+3),x));
function inverse3(A){
 const d=determinant3(A);if(!(d>0))throw new RangeError('Reference orientation must be positive');
 return [A[4]*A[8]-A[5]*A[7],A[2]*A[7]-A[1]*A[8],A[1]*A[5]-A[2]*A[4],A[5]*A[6]-A[3]*A[8],A[0]*A[8]-A[2]*A[6],A[2]*A[3]-A[0]*A[5],A[3]*A[7]-A[4]*A[6],A[1]*A[6]-A[0]*A[7],A[0]*A[4]-A[1]*A[3]].map(v=>v/d);
}
const edges=vertices=>Array.from({length:9},(_,i)=>vertices[1+i%3][Math.floor(i/3)]-vertices[0][Math.floor(i/3)]);
export const TETRAHEDRON_FACES=Object.freeze([[0,2,1],[0,1,3],[0,3,2],[1,2,3]]);
export const BOX_FACES=Object.freeze([[0,2,3],[0,3,1],[4,5,7],[4,7,6],[0,1,5],[0,5,4],[2,6,7],[2,7,3],[0,4,6],[0,6,2],[1,3,7],[1,7,5]]);

export function boundaryMeasurements(vertices,faces){
 if(vertices.some(v=>v.length!==3||!v.every(Number.isFinite)))throw new RangeError('Finite three-dimensional vertices required');
 const origin=[0,1,2].map(d=>vertices.reduce((s,v)=>s+v[d],0)/vertices.length);
 let signedVolumeM3=0,surfaceAreaM2=0;const closureVectorM2=[0,0,0];
 for(const face of faces){
  const [a,b,c]=face.map(i=>vertices[i]);
  const normal=cross(subtract(b,a),subtract(c,a));
  surfaceAreaM2+=norm(normal)/2;
  for(let d=0;d<3;d++)closureVectorM2[d]+=normal[d]/2;
  signedVolumeM3+=dot(subtract(a,origin),normal)/6;
 }
 return {signedVolumeM3,surfaceAreaM2,closureVectorM2};
}
export function measureTetrahedron(reference,current){
 if(reference.length!==4||current.length!==4)throw new RangeError('Four vertices required');
 const F=multiply3(edges(current),inverse3(edges(reference))),J=determinant3(F);
 const referenceBoundary=boundaryMeasurements(reference,TETRAHEDRON_FACES),currentBoundary=boundaryMeasurements(current,TETRAHEDRON_FACES);
 const volumeRatio=currentBoundary.signedVolumeM3/referenceBoundary.signedVolumeM3;
 const C=Array.from({length:9},(_,i)=>{const r=Math.floor(i/3),c=i%3;return [0,1,2].reduce((s,k)=>s+F[3*k+r]*F[3*k+c],0);});
 const greenStrain=C.map((v,i)=>(v-(Math.floor(i/3)===i%3?1:0))/2);
 return {accepted:J>0&&currentBoundary.signedVolumeM3>0,reason:J>0?'Prescribed positive-orientation geometry':'Rejected nonpositive orientation; retain the prior displayed state',F,J,greenStrain,referenceBoundary,currentBoundary,volumeRatio,volumeMeasurementDifference:volumeRatio-J,reference,current};
}
export function deformationState(p=DEFORMATION_DEFAULTS){
 if(!Object.values(p).every(Number.isFinite)||p.sx<=0||p.sy<=0||p.sz<=0)throw new RangeError('Positive stretches and finite parameters required');
 const angle=p.angle*Math.PI/180,c=Math.cos(angle),s=Math.sin(angle),R=[c,-s,0,s,c,0,0,0,1],U=[p.sx,p.shear,0,0,p.sy,0,0,0,p.sz];
 const imposedF=multiply3(R,U),reference=[[0,0,0],[PROPERTY_DIMENSIONS[0],0,0],[0,PROPERTY_DIMENSIONS[1],0],[0,0,PROPERTY_DIMENSIONS[2]]];
 const translationM=[p.tx,p.ty,p.tz].map(v=>v/1000),current=reference.map(x=>transform(imposedF,x,translationM));
 return {...measureTetrahedron(reference,current),imposedF,translationM,analyticJ:p.sx*p.sy*p.sz};
}
export function isochoricState(p=ISOCHORIC_DEFAULTS){
 if(!['independent','isochoric'].includes(p.mode)||!Number.isFinite(p.axial)||!Number.isFinite(p.lateral)||p.axial<=0||p.lateral<=0)throw new RangeError('Positive prescribed stretches required');
 const b=p.mode==='isochoric'?1/Math.sqrt(p.axial):p.lateral;
 const reference=Array.from({length:8},(_,i)=>PROPERTY_DIMENSIONS.map((L,d)=>(i>>d&1)*L)),F=[p.axial,0,0,0,b,0,0,0,b],current=reference.map(x=>transform(F,x));
 const referenceBoundary=boundaryMeasurements(reference,BOX_FACES),currentBoundary=boundaryMeasurements(current,BOX_FACES);
 const lengthM=norm(subtract(current[1],current[0]));
 const crossSectionAreaM2=norm(cross(subtract(current[2],current[0]),subtract(current[4],current[0])));
 const areaLengthVolumeM3=crossSectionAreaM2*lengthM;
 const J=p.axial*b*b,volumeRatio=currentBoundary.signedVolumeM3/referenceBoundary.signedVolumeM3;
 return {accepted:J>0,F,J,lateralStretch:b,lengthM,crossSectionAreaM2,exteriorAreaM2:currentBoundary.surfaceAreaM2,areaLengthVolumeM3,referenceBoundary,currentBoundary,volumeRatio,volumeMeasurementDifference:volumeRatio-J,areaLengthMeasurementDifferenceM3:areaLengthVolumeM3-currentBoundary.signedVolumeM3,reference,current};
}

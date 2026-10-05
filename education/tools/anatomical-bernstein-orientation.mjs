/** Exact integer Bernstein signs for a P2 tetrahedron's Jacobian determinant.
 * Binary64 nodal positions are treated as exact dyadic numbers. This certifies
 * orientation of the stored interpolant, not equilibrium or contact. */
import {quadraticShape} from '../web/anatomical-element.mjs';
const corners=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],gradients=corners.map(L=>quadraticShape(L).gradient);
const view=new DataView(new ArrayBuffer(8));
function dyadic(x){
 if(!Number.isFinite(x))throw Error('Finite stored node required');view.setFloat64(0,x);const bits=view.getBigUint64(0),sign=bits>>63n?-1n:1n,exponent=Number((bits>>52n)&2047n),fraction=bits&((1n<<52n)-1n);
 return {n:sign*(exponent?fraction+(1n<<52n):fraction),e:exponent?exponent-1023-52:-1074};
}
const determinantColumns=(a,b,c)=>a[0]*(b[1]*c[2]-b[2]*c[1])-b[0]*(a[1]*c[2]-a[2]*c[1])+c[0]*(a[1]*b[2]-a[2]*b[1]);
export function exactJacobianBernstein(nodes){
 if(nodes.length!==10||nodes.some(n=>n.length!==3))throw Error('Ten P2 nodes required');
 const values=nodes.map(X=>X.map(dyadic)),e=Math.min(0,...values.flat().filter(v=>v.n!==0n).map(v=>v.e)),integers=values.map(X=>X.map(v=>v.n<<BigInt(v.e-e)));
 const matrices=gradients.map(g=>[0,1,2].map(k=>[0,1,2].map(d=>integers.reduce((s,X,i)=>{if(!Number.isInteger(g[i][k]))throw Error('Exact corner shape gradient required');return s+X[d]*BigInt(g[i][k]);},0n))));
 const sums=new Map();
 for(let i=0;i<4;i++)for(let j=0;j<4;j++)for(let k=0;k<4;k++){
  const alpha=[0,0,0,0];alpha[i]++;alpha[j]++;alpha[k]++;const key=alpha.join(','),r=sums.get(key)??{alpha,n:0n,count:0};r.n+=determinantColumns(matrices[i][0],matrices[j][1],matrices[k][2]);r.count++;sums.set(key,r);
 }
 // All multiplicities are 1, 3 or 6; common denominator is exactly 6*2^(-3e).
 const coefficients=[...sums.values()].map(r=>({multiIndex:r.alpha,numerator:r.n*BigInt(6/r.count)})),minimum=coefficients.reduce((a,b)=>a.numerator<b.numerator?a:b),maximum=coefficients.reduce((a,b)=>a.numerator>b.numerator?a:b);
 return {allStrictlyPositive:minimum.numerator>0n,minimumNumerator:minimum.numerator.toString(),maximumNumerator:maximum.numerator.toString(),minimumMultiIndex:minimum.multiIndex,denominatorFactor:6,denominatorPowerOfTwo:-3*e,coefficients:coefficients.map(c=>({multiIndex:c.multiIndex,numerator:c.numerator.toString()}))};
}
export function exactElementOrientation(reference,current){
 const rest=exactJacobianBernstein(reference),deformed=exactJacobianBernstein(current);
 return {referencePositive:rest.allStrictlyPositive,currentPositive:deformed.allStrictlyPositive,orientationCertified:rest.allStrictlyPositive&&deformed.allStrictlyPositive,reference:rest,current:deformed};
}

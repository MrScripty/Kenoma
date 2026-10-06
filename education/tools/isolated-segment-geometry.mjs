/** Exact geometry of an archived straight P2 nodal segment only.
 * Extends the existing determinant multilinearity, without changing its gate.
 * All binary64 inputs are interpreted as exact dyadic rationals. */
import {quadraticShape} from '../web/anatomical-element.mjs';
const corners=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],gradients=corners.map(L=>quadraticShape(L).gradient);
const view=new DataView(new ArrayBuffer(8));
export function dyadic(x){
 if(!Number.isFinite(x))throw Error('Finite stored geometry required');view.setFloat64(0,x);const bits=view.getBigUint64(0),sign=bits>>63n?-1n:1n,exponent=Number(bits>>52n&2047n),fraction=bits&((1n<<52n)-1n);
 return {n:sign*(exponent?fraction+(1n<<52n):fraction),e:exponent?exponent-1023-52:-1074};
}
const det=(a,b,c)=>a[0]*(b[1]*c[2]-b[2]*c[1])-b[0]*(a[1]*c[2]-a[2]*c[1])+c[0]*(a[1]*b[2]-a[2]*b[1]);
export function elementSegmentPolynomials(reference,start,end){
 for(const nodes of [reference,start,end])if(nodes.length!==10||nodes.some(v=>v.length!==3))throw Error('Ten P2 nodes required');
 const values=[reference,start,end].map(nodes=>nodes.map(v=>v.map(dyadic))),e=Math.min(0,...values.flat(2).filter(v=>v.n!==0n).map(v=>v.e));
 const integers=values.map(nodes=>nodes.map(v=>v.map(x=>x.n===0n?0n:x.n<<BigInt(x.e-e))));
 const matrices=integers.map(nodes=>gradients.map(G=>[0,1,2].map(k=>[0,1,2].map(d=>nodes.reduce((s,X,i)=>{if(!Number.isInteger(G[i][k]))throw Error('Integer corner gradient required');return s+X[d]*BigInt(G[i][k]);},0n)))));
 const [R,U,V]=matrices,D=V.map((matrix,r)=>matrix.map((column,c)=>column.map((v,d)=>v-U[r][c][d]))),sums=new Map();
 for(let i=0;i<4;i++)for(let j=0;j<4;j++)for(let k=0;k<4;k++){
  const multiIndex=[0,0,0,0];multiIndex[i]++;multiIndex[j]++;multiIndex[k]++;const key=multiIndex.join(','),row=sums.get(key)??{multiIndex,reference:0n,power:[0n,0n,0n,0n],count:0};
  const a=U[i][0],b=U[j][1],c=U[k][2],da=D[i][0],db=D[j][1],dc=D[k][2];
  const power=[det(a,b,c),det(da,b,c)+det(a,db,c)+det(a,b,dc),det(da,db,c)+det(da,b,dc)+det(a,db,dc),det(da,db,dc)];
  row.reference+=det(R[i][0],R[j][1],R[k][2]);for(let t=0;t<4;t++)row.power[t]+=power[t];row.count++;sums.set(key,row);
 }
 return {denominatorFactor:6,denominatorPowerOfTwo:-3*e,coefficients:[...sums.values()].map(row=>({multiIndex:row.multiIndex,referenceNumerator:row.reference*BigInt(6/row.count),currentPowerNumerators:row.power.map(v=>v*BigInt(6/row.count))}))};
}
export function evaluateNumerator(power,n,d){return power[0]*d**3n+power[1]*n*d**2n+power[2]*n**2n*d+power[3]*n**3n;}
/** Degree3 time-Bernstein coefficients on [0,n/d], with positive common
 * multiplier3*d^3. Spatial Bernstein coefficients are retained unchanged. */
export function prefixControlNumerators(power,n,d){
 const [a,b,c,f]=power,A=3n*d**3n*a,B=n*d**2n*b,C=n**2n*d*c,D=n**3n*f;
 return [A,A+B,A+2n*B+C,A+3n*B+3n*C+3n*D];
}
export function guardedPower(row,guard=1e-6){
 const g=dyadic(guard);if(!(g.n>0n&&g.e<=0))throw Error('Positive dyadic domain guard required');const denominator=1n<<BigInt(-g.e),power=row.currentPowerNumerators.map(v=>v*denominator);
 power[0]-=g.n*row.referenceNumerator;return {power,guardNumerator:g.n,guardDenominator:denominator};
}
export function certifyPrefix(elements,n,d){
 let minimum=null;
 for(const [element,polynomial] of elements.entries())for(const row of polynomial.coefficients){
  if(row.referenceNumerator<=0n)throw Error('Reference spatial coefficient not positive');
  const {power}=guardedPower(row),controls=prefixControlNumerators(power,n,d);
  for(let timeControl=0;timeControl<4;timeControl++){
   const value=controls[timeControl];if(value<=0n)return {certified:false,element,multiIndex:row.multiIndex,timeControl,numerator:value.toString()};
   if(!minimum||value<minimum.numerator)minimum={element,multiIndex:row.multiIndex,timeControl,numerator:value};
  }
 }
 return {certified:true,minimumControl:{...minimum,numerator:minimum.numerator.toString()},scope:'All space×time Bernstein controls for det(current)-binary64(1e-6)*det(reference) strictly positive over every tetrahedron and t∈[0,n/d].'};
}
export function locateCertifiedPrefix(elements,bits=40){
 const denominator=1n<<BigInt(bits);if(!certifyPrefix(elements,0n,denominator).certified)throw Error('Starting field cannot certify the unchanged domain guard');
 if(certifyPrefix(elements,denominator,denominator).certified)return {lowerNumerator:denominator,upperNumerator:denominator,denominator,lowerCertificate:certifyPrefix(elements,denominator,denominator),upperCertificate:null};
 let lower=0n,upper=denominator;
 while(upper-lower>1n){const middle=(lower+upper)/2n;if(certifyPrefix(elements,middle,denominator).certified)lower=middle;else upper=middle;}
 return {lowerNumerator:lower,upperNumerator:upper,denominator,lowerCertificate:certifyPrefix(elements,lower,denominator),upperCertificate:certifyPrefix(elements,upper,denominator)};
}

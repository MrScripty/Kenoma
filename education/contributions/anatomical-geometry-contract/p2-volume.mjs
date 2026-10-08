/** Algebraic signed P2 material volume. No sampled material quadrature.
 * Integrates the cubic parent determinant coefficient by coefficient.
 * A positive integral does not certify orientation or an unfolded body. */
const edges=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]];
const G=[[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]];
const corners=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]];
const derivative=L=>[...L.map((l,i)=>G[i].map(v=>(4*l-1)*v)),...edges.map(([i,j])=>G[i].map((v,d)=>4*(L[i]*G[j][d]+L[j]*v)))];
const jacobian=(X,L)=>[0,1,2].map(d=>[0,1,2].map(k=>{const g=derivative(L);return X.reduce((s,p,i)=>s+p[d]*g[i][k],0);}));
// Linear polynomials encoded [constant, xi, eta, zeta].
function product(a,b,c){
 const result=new Map(),powers=[[0,0,0],[1,0,0],[0,1,0],[0,0,1]];
 for(let i=0;i<4;i++)for(let j=0;j<4;j++)for(let k=0;k<4;k++){
  const key=powers[i].map((v,d)=>v+powers[j][d]+powers[k][d]).join(',');
  result.set(key,(result.get(key)||0)+a[i]*b[j]*c[k]);
 }
 return result;
}
export function determinantCoefficients(X) {
 if(X.length!==10||X.some(p=>p.length!==3||!p.every(Number.isFinite)))throw Error('Ten finite P2 positions required');
 // Translation cancels analytically; subtract first node to avoid atlas-origin cancellation.
 const local=X.map(p=>p.map((v,d)=>v-X[0][d]));
 const J=corners.map(L=>jacobian(local,L));
 const entry=(r,c)=>[J[0][r][c],...J.slice(1).map(j=>j[r][c]-J[0][r][c])];
 const result=new Map();
 for(const [cols,sign]of [[[0,1,2],1],[[1,2,0],1],[[2,0,1],1],[[0,2,1],-1],[[2,1,0],-1],[[1,0,2],-1]])
  for(const [key,value]of product(entry(0,cols[0]),entry(1,cols[1]),entry(2,cols[2])))result.set(key,(result.get(key)||0)+sign*value);
 return result;
}
const factorial=[1,1,2,6,24,120,720];
export function signedP2VolumeM3(X) {
 let volume=0;
 for(const [key,value]of determinantCoefficients(X)){
  const [i,j,k]=key.split(',').map(Number);
  volume+=value*factorial[i]*factorial[j]*factorial[k]/factorial[i+j+k+3];
 }
 if(!Number.isFinite(volume))throw Error('Nonfinite algebraic volume');
 return volume;
}

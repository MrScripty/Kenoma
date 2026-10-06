/** Ten-node quadratic isoparametric tetrahedra and positive quadrature. */
import {determinant,inverseTranspose,muscleMaterial} from './anatomical-material.mjs';
export const EDGE_PAIRS=Object.freeze([[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]);
const outerSum=(x,g)=>Array.from({length:9},(_,k)=>x.reduce((sum,X,i)=>sum+X[Math.floor(k/3)]*g[i][k%3],0));
export function quadraticShape(L){
 const G=[[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]],N=L.map(l=>l*(2*l-1)),gradient=L.map((l,i)=>G[i].map(v=>(4*l-1)*v));
 for(const [i,j] of EDGE_PAIRS){N.push(4*L[i]*L[j]);gradient.push(G[i].map((v,d)=>4*(L[i]*G[j][d]+L[j]*v)));}
 return {N,gradient};
}
const a=(5+3*Math.sqrt(5))/20,b=(5-Math.sqrt(5))/20;
const four=Array.from({length:4},(_,i)=>({L:Array.from({length:4},(_,j)=>i===j?a:b),weight:.25}));
const corners=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],mid=(i,j)=>corners[i].map((v,k)=>(v+corners[j][k])/2),vertices=[...corners,...EDGE_PAIRS.map(([i,j])=>mid(i,j))];
// Four corner subtetrahedra, then a consistent split of the central octahedron.
const subtets=[[0,4,5,6],[1,4,7,8],[2,5,7,9],[3,6,8,9],[4,5,6,9],[4,5,7,9],[4,7,8,9],[4,6,8,9]];
export const QUADRATURE=Object.freeze({four,subdivided32:subtets.flatMap(t=>four.map(point=>({L:[0,1,2,3].map(k=>point.L.reduce((sum,l,i)=>sum+l*vertices[t[i]][k],0)),weight:point.weight/8})))});
export function midpointNodes(corners){return [...corners.map(X=>X.slice()),...EDGE_PAIRS.map(([i,j])=>corners[i].map((v,d)=>(v+corners[j][d])/2))];}
export function prepareQuadraticElement(reference,{quadrature='four',fibre=[0,1,0]}={}){
 if(reference.length!==10||reference.some(X=>X.length!==3||!X.every(Number.isFinite))||!QUADRATURE[quadrature])throw new RangeError('Quadratic reference element');
 const points=QUADRATURE[quadrature].map(({L,weight})=>{
  const shape=quadraticShape(L),jacobian=outerSum(reference,shape.gradient),J=determinant(jacobian);if(!(J>1e-15))throw new RangeError('Invalid reference quadrature Jacobian');const invT=inverseTranspose(jacobian,J);
  const gradient=shape.gradient.map(g=>[0,1,2].map(i=>[0,1,2].reduce((sum,j)=>sum+invT[3*i+j]*g[j],0)));
  const direction=typeof fibre==='function'?fibre(L,shape.N):fibre;
  return {L,N:shape.N,gradient,referenceWeightM3:weight*J/6,fibre:direction.slice()};
 });
 return {points,referenceVolumeM3:points.reduce((sum,p)=>sum+p.referenceWeightM3,0),quadrature};
}
export function evaluateQuadraticElement(element,current,a,material){
 if(current.length!==10||current.some(X=>X.length!==3||!X.every(Number.isFinite)))throw new RangeError('Quadratic current element');
 const gradient=Array.from({length:10},()=>[0,0,0]),energy={matrix:0,volume:0,passiveFiber:0,activePotential:0},samples=[];
 for(const point of element.points){
  const F=outerSum(current,point.gradient),r=muscleMaterial(F,point.fibre,a,material),w=point.referenceWeightM3;
  for(const key of Object.keys(energy))energy[key]+=w*r.energy[key];
  for(let i=0;i<10;i++)for(let d=0;d<3;d++)gradient[i][d]+=w*[0,1,2].reduce((sum,k)=>sum+r.P[d*3+k]*point.gradient[i][k],0);
  samples.push({J:r.J,lambda:r.lambda,referenceWeightM3:w,P:r.P});
 }
 const passiveStoredJ=energy.matrix+energy.volume+energy.passiveFiber;
 return {energy,passiveStoredJ,solvePotentialJ:passiveStoredJ+energy.activePotential,gradient,samples,currentVolumeM3:samples.reduce((sum,s)=>sum+s.J*s.referenceWeightM3,0),minJ:Math.min(...samples.map(s=>s.J))};
}

/** Deterministic tensor and independent affine-tetra geometry, exact integer volumes. */
import assert from 'node:assert/strict';
import {GAUSS} from './fixed-field-integration-protocol.mjs';
import {shells} from './element247-shell-protocol.mjs';
import {recipe,regionPointCount} from './fine-window-protocol.mjs';
export function determinantInteger(v){const a=[1,2,3].map(i=>[1,2,3].map(j=>BigInt(v[j][i]-v[0][i])));return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]);}
export function faceTriangles(m){
 const vertices=[];for(let i=0;i<=m;i++)for(let j=0;j<=m-i;j++)vertices.push([i,j]);const ranks=new Map(vertices.map((v,i)=>[v.join(','),i]));const result=[];
 for(let i=0;i<m;i++)for(let j=0;j<m-i;j++)result.push([[i,j],[i+1,j],[i,j+1]]);
 for(let i=0;i<m-1;i++)for(let j=0;j<m-1-i;j++)result.push([[i+1,j],[i+1,j+1],[i,j+1]]);
 for(const triangle of result)triangle.sort((a,b)=>ranks.get(a.join(','))-ranks.get(b.join(',')));assert.equal(result.length,m*m);return result;
}
export function* regionTetrahedra(r,s){
 assert.deepEqual(r,recipe(r.element,r.id));assert.deepEqual(s,shells(r.depth).find(x=>x.id===s.id));assert.equal(r.kind,'graded-affine-tetra');const m=r.faceParts,D=2**r.depth*m*r.radialParts,corner=[0,0,0,0];corner[r.corner]=D;
 const vertex=(radial,[i,j])=>{const radius=radial*D;assert.ok(Number.isInteger(radius)&&Number.isInteger(radius/m));const v=[0,0,0,0];v[r.corner]=D-radius;v[r.faceOrder[0]]=radius/m*i;v[r.faceOrder[1]]=radius/m*j;v[r.faceOrder[2]]=radius/m*(m-i-j);return v;};
 let index=0;for(const triangle of faceTriangles(m)){
  const pieces=[];if(s.id==='core')pieces.push([corner,...triangle.map(v=>vertex(s.hi,v))]);
  else for(let radialPart=0;radialPart<r.radialParts;radialPart++){const lo=s.lo+(s.hi-s.lo)*radialPart/r.radialParts,hi=s.lo+(s.hi-s.lo)*(radialPart+1)/r.radialParts,A=triangle.map(v=>vertex(lo,v)),B=triangle.map(v=>vertex(hi,v));pieces.push([A[0],A[1],A[2],B[2]],[A[0],A[1],B[1],B[2]],[A[0],B[0],B[1],B[2]]);}
  for(const vertices of pieces){let det=determinantInteger(vertices);assert.notEqual(det,0n,'Degenerate reference subtetrahedron');if(det<0n){[vertices[2],vertices[3]]=[vertices[3],vertices[2]];det=-det;}yield {vertices,det,D,index:index++,region:s.id};}
 }
 assert.equal(index,regionPointCount(r,s)/125);
}
export function* regionRule(r,s){
 assert.deepEqual(r,recipe(r.element,r.id));assert.deepEqual(s,shells(r.depth).find(x=>x.id===s.id));const g=GAUSS[5];let count=0;
 if(r.kind==='tensor-shell'){
  for(let rp=0;rp<r.radialParts;rp++){const dr=(s.hi-s.lo)/r.radialParts,rlo=s.lo+rp*dr;for(let ap=0;ap<r.angularParts;ap++)for(let bp=0;bp<r.angularParts;bp++)for(let i=0;i<5;i++)for(let j=0;j<5;j++)for(let k=0;k<5;k++){
   const radial=rlo+dr*g.x[i],a=(ap+g.x[j])/r.angularParts,b=(bp+g.x[k])/r.angularParts,L=[0,0,0,0];L[r.corner]=1-radial;L[r.faceOrder[0]]=radial*a;L[r.faceOrder[1]]=radial*(1-a)*b;L[r.faceOrder[2]]=radial*(1-a)*(1-b);count++;yield {L,weight:6*dr*g.w[i]*g.w[j]*g.w[k]*(radial*radial*(1-a))/r.angularParts**2,r:radial,shell:s.id};
  }}
 }else for(const tet of regionTetrahedra(r,s)){
  const normalizedDet=Number(tet.det)/tet.D**3,V=tet.vertices.map(v=>v.map(x=>x/tet.D));
  for(let i=0;i<5;i++)for(let j=0;j<5;j++)for(let k=0;k<5;k++){const u=g.x[i],v=g.x[j],w=g.x[k],B=[1-u,u*(1-v),u*v*(1-w),u*v*w],L=[0,1,2,3].map(a=>B.reduce((sum,b,n)=>sum+b*V[n][a],0));count++;yield {L,weight:6*normalizedDet*g.w[i]*g.w[j]*g.w[k]*u*u*v,r:r.faceOrder.reduce((sum,a)=>sum+L[a],0),shell:s.id};}
 }
 assert.equal(count,regionPointCount(r,s));
}
export function packPoints(points){const bytes=Buffer.alloc(points.length*48);points.forEach((p,i)=>[...p.L,p.weight,p.r].forEach((x,j)=>bytes.writeDoubleLE(x,i*48+j*8)));return bytes;}
export function unpackPoints(bytes){assert.equal(bytes.length%48,0);const points=[];for(let i=0;i<bytes.length;i+=48)points.push({L:[0,1,2,3].map(j=>bytes.readDoubleLE(i+j*8)),weight:bytes.readDoubleLE(i+32),r:bytes.readDoubleLE(i+40)});return points;}
export function exactCoverage(r){
 assert.deepEqual(r,recipe(r.element,r.id));const D=2**r.depth*r.faceParts*r.radialParts,den=BigInt(D)**3n,faces=new Map(),regionVolumes=[];let determinantSum=0n,tetrahedra=0;
 for(const s of shells(r.depth)){let sum=0n;for(const tet of regionTetrahedra(r,s)){
  assert.equal(tet.D,D);assert.ok(tet.det>0n);sum+=tet.det;tetrahedra++;
  for(let omitted=0;omitted<4;omitted++){const face=tet.vertices.filter((_v,i)=>i!==omitted),keys=face.map(v=>v.join(',')),sorted=keys.slice().sort();let inversions=0;for(let i=0;i<3;i++)for(let j=i+1;j<3;j++)if(keys[i]>keys[j])inversions++;const sign=(omitted%2?-1:1)*(inversions%2?-1:1),key=sorted.join(';'),old=faces.get(key);if(old){assert.equal(old.count,1,'Nonmanifold face');assert.equal(old.sign,-sign,'Interior face orientation');old.count=2;}else faces.set(key,{count:1,sign,vertices:face});
  }
 }const hi=BigInt(s.hi*D),lo=BigInt(s.lo*D),expected=hi**3n-lo**3n;assert.equal(sum,expected,'Exact region reference volume');regionVolumes.push({shell:s.id,numerator:String(sum),denominator:String(den)});determinantSum+=sum;}
 assert.equal(determinantSum,den,'Exact complete tetrahedral volume');let boundaryFaces=0;for(const face of faces.values())if(face.count===1){boundaryFaces++;assert.ok([0,1,2,3].some(i=>face.vertices.every(v=>v[i]===0)),'Exposed interior face/gap');}
 return {corner:r.corner,rule:r.id,tetrahedra,boundaryFaces,interiorFaces:faces.size-boundaryFaces,exactVolumeNumerator:String(determinantSum),exactVolumeDenominator:String(den),regionVolumes,conformingPositiveOrientedMesh:true};
}

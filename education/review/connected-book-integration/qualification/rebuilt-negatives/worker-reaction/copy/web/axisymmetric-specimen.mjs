/** Connected Q2 axisymmetric passive frustum, SI, prescribed end displacement.
 * No mixed pressure, reduced rings, activation or postsolve volume correction.
 * Axis radial DOFs are zero; axial parity enforces z_R=0 on the axis.
 */
import {axisymmetricMaterial,PASSIVE_MATERIAL} from './axisymmetric-material.mjs';
export const SPECIMEN=Object.freeze({length:.05,radius:.005,ratio:1.5,...PASSIVE_MATERIAL});
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const maximum=a=>a.reduce((s,x)=>Math.max(s,Math.abs(x)),0);
export function gaussLegendre(order){
 if(!Number.isInteger(order)||order<2||order>12)throw new RangeError('Gauss order 2..12');
 const points=[];
 for(let i=0;i<order;i++){
  let x=Math.cos(Math.PI*(i+.75)/(order+.5)),dp=0;
  for(let k=0;k<30;k++){
   let p0=1,p1=x;
   for(let n=2;n<=order;n++){const p=((2*n-1)*x*p1-(n-1)*p0)/n;p0=p1;p1=p;}
   dp=order*(x*p1-p0)/(x*x-1);const step=p1/dp;x-=step;if(Math.abs(step)<2e-16)break;
  }
  // Reevaluate derivative at the final node.
  let p0=1,p1=x;for(let n=2;n<=order;n++){const p=((2*n-1)*x*p1-(n-1)*p0)/n;p0=p1;p1=p;}
  dp=order*(x*p1-p0)/(x*x-1);points.push({x,weight:2/((1-x*x)*dp*dp)});
 }
 return points.sort((a,b)=>a.x-b.x);
}
const oneShape=x=>({N:[x*(x-1)/2,1-x*x,x*(x+1)/2],D:[x-.5,-2*x,x+.5]});
export function q2Shape(xi,eta){
 const r=oneShape(xi),z=oneShape(eta),N=[],D=[];
 for(let j=0;j<3;j++)for(let i=0;i<3;i++){N.push(r.N[i]*z.N[j]);D.push([r.D[i]*z.N[j],r.N[i]*z.D[j]]);}
 return {N,D};
}
export function frustumVolume(radius,length,ratio){return Math.PI*length*radius*radius*(1+ratio+ratio*ratio)/3;}

function pointFor(mesh,cell,xi,eta){
 const s=q2Shape(xi,eta),X=cell.nodes.map(i=>mesh.nodes[i]);
 const R=dot(s.N,X.map(v=>v[0])),Z=dot(s.N,X.map(v=>v[1]));
 const rr=dot(s.D.map(v=>v[0]),X.map(v=>v[0])),rz=dot(s.D.map(v=>v[1]),X.map(v=>v[0]));
 const zr=dot(s.D.map(v=>v[0]),X.map(v=>v[1])),zz=dot(s.D.map(v=>v[1]),X.map(v=>v[1]));
 const det=rr*zz-rz*zr;if(!(det>0))throw new RangeError('Positive reference mapping');
 const G=s.D.map(v=>[(zz*v[0]-zr*v[1])/det,(-rz*v[0]+rr*v[1])/det]);
 const basis=[];
 for(let i=0;i<9;i++){
  const hoop=R>0?s.N[i]/R:0;
  basis.push([G[i][0],G[i][1],0,0,hoop],[0,0,G[i][0],G[i][1],0]);
 }
 const combined=new Map();
 for(let local=0;local<18;local++)for(const [id,weight] of mesh.rows[2*cell.nodes[Math.floor(local/2)]+local%2]){
  if(!combined.has(id))combined.set(id,Array(5).fill(0));const d=combined.get(id);
  for(let k=0;k<5;k++)d[k]+=weight*basis[local][k];
 }
 return {R,Z,N:s.N,G,det,basis,derivatives:[...combined].map(([id,D])=>({id,D})),cell};
}

export function prepareAxisymmetric({axialCells=8,radialCells=4,order=5,ratio=1.5}={}){
 if(!Number.isInteger(axialCells)||axialCells<2||axialCells>32||!Number.isInteger(radialCells)||radialCells<1||radialCells>16||![1,1.5].includes(ratio))throw new RangeError('Bounded connected mesh and uniform/fixed-taper geometry');
 const parameters={...SPECIMEN,ratio},{length,radius}=parameters,nr=2*radialCells+1,nz=2*axialCells+1,nodes=[];
 // The declared end plane is exact; repeated multiplication/division can overshoot it.
 for(let j=0;j<nz;j++){const Z=j===nz-1?length:j*length/(nz-1),a=radius*(1+(ratio-1)*Z/length);for(let i=0;i<nr;i++)nodes.push([a*i/(nr-1),Z]);}
 const rows=Array.from({length:2*nodes.length},()=>[]),fixedEnd=Array(2*nodes.length).fill(false),upperAxialDofs=[],freeMetadata=[];
 for(let j=0;j<nz;j++)for(let i=0;i<nr;i++)for(let component=0;component<2;component++){
  const node=j*nr+i,id=2*node+component;
  if(component===0&&i===0)continue;
  if(component===1&&(j===0||j===nz-1)){fixedEnd[id]=true;if(j===nz-1)upperAxialDofs.push(id);continue;}
  if(component===1&&i===0)continue;
  rows[id]=[[freeMetadata.length,1]];freeMetadata.push({node,component});
 }
 // Regular even axial field at R=0: Q2 edge derivative (-3u0+4u1-u2)=0.
 for(let j=1;j<nz-1;j++)rows[2*j*nr+1]=[[rows[2*(j*nr+1)+1][0][0],4/3],[rows[2*(j*nr+2)+1][0][0],-1/3]];
 const cells=[];
 for(let j=0;j<axialCells;j++)for(let i=0;i<radialCells;i++)cells.push({radial:i,axial:j,nodes:Array.from({length:9},(_,k)=>(2*j+Math.floor(k/3))*nr+2*i+k%3)});
 const mesh={parameters,axialCells,radialCells,order,nr,nz,nodes,rows,fixedEnd,upperAxialDofs,freeMetadata,freeCount:freeMetadata.length,cells};
 const rule=gaussLegendre(order);mesh.points=[];mesh.bandwidth=0;
 for(const cell of cells)for(const z of rule)for(const r of rule){
  const p=pointFor(mesh,cell,r.x,z.x);p.weightM3=2*Math.PI*p.R*p.det*r.weight*z.weight;mesh.points.push(p);
  const ids=p.derivatives.map(d=>d.id);mesh.bandwidth=Math.max(mesh.bandwidth,Math.max(...ids)-Math.min(...ids));
 }
 mesh.referenceVolumeM3=mesh.points.reduce((s,p)=>s+p.weightM3,0);
 mesh.exactReferenceVolumeM3=frustumVolume(radius,length,ratio);
 mesh.forceScaleN=parameters.mu*Math.PI*radius*radius;mesh.energyScaleJ=parameters.mu*mesh.exactReferenceVolumeM3;
 return mesh;
}

export function fullDisplacement(mesh,q,epsilon){
 if(q.length!==mesh.freeCount||!Array.from(q).every(Number.isFinite)||!Number.isFinite(epsilon)||Math.abs(epsilon)>.101)throw new RangeError('Connected displacement domain');
 const u=new Float64Array(2*mesh.nodes.length);
 for(let id=0;id<u.length;id++){
  for(const [k,w] of mesh.rows[id])u[id]+=w*q[k];
 }
 // Boundary membership comes from mesh topology, never coordinate equality.
 for(const id of mesh.upperAxialDofs)u[id]=epsilon*mesh.parameters.length;
 return u;
}
function deformation(point,u){
 const v=[1,0,0,1,1];
 for(let local=0;local<18;local++){const value=u[2*point.cell.nodes[Math.floor(local/2)]+local%2];for(let k=0;k<5;k++)v[k]+=point.basis[local][k]*value;}
 return v;
}
const bandIndex=(n,width,i,j)=>{if(i<j)[i,j]=[j,i];if(i-j>width)throw new Error('Tangent bandwidth exceeded');return i*(width+1)+i-j;};
export function bandMultiply(values,n,width,x){
 const out=new Float64Array(n);
 for(let i=0;i<n;i++)for(let j=Math.max(0,i-width);j<=i;j++){const a=values[i*(width+1)+i-j];out[i]+=a*x[j];if(j!==i)out[j]+=a*x[i];}
 return out;
}
export function assembleAxisymmetric(mesh,q,epsilon,{tangent=true,samples=false}={}){
 const u=fullDisplacement(mesh,q,epsilon),g=new Float64Array(mesh.freeCount),fullGradient=new Float64Array(u.length),H=tangent?new Float64Array(mesh.freeCount*(mesh.bandwidth+1)):null;
 let energyJ=0,volumeM3=0,matrixEnergyJ=0,volumeEnergyJ=0,minJ=Infinity,maxJ=-Infinity,weightedJDefect2=0;
 const observed=[];
 for(const p of mesh.points){
  const v=deformation(p,u),m=axisymmetricMaterial(v,mesh.parameters),w=p.weightM3;
  energyJ+=w*m.energyPa;matrixEnergyJ+=w*m.matrixEnergyPa;volumeEnergyJ+=w*m.volumeEnergyPa;volumeM3+=w*m.J;minJ=Math.min(minJ,m.J);maxJ=Math.max(maxJ,m.J);weightedJDefect2+=w*(m.J-1)**2;
  for(let local=0;local<18;local++)fullGradient[2*p.cell.nodes[Math.floor(local/2)]+local%2]+=w*dot(p.basis[local],m.gradient);
  for(const {id,D} of p.derivatives)g[id]+=w*dot(D,m.gradient);
  if(tangent){
   const hd=p.derivatives.map(({D})=>m.tangent.map(row=>dot(row,D)));
   for(let i=0;i<p.derivatives.length;i++)for(let j=0;j<=i;j++){
    const di=p.derivatives[i],dj=p.derivatives[j];H[bandIndex(mesh.freeCount,mesh.bandwidth,di.id,dj.id)]+=w*dot(di.D,hd[j]);
   }
  }
  if(samples)observed.push({R:p.R,Z:p.Z,J:m.J,referenceWeightM3:w,v,cauchy:m.cauchy});
 }
 let leftReactionN=0,rightReactionN=0;
 for(let i=0;i<mesh.nr;i++){leftReactionN+=fullGradient[2*i+1];rightReactionN+=fullGradient[2*((mesh.nz-1)*mesh.nr+i)+1];}
 return {u,g,H,energyJ,matrixEnergyJ,volumeEnergyJ,volumeM3,volumeRatio:volumeM3/mesh.exactReferenceVolumeM3,minJ,maxJ,weightedRmsJDefect:Math.sqrt(weightedJDefect2/mesh.exactReferenceVolumeM3),fullGradient,leftReactionN,rightReactionN,endBalanceN:leftReactionN+rightReactionN,maxFreeResidualN:maximum(g),scaledMaxFreeResidual:maximum(g)/mesh.forceScaleN,samples:observed};
}

/** Jacobi-scaled band Cholesky of the ORIGINAL assembled tangent.
 * Pivot spread is a diagnostic, not a condition number or stability theorem.
 */
export function solveBandSPD(H,g,n,width){
 const size=width+1,L=new Float64Array(H.length),scale=Float64Array.from({length:n},(_,i)=>Math.sqrt(H[i*size]));
 if(Array.from(scale).some(x=>!(x>0&&Number.isFinite(x))))throw new Error('Original tangent has nonpositive diagonal');
 let minPivot=Infinity,maxPivot=0;
 for(let i=0;i<n;i++)for(let j=Math.max(0,i-width);j<=i;j++){
  let value=H[i*size+i-j]/(scale[i]*scale[j]);
  for(let k=Math.max(0,i-width,j-width);k<j;k++)value-=L[i*size+i-k]*L[j*size+j-k];
  if(i===j){if(!(value>1e-13&&Number.isFinite(value)))throw new Error('Original free tangent failed positive scaled Cholesky pivot');L[i*size]=Math.sqrt(value);minPivot=Math.min(minPivot,value);maxPivot=Math.max(maxPivot,value);}
  else L[i*size+i-j]=value/L[j*size];
 }
 const y=new Float64Array(n),x=new Float64Array(n);
 for(let i=0;i<n;i++){let value=-g[i]/scale[i];for(let j=Math.max(0,i-width);j<i;j++)value-=L[i*size+i-j]*y[j];y[i]=value/L[i*size];}
 for(let i=n-1;i>=0;i--){let value=y[i];for(let j=i+1;j<=Math.min(n-1,i+width);j++)value-=L[j*size+j-i]*x[j];x[i]=value/L[i*size];}
 const step=x.map((v,i)=>v/scale[i]),residual=bandMultiply(H,n,width,step).map((v,i)=>v+g[i]);
 return {step,minScaledPivot:minPivot,maxScaledPivot:maxPivot,scaledPivotSpread:maxPivot/minPivot,linearResidualN:maximum(residual),linearRelativeResidual:maximum(residual)/Math.max(maximum(g),Number.MIN_VALUE)};
}

export function solveAxisymmetric(mesh,epsilon,{maxIterations=25,tolerance=1e-8,initial=null}={}){
 if(!Number.isInteger(maxIterations)||maxIterations<0||maxIterations>40||!Number.isFinite(tolerance)||tolerance<1e-12||tolerance>1e-3)throw new RangeError('Explicit bounded solver options');
 let q=initial?Float64Array.from(initial):Float64Array.from(mesh.freeMetadata,({node,component})=>component===1?epsilon*mesh.nodes[node][1]:0);
 const history=[];let evaluation=assembleAxisymmetric(mesh,q,epsilon),failure=null,iterations=0;
 for(;iterations<maxIterations&&evaluation.scaledMaxFreeResidual>tolerance;iterations++){
  let linear;
  try{linear=solveBandSPD(evaluation.H,evaluation.g,mesh.freeCount,mesh.bandwidth);}catch(error){failure=String(error.message);break;}
  const slope=dot(evaluation.g,linear.step);if(!(slope<0)){failure='Original tangent did not give a descent step';break;}
  let accepted=false,alpha=1;
  const energyRoundoffAllowanceJ=64*Number.EPSILON*mesh.energyScaleJ;
  for(let attempt=0;attempt<30;attempt++,alpha*=.5){
   const trial=q.map((v,i)=>v+alpha*linear.step[i]);let next;
   try{next=assembleAxisymmetric(mesh,trial,epsilon,{tangent:false});}catch{continue;}
   if(next.energyJ<=evaluation.energyJ+1e-4*alpha*slope+energyRoundoffAllowanceJ){
    history.push({iteration:iterations,energyJ:evaluation.energyJ,maxFreeResidualN:evaluation.maxFreeResidualN,scaledMaxFreeResidual:evaluation.scaledMaxFreeResidual,alpha,energyRoundoffAllowanceJ,...Object.fromEntries(Object.entries(linear).filter(([k])=>k!=='step'))});
    q=trial;evaluation=assembleAxisymmetric(mesh,q,epsilon);accepted=true;break;
   }
  }
  if(!accepted){failure='Admissible original-energy line search exhausted';break;}
 }
 const converged=evaluation.scaledMaxFreeResidual<=tolerance;
 return {q:Array.from(q),epsilon,converged,iterations,maxIterations,tolerance,failure,history,diagnostics:{energyJ:evaluation.energyJ,matrixEnergyJ:evaluation.matrixEnergyJ,volumeEnergyJ:evaluation.volumeEnergyJ,volumeM3:evaluation.volumeM3,volumeRatio:evaluation.volumeRatio,minQuadratureJ:evaluation.minJ,maxQuadratureJ:evaluation.maxJ,weightedRmsJDefect:evaluation.weightedRmsJDefect,maxFreeResidualN:evaluation.maxFreeResidualN,scaledMaxFreeResidual:evaluation.scaledMaxFreeResidual,leftReactionN:evaluation.leftReactionN,rightReactionN:evaluation.rightReactionN,endBalanceN:evaluation.endBalanceN,forceScaleN:mesh.forceScaleN,energyScaleJ:mesh.energyScaleJ,freeDofs:mesh.freeCount,bandwidth:mesh.bandwidth,quadratureOrder:mesh.order},scope:'Connected passive finite-compliance equilibrium within the declared axisymmetric Q2 displacement space; no exact incompressibility, anatomy or unrestricted buckling/stability guarantee'};
}

/** Quasistatic numerical load continuation, not a material history model.
 * Each stage solves the same full field. No transfer between different meshes.
 * Failure retains the actual reached pose and explicitly records the requested one.
 */
export function solveAxisymmetricPath(mesh,epsilon,{increment=.02,maxIterations=25,tolerance=1e-8}={}){
 if(!Number.isFinite(increment)||increment<=0||increment>.02)throw new RangeError('Continuation increment in (0,.02]');
 const count=Math.max(1,Math.ceil(Math.abs(epsilon)/increment)),stages=[];
 let state=solveAxisymmetric(mesh,0,{maxIterations,tolerance}),previous=0;
 for(let step=1;step<=count;step++){
  const next=epsilon*step/count,initial=state.q.map((value,i)=>value+(mesh.freeMetadata[i].component===1?(next-previous)*mesh.nodes[mesh.freeMetadata[i].node][1]:0));
  state=solveAxisymmetric(mesh,next,{maxIterations,tolerance,initial});
  stages.push({epsilon:next,converged:state.converged,iterations:state.iterations,failure:state.failure,scaledMaxFreeResidual:state.diagnostics.scaledMaxFreeResidual,history:state.history});
  previous=next;if(!state.converged)break;
 }
 return {...state,requestedEpsilon:epsilon,reachedRequestedPose:state.epsilon===epsilon,continuation:{increment,stages},converged:state.converged&&state.epsilon===epsilon};
}

function pointWithDisplacement(mesh,u,R,Z){
 const {length,radius,ratio}=mesh.parameters,a=radius*(1+(ratio-1)*Z/length);
 if(![R,Z].every(Number.isFinite)||Z<0||Z>length||R<0||R>a*(1+1e-12))throw new RangeError('Material point inside reference frustum');
 const iz=Math.min(mesh.axialCells-1,Math.floor(Z/length*mesh.axialCells)),ir=Math.min(mesh.radialCells-1,Math.floor(R/a*mesh.radialCells));
 const cell=mesh.cells[iz*mesh.radialCells+ir],eta=2*(Z/length*mesh.axialCells-iz)-1,xi=2*(R/a*mesh.radialCells-ir)-1,p=pointFor(mesh,cell,xi,eta),v=deformation(p,u);
 if(R===0){v[4]=v[0];} // regular axis r/R -> r_R; no volume assignment.
 const m=axisymmetricMaterial(v,mesh.parameters),r=R+dot(p.N,cell.nodes.map(n=>u[2*n])),z=Z+dot(p.N,cell.nodes.map(n=>u[2*n+1]));
 return {R,Z,r,z,v,...m,axialLineStretch:Math.hypot(v[1],v[3]),radialLineStretch:Math.hypot(v[0],v[2]),hoopStretch:v[4]};
}
export function materialPoint(mesh,state,R,Z){return pointWithDisplacement(mesh,fullDisplacement(mesh,state.q,state.epsilon),R,Z);}
export function createMaterialSampler(mesh,state){const u=fullDisplacement(mesh,state.q,state.epsilon);return (R,Z)=>pointWithDisplacement(mesh,u,R,Z);}

export function cutForce(mesh,state,Z,order=9){
 const {length,radius,ratio}=mesh.parameters,a=radius*(1+(ratio-1)*Z/length),rule=gaussLegendre(order);let N=0;
 for(let cell=0;cell<mesh.radialCells;cell++)for(const p of rule){const R=a*(cell+(p.x+1)/2)/mesh.radialCells,m=materialPoint(mesh,state,R,Z);N+=2*Math.PI*R*m.gradient[3]*p.weight*a/(2*mesh.radialCells);}
 return N;
}
export function sideTraction(mesh,state,Z){
 const {length,radius,ratio}=mesh.parameters,a=radius*(1+(ratio-1)*Z/length),slope=radius*(ratio-1)/length,m=materialPoint(mesh,state,a,Z),normal=[1,-slope].map(x=>x/Math.hypot(1,slope));
 return {Z,normal,nominalTractionPa:[m.gradient[0]*normal[0]+m.gradient[1]*normal[1],m.gradient[2]*normal[0]+m.gradient[3]*normal[1]],J:m.J};
}

/** One connected watertight boundary, sampled from the SOLVED Q2 map.
 * Finite azimuth tessellation error is measured, never volume-corrected.
 */
export function revolvedBoundary(mesh,state,{azimuth=128,axialSubdivisions=4}={}){
 if(!Number.isInteger(azimuth)||azimuth<8||azimuth>512||!Number.isInteger(axialSubdivisions)||axialSubdivisions<1||axialSubdivisions>16)throw new RangeError('Declared rendering tessellation');
 const rings=mesh.axialCells*axialSubdivisions+1,vertices=[],indices=[],reference=[];
 for(let j=0;j<rings;j++){
  const Z=j===rings-1?mesh.parameters.length:mesh.parameters.length*j/(rings-1),R=mesh.parameters.radius*(1+(mesh.parameters.ratio-1)*Z/mesh.parameters.length),m=materialPoint(mesh,state,R,Z);
  for(let i=0;i<azimuth;i++){const angle=2*Math.PI*i/azimuth;vertices.push([m.r*Math.cos(angle),m.r*Math.sin(angle),m.z]);reference.push([R*Math.cos(angle),R*Math.sin(angle),Z]);}
 }
 for(let j=0;j<rings-1;j++)for(let i=0;i<azimuth;i++){
  const k=(i+1)%azimuth,a=j*azimuth+i,b=j*azimuth+k,c=(j+1)*azimuth+i,d=(j+1)*azimuth+k;indices.push([a,b,c],[b,d,c]);
 }
 for(const [side,j] of [[-1,0],[1,rings-1]]){
  const center=vertices.length,Z=side<0?0:mesh.parameters.length,m=materialPoint(mesh,state,0,Z);vertices.push([0,0,m.z]);reference.push([0,0,Z]);
  for(let i=0;i<azimuth;i++){const a=j*azimuth+i,b=j*azimuth+(i+1)%azimuth;indices.push(side<0?[center,b,a]:[center,a,b]);}
 }
 return {vertices,referenceVertices:reference,indices,azimuth,axialSubdivisions,rings};
}
export function signedBoundaryVolume(vertices,indices){
 let volume=0;
 for(const [i,j,k] of indices){const a=vertices[i],b=vertices[j],c=vertices[k];volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;}
 return volume;
}

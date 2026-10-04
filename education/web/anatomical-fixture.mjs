/** Small actual quadratic-tet block fixture, distinct from anatomical remesh. */
import {EDGE_PAIRS,prepareQuadraticElement,evaluateQuadraticElement} from './anatomical-element.mjs';
import {MUSCLE_FIXTURE} from './anatomical-material.mjs';
import {minimize} from './anatomical-solver.mjs';
export function blockFixture({quadrature='four',refinement=1,width=.04,depth=.03,length=.12}={}){
 const nodes=[],index=(i,j,k)=>i+(refinement+1)*(j+(refinement+1)*k);for(let k=0;k<=refinement;k++)for(let j=0;j<=refinement;j++)for(let i=0;i<=refinement;i++)nodes.push([width*i/refinement,depth*j/refinement,length*k/refinement]);
 const tets=[];for(let k=0;k<refinement;k++)for(let j=0;j<refinement;j++)for(let i=0;i<refinement;i++){const a=index(i,j,k),b=index(i+1,j,k),c=index(i,j+1,k),d=index(i+1,j+1,k),e=index(i,j,k+1),f=index(i+1,j,k+1),g=index(i,j+1,k+1),h=index(i+1,j+1,k+1);tets.push([a,b,d,h],[a,d,c,h],[a,c,g,h],[a,g,e,h],[a,e,f,h],[a,f,b,h]);}
 const edges=new Map(),connectivity=tets.map(t=>[...t,...EDGE_PAIRS.map(([i,j])=>{const key=[t[i],t[j]].sort((a,b)=>a-b).join(',');if(!edges.has(key)){edges.set(key,nodes.length);nodes.push(nodes[t[i]].map((v,d)=>(v+nodes[t[j]][d])/2));}return edges.get(key);})]);
 const elements=connectivity.map(t=>prepareQuadraticElement(t.map(i=>nodes[i]),{quadrature,fibre:[0,0,1]}));
 return {nodes,connectivity,elements,length,area:width*depth,volume:width*depth*length};
}
export function blockEnergy(fixture,positions,activation,material=MUSCLE_FIXTURE){
 const gradient=positions.map(()=>[0,0,0]);let energy=0,passiveStoredJ=0,currentVolumeM3=0,minJ=Infinity,stretch=0;
 for(let k=0;k<fixture.elements.length;k++){const ids=fixture.connectivity[k],r=evaluateQuadraticElement(fixture.elements[k],ids.map(i=>positions[i]),activation,material);energy+=r.solvePotentialJ;passiveStoredJ+=r.passiveStoredJ;currentVolumeM3+=r.currentVolumeM3;minJ=Math.min(minJ,r.minJ);for(const sample of r.samples)stretch+=sample.lambda*sample.referenceWeightM3;for(let i=0;i<10;i++)for(let d=0;d<3;d++)gradient[ids[i]][d]+=r.gradient[i][d];}
 return {energy,gradient,passiveStoredJ,currentVolumeM3,minJ,meanFibreStretch:stretch/fixture.volume};
}
export function solveBlock(fixture,{activation=.05,loadN=0,fixedEnd=false,material=MUSCLE_FIXTURE,start,solver={}}={}){
 const {nodes,length}=fixture,bottom=nodes.map((X,i)=>X[2]<1e-10?i:-1).filter(i=>i>=0),top=nodes.map((X,i)=>X[2]>length-1e-10?i:-1).filter(i=>i>=0),held=new Set([...bottom,...(fixedEnd?top:[])]),free=nodes.flatMap((_,i)=>held.has(i)?[]:[0,1,2].map(d=>[i,d]));
 const unit=blockEnergy(fixture,nodes,1,{...material,sigma0:1}),weights=nodes.map((_,i)=>top.includes(i)?unit.gradient[i][2]/fixture.area:0),scale=length;
 const positionsFrom=x=>nodes.map((X,i)=>X.slice());
 const objective=x=>{const positions=positionsFrom(x);free.forEach(([i,d],j)=>positions[i][d]+=scale*x[j]);const r=blockEnergy(fixture,positions,activation,material);r.energy-=loadN*positions.reduce((s,X,i)=>s+weights[i]*(X[2]-nodes[i][2]),0);for(const i of top)r.gradient[i][2]-=loadN*weights[i];return {...r,positions,maximumFreeNodalForceN:Math.max(...r.gradient.filter((_,i)=>!held.has(i)).map(v=>Math.hypot(...v))),maximumFreeForceComponentN:Math.max(...free.map(([i,d])=>Math.abs(r.gradient[i][d]))),gradient:Float64Array.from(free,([i,d])=>scale*r.gradient[i][d])};};
 const initial=start?Float64Array.from(free,([i,d])=>(start[i][d]-nodes[i][d])/scale):new Float64Array(free.length),r=minimize(objective,initial,{initialInverseScale:1/(material.bulk*fixture.volume),maxIterations:1200,tolerance:1e-6,...solver}),raw=blockEnergy(fixture,r.positions,activation,material),reactionN=top.reduce((s,i)=>s+raw.gradient[i][2],0);
 return {...r,topMeanLengthM:r.positions.reduce((s,X,i)=>s+weights[i]*X[2],0),fixedEndReactionN:reactionN,loadN,activation,weights};
}

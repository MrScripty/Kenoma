/** Frozen-state diagnostic helpers only. Energy gradients are N; positions m.
 * No optimizer or constitutive/boundary change. Euclidean nodal decomposition
 * is an explicitly chosen metric, not a solve/error or inf-sup certificate. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {muscleMaterial,inverseTranspose,tendonSegment} from '../web/anatomical-material.mjs';

export const hashBytes=bytes=>createHash('sha256').update(bytes).digest('hex');
export function validateFrozenInputs(root,manifest){
 if(manifest.stationarity_tolerance_N!==1e-4||manifest.activation!==1||JSON.stringify(manifest.quadrature_points_per_element)!=='[32,256,2048]')throw Error('Frozen diagnostic contract changed');
 for(const [path,expected] of Object.entries(manifest.inputs))if(hashBytes(fs.readFileSync(root+path))!==expected)throw Error('Frozen input changed: '+path);
}
export const maxAbs=x=>x.reduce((m,v)=>Math.max(m,Math.abs(v)),0);
export const norm2=x=>Math.sqrt(x.reduce((s,v)=>s+v*v,0));
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
export function decomposeVector(g,columns){
 const Q=[];
 for(const column of columns){
  if(column.length!==g.length)throw Error('Nodal decomposition dimensions');
  const q=Float64Array.from(column),initial=norm2(q);
  for(let pass=0;pass<2;pass++)for(const b of Q){const d=dot(q,b);for(let k=0;k<q.length;k++)q[k]-=d*b[k];}
  const length=norm2(q);if(length>1e-11*Math.max(1,initial))Q.push(q.map(v=>v/length));
 }
 const retained=new Float64Array(g.length);
 for(const q of Q){const d=dot(g,q);for(let k=0;k<g.length;k++)retained[k]+=d*q[k];}
 const omitted=Float64Array.from(g,(v,k)=>v-retained[k]),totalNorm=norm2(g),retainedNorm=norm2(retained),omittedNorm=norm2(omitted);
 const orthogonality=maxAbs(Q.map(q=>dot(q,omitted))),parseval=Math.abs(totalNorm**2-retainedNorm**2-omittedNorm**2);
 if(orthogonality>1e-9*Math.max(1,totalNorm)||parseval>1e-10*Math.max(1,totalNorm**2))throw Error('Nodal orthogonal decomposition control');
 return {rank:Q.length,totalL2N:totalNorm,retainedL2N:retainedNorm,omittedL2N:omittedNorm,omittedSquaredNormFraction:totalNorm?omittedNorm**2/totalNorm**2:0,maximumRetainedComponentN:maxAbs(retained),maximumOmittedComponentN:maxAbs(omitted),maximumOmittedDotUnitModeN:orthogonality,parsevalDifferenceN2:parseval,retained:Array.from(retained),omitted:Array.from(omitted)};
}
export function projectLegacy(body,nodal){
 const result=new Float64Array(63);
 for(const [n,modes] of body.nodeModes.entries())for(const m of modes)for(let d=0;d<3;d++)result[m.base+d]+=m.value*nodal[n][d];
 return result;
}
export function freeResolution(body,nodal){
 const source=body.source,held=new Set([...source.distal_nodes,...source.proximal_nodes]);
 const free=source.nodes_m.map((_,n)=>n).filter(n=>!held.has(n)),columns=Array.from({length:45},()=>new Float64Array(3*free.length));
 for(const [i,node] of free.entries())for(const m of body.nodeModes[node])if(m.base>=9&&m.base<54)for(let d=0;d<3;d++)columns[m.base+d-9][3*i+d]+=m.value;
 const vector=free.flatMap(n=>nodal[n]),decomposition=decomposeVector(vector,columns),maximum=maxAbs(vector),index=vector.findIndex(v=>Math.abs(v)===maximum);
 if(decomposition.rank!==45)throw Error('Frozen free-mode rank changed');
 return {freeNodes:free,freeComponents:vector.length,heldNodes:held.size,largest:{node:free[Math.floor(index/3)],axis:index%3,gradientN:vector[index]},maximumFreeNodalComponentN:maximum,passesUnchangedFullNodalGate:maximum<=1e-4,...decomposition};
}
export function nodalSheets(source,sheets,positions){
 const gradient=source.nodes_m.map(()=>[0,0,0]);let energyJ=0;
 const weights=p=>Array.from({length:16},(_,k)=>({node:16*p.sourceRing+k,value:(1-.7)/16+(16*p.sourceRing+k===p.sourcePerimeterNode?.7:0)}));
 const point=p=>p.referenceM.map((v,d)=>v+weights(p).reduce((s,m)=>s+m.value*(positions[m.node][d]-source.nodes_m[m.node][d]),0));
 for(const [matrix,pairs] of [[false,sheets.branches],[true,sheets.matrix]])for(const p of pairs){
  const A=point(p.a),B=point(p.b),delta=A.map((v,d)=>v-B[d]),length=Math.hypot(...delta);
  if(!(length>1e-8))throw Error('Frozen sheet collapse');
  const r=matrix?{forceN:p.stiffnessNPerM*(length-p.L0M),storedEnergyJ:.5*p.stiffnessNPerM*(length-p.L0M)**2}:tendonSegment(length,p.L0M,p.A0M2);
  energyJ+=r.storedEnergyJ;
  for(const [endpoint,sign] of [[p.a,1],[p.b,-1]])for(const m of weights(endpoint))for(let d=0;d<3;d++)gradient[m.node][d]+=sign*m.value*r.forceN*delta[d]/length;
 }
 return {energyJ,gradientN:gradient};
}
export function constitutiveComponents(F,fibre,activation,material){
 const result=muscleMaterial(F,fibre,activation,material),invT=inverseTranspose(F,result.J);
 const bulk=invT.map(v=>material.bulk*Math.log(result.J)*v);
 const passiveScale=material.kf/material.b*Math.expm1(material.b*Math.max(result.lambda-1,0));
 const passive=F.map((_,i)=>passiveScale*result.direction[Math.floor(i/3)]*fibre[i%3]);
 const active=result.Pactive;
 const I1=F.reduce((s,v)=>s+v*v,0);
 const matrix=F.map((v,i)=>material.mu*result.J**(-2/3)*(v-I1/3*invT[i]));
 const sum=matrix.map((v,i)=>v+bulk[i]+passive[i]+active[i]);
 if(maxAbs(sum.map((v,i)=>v-result.P[i]))>1e-9*Math.max(1,maxAbs(result.P)))throw Error('Constitutive component sum');
 return {result,stressesPa:{matrix,bulk,passiveFibre:passive,active}};
}
export function componentNodalGradients(prepared,positions,activation,material){
 const components=Object.fromEntries(['matrix','bulk','passiveFibre','active'].map(key=>[key,prepared.source.nodes_m.map(()=>[0,0,0])]));
 for(const e of prepared.elements){
  const X=e.nodes.map(i=>positions[i]);
  for(const p of e.points){
   const F=Array.from({length:9},(_,k)=>X.reduce((s,v,i)=>s+v[Math.floor(k/3)]*p.gradient[i][k%3],0));
   const {stressesPa}=constitutiveComponents(F,p.fibre,activation,material);
   for(const [key,P] of Object.entries(stressesPa))for(let i=0;i<10;i++)for(let d=0;d<3;d++)for(let k=0;k<3;k++)components[key][e.nodes[i]][d]+=p.weightM3*P[3*d+k]*p.gradient[i][k];
  }
 }
 return components;
}

/** Authored intramuscular biceps aponeurosis strips, mechanically embedded in
 * the same restricted P2 field. Geometry is atlas-derived; no internal sheet
 * segmentation/pennation measurement is claimed. Blemker 2005 motivates the
 * overlapping proximal/distal architecture, not these dimensions or laws.
 */
import {modalSample} from './anatomical-modal.mjs';import {tendonSegment} from './anatomical-material.mjs';
const sub=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),norm=a=>Math.hypot(...a);
export function prepareIntramuscularAponeuroses(body){
 const m=body.source;if(!['FJ1512','FJ1478'].includes(m.element_id))return {strips:[],branches:[],matrix:[],limits:'No internal sheet geometry authored for this head.'};const zero=new Float64Array(63),strips=[],branches=[],matrix=[];
 function point(r,j){const ids=Array.from({length:16},(_,k)=>16*r+k),weights=ids.map((_,k)=>(1-.7)/16+(k===j?.7:0)),sample=modalSample(body,ids,weights,zero);return {referenceM:sample.position,modes:sample.modes,sourceRing:r,sourcePerimeterNode:16*r+j,insetFraction:.7};}
 for(const [label,rings,posterior] of [['proximal',[2,3,4,5,6],true],['distal',[0,1,2,3,4],false]]){const points=rings.map(r=>{let j=0;for(let k=1;k<16;k++)if(posterior?m.nodes_m[16*r+k][1]>m.nodes_m[16*r+j][1]:m.nodes_m[16*r+k][1]<m.nodes_m[16*r+j][1])j=k;return [(j+15)%16,j,(j+1)%16].map(k=>point(r,k));}),thicknessM=.001,muPa=1000;
  for(let r=0;r<points.length-1;r++){const width=.5*(norm(sub(points[r][0].referenceM,points[r][2].referenceM))+norm(sub(points[r+1][0].referenceM,points[r+1][2].referenceM)));for(let k=0;k<3;k++){const a=points[r][k],b=points[r+1][k],L0=norm(sub(a.referenceM,b.referenceM));branches.push({a,b,L0M:L0,A0M2:width*thicknessM/3,group:label+' internal aponeurosis axial'});}}
  for(let r=0;r<points.length;r++)for(const [i,j] of [[0,1],[1,2]]){const a=points[r][i],b=points[r][j],L0=norm(sub(a.referenceM,b.referenceM)),longitudinalSpan=norm(sub(points[Math.min(r+1,points.length-1)][i].referenceM,points[Math.max(0,r-1)][i].referenceM))*.5;matrix.push({a,b,L0M:L0,stiffnessNPerM:muPa*thicknessM*longitudinalSpan/L0,group:label+' internal aponeurosis transverse matrix'});}
  strips.push({label,sourceRings:rings,points,thicknessM,muPa,positionRule:'70% of the perimeter-node offset from each ring mean; posterior proximal strip and anterior distal strip, each over five of seven planes.',limits:'An authored embedded strip, not a measured internal aponeurosis, volume mesh or pennation map.'});
 }return {strips,branches,matrix,source:'https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf',limits:'Overlapping proximal/posterior and distal/anterior authored strips. Tension-only axial branches plus weak transverse edge matrix; no full solid sheet.'};
}
export function evaluateIntramuscularAponeuroses(body,sheets,x,{hessian=true}={}){
 const n=63,gradient=new Float64Array(n),H=hessian?new Float64Array(n*n):null;let axialEnergyJ=0,matrixEnergyJ=0;
 const position=p=>p.referenceM.map((v,d)=>v+p.modes.reduce((s,m)=>s+m.value*x[m.base+d],0));
 function pair(pair,matrix){const A=position(pair.a),B=position(pair.b),d=sub(A,B),length=norm(d);if(!(length>1e-8))throw new RangeError('Internal sheet branch collapsed');const u=d.map(v=>v/length),r=matrix?{forceN:pair.stiffnessNPerM*(length-pair.L0M),stiffnessNPerM:pair.stiffnessNPerM,storedEnergyJ:.5*pair.stiffnessNPerM*(length-pair.L0M)**2}:tendonSegment(length,pair.L0M,pair.A0M2),force=u.map(v=>v*r.forceN),C=Array.from({length:9},(_,i)=>r.stiffnessNPerM*u[Math.floor(i/3)]*u[i%3]+r.forceN/length*((Math.floor(i/3)===i%3?1:0)-u[Math.floor(i/3)]*u[i%3])),columns=[...pair.a.modes,...pair.b.modes.map(m=>({...m,value:-m.value}))];for(const a of columns)for(let i=0;i<3;i++){gradient[a.base+i]+=a.value*force[i];if(H)for(const b of columns)for(let j=0;j<3;j++)H[(a.base+i)*n+b.base+j]+=a.value*b.value*C[3*i+j];}return r.storedEnergyJ;}
 for(const p of sheets.branches)axialEnergyJ+=pair(p,false);for(const p of sheets.matrix)matrixEnergyJ+=pair(p,true);return {energy:axialEnergyJ+matrixEnergyJ,axialEnergyJ,matrixEnergyJ,gradient,hessian:H};
}

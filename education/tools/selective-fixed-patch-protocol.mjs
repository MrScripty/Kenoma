/** Closed selective protocol. Geometry/vector arithmetic; no material evaluator. */
import assert from 'node:assert/strict';
import {PATCH,GAUSS} from './fixed-field-integration-protocol.mjs';
import {shells,assertCoverage} from './element247-shell-protocol.mjs';
import {ALL_TERMS,emptyAssembly,scatter,componentSumCheck,vectors,energyZeros} from './fixed-field-integration-assembly.mjs';
export {PATCH,ALL_TERMS};
export const STATES=['control45','terminal46'];
export const QUIET=[195,196,198,199,202,237,240,243,244],SECONDARY=[197,200,203,206,246,248];
export const CORNERS={197:3,200:3,203:2,206:1,246:0,247:0,248:0};
export const BUDGET=Object.freeze({plannedMaterialCalls:497500,maximumMaterialCalls:497500,maximumWallSeconds:300,nodeHeapMiB:1024,maximumRssBytes:2147483648,maximumOutputBytes:67108864,invocations:1});
export const FORCE_GATE_N=1e-5,WORK_GATE_J=5.492029235357012e-7;
export const RESULTS=['PASS_BOUNDED_SELECTIVE_FIXED_PATCH_AGREEMENT','UNRESOLVED_FIXED_PATCH_INTEGRATION'];
export const RECON={forceN:1e-8,energyJ:1e-9};
export function recipe(element,id){
 assert.ok(SECONDARY.includes(element)?['C55','A55'].includes(id):element===247&&['F44','R44','X44'].includes(id),'Unregistered element/rule');
 const corner=CORNERS[element],face=[0,1,2,3].filter(n=>n!==corner),depth=id==='X44'?22:20;
 if(id==='X44')face.splice(0,3,2,3,1);
 const angularParts=id==='C55'?1:id==='A55'?2:4,radialParts=id==='R44'?2:1;
 return {element,id,corner,faceOrder:face,depth,radialParts,angularParts,radialOrder:5,angularOrder:5,points:(depth+1)*125*radialParts*angularParts**2};
}
export const SCHEDULE=[...SECONDARY.flatMap(e=>['C55','A55'].map(id=>recipe(e,id))),...['F44','R44','X44'].map(id=>recipe(247,id))];
export const NORMALIZED_RECIPES=[...new Map(SCHEDULE.map(r=>[`${r.id}-c${r.corner}`,r])).values()];
export const normalizationKey=r=>`${r.id}-c${r.corner}`;
export const regionKey=(r,s)=>`${r.element}-${r.id}-${s}`;
export function* regionRule(r,s){
 assert.deepEqual(r,recipe(r.element,r.id));assert.deepEqual(s,shells(r.depth).find(x=>x.id===s.id));
 const g=GAUSS[5];
 for(let rp=0;rp<r.radialParts;rp++){const dr=(s.hi-s.lo)/r.radialParts,rlo=s.lo+rp*dr;
 for(let ap=0;ap<r.angularParts;ap++)for(let bp=0;bp<r.angularParts;bp++)for(let i=0;i<5;i++)for(let j=0;j<5;j++)for(let k=0;k<5;k++){
  const radial=rlo+dr*g.x[i],a=(ap+g.x[j])/r.angularParts,b=(bp+g.x[k])/r.angularParts,L=[0,0,0,0];
  L[r.corner]=1-radial;L[r.faceOrder[0]]=radial*a;L[r.faceOrder[1]]=radial*(1-a)*b;L[r.faceOrder[2]]=radial*(1-a)*(1-b);
  yield {L,weight:6*dr*g.w[i]*g.w[j]*g.w[k]*(radial*radial*(1-a))/r.angularParts**2,r:radial,shell:s.id,comparisonShell:s.hi<=2**-20?'core':s.id};
 }}
}
export function packPoints(points){const b=Buffer.alloc(points.length*48);points.forEach((p,i)=>[...p.L,p.weight,p.r].forEach((v,d)=>b.writeDoubleLE(v,i*48+d*8)));return b;}
export function canonicalAlpha(alpha,r){return [r.corner,...r.faceOrder].map(i=>alpha[i]);}
export function canonicalPolynomial(poly,r){return {...poly,coefficients:poly.coefficients.map(c=>({...c,multiIndex:canonicalAlpha(c.multiIndex,r)}))};}
export function validateLocal(row,element){
 assert.equal(row.element,element);assert.ok(Number.isInteger(row.pointCount)&&row.pointCount>0&&row.pointCount<=131072);assert.ok(Number.isFinite(row.minimumSampleJ)&&row.minimumSampleJ>1e-6);
 for(const t of ALL_TERMS){assert.ok(Number.isFinite(row.energiesJ[t]));const v=row.localGradientsN[t];assert.ok(Array.isArray(v)&&v.length===10&&v.every(a=>Array.isArray(a)&&a.length===3&&a.every(Number.isFinite)),'Finite complete local forces');}
}
export function regionRow(local,r,s){
 validateLocal(local,r.element);assert.equal(local.pointCount,125*r.radialParts*r.angularParts**2);
 assert.ok(local.shell===undefined||local.shell===s.id);assert.ok(local.id===undefined||local.id===s.id);
 assert.ok(local.comparisonShell===undefined||local.comparisonShell===(s.hi<=2**-20?'core':s.id));
 return {...local,id:s.id,shell:s.id,comparisonShell:s.hi<=2**-20?'core':s.id,lo:s.lo,hi:s.hi};
}
export function constructStage(source,r,rows){
 assert.equal(source.nodes_m.length,585);assert.deepEqual(rows.map(x=>x.shell),shells(r.depth).map(x=>x.id),'Region omission/order');
 const total={element:r.element,pointCount:r.points,minimumSampleJ:Infinity,localGradientsN:vectors(10),energiesJ:energyZeros()},bins=shells(20).map(s=>({element:r.element,shell:s.id,originalShells:[],localGradientsN:vectors(10),energiesJ:energyZeros()})),direct=emptyAssembly(585);
 for(const [i,row] of rows.entries()){
  const expected=regionRow(row,r,shells(r.depth)[i]);assert.deepEqual(row,expected,'Serialized constructor identity');
  const bin=bins.find(x=>x.shell===row.comparisonShell);assert.ok(bin);bin.originalShells.push(row.shell);total.minimumSampleJ=Math.min(total.minimumSampleJ,row.minimumSampleJ);scatter(source,row,direct);
  for(const t of ALL_TERMS){for(const out of [total,bin]){out.energiesJ[t]+=row.energiesJ[t];for(let n=0;n<10;n++)for(let d=0;d<3;d++)out.localGradientsN[t][n][d]+=row.localGradientsN[t][n][d];}}
 }
 assertCoverage(shells(r.depth));let force=0,energy=0;const independent=emptyAssembly(585);scatter(source,total,independent);
 for(const t of ALL_TERMS){energy=Math.max(energy,Math.abs(independent.energiesJ[t]-direct.energiesJ[t]));for(let n=0;n<585;n++)for(let d=0;d<3;d++)force=Math.max(force,Math.abs(independent.nodal[t][n][d]-direct.nodal[t][n][d]));}
 assert.ok(force<=RECON.forceN&&energy<=RECON.energyJ);return {...total,recipe:r,comparisonShells:bins,reconstruction:{maximumForceDifferenceN:force,maximumEnergyDifferenceJ:energy,all585Nodes:true,component:componentSumCheck(direct)}};
}
export function candidateRule(q,e){assert.ok(['Q0','Q1','Q2'].includes(q)&&PATCH.includes(e));return QUIET.includes(e)?{Q0:'D4',Q1:'D5',Q2:'U5'}[q]:SECONDARY.includes(e)?{Q0:'C55',Q1:'A55',Q2:'D5'}[q]:{Q0:'A55',Q1:'F44',Q2:'X44'}[q];}
export function compareUnits(source,units,direction,expectedUnits){
 assert.equal(units.length,expectedUnits);assert.equal(new Set(units.map(x=>x.id)).size,expectedUnits);assert.equal(direction.length,585);
 const terms={};for(const t of ALL_TERMS){const signed=Array.from({length:585},()=>[0,0,0]),triangle=Array.from({length:585},()=>[0,0,0]);let work=0,workTriangle=0;const differences=[];
 for(const unit of units){assert.equal(unit.a.element,unit.b.element);const ids=source.elements_ten_node[unit.a.element];let w=0;const delta=unit.a.localGradientsN[t].map((v,i)=>v.map((x,d)=>{const z=x-unit.b.localGradientsN[t][i][d];assert.ok(Number.isFinite(z));signed[ids[i]][d]+=z;triangle[ids[i]][d]+=Math.abs(z);w+=z*direction[ids[i]][d];return z;}));work+=w;workTriangle+=Math.abs(w);differences.push({id:unit.id,element:unit.a.element,localDifferenceN:delta,directionalDifferenceJ:w});}
 const c={differences,aggregateDifferenceN:signed,absoluteUnitDifferenceN:triangle,aggregateInfinityN:Math.max(...signed.flat().map(Math.abs)),unitTriangleInfinityN:Math.max(...triangle.flat()),aggregateDirectionalDifferenceJ:Math.abs(work),unitTriangleDirectionalDifferenceJ:workTriangle,forceGateN:FORCE_GATE_N,workGateJ:WORK_GATE_J};c.pass=c.aggregateInfinityN<=FORCE_GATE_N&&c.unitTriangleInfinityN<=FORCE_GATE_N&&c.aggregateDirectionalDifferenceJ<=WORK_GATE_J&&c.unitTriangleDirectionalDifferenceJ<=WORK_GATE_J;terms[t]=c;
 }return {units:expectedUnits,differenceSign:'a-minus-b',terms,pass:ALL_TERMS.every(t=>terms[t].pass),qualification:false};
}
